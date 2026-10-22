#!/usr/bin/env python3
"""ep13 대사 미리듣기: 고른 대사(voice/lines/<id>.mp3)를 참조 영상의 그 대사 시작 시각에 놓아 한 파일로(겹치는 맞고함도 그대로 겹침).
사용: python3 tools/ep13_voice_preview.py [--bgm outputs/ep13/bgm/office_tension.mp3 --bgm-db -26] → outputs/ep13/voice/preview.mp3
"""
import argparse, json, os, subprocess
import numpy as np
import imageio_ffmpeg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, 'outputs/ep13')
FF = imageio_ffmpeg.get_ffmpeg_exe(); SR = 44100


def pcm(p):
    return np.frombuffer(subprocess.run([FF, '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--bgm'); ap.add_argument('--bgm-db', type=float, default=-26)
    a = ap.parse_args()
    S = json.load(open(os.path.join(EP, 'script.json')))
    total = max(l['ref'][1] for l in S['lines']) + 1.0
    mix = np.zeros(int(total * SR), np.float32)
    for l in S['lines']:
        p = os.path.join(EP, f'voice/lines/{l["id"]}.mp3')
        if not os.path.exists(p):
            print('없음', l['id']); continue
        x = pcm(p); i = int(l['ref'][0] * SR); n = min(len(x), len(mix) - i)
        mix[i:i + n] += x[:n]
    if a.bgm:
        b = pcm(os.path.join(ROOT, a.bgm))[:len(mix)]
        b = b / (np.sqrt(np.mean(b ** 2)) + 1e-9) * 10 ** (a.bgm_db / 20)
        mix[:len(b)] += b
    out = os.path.join(EP, 'voice/preview.wav')
    import wave
    with wave.open(out, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix, -1, 1) * 32767).astype('<i2').tobytes())
    mp3 = out.replace('.wav', '.mp3')
    subprocess.run([FF, '-y', '-v', 'error', '-i', out, '-c:a', 'libmp3lame', '-q:a', '2', mp3], check=True); os.remove(out)
    print('미리듣기', os.path.relpath(mp3, ROOT), f'{total:.1f}s')


if __name__ == '__main__':
    main()
