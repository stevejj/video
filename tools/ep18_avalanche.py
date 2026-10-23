#!/usr/bin/env python3
"""ep18 2번 옷 산사태 — 0원 버전(Kling 대신).
사용: python3 tools/ep18_avalanche.py [--out outputs/ep18/test/avalanche_free.mp4]
- 0~1.85s F2a: 창수 "입을 옷이… 없다고?" 몸 통통 + 문 덜컹(작은 흔들림이 점점 커짐).
- 1.80s 문틈에서 옷이 화면 쪽으로 튀어나옴 → 흰 번쩍 → F2b(옷 산더미)로 바뀜 + 큰 흔들림 + 위에서 옷이 우르르 떨어짐.
- 산더미가 살짝 눌렸다 펴짐. 꼭대기의 창수 날개 끝이 파닥.
- 옷 조각: F2b 바닥 옷을 ISNet으로 오린 것(outputs/ep18/sprites).
"""
import argparse, os, subprocess, sys, tempfile
import numpy as np
import cv2
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cutout, talk_bob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, 'outputs/ep18')
FF, FPS, W, H = talk_bob.FF, 24, 1080, 1920
K = W / 768
VOICE_AT, BURST, DUR = 0.15, 1.82, 4.4
SPRITES = ['pants', 'beanie', 'dress', 'cardi', 'shirt_y']


def big(p):
    im = Image.open(p).convert('RGB')
    return im.resize((W, int(im.height * K)), Image.LANCZOS)


def cut(img, box):
    x0, y0, x1, y1 = [int(v * K) for v in box]
    al = np.asarray(cutout.alpha(img.crop((x0, y0, x1, y1)), talk_bob.MODEL)).astype(np.float32) / 255
    al = np.clip((al - 0.15) / 0.7, 0, 1)
    full = np.zeros((img.height, img.width), np.float32); full[y0:y1, x0:x1] = al
    base = np.asarray(img)
    mask = cv2.dilate((full > 0.05).astype(np.uint8), np.ones((13, 13), np.uint8))
    plate = Image.fromarray(cv2.inpaint(base, mask * 255, 9, cv2.INPAINT_TELEA))
    ys, xs = np.where(full > 0.5)
    return plate, Image.fromarray(np.dstack([base, (full * 255).astype(np.uint8)]), 'RGBA'), (xs.mean(), ys.max())


def affine(layer, pivot, sx, sy, ang):
    ca, sa = np.cos(np.radians(ang)), np.sin(np.radians(ang))
    inv = np.linalg.inv(np.array([[sx * ca, -sy * sa], [sx * sa, sy * ca]]))
    off = np.array(pivot) - inv @ np.array(pivot)
    return layer.transform(layer.size, Image.AFFINE, (inv[0, 0], inv[0, 1], off[0], inv[1, 0], inv[1, 1], off[1]), Image.BICUBIC)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', default=f'{EP}/test/avalanche_free.mp4')
    a = ap.parse_args()
    A, B = big(f'{EP}/img/F2a_v1.png'), big(f'{EP}/img/F2b_v1.png')
    plateA, chang, footA = cut(A, (200, 735, 430, 1085))
    plateB, wing, _ = cut(B, (360, 605, 435, 695))
    wing_pivot = (int(398 * K), int(690 * K))
    n = int(DUR * FPS)
    env = talk_bob.envelope([('c', f'{EP}/voice/lines/C2.mp3', VOICE_AT)], 'c', n)
    rng = np.random.default_rng(7)
    spr = [Image.open(f'{EP}/sprites/{s}.png') for s in SPRITES]
    spr = [s.crop(s.getbbox()) for s in spr]
    # 문틈에서 튀어나오는 옷(화면 쪽으로 커짐)
    burst = [dict(s=spr[i % 5], dx=rng.uniform(-900, 900), dy=rng.uniform(-700, 500), r=rng.uniform(-400, 400), t0=BURST - 0.06 + i * 0.015) for i in range(7)]
    # 위에서 떨어지는 옷
    rain = [dict(s=spr[i % 5], x=rng.uniform(-60, W - 120), t0=BURST + 0.05 + rng.uniform(0, 0.55), sc=rng.uniform(0.9, 1.6),
                 r0=rng.uniform(0, 360), vr=rng.uniform(-500, 500), fl=rng.random() < 0.5) for i in range(16)]
    gap = (int(390 * K), int(600 * K))
    tmp = tempfile.mkdtemp(prefix='aval_')
    for f in range(n):
        t = f / FPS
        if t < BURST:
            fr = plateA.copy()
            e = env[f]
            layer = affine(chang, footA, 1 - 0.025 * e, 1 + 0.05 * e, 1.5 * e * np.sin(2 * np.pi * 2.2 * t))
            fr.paste(layer, (0, 0), layer)
            amp = 0 if t < 1.0 else 2 + 6 * (t - 1.0) / (BURST - 1.0)
        else:
            fr = plateB.copy()
            u = t - BURST
            sq = 1 + 0.05 * np.exp(-u * 9) * np.cos(u * 28)          # 산더미 눌렸다 펴짐(아래 기준)
            if abs(sq - 1) > 1e-3:
                fr = fr.resize((W, int(fr.height * sq)), Image.BICUBIC); fr = fr.crop((0, fr.height - B.height, W, fr.height))
            ang = 10 * np.sin(2 * np.pi * 6 * t) if 2.9 < t < 3.7 else 0
            wl = affine(wing, wing_pivot, 1, 1, ang)
            fr.paste(wl, (0, 0), wl)
            amp = 30 * np.exp(-u * 5)
        fr = fr.convert('RGBA')
        for b in burst:                                               # 튀어나오는 옷
            u = t - b['t0']
            if 0 <= u < 0.35:
                sc = 0.4 + u * 9
                s = b['s'].rotate(b['r'] * u, expand=True, resample=Image.BICUBIC)
                s = s.resize((max(1, int(s.width * sc)), max(1, int(s.height * sc))), Image.BICUBIC)
                fr.alpha_composite(s, (int(gap[0] + b['dx'] * u * 2.5 - s.width / 2), int(gap[1] + b['dy'] * u * 2.5 - s.height / 2)))
        for d in rain:                                                # 우르르 떨어지는 옷
            u = t - d['t0']
            if 0 <= u < 1.2:
                y = -300 + 3600 * u * u + 500 * u
                if y > fr.height:
                    continue
                s = d['s'].transpose(Image.FLIP_LEFT_RIGHT) if d['fl'] else d['s']
                s = s.resize((int(s.width * d['sc']), int(s.height * d['sc'])), Image.BICUBIC).rotate(d['r0'] + d['vr'] * u, expand=True, resample=Image.BICUBIC)
                fr.alpha_composite(s, (int(d['x']), int(y)))
        fr = fr.convert('RGB')
        if BURST <= t < BURST + 0.17:                                 # 흰 번쩍
            k = 1 - (t - BURST) / 0.17
            fr = Image.blend(fr, Image.new('RGB', fr.size, 'white'), 0.85 * k)
        dx, dy = (rng.uniform(-amp, amp), rng.uniform(-amp, amp)) if amp > 0.5 else (0, 0)
        z = 1.02 + 0.03 * f / n
        cw, ch = W / z, H / z
        cx, cy = W / 2 + dx, fr.height / 2 + dy
        fr.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.LANCZOS).save(f'{tmp}/{f:04d}.png')
    sfx = f'{EP}/sfx/el'
    fc = (f'[1:a]adelay={int(VOICE_AT * 1000)}:all=1[v];[2:a]adelay=1000:all=1,volume=0.7[r];'
          f'[3:a]adelay={int((BURST - 0.05) * 1000)}:all=1[av];[v][r][av]amix=inputs=3:normalize=0,apad[a]')
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    subprocess.run([FF, '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%04d.png', '-i', f'{EP}/voice/lines/C2.mp3',
                    '-i', f'{sfx}/door_rattle.mp3', '-i', f'{sfx}/clothes_avalanche.mp3', '-filter_complex', fc,
                    '-map', '0:v', '-map', '[a]', '-t', str(DUR), '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', a.out], check=True)
    print('완료', a.out)


if __name__ == '__main__':
    main()
