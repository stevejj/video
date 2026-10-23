#!/usr/bin/env python3
"""ep18 4번 옷 더미에서 창수 얼굴 쑥(0원) v2.
사용: python3 tools/ep18_popup.py [--out outputs/ep18/test/popup_free_v2.mp4]
- v2(사용자): 더미 위로 날개가 보이면 이상함 → 날개 지운 더미(F2b_nowing, 옆 칸 벽을 옮겨 붙여 0원)에서 시작.
  얼굴이 올라올 때 옷 더미도 같이 살짝 무너져야 자연스러움 →
  (1) 더미 꼭대기가 안에서 꿈틀(작게 부풂) → (2) 머리가 올라오며 꼭대기가 크게 부풀었다 가라앉음
  (3) 머리 위에 덮여 있던 옷 3벌이 양쪽 비탈로 미끄러져 내려가 멈춤 → F4a로 섞어 바꿈 → 대사 동안 머리만 통통.
"""
import argparse, os, subprocess, sys, tempfile
import numpy as np
import cv2
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import talk_bob, ep18_avalanche as av

EP = av.EP
FF, FPS, W, H, K = av.FF, av.FPS, av.W, av.H, av.K
WIGGLE, HOLD, RISE, VOICE_AT, DUR = 0.15, 0.55, 0.38, 1.15, 3.0
PILE_Y = int(688 * K)
# 머리 위에서 미끄러져 내려가는 옷: (조각, 출발 x,y → 멈춤 x,y, 회전, 크기) — 768 기준 좌표
SLIDE = [('shirt_y', (395, 650), (255, 805), -38, 0.62), ('beanie', (430, 655), (545, 790), 30, 0.7), ('cardi', (370, 665), (300, 760), -20, 0.55)]


def bulge(img, cx, cy, amp, sx=95 * K, sy=70 * K):
    """(cx, cy) 둘레를 위로 amp px 부풀림(옷 더미가 안에서 밀림)."""
    if abs(amp) < 0.3:
        return img
    a = np.asarray(img)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = float(cx), float(cy)
    g = np.exp(-((xx - cx) ** 2) / (2 * sx ** 2) - ((yy - cy) ** 2) / (2 * sy ** 2))
    return Image.fromarray(cv2.remap(a, xx, (yy + amp * g).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', default=f'{EP}/test/popup_free_v2.mp4')
    a = ap.parse_args()
    B, C = av.big(f'{EP}/img/F2b_nowing.png'), av.big(f'{EP}/img/F4a_v1.png')
    _, head, foot = av.cut(C, (295, 525, 470, 700))
    hx = foot[0]
    pivot = (hx, PILE_Y)
    spr = {}
    for nm, *_ in SLIDE:
        s = Image.open(f'{EP}/sprites/{nm}.png'); spr[nm] = s.crop(s.getbbox())
    n = int(DUR * FPS)
    env = talk_bob.envelope([('c', f'{EP}/voice/lines/C4a.mp3', VOICE_AT)], 'c', n)
    tmp = tempfile.mkdtemp(prefix='pop_')
    import time; T0 = time.time()
    for f in range(n):
        t = f / FPS
        if os.environ.get('POP_DEBUG'): print(f, round(time.time() - T0, 1), flush=True)
        u = t - HOLD
        p = min(max(u / RISE, 0), 1)
        if t < WIGGLE:
            amp = 0
        elif u < 0:                                                    # 안에서 꿈틀
            amp = 7 * abs(np.sin(2 * np.pi * 5 * (t - WIGGLE)))
        else:                                                          # 머리가 밀고 올라오며 부풀었다 가라앉음
            amp = 34 * np.sin(np.pi * min(p * 1.15, 1)) ** 1.2
        if p < 1:
            fr = bulge(B, hx, PILE_Y + 40 * K, amp).convert('RGBA')
            if u >= 0:
                off = (1 - p) ** 2 * 270 - 24 * np.sin(np.pi * p) * (p > 0.6)
                moved = np.asarray(head.transform(head.size, Image.AFFINE, (1, 0, 0, 0, 1, -off), Image.BICUBIC)).copy()
                moved[int(PILE_Y - amp * 0.7):, :, 3] = 0                # 부푼 꼭대기 아래로는 안 보임
                fr.alpha_composite(Image.fromarray(moved, 'RGBA'))
        else:
            fr = C.copy().convert('RGBA')
            e = env[f]
            layer = av.affine(head, pivot, 1 - 0.03 * e, 1 + 0.06 * e, 2 * e * np.sin(2 * np.pi * 2.4 * t))
            fr.alpha_composite(layer)
            k = (u - RISE) / 0.12                                      # 더미 꼭대기 차이를 섞어 숨김
            if k < 1:
                prev = bulge(B, hx, PILE_Y + 40 * K, 0).convert('RGBA'); prev.alpha_composite(head)
                fr = Image.blend(prev, fr, max(k, 0))
        for i, (nm, (x0, y0), (x1, y1), rot, sc) in enumerate(SLIDE):   # 옷이 비탈로 미끄러짐
            q = min(max((t - (HOLD + RISE * (0.5 + i * 0.08))) / 0.45, 0), 1)
            if q <= 0:
                continue
            q = 1 - (1 - q) ** 2                                       # 빨리 출발해 천천히 멈춤
            bounce = 10 * np.sin(np.pi * min(max((q - 0.85) / 0.15, 0), 1))
            x = (x0 + (x1 - x0) * q) * K; y = (y0 + (y1 - y0) * q) * K - bounce
            s = spr[nm].resize((int(spr[nm].width * sc), int(spr[nm].height * sc)), Image.BICUBIC).rotate(rot * q, expand=True, resample=Image.BICUBIC)
            fr.alpha_composite(s, (int(x - s.width / 2), int(y - s.height / 2)))
        fr = fr.convert('RGB')
        sh = 8 * np.exp(-(u - RISE * 0.7) * 12) if u > RISE * 0.7 else 0
        dx, dy = (np.random.uniform(-sh, sh), np.random.uniform(-sh, sh)) if sh > 0.5 else (0, 0)
        z = 1.04 + 0.05 * f / n
        cw, ch = W / z, H / z
        cx, cy = W / 2 + dx, PILE_Y * 0.55 + fr.height * 0.45 / 2 + dy
        cy = min(max(cy, ch / 2), fr.height - ch / 2)
        fr.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.LANCZOS).save(f'{tmp}/{f:04d}.png')
    fc = (f'[1:a]adelay={int(HOLD * 1000)}:all=1[p];[2:a]adelay={int(VOICE_AT * 1000)}:all=1[v];[p][v]amix=inputs=2:normalize=0,apad[a]')
    subprocess.run([FF, '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%04d.png', '-i', f'{EP}/sfx/el/pop_up.mp3', '-i', f'{EP}/voice/lines/C4a.mp3',
                    '-filter_complex', fc, '-map', '0:v', '-map', '[a]', '-t', str(DUR), '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', a.out], check=True)
    print('완료', a.out)


if __name__ == '__main__':
    main()
