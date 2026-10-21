#!/usr/bin/env python3
"""ep11 = ep07 포장마차 클립 재사용(Kling 0) + 새 대사(맥주 광고 따라하기). 0원 조립.
사용: python3 tools/ep11_edit.py → voice/talk_track.wav, voice/s5_track.wav, text_overlay.json, voice_profile ep11 placements
- 새 대사를 원래 대사의 말소리 구간 길이에 맞춰 늘리고 줄임(0.75~1.35배). 입모양은 원래 대사 리듬 그대로.
- 마지막 장면은 원래 s5_track에서 L8 자리만 새 대사로, 뒤 웃음은 그대로.
- 캬~(L7m·L7c), 효과음, 편집표, 효과는 ep07 그대로.
"""
import json, os, re, subprocess, wave
import numpy as np
import imageio_ffmpeg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, 'outputs/ep11'); FF = imageio_ffmpeg.get_ffmpeg_exe(); SR = 44100
# ep07 talk_track 말소리 구간(시작, 길이) — silencedetect로 잼
SLOT = {'L1': (0.23, 1.12), 'L2': (2.13, 1.27), 'L3': (4.23, 1.14), 'L4': (5.85, 0.82), 'L5': (7.93, 0.72), 'L6': (8.94, 0.31)}
L8_SLOT = (0.34, 1.29)   # s5_track 안
S5_AT = 16.45            # ep07 placements의 s5_track 시작


def pcm(f):
    return np.frombuffer(subprocess.run([FF, '-v', 'error', '-i', f, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout, np.float32).copy()


def dur(f):
    return float(re.search(r'Duration: \d+:\d+:([\d.]+)', subprocess.run([FF, '-i', f], capture_output=True, text=True).stderr).group(1))


def fit(src, target, dst):
    r = min(max(dur(src) / target, 0.75), 1.35)
    subprocess.run([FF, '-y', '-v', 'error', '-i', src, '-af', f'atempo={r:.3f}', '-ac', '1', '-ar', str(SR), dst], check=True)
    return r, dur(dst)


def save(x, path):
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes())


def main():
    pp = os.path.join(ROOT, 'outputs/voice_profile.json'); P = json.load(open(pp)); V = P['episodes']['ep11']
    L = {l['cut']: l for l in V['lines']}
    talk = np.zeros(int(9.6 * SR), np.float32); subs = []
    for c, (t0, ln) in SLOT.items():
        dst = os.path.join(EP, f'voice/lines/{c}_fit.wav'); r, d = fit(os.path.join(ROOT, L[c]['file']), ln, dst)
        a = pcm(dst); i = int(t0 * SR); talk[i:i + len(a)] += a[:len(talk) - i]
        subs.append((c, t0, t0 + max(d, ln) + 0.15)); print(f'{c} {r:.2f}배 → {d:.2f}s (자리 {ln}s)')
    save(talk, os.path.join(EP, 'voice/talk_track.wav'))
    dst = os.path.join(EP, 'voice/lines/L8_fit.wav'); r, d = fit(os.path.join(ROOT, L['L8']['file']), L8_SLOT[1], dst)
    s5 = pcm(os.path.join(ROOT, 'outputs/ep07/voice/s5_track.mp3')); s5[int(0.30 * SR):int(1.80 * SR)] = 0
    a = pcm(dst); i = int(L8_SLOT[0] * SR); s5[i:i + len(a)] += a[:len(s5) - i]
    save(s5, os.path.join(EP, 'voice/s5_track.wav')); print(f'L8 {r:.2f}배 → {d:.2f}s')
    subs.append(('L8', S5_AT + L8_SLOT[0], S5_AT + L8_SLOT[0] + max(d, L8_SLOT[1]) + 0.3))

    E7 = P['episodes']['ep07']
    V['placements'] = [{'file': 'outputs/ep11/voice/talk_track.wav', 'at': 0.0}] + [x for x in E7['placements'] if 'L7' in x['file']] + \
                      [{'file': 'outputs/ep11/voice/s5_track.wav', 'at': S5_AT}]
    if E7.get('bgm'):
        V['bgm'] = E7['bgm']
    json.dump(P, open(pp, 'w'), ensure_ascii=False, indent=1)

    T = json.load(open(os.path.join(ROOT, 'outputs/ep07/text_overlay.json')))
    # 제목(사용자): "부부의 초겨울 / 맥주광고 따라하기", 노란색 = "맥주광고"
    T['title']['lines'] = [{'text': '부부의 초겨울', 'color': '#FFFFFF'},
                           {'spans': [{'text': '맥주광고', 'color': '#FFD84A'}, {'text': ' 따라하기', 'color': '#FFFFFF'}]}]
    keep = [s for s in T['subtitles'] if s['speaker'] == 'sfx']          # 캬~
    new = [{'cut': c, 'text': L[c]['subtitle'], 'speaker': L[c]['speaker'], 'start': round(a0, 2), 'end': round(a1, 2), 'x': 0.5} for c, a0, a1 in subs]
    T['subtitles'] = sorted(new + keep, key=lambda s: s['start'])
    T['note'] = 'ep11: ep07 클립 + 새 대사(맥주 광고 따라하기)'
    json.dump(T, open(os.path.join(EP, 'text_overlay.json'), 'w'), ensure_ascii=False, indent=1)
    for s in T['subtitles']:
        print(s['start'], s['end'], s['text'])


if __name__ == '__main__':
    main()
