#!/usr/bin/env python3
"""감정 따라 하기 녹음(ep13~): 대사마다 ElevenLabs v3 후보를 여러 개 만들고, 참조 연기(분리한 목소리)와 감정이 가장 비슷한 것을 고른다.
사용:
  python3 tools/voice_emote.py --ep ep13 ref                  # 참조 대사별 감정 수치 → voice/ref_features.json
  python3 tools/voice_emote.py --ep ep13 gen [--only 01,07]   # 후보 생성(태그 × seed × stability) → voice/cands/<id>/
  python3 tools/voice_emote.py --ep ep13 pick [--only ...]    # 받아쓰기·감정·길이 점수 → 1등을 voice/lines/<id>.mp3 (배속·음량·삐)
입력: outputs/<ep>/script.json (lines: id, sp, ref[시작,끝], text, tags[], sub?)
감정 수치(화자별로 표준화해서 비교 — 남자 배우 vs 미순 목소리처럼 높이가 달라도 '평소보다 얼마나 높고 크고 빠른가'로 맞춤):
  f0 중앙값(반음)·f0 폭(p90-p10)·세기(크게 낸 구간 RMS dB)·밝기(스펙트럼 중심)·말 빠르기(음절/초)
'새끼'는 tts에 그대로 넣어 억양을 살리고, 고른 파일에서 그 자리만 삐 소리로 덮는다(사용자 2026-10-22: 새끼는 삐 처리).
"""
import argparse, json, os, re, subprocess, sys, difflib, time, warnings
from concurrent.futures import ThreadPoolExecutor
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import voice_gen as vg

SR = 16000
warnings.filterwarnings('ignore')
W = {'f0': 1.0, 'f0r': 0.7, 'loud': 1.0, 'bright': 0.8, 'rate': 0.6}
KEYWORDS = ['수박', '옷도', '옷 같은', '명심', '애호박']
BEEP_WORDS = ['새끼', '새기', '세끼', '색기', '새키']


def pcm(path, t0=None, t1=None):
    cmd = [vg.FF, '-v', 'error']
    if t0 is not None:
        cmd += ['-ss', f'{t0:.3f}', '-t', f'{t1 - t0:.3f}']
    cmd += ['-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).copy()


def syllables(text):
    return max(1, len(re.findall(r'[가-힣]', text)))


def features(x, text):
    import librosa
    if len(x) < SR * 0.15:
        x = np.pad(x, (0, int(SR * 0.15) - len(x)))
    hop = 160
    rms = librosa.feature.rms(y=x, frame_length=800, hop_length=hop)[0]
    db = 20 * np.log10(rms + 1e-7)
    act = db > db.max() - 30
    idx = np.where(act)[0]
    dur = (idx[-1] - idx[0] + 1) * hop / SR if len(idx) else len(x) / SR
    loud = float(np.mean(np.sort(db[act])[-max(1, int(act.sum() * 0.5)):]))
    cen = librosa.feature.spectral_centroid(y=x, sr=SR, n_fft=1024, hop_length=hop)[0]
    bright = float(np.log(np.mean(cen[act[:len(cen)]]) + 1))
    f0, vf, _ = librosa.pyin(x, fmin=65, fmax=700, sr=SR, frame_length=1024, hop_length=hop)
    f = f0[vf & ~np.isnan(f0)] if vf is not None else np.array([])
    st = 12 * np.log2(f / 55.0) if len(f) > 3 else None   # 목소리 높이를 못 잡으면(숨소리·짧은 고함) 높이 항목은 비교에서 뺌
    return {'f0': float(np.median(st)) if st is not None else None, 'f0r': float(np.percentile(st, 90) - np.percentile(st, 10)) if st is not None else None,
            'loud': loud, 'bright': bright, 'rate': syllables(text) / max(dur, 0.2), 'dur': round(dur, 3)}


def zscore(rows):
    """rows: {key: feat} → {key: z-feat} (같은 화자 안에서)."""
    out = {}
    keys = list(rows)
    for k in W:
        v = np.array([np.nan if rows[r][k] is None else rows[r][k] for r in keys], float)
        m, s = np.nanmedian(v), max(np.nanstd(v), 1e-6)
        for r, vi in zip(keys, v):
            out.setdefault(r, {})[k] = None if np.isnan(vi) else float((vi - m) / s)
    return out


def paths(ep):
    base = os.path.join(ROOT, f'outputs/{ep}')
    return base, json.load(open(os.path.join(base, 'script.json')))


def cmd_ref(ep):
    base, S = paths(ep)
    voc = os.path.join(base, 'ref/sep/htdemucs/ref_audio/vocals.wav')
    feats = {}
    for l in S['lines']:
        t0, t1 = l['ref']
        feats[l['id']] = dict(features(pcm(voc, t0, t1), l['text']), sp=l['sp'])
    json.dump(feats, open(os.path.join(base, 'voice/ref_features.json'), 'w'), ensure_ascii=False, indent=1)
    print('참조 감정 수치', len(feats), '줄 → voice/ref_features.json')


def cand_list(l, seeds, stabs):
    return [(ti, s, st) for ti in range(len(l['tags'])) for s in seeds for st in stabs]


def cmd_gen(ep, only, seeds, stabs):
    base, S = paths(ep)
    P = json.load(open(vg.PROF))
    jobs = []
    for l in S['lines']:
        if only and l['id'] not in only:
            continue
        d = os.path.join(base, f'voice/cands/{l["id"]}'); os.makedirs(d, exist_ok=True)
        for ti, s, st in cand_list(l, seeds, stabs):
            out = os.path.join(d, f't{ti}_s{s}_st{st}.mp3')
            if not os.path.exists(out + '.t.mp3'):
                jobs.append((l, ti, s, st, out))

    def run(j):
        l, ti, s, st, out = j
        text = f'{l["tags"][ti]} {l["text"]}'
        for k in range(5):   # 동시 요청 한도(3) 초과(429)면 잠깐 쉬고 다시
            try:
                vg.post(f'/v1/text-to-speech/{P["voices"][l["sp"]]}?output_format=mp3_44100_128',
                        {'text': text, 'model_id': P['model_id'], 'language_code': 'ko', 'seed': s,
                         'voice_settings': dict(P['voice_settings'], stability=st)}, out)
                break
            except SystemExit as e:
                if '429' not in str(e) or k == 4:
                    raise
                time.sleep(3 + 3 * k)
        vg.trim(out, out + '.t.mp3')
        return l['id']
    print('후보 생성', len(jobs), '개')
    with ThreadPoolExecutor(2) as ex:
        for i, _ in enumerate(ex.map(run, jobs)):
            if i % 20 == 0:
                print(f'  {i + 1}/{len(jobs)}', flush=True)
    print('완료')


def norm_text(t):
    t = t.replace('씨지엠', 'CGM').replace('네가', '니가').replace('너희', '너네')   # whisper 표기 차이(발음은 같음)
    return re.sub(r'[^가-힣a-zA-Z0-9]', '', t).upper()


def beep(path, words, out):
    """whisper 단어 시각에서 '새끼' 음절 자리를 찾아 원음을 끄고 1kHz 삐로 덮음. 찾은 구간 목록 반환."""
    x = pcm(path).astype(np.float64)
    spans = []
    for w in words:
        txt = re.sub(r'[^가-힣]', '', w['word'])
        for bw in BEEP_WORDS:
            i = txt.find(bw)
            if i >= 0:
                n = len(txt); a = w['start'] + (w['end'] - w['start']) * i / n; b = w['start'] + (w['end'] - w['start']) * (i + 2) / n
                spans.append((max(0, a - 0.03), b + 0.03)); break
    y = x.copy()
    for a, b in spans:
        i0, i1 = int(a * SR), min(len(y), int(b * SR))
        n = i1 - i0
        if n <= 0:
            continue
        env = np.ones(n); f = min(int(0.008 * SR), n // 2)
        if f:
            env[:f] = np.linspace(0, 1, f); env[-f:] = np.linspace(1, 0, f)
        lvl = np.sqrt(np.mean(x[max(0, i0 - SR // 4):i1 + SR // 4] ** 2)) * 1.2
        y[i0:i1] = y[i0:i1] * (1 - env) + np.sin(2 * np.pi * 1000 * np.arange(n) / SR) * lvl * 1.414 * env
    tmp = out + '.wav'
    import wave
    with wave.open(tmp, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((np.clip(y, -1, 1) * 32767).astype('<i2').tobytes())
    subprocess.run([vg.FF, '-y', '-v', 'error', '-i', tmp, '-ar', '44100', '-c:a', 'libmp3lame', '-q:a', '2', out], check=True)
    os.remove(tmp)
    return [[round(a, 3), round(b, 3)] for a, b in spans]


def transcribe(m, path, words=False):
    pad = path + '.pad.wav'
    subprocess.run([vg.FF, '-y', '-v', 'error', '-i', path, '-af', 'adelay=500,apad=pad_dur=0.4', '-ar', str(SR), '-ac', '1', pad], check=True)
    seg, _ = m.transcribe(pad, language='ko', word_timestamps=words, beam_size=5)
    seg = list(seg); os.remove(pad)
    text = ''.join(s.text for s in seg)
    ws = [{'word': w.word, 'start': w.start - 0.5, 'end': w.end - 0.5} for s in seg for w in (s.words or [])] if words else []
    return text, ws


def cmd_pick(ep, only):
    from faster_whisper import WhisperModel
    base, S = paths(ep)
    P = json.load(open(vg.PROF)); vg.POST = P.get('post', {})
    sp_out = vg.POST.get('speedup_outer', 1.0)
    ref = json.load(open(os.path.join(base, 'voice/ref_features.json')))
    m = WhisperModel('medium', compute_type='int8')
    cache_p = os.path.join(base, 'voice/cand_scores.json')
    cache = json.load(open(cache_p)) if os.path.exists(cache_p) else {}
    # 1) 후보 수치(받아쓰기 포함, 캐시)
    for l in S['lines']:
        d = os.path.join(base, f'voice/cands/{l["id"]}')
        for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if not f.endswith('.t.mp3') or f in cache.get(l['id'], {}):
                continue
            p = os.path.join(d, f)
            ft = features(pcm(p), l['text']); ft['dur'] = round(vg.duration(p) / sp_out, 3)
            ft['heard'] = '' if l.get('sub') == '' else transcribe(m, p)[0]
            cache.setdefault(l['id'], {})[f] = ft
        json.dump(cache, open(cache_p, 'w'), ensure_ascii=False, indent=1)
    # 2) 화자별 표준화 → 거리
    zr = {}
    for sp in ('changsu', 'misun'):
        zr.update(zscore({i: f for i, f in ref.items() if f['sp'] == sp}))
    zc = {}
    for sp in ('changsu', 'misun'):
        rows = {(i, f): v for l in S['lines'] if l['sp'] == sp for i in [l['id']] for f, v in cache.get(i, {}).items()}
        zc.update(zscore(rows))
    picks_p = os.path.join(base, 'voice/picks.json')
    picks = json.load(open(picks_p)) if os.path.exists(picks_p) else {}
    outdir = os.path.join(base, 'voice/lines'); os.makedirs(outdir, exist_ok=True)
    for l in S['lines']:
        if (only and l['id'] not in only) or l['id'] not in cache:
            continue
        rdur = l['ref'][1] - l['ref'][0]
        want = norm_text(l['text'])
        rows = []
        for f, v in cache[l['id']].items():
            ks = [k for k in W if zr[l['id']][k] is not None]
            emo = sum(W[k] * abs((zc[(l['id'], f)][k] if zc[(l['id'], f)][k] is not None else 2.0) - zr[l['id']][k]) for k in ks) / sum(W[k] for k in ks)
            heard = norm_text(v['heard'])
            txt = 0.0 if l.get('sub') == '' else (1 - difflib.SequenceMatcher(None, want, heard).ratio()) * 4
            miss = [k for k in KEYWORDS if norm_text(k) in want and norm_text(k) not in heard]
            txt += 1.5 * len(miss)
            dur = max(0, v['dur'] - (rdur + 0.25)) * 2 + max(0, 0.6 * rdur - v['dur'])
            rows.append({'file': f, 'score': round(emo + txt + dur, 3), 'emo': round(emo, 3), 'txt': round(txt, 3), 'dur_pen': round(dur, 3),
                         'dur': v['dur'], 'heard': v['heard'], 'miss': miss})
        rows.sort(key=lambda r: r['score'])
        best = rows[0]
        src = os.path.join(base, f'voice/cands/{l["id"]}/{best["file"]}')
        dst = os.path.join(outdir, f'{l["id"]}.mp3')
        vg.finalize(src, dst, P['loudnorm'], l['sp'], False)
        spans = []
        if '새끼' in l['text']:
            _, ws = transcribe(m, dst, words=True)
            spans = beep(dst, ws, dst + '.b.mp3')
            os.replace(dst + '.b.mp3', dst)
        picks[l['id']] = {'pick': best, 'top': rows[:5], 'n': len(rows), 'beep': spans, 'file': os.path.relpath(dst, ROOT),
                          'len': round(vg.duration(dst), 2), 'ref': l['ref']}
        flag = ' ⚠ 삐 자리 못 찾음' if '새끼' in l['text'] and not spans else ''
        print(f'{l["id"]} {l["sp"]:7s} {best["file"]:22s} 점수 {best["score"]:.2f} (감정 {best["emo"]:.2f} 글자 {best["txt"]:.2f} 길이 {best["dur_pen"]:.2f}) '
              f'{best["dur"]:.2f}s/{rdur:.2f}s 「{best["heard"].strip()}」{flag}')
        json.dump(picks, open(picks_p, 'w'), ensure_ascii=False, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ep', required=True); ap.add_argument('cmd', choices=['ref', 'gen', 'pick'])
    ap.add_argument('--only', default=''); ap.add_argument('--seeds', default='42,7,1234'); ap.add_argument('--stab', default='0.0,0.5')
    a = ap.parse_args(); only = set(x for x in a.only.split(',') if x)
    if a.cmd == 'ref':
        cmd_ref(a.ep)
    elif a.cmd == 'gen':
        cmd_gen(a.ep, only, [int(s) for s in a.seeds.split(',')], [float(s) for s in a.stab.split(',')])
    else:
        cmd_pick(a.ep, only)


if __name__ == '__main__':
    main()
