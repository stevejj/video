#!/usr/bin/env python3
"""말할 때 몸 통통(0원, Kling 대신): 정지 이미지에서 캐릭터를 오려 목소리 크기에 맞춰 들썩이게 한다.
사용: python3 tools/talk_bob.py --img F1.png --out OUT.mp4 \
        --char changsu:125,740,315,1095 --char misun:330,795,535,1095 \
        --line changsu:outputs/ep18/voice/lines/C1a.mp3:0.3 --line misun:outputs/ep18/voice/lines/C1b.mp3:1.9 [--dur 4.0 --push 1.06]
- 캐릭터: ISNet 누끼(tools/cutout.alpha) → 원래 자리는 cv2.inpaint로 메운 배경판.
- 말할 때: 발 기준으로 위로 늘었다(최대 +5%) 옆으로 살짝 줄고(-2.5%), 아주 살짝 좌우 기울기. 쉬는 동안 숨쉬기(±0.8%).
- 화면: 1080x1920, 천천히 밀어 들어가기(--push). 소리 포함 미리보기 mp4.
"""
import argparse, os, subprocess, sys, tempfile
import numpy as np
import cv2
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cutout
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
MODEL = '/tmp/claude-0/-home-user-video/f018d661-8ddb-51f7-8e2d-f2480d28ac5d/scratchpad/models/isnet.onnx'
FPS, W, H, SR = 24, 1080, 1920, 16000


def pcm(path):
    raw = subprocess.run([FF, '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def envelope(lines, name, n):
    """프레임별 0~1 목소리 크기(빨리 오르고 천천히 내려옴)."""
    e = np.zeros(n)
    for who, path, at in lines:
        if who != name:
            continue
        x = pcm(path); hop = SR // FPS
        r = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop, hop)])
        r = r / (np.percentile(r, 95) + 1e-6)
        s = int(round(at * FPS))
        for i, v in enumerate(r):
            if 0 <= s + i < n:
                e[s + i] = max(e[s + i], min(v, 1.2))
    out = np.zeros(n); y = 0.0
    for i in range(n):
        y = e[i] if e[i] > y else y * 0.72 + e[i] * 0.28
        out[i] = y
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--img', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--char', action='append', default=[]); ap.add_argument('--line', action='append', default=[])
    ap.add_argument('--dur', type=float, default=4.0); ap.add_argument('--push', type=float, default=1.06)
    a = ap.parse_args()
    src = Image.open(a.img).convert('RGB')
    k = W / src.width
    big = src.resize((W, int(src.height * k)), Image.LANCZOS)
    base = np.asarray(big).copy()
    chars, union = [], np.zeros(base.shape[:2], np.uint8)
    for c in a.char:
        name, box = c.split(':'); x0, y0, x1, y1 = [int(int(v) * k) for v in box.split(',')]
        al = np.asarray(cutout.alpha(big.crop((x0, y0, x1, y1)), MODEL)).astype(np.float32) / 255
        al = np.clip((al - 0.15) / 0.7, 0, 1)
        full = np.zeros(base.shape[:2], np.float32); full[y0:y1, x0:x1] = al
        rgba = np.dstack([base, (full * 255).astype(np.uint8)])
        ys, xs = np.where(full > 0.5)
        chars.append(dict(name=name, rgba=Image.fromarray(rgba, 'RGBA'), foot=(xs.mean(), ys.max()), top=ys.min()))
        union |= (full > 0.05).astype(np.uint8)
    union = cv2.dilate(union, np.ones((15, 15), np.uint8))
    plate = Image.fromarray(cv2.inpaint(base, union * 255, 9, cv2.INPAINT_TELEA))
    lines = [(w, p, float(t)) for w, p, t in (l.split(':') for l in a.line)]
    n = int(a.dur * FPS)
    env = {c['name']: envelope(lines, c['name'], n) for c in chars}
    tmp = tempfile.mkdtemp(prefix='bob_')
    for f in range(n):
        fr = plate.copy(); t = f / FPS
        for j, c in enumerate(chars):
            e = env[c['name']][f]
            breath = 0.008 * np.sin(2 * np.pi * 0.45 * t + j * 1.7)
            sy, sx = 1 + 0.05 * e + breath, 1 - 0.025 * e - breath * 0.5
            ang = 1.6 * e * np.sin(2 * np.pi * 2.2 * t + j)
            fx, fy = c['foot']
            # 발 기준 확대·기울이기(아핀): 발 위치는 고정
            ca, sa = np.cos(np.radians(ang)), np.sin(np.radians(ang))
            m = np.array([[sx * ca, -sy * sa], [sx * sa, sy * ca]])
            inv = np.linalg.inv(m)
            off = np.array([fx, fy]) - inv @ np.array([fx, fy])
            layer = c['rgba'].transform(c['rgba'].size, Image.AFFINE, (inv[0, 0], inv[0, 1], off[0], inv[1, 0], inv[1, 1], off[1]), Image.BICUBIC)
            fr.paste(layer, (0, 0), layer)
        z = 1 + (a.push - 1) * (0.5 - 0.5 * np.cos(np.pi * f / max(n - 1, 1)))
        cw, ch = W / z, H / z
        tgt = np.mean([(c['top'] + c['foot'][1]) / 2 for c in chars])   # 캐릭터 쪽으로 밀어 들어감
        cx, cy = W / 2, fr.height / 2 + (tgt - fr.height / 2) * (1 - 1 / z) * 2
        cy = min(max(cy, ch / 2), fr.height - ch / 2)
        fr.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.LANCZOS).save(f'{tmp}/{f:04d}.png')
    ins, fc = [], []
    for i, (w, p, t) in enumerate(lines):
        ins += ['-i', p]; fc.append(f'[{i + 1}:a]adelay={int(t * 1000)}:all=1[a{i}]')
    fc.append(''.join(f'[a{i}]' for i in range(len(lines))) + f'amix=inputs={len(lines)}:normalize=0,apad[a]')
    subprocess.run([FF, '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%04d.png', *ins, '-filter_complex', ';'.join(fc),
                    '-map', '0:v', '-map', '[a]', '-t', str(a.dur), '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', a.out], check=True)
    Image.open(f'{tmp}/{n // 2:04d}.png').save(os.path.splitext(a.out)[0] + '_mid.png')
    print('완료', a.out)


if __name__ == '__main__':
    main()
