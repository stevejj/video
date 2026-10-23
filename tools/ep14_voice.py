#!/usr/bin/env python3
"""ep14 김장 수술실 녹음 후처리·재녹음·미리듣기.
사용:
  python3 tools/ep14_voice.py regen 9 5b 3      # 지정 줄을 seed 여러 개로 다시 뽑아 받아쓰기 점수로 채택(드라이 파일)
  python3 tools/ep14_voice.py fx                # 드라이 → 줄별 효과(울림·쉼 늘리기) → lines/<컷>.mp3
  python3 tools/ep14_voice.py preview           # 대사만 이어 붙인 미리듣기
줄별 설정은 프로필 episodes.ep14.lines[*] 의 fx / pauses / gap_before.
- fx "room": 아주 살짝 울림(나는 실패하지 않습니다 3번, 사용자 2026-10-22)
- fx "cave_light": 속마음 동굴 울림을 약하게(3번 "또 시작이네" — 기본 동굴이 너무 세서 안 들림, 사용자)
- pauses: 단어 사이 쉼(초). whisper 단어 시각으로 자르고 무음을 넣음(5b "나는.... 실패하지.... 않습니다")
"""
import json, os, re, subprocess, sys, tempfile, difflib, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_gen as vg

ROOT = vg.ROOT; FF = vg.FF; SR = 44100
LINES = os.path.join(ROOT, 'outputs/ep14/voice/lines')
SEEDS = [42, 7, 1234, 99, 2024, 555, 11, 77]
ROOM = {'pre': 0.04, 'decay': 0.35, 'wet': 0.22, 'band': [300, 6000]}
CAVE_LIGHT_WET = 0.45   # 기본 속마음 1.6 → 약하게
_model = None


def whisper():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        sp = os.environ.get('WHISPER_DIR', os.path.join(tempfile.gettempdir(), 'whisper'))
        _model = WhisperModel('medium', device='cpu', compute_type='int8', download_root=sp)
    return _model


def pcm(path, sr=SR):
    d = subprocess.run([FF, '-loglevel', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(sr), '-'], capture_output=True).stdout
    return np.frombuffer(d, np.float32).copy()


def save(x, path):
    tmp = path + '.wav'
    with wave.open(tmp, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes())
    if path.endswith('.mp3'):
        subprocess.run([FF, '-y', '-loglevel', 'error', '-i', tmp, '-c:a', 'libmp3lame', '-q:a', '2', path], check=True); os.remove(tmp)
    else:
        os.replace(tmp, path)


def heard(x, words=False):
    a = np.concatenate([x, np.zeros(SR // 2, np.float32)])
    a16 = np.interp(np.arange(0, len(a), SR / 16000), np.arange(len(a)), a).astype(np.float32)
    seg, _ = whisper().transcribe(a16, language='ko', beam_size=5, word_timestamps=words)
    seg = list(seg)
    if words:
        return [(w.word.strip(), w.start, w.end) for s in seg for w in s.words]
    return ''.join(s.text for s in seg).strip()


norm = lambda s: re.sub(r'[^가-힣]', '', s)


def regen(P, cuts):
    tmp = tempfile.mkdtemp()
    for l in P['episodes']['ep14']['lines']:
        if l['cut'] not in cuts:
            continue
        ref = norm(l.get('asr_ref', l['subtitle'])); res = []
        for seed in SEEDS[:l.get('n_seeds', 6)]:
            raw = f'{tmp}/{l["cut"]}_{seed}.mp3'
            vg.post(f'/v1/text-to-speech/{P["voices"][l["speaker"]]}?output_format=mp3_44100_128',
                    {'text': vg.tts_text(P, l), 'model_id': P['model_id'], 'language_code': 'ko', 'seed': seed,
                     'voice_settings': dict(P['voice_settings'], speed=vg.speed_for(P, l))}, raw)
            if vg.duration(raw) <= 0:
                continue
            vg.trim(raw, raw + '.t.mp3'); raw += '.t.mp3'
            dry = f'{tmp}/{l["cut"]}_{seed}_dry.mp3'
            sp = vg.finalize(raw, dry, P['loudnorm'], l['speaker'], False, 1.0, l.get('speedup_override'))
            h = heard(pcm(dry)); score = difflib.SequenceMatcher(None, ref, norm(h)).ratio(); d = vg.duration(dry)
            print(f'  {l["cut"]} seed {seed}: {d:.2f}s 들림 "{h}" 점수 {score:.2f}', flush=True)
            res.append((round(score, 1), -abs(d - l['max_len'] * 0.8), seed, dry, d, sp))
        score, _, seed, dry, d, sp = max(res)
        dst = os.path.join(LINES, f'{l["cut"]}_dry.mp3'); os.replace(dry, dst)
        l.update(seed=seed, speedup=sp, tempo=1.0, dry=os.path.relpath(dst, ROOT), asr=score)
        print(f'→ {l["cut"]} 채택 seed {seed} 점수 {score} {d:.2f}s', flush=True)


def room(x):
    from scipy.signal import fftconvolve, butter, sosfilt
    R = ROOM; rng = np.random.default_rng(3); n = int(R['decay'] * 5 * SR); tt = np.arange(n) / SR
    ir = np.concatenate([np.zeros(int(R['pre'] * SR)), rng.standard_normal(n) * np.exp(-tt / R['decay'])]); ir /= np.sqrt((ir ** 2).sum())
    y = np.concatenate([x, np.zeros(int(R['decay'] * 4 * SR), np.float32)])
    wet = sosfilt(butter(2, R['band'], 'bandpass', fs=SR, output='sos'), fftconvolve(y, ir)[:len(y)])
    return y + R['wet'] * wet


def cave_light(x):
    from scipy.signal import fftconvolve
    ir = pcm(os.path.join(ROOT, 'assets/ir/cave_big.wav')); ir /= np.sqrt((ir ** 2).sum())
    y = np.concatenate([x, np.zeros(int(2.0 * SR), np.float32)]) * 10 ** (-3 / 20)
    wet = fftconvolve(y, ir)[:len(y)]
    return y + CAVE_LIGHT_WET * wet


def pitch_shift(path, semitones):
    r = 2 ** (semitones / 12)
    d = subprocess.run([FF, '-loglevel', 'error', '-i', path, '-af', f'asetrate={SR}*{r:.5f},aresample={SR},atempo={1 / r:.5f}',
                        '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(d, np.float32).copy()


def fall_contour(x, drops):
    """구절마다 음높이를 '내려가며 끝나게' 다시 그림(WORLD 보코더). ElevenLabs는 결연한 대사를 끝을 올려 읽음 →
    구절 안의 원래 오르내림 기울기를 빼고, 구절 끝까지 drops[i] 반음 내려가는 기울기를 넣는다. 억양의 작은 굴곡은 남김."""
    import pyworld as pw
    xd = x.astype(np.float64)
    f0, t = pw.harvest(xd, SR, f0_floor=80, f0_ceil=700, frame_period=5)
    sp = pw.cheaptrick(xd, f0, t, SR); ap = pw.d4c(xd, f0, t, SR)
    voiced = f0 > 0
    # 구절 = 0.3s 이상 무성 구간으로 나뉜 덩어리
    idx = np.where(voiced)[0]; phrases = []; s = idx[0]
    for a, b in zip(idx[:-1], idx[1:]):
        if (b - a) * 0.005 > 0.3:
            phrases.append((s, a)); s = b
    phrases.append((s, idx[-1]))
    st = np.zeros_like(f0); st[voiced] = 12 * np.log2(f0[voiced])
    for (a, b), d in zip(phrases, drops):
        m = voiced[a:b + 1]; tt = t[a:b + 1] - t[a]; T = max(tt[-1], 1e-3)
        k = np.polyfit(tt[m], st[a:b + 1][m], 1)[0]
        st[a:b + 1][m] -= k * tt[m] + d * tt[m] / T
    f0n = np.where(voiced, 2 ** (st / 12), 0)
    y = pw.synthesize(f0n, sp, ap, SR, frame_period=5).astype(np.float32)
    print('    구절:', [(round(t[a], 2), round(t[b], 2)) for a, b in phrases], '내림', drops)
    return y[:len(x)] * (np.abs(x).max() / max(1e-6, np.abs(y).max()))


def stretch_pauses(x, gaps):
    """말 안의 쉼(무음 구간)을 앞에서부터 gaps[i]초로 바꿈. whisper 단어 경계는 자음에 걸려 소리를 자를 수 있어 무음 검출로 함."""
    hop = SR // 100; env = np.abs(x[:len(x) // hop * hop]).reshape(-1, hop).max(1)
    quiet = env < 0.02; runs = []; s = None
    for i, q in enumerate(np.append(quiet, False)):
        if q and s is None:
            s = i
        elif not q and s is not None:
            if i - s >= 12 and s > 0:   # 0.12s 이상, 맨 앞 제외
                runs.append((s, i))
            s = None
    runs = [r for r in runs if r[1] < len(env) - 5][:len(gaps)]
    print('    쉼 찾음:', [(a / 100, (b - a) / 100) for a, b in runs])
    out = []; pos = 0
    for (a, b), g in zip(runs, gaps):
        keep = 0.05   # 무음 양 끝 50ms는 남겨 숨 이어짐 유지
        out += [x[pos:(a * hop + int(keep * SR))], np.zeros(max(0, int((g - 2 * keep) * SR)), np.float32)]
        pos = b * hop - int(keep * SR)
    out.append(x[pos:])
    return np.concatenate(out)


def fx(P):
    for l in P['episodes']['ep14']['lines']:
        src = l.get('dry')
        if not src:
            continue
        x = pcm(os.path.join(ROOT, src))
        if l.get('pitch'):   # 반음 단위 음높이만 바꿈(길이 그대로): 2번 "저 오리" 낮게(사용자)
            x = pitch_shift(os.path.join(ROOT, src), l['pitch'])
        if l.get('pauses'):
            x = stretch_pauses(x, l['pauses'])
        if l.get('fall'):
            x = fall_contour(x, l['fall'])
        speech = len(x) / SR
        if l.get('fx') == 'room':
            x = room(x)
        elif l.get('fx') == 'cave_light':
            x = cave_light(x)
        x = x / max(1.0, np.abs(x).max() / 0.95)
        dst = os.path.join(LINES, f'{l["cut"]}.mp3'); save(x, dst)
        l.update(file=os.path.relpath(dst, ROOT), len=round(speech, 2), len_file=round(vg.duration(dst), 2))
        print(f'{l["cut"]}: {l.get("fx", "-")} 쉼 {l.get("pauses")} → 말 {speech:.2f}s')


def preview(P):
    E = P['episodes']['ep14']; t = 0.0; ins = []; fl = []; place = []
    for i, l in enumerate(E['lines']):
        t += l.get('gap_before', 0.3)
        ins += ['-i', os.path.join(ROOT, l['file'])]; ms = int(t * 1000)
        fl.append(f'[{i}:a]adelay={ms}|{ms}[a{i}]'); place.append({'cut': l['cut'], 'at': round(t, 2), 'file': l['file']})
        t += l['len']
    end = t + 2.0; n = len(E['lines'])
    fc = ';'.join(fl) + ';' + ''.join(f'[a{i}]' for i in range(n)) + f'amix=inputs={n}:normalize=0,atrim=0:{end:.2f},alimiter=limit=0.9[o]'
    out = os.path.join(ROOT, 'outputs/ep14/voice/preview.mp3')
    subprocess.run([FF, '-y', '-loglevel', 'error', *ins, '-filter_complex', fc, '-map', '[o]', '-c:a', 'libmp3lame', '-q:a', '2', out], check=True)
    E['placements'] = place; E['preview'] = {'file': os.path.relpath(out, ROOT), 'len': round(end, 2)}
    for p, l in zip(place, E['lines']):
        print(f"{p['at']:6.2f}s {l['cut']:4} {l['len']:.2f}s {l['subtitle']}")
    print('총', round(end, 1), 's')


if __name__ == '__main__':
    P = json.load(open(vg.PROF)); vg.POST = P['post']; vg.SPEEDUP = vg.POST.get('speedup', 1.0)
    cmd = sys.argv[1]
    if cmd == 'regen':
        regen(P, set(sys.argv[2:]))
    elif cmd == 'fx':
        fx(P)
    elif cmd == 'preview':
        preview(P)
    json.dump(P, open(vg.PROF, 'w'), ensure_ascii=False, indent=1)
