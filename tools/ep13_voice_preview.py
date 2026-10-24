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
    # 놓을 시각: 참조 시작 시각. 앞 대사가 길어 부딪히면 끝난 뒤 0.05s로 밀고(뒤 빈틈이 흡수), overlap 줄(맞고함)은 그대로 겹침
    place, prev_end, xs = [], 0.0, {}
    for l in sorted(S['lines'], key=lambda l: l['ref'][0]):
        p = os.path.join(EP, f'voice/lines/{l["id"]}.mp3')
        if not os.path.exists(p):
            print('없음', l['id']); continue
        xs[l['id']] = x = pcm(p)
        t = l['ref'][0] if l.get('overlap') else max(l['ref'][0], prev_end + 0.05)
        place.append({'id': l['id'], 'sp': l['sp'], 'at': round(t, 3), 'len': round(len(x) / SR, 3), 'shift': round(t - l['ref'][0], 3)})
        prev_end = max(prev_end, t + len(x) / SR)
    total = prev_end + 1.0
    mix = np.zeros(int(total * SR), np.float32)
    for pl in place:
        x = xs[pl['id']]; i = int(pl['at'] * SR); mix[i:i + len(x)] += x
    json.dump(place, open(os.path.join(EP, 'voice/placements.json'), 'w'), ensure_ascii=False, indent=1)
    print('밀린 줄:', [(p_['id'], p_['shift']) for p_ in place if p_['shift'] > 0.01])
    if a.bgm:
        # 배경음은 71s쯤 이미 사라지므로 마지막 대사 끝까지 가게 살짝 느리게 늘림(높이 그대로)
        tempo = max(0.85, min(1.0, 71.0 / (total - 0.5)))
        b = np.frombuffer(subprocess.run([FF, '-v', 'error', '-i', os.path.join(ROOT, a.bgm), '-af', f'atempo={tempo:.4f}', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                                         capture_output=True).stdout, np.float32)[:len(mix)]
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
