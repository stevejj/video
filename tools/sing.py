#!/usr/bin/env python3
"""캐릭터 목소리로 노래 부르기(ep15~, 0원 + ElevenLabs 말하기 녹음).
원곡 목소리(분리)에서 음절마다 시작 시각·음정 곡선을 뽑고(악보), 미순·창수가 가사를 '말한' 녹음을
WORLD 보코더로 음절 길이를 맞추고 원곡 음정 곡선을 입혀 노래로 만든다. 원곡 가수 목소리는 결과에 들어가지 않는다.
사용:
  python3 tools/sing.py --ep ep15 score     # 악보: ref/score.json (음절 on/off) + ref/f0_crepe.npy(10ms 음정 곡선)
  python3 tools/sing.py --ep ep15 tts       # 줄마다 말하기 녹음(배속 1.25 = 캐릭터 음색) → sing/tts/<id>_<sp>.wav
  python3 tools/sing.py --ep ep15 synth     # 노래 합성 → sing/<sp>.wav (전체 시간축), sing/report.json(음정·박자 오차)
입력: outputs/<ep>/ref/lyrics.json (lines: id, sp changsu|misun|both, t[시작,끝], text, lang?), ref/sep/htdemucs/ref_audio/vocals.wav
가사·원곡·악보는 저작권 때문에 ref/(gitignore)에만 둔다.
"""
import argparse, json, os, re, subprocess, sys, warnings
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import voice_emote as ve
import voice_gen as vg
warnings.filterwarnings('ignore')

FS = 44100
FP = 5.0                 # WORLD 프레임 간격(ms)
CORR = 0.6               # 음정 보정: 가장 가까운 반음 쪽으로 당기는 정도(0=원곡 곡선 그대로, 1=반음에 딱)
_MMS = {}


def base(ep):
    return os.path.join(ROOT, f'outputs/{ep}')


def units(line):
    """정렬 단위: 한글은 음절, 영어는 단어. (보이는 글자, MMS 토큰)"""
    if line.get('lang') == 'en':
        ws = re.findall(r"[A-Za-z']+", line['text'])
        return [(w, re.sub(r"[^a-z]", '', w.lower())) for w in ws]
    return [(c, ve.romanize(c)) for c in re.findall(r'[가-힣]', line['text'])]


def mms_align(x16, toks):
    import torch, torchaudio
    if not _MMS:
        bd = torchaudio.pipelines.MMS_FA
        _MMS.update(model=bd.get_model(with_star=False), tok=bd.get_tokenizer(), al=bd.get_aligner())
    t = torch.from_numpy(np.ascontiguousarray(x16, dtype=np.float32))[None]
    with torch.inference_mode():
        em, _ = _MMS['model'](t)
    sp = _MMS['al'](em[0], _MMS['tok'](toks))
    fr = t.shape[1] / em.shape[1] / 16000
    return [(s[0].start * fr, s[-1].end * fr) for s in sp]


def env10(x16):
    h = 160
    return np.array([np.sqrt(np.mean(x16[i:i + h] ** 2)) + 1e-7 for i in range(0, len(x16) - h, h)])


# ───────────── 악보 ─────────────
def boundary_candidates(md, voiced, edb, i0, i1):
    """음절 경계 후보(10ms 프레임 번호, 세기): 음이 바뀌는 곳·자음 때문에 소리가 잠깐 작아지는 골·소리가 끊겼다 다시 나는 곳."""
    c = {}
    for i in range(i0 + 8, i1 - 8):
        L = md[i - 8:i - 2]; R = md[i + 2:i + 8]
        L = L[~np.isnan(L)]; R = R[~np.isnan(R)]
        if len(L) >= 3 and len(R) >= 3:
            d = abs(np.median(R) - np.median(L))
            if d >= 0.7:
                c[i] = max(c.get(i, 0), 1.0 + min(d, 4) / 2)
    sm = np.convolve(edb, np.ones(3) / 3, 'same')
    for i in range(i0 + 3, i1 - 3):
        if sm[i] <= sm[i - 1] and sm[i] <= sm[i + 1]:
            depth = min(sm[max(i0, i - 10):i].max(), sm[i + 1:min(i1, i + 11)].max()) - sm[i]
            if depth >= 3:
                c[i] = max(c.get(i, 0), min(depth, 15) / 5)
    for i in range(i0 + 4, i1):
        if voiced[i] and not voiced[i - 1] and not voiced[max(i0, i - 4):i].any():
            c[i] = max(c.get(i, 0), 1.5)
    # 가까운 후보(80ms 안)는 센 것 하나만
    keep = []
    for i in sorted(c, key=lambda k: -c[k]):
        if all(abs(i - j) >= 8 for j in keep):
            keep.append(i)
    return sorted((i, c[i]) for i in keep)


def choose(cands, prior, sigma=0.3, lam=1.0, gap=8):
    """후보 중 len(prior)개를 순서대로 골라, 기준 시각(prior, 10ms 프레임)과 가까우면서 센 경계가 되게(DP). sigma는 숫자 또는 음절별 목록(초)."""
    sig = sigma if isinstance(sigma, (list, tuple)) else [sigma] * len(prior)
    n, m = len(prior), len(cands)
    if n == 0:
        return []
    if m < n:
        return list(prior)
    INF = 1e18; cost = np.full((n, m), INF); back = np.zeros((n, m), int)
    for j, (c, w) in enumerate(cands):
        cost[0, j] = ((c - prior[0]) / 100) ** 2 / (2 * sig[0] ** 2) - lam * w
    for k in range(1, n):
        best, bj = INF, -1; jj = 0
        for j, (c, w) in enumerate(cands):
            while jj < j and cands[jj][0] <= c - gap:
                if cost[k - 1, jj] < best:
                    best, bj = cost[k - 1, jj], jj
                jj += 1
            if bj >= 0:
                cost[k, j] = best + ((c - prior[k]) / 100) ** 2 / (2 * sig[k] ** 2) - lam * w; back[k, j] = bj
    j = int(np.argmin(cost[n - 1])); out = []
    for k in range(n - 1, -1, -1):
        out.append(cands[j][0]); j = back[k, j]
    return out[::-1]


def whisper_anchors(B, l, us):
    """whisper 단어 시작 시각(ref/whisper_words.txt)을 가사 음절에 맞춰, 단어 첫 음절의 기준 시각으로 씀. {음절 번호: 초}"""
    import difflib
    ws = []
    for ln in open(os.path.join(B, 'ref/whisper_words.txt')):
        for w, t in re.findall(r'(\S+)@([\d.]+)', ln):
            ws.append((w, float(t)))
    a, b = l['t']
    ws = [(w, t) for w, t in ws if a - 0.3 <= t <= b + 0.3]
    if l.get('lang') == 'en':
        wl = [re.sub(r"[^a-z]", '', w.lower()) for w, _ in ws]
        ul = [u[1] for u in us]
        sm = difflib.SequenceMatcher(None, ul, wl)
        return {i: ws[j][1] for blk in sm.get_matching_blocks() for i, j in zip(range(blk.a, blk.a + blk.size), range(blk.b, blk.b + blk.size))}
    wsy, first = [], []
    for w, t in ws:
        sy = re.findall(r'[가-힣]', w)
        for k, c in enumerate(sy):
            wsy.append(c); first.append(t if k == 0 else None)
    ly = [u[0] for u in us]
    sm = difflib.SequenceMatcher(None, ly, wsy, autojunk=False)
    out = {}
    for blk in sm.get_matching_blocks():
        for i, j in zip(range(blk.a, blk.a + blk.size), range(blk.b, blk.b + blk.size)):
            if first[j] is not None:
                out[i] = first[j]
    return out


def cmd_score(ep, mode='dp'):
    B = base(ep); L = json.load(open(os.path.join(B, 'ref/lyrics.json')))['lines']
    voc = ve.pcm(os.path.join(B, 'ref/sep/htdemucs/ref_audio/vocals.wav'))
    f0p = os.path.join(B, 'ref/f0_crepe.npy')
    if not os.path.exists(f0p):
        import torch, torchcrepe
        f, p = torchcrepe.predict(torch.tensor(voc)[None], 16000, hop_length=160, fmin=70, fmax=1000, model='full',
                                  decoder=torchcrepe.decode.viterbi, return_periodicity=True, batch_size=512, device='cpu')
        np.save(f0p, np.stack([f[0].numpy(), p[0].numpy()]))
    f0, per = np.load(f0p)
    voiced = per > 0.4
    md = np.where(voiced, 69 + 12 * np.log2(np.maximum(f0, 1) / 440), np.nan)
    e = env10(voc); edb = 20 * np.log10(e)
    out = []
    for l in L:
        a, b = l['t']; us = units(l)
        sp = mms_align(voc[int(a * 16000):int(b * 16000)], [u[1] for u in us])
        ctc = [int((a + s[0]) * 100) for s in sp]
        anc = whisper_anchors(B, l, us)            # 단어 첫 음절 = whisper 단어 시작(±0.12s), 나머지 = CTC(±0.4s)
        prior = [int(anc[k] * 100) if k in anc else ctc[k] for k in range(len(us))]
        sig = [0.12 if k in anc else 0.4 for k in range(len(us))]
        i0, i1 = int(a * 100), min(len(edb), int(b * 100))
        top = np.percentile(edb[i0:i1], 95)
        act = np.where((edb[i0:i1] > top - 25) & voiced[i0:i1])[0]
        allc = boundary_candidates(md, voiced, edb, i0, i1)
        # 첫 음절: 기준 시각 -0.1~+0.45s 안에서 '소리가 다시 나는 곳' 중 가장 센 것(앞 줄 꼬리 소리를 피함)
        st = [(c, w) for c, w in allc if prior[0] - 10 <= c <= prior[0] + 45]
        first = max(st, key=lambda cw: cw[1])[0] if st else (i0 + int(act[0]) if len(act) else ctc[0])
        cands = [(c, w) for c, w in allc if c > first + 6]
        ons = [first] + choose(cands, prior[1:], sig[1:]) if mode == 'dp' else ctc
        syl = []
        for k, u in enumerate(us):
            on = ons[k] / 100; nxt = ons[k + 1] / 100 if k + 1 < len(ons) else (i0 + int(act[-1]) + 1) / 100 if len(act) else b
            off = nxt - 0.02; quiet = 0
            for i in range(ons[k] + 6, int(nxt * 100)):
                quiet = quiet + 1 if edb[i] < top - 28 else 0
                if quiet >= 8:
                    off = (i - 7) / 100; break
            off = max(off, on + 0.08)
            j0, j1 = int(on * 100), int(off * 100) + 1; m = voiced[j0:j1]
            hz = float(np.median(f0[j0:j1][m])) if m.any() else 0.0
            syl.append({'u': u[0], 'on': round(on, 3), 'off': round(off, 3), 'hz': round(hz, 1),
                        'midi': round(69 + 12 * np.log2(hz / 440), 2) if hz else None})
        out.append({'id': l['id'], 'sp': l['sp'], 'syl': syl})
        print(l['id'], l['sp'], ' '.join(f"{s['u']}{s['on']:.2f}/{(s['midi'] or 0):.0f}" for s in syl))
    json.dump({'lines': out}, open(os.path.join(B, f'ref/score_{mode}.json'), 'w'), ensure_ascii=False, indent=1)


# ───────────── 말하기 녹음 ─────────────
def cmd_tts(ep, seed):
    B = base(ep); L = json.load(open(os.path.join(B, 'ref/lyrics.json')))['lines']
    P = json.load(open(vg.PROF)); d = os.path.join(B, 'sing/tts'); os.makedirs(d, exist_ok=True)
    for l in L:
        for sp in (['misun', 'changsu'] if l['sp'] == 'both' else [l['sp']]):
            out = os.path.join(d, f'{l["id"]}_{sp}.wav')
            if os.path.exists(out):
                continue
            raw = out.replace('.wav', '.mp3')
            vg.post(f'/v1/text-to-speech/{P["voices"][sp]}?output_format=mp3_44100_128',
                    {'text': f'[softly] {l["text"]}', 'model_id': P['model_id'], 'language_code': l.get('lang', 'ko'), 'seed': seed,
                     'voice_settings': dict(P['voice_settings'], stability=0.5)}, raw)
            vg.trim(raw, raw + '.t.mp3')
            # 캐릭터 음색 = 배속 1.25(높이+속도, voice_profile post.speedup_outer). 길이는 합성에서 다시 맞춤
            subprocess.run([vg.FF, '-y', '-v', 'error', '-i', raw + '.t.mp3', '-af', f'asetrate={FS}*1.25,aresample={FS}', '-ac', '1', '-ar', str(FS), out], check=True)
            print('녹음', os.path.relpath(out, ROOT))


# ───────────── 합성 ─────────────
def target_midi(f0, per, t):
    """참조 곡선(10ms)에서 시각 t들의 목표 음정(midi). 끊긴 곳은 앞뒤로 이어 채우고, 80ms 중앙값 기준 가장 가까운 반음으로 CORR만큼 당김."""
    idx = np.clip((t * 100).astype(int), 0, len(f0) - 1)
    hz = np.where(per[idx] > 0.35, f0[idx], np.nan)
    m = 69 + 12 * np.log2(hz / 440)
    ok = ~np.isnan(m)
    if ok.sum() == 0:
        return None
    m = np.interp(np.arange(len(m)), np.where(ok)[0], m[ok])
    k = max(1, int(80 / FP)); pad = np.pad(m, (k, k), mode='edge')
    smooth = np.array([np.median(pad[i:i + 2 * k + 1]) for i in range(len(m))])
    note = np.round(smooth)
    return note + (1 - CORR) * (m - note)


def synth_line(x, syl_src, syl_dst, f0ref, perref, t_line0, n_frames_total, out_f0, out_sp, out_ap, sp_floor):
    import pyworld as pw
    f0s, ts = pw.harvest(x, FS, f0_floor=70, f0_ceil=1000, frame_period=FP)
    sps = pw.cheaptrick(x, f0s, ts, FS); aps = pw.d4c(x, f0s, ts, FS)
    ns = len(f0s)
    for (s0, s1), sd in zip(syl_src, syl_dst):
        d0, d1 = sd['on'], sd['off']
        i0, i1 = int(s0 * 1000 / FP), max(int(s0 * 1000 / FP) + 2, int(s1 * 1000 / FP))
        i1 = min(i1, ns)
        vo = np.where(f0s[i0:i1] > 0)[0]
        c = int(vo[0]) if len(vo) else 0                         # 첫 유성(모음) 프레임까지 = 자음
        c = min(c, int(0.12 * 1000 / FP), max(0, (i1 - i0) - 2))
        j0, j1 = int(d0 * 1000 / FP), min(n_frames_total, int(d1 * 1000 / FP))
        n = j1 - j0
        if n <= 1:
            continue
        cons = min(c, n // 3)
        src_idx = np.concatenate([np.linspace(i0, i0 + c, cons, endpoint=False),
                                  np.linspace(i0 + c, i1 - 1, n - cons)]).astype(int)
        src_idx = np.clip(src_idx, 0, ns - 1)
        tm = np.arange(j0, j1) * FP / 1000
        mid = target_midi(f0ref, perref, tm)
        voiced = f0s[src_idx] > 0
        voiced[cons:] = True if mid is not None else voiced[cons:]
        tgt = 440 * 2 ** ((mid - 69) / 12) if mid is not None else f0s[src_idx]
        sp = sps[src_idx].copy(); ap = aps[src_idx].copy()
        # 음절 끝 40ms 부드럽게 줄임(뚝 끊김 방지)
        r = min(n, int(40 / FP)); g = np.ones(n); g[-r:] = np.linspace(1, 0.05, r)
        sp *= (g ** 2)[:, None]
        out_f0[j0:j1] = np.where(voiced, tgt, 0); out_sp[j0:j1] = np.maximum(sp, sp_floor); out_ap[j0:j1] = ap


def cmd_synth(ep, mode='dp'):
    import pyworld as pw
    B = base(ep); L = {l['id']: l for l in json.load(open(os.path.join(B, 'ref/lyrics.json')))['lines']}
    SC = json.load(open(os.path.join(B, f'ref/score_{mode}.json')))['lines']
    f0ref, perref = np.load(os.path.join(B, 'ref/f0_crepe.npy'))
    total = len(f0ref) / 100 + 1.0
    nf = int(total * 1000 / FP) + 1; fft = pw.get_cheaptrick_fft_size(FS); nb = fft // 2 + 1
    tracks = {}
    report = []
    for sp in ('misun', 'changsu'):
        F = np.zeros(nf); SP = np.full((nf, nb), 1e-12); AP = np.ones((nf, nb))
        for ln in SC:
            if ln['sp'] not in (sp, 'both'):
                continue
            l = L[ln['id']]
            x = ve.pcm(os.path.join(B, f'sing/tts/{ln["id"]}_{sp}.wav')).astype(np.float64)   # 16k로 정렬
            al = mms_align(x.astype(np.float32), [u[1] for u in units(l)])
            ex = 20 * np.log10(env10(x))
            on = [max(0.0, al[0][0] - 0.04)]
            for k in range(1, len(al)):   # 두 음절 사이 경계 = 앞 음절 정렬 끝~뒤 음절 정렬 시작(+30ms) 사이 가장 작은 소리(자음이 뒤 음절로 가게)
                i0 = int(al[k - 1][1] * 100); i1 = max(i0 + 1, int(al[k][0] * 100) + 3)
                on.append((i0 + int(np.argmin(ex[i0:i1]))) / 100 if i1 <= len(ex) else al[k][0])
            on.append(len(x) / 16000)
            syl_src = [(on[k], on[k + 1]) for k in range(len(al))]
            x44 = subprocess.run([vg.FF, '-v', 'error', '-i', os.path.join(B, f'sing/tts/{ln["id"]}_{sp}.wav'), '-ac', '1', '-ar', str(FS), '-f', 'f64le', '-'],
                                 capture_output=True).stdout
            x44 = np.frombuffer(x44, np.float64).copy()
            synth_line(x44, syl_src, ln['syl'], f0ref, perref, l['t'][0], nf, F, SP, AP, 1e-12)
        y = pw.synthesize(F, SP, AP, FS, FP)
        y = y / (np.max(np.abs(y)) + 1e-9) * 0.7
        p = os.path.join(B, f'sing/{mode}_{sp}.wav'); write_wav(p, y, FS); tracks[sp] = p
        print('합성', os.path.relpath(p, ROOT), f'{len(y) / FS:.1f}s')
    json.dump(evaluate(B, SC, f0ref, perref, mode), open(os.path.join(B, f'sing/report_{mode}.json'), 'w'), ensure_ascii=False, indent=1)


def cmd_eval(ep, mode='dp'):
    B = base(ep); SC = json.load(open(os.path.join(B, f'ref/score_{mode}.json')))['lines']
    f0ref, perref = np.load(os.path.join(B, 'ref/f0_crepe.npy'))
    json.dump(evaluate(B, SC, f0ref, perref, mode), open(os.path.join(B, f'sing/report_{mode}.json'), 'w'), ensure_ascii=False, indent=1)


def write_wav(p, y, fs):
    import wave
    with wave.open(p, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(fs); w.writeframes((np.clip(y, -1, 1) * 32767).astype('<i2').tobytes())


def evaluate(B, SC, f0ref, perref, mode='dp'):
    """합성 결과를 다시 CREPE로 재서 줄마다 음정 오차(센트, 중앙값·90%)와 음절 시작 오차(ms) 보고."""
    import torch, torchcrepe, difflib
    from faster_whisper import WhisperModel
    wm = WhisperModel('medium', compute_type='int8')
    rep = {}
    L = {l['id']: l for l in json.load(open(os.path.join(B, 'ref/lyrics.json')))['lines']}
    for sp in ('misun', 'changsu'):
        x = ve.pcm(os.path.join(B, f'sing/{mode}_{sp}.wav'))
        f, p = torchcrepe.predict(torch.tensor(x)[None], 16000, hop_length=160, fmin=70, fmax=1000, model='full',
                                  decoder=torchcrepe.decode.viterbi, return_periodicity=True, batch_size=512, device='cpu')
        f, p = f[0].numpy(), p[0].numpy()
        for ln in SC:
            if ln['sp'] not in (sp, 'both'):
                continue
            a, b = ln['syl'][0]['on'], ln['syl'][-1]['off']
            i0, i1 = int(a * 100), min(len(f), int(b * 100))
            m = (p[i0:i1] > 0.5) & (perref[i0:i1] > 0.5)
            cents = np.abs(1200 * np.log2(f[i0:i1][m] / f0ref[i0:i1][m])) if m.any() else np.array([np.nan])
            l = L[ln['id']]
            w0 = max(0.0, a - 0.3)
            al = mms_align(x[int(w0 * 16000):int((b + 0.3) * 16000)], [u[1] for u in units(l)])
            on_err = [abs((w0 + s0) - s['on']) * 1000 for (s0, _), s in zip(al, ln['syl'])]
            seg = x[int(w0 * 16000):int((b + 0.3) * 16000)]
            tmp = os.path.join(B, f'sing/_e.wav'); write_wav(tmp, np.concatenate([np.zeros(8000), seg, np.zeros(6400)]), 16000)
            heard = ''.join(t.text for t in wm.transcribe(tmp, language=l.get('lang', 'ko'), beam_size=5)[0]); os.remove(tmp)
            nt = lambda z: re.sub(r'[^가-힣a-z]', '', z.lower())
            words = round(difflib.SequenceMatcher(None, nt(l['text']), nt(heard)).ratio(), 2)
            rep[f'{ln["id"]}_{sp}'] = {'words': words, 'heard': heard.strip(), 'cents_med': round(float(np.nanmedian(cents)), 1), 'cents_p90': round(float(np.nanpercentile(cents, 90)), 1),
                                       'onset_ms_med': round(float(np.median(on_err)), 1), 'onset_ms_max': round(float(np.max(on_err)), 1)}
            print(ln['id'], sp, rep[f'{ln["id"]}_{sp}'])
    return rep


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ep', required=True); ap.add_argument('cmd', choices=['score', 'tts', 'synth', 'eval'])
    ap.add_argument('--seed', type=int, default=42); ap.add_argument('--mode', default='dp', choices=['dp', 'ctc'])
    a = ap.parse_args()
    {'score': lambda: cmd_score(a.ep, a.mode), 'tts': lambda: cmd_tts(a.ep, a.seed), 'synth': lambda: cmd_synth(a.ep, a.mode),
     'eval': lambda: cmd_eval(a.ep, a.mode)}[a.cmd]()


if __name__ == '__main__':
    main()
