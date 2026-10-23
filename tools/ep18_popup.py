#!/usr/bin/env python3
"""ep18 4번 옷 더미에서 창수 얼굴 쑥(0원).
사용: python3 tools/ep18_popup.py [--out outputs/ep18/test/popup_free.mp4]
- F2b(옷 더미, 날개 끝) 잠깐 → 날개 끝 쏙 들어감 → 창수 머리(F4a에서 오림)가 더미 뒤에서 튀어 올라옴(살짝 넘쳤다 자리).
  머리는 더미 윗선(PILE_Y) 아래로는 안 보이게 잘라서 "더미 속에서 나오는" 느낌.
- 다 올라오면 F4a 원본으로 2프레임 섞어 바꿈 → "그럼 이건 다 뭔데?" 동안 머리만 통통.
"""
import argparse, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import talk_bob, ep18_avalanche as av

EP = av.EP
FF, FPS, W, H, K = av.FF, av.FPS, av.W, av.H, av.K
HOLD, RISE, VOICE_AT, DUR = 0.5, 0.32, 1.05, 2.9
PILE_Y = int(688 * K)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', default=f'{EP}/test/popup_free.mp4')
    a = ap.parse_args()
    B, C = av.big(f'{EP}/img/F2b_v1.png'), av.big(f'{EP}/img/F4a_v1.png')
    plateB, wing, _ = av.cut(B, (360, 605, 435, 695))
    _, head, foot = av.cut(C, (295, 525, 470, 700))
    hd = np.asarray(head).copy(); hd[PILE_Y:, :, 3] = 0; head = Image.fromarray(hd, 'RGBA')   # 더미 윗선 아래는 안 보이게
    pivot = (foot[0], PILE_Y)
    n = int(DUR * FPS)
    env = talk_bob.envelope([('c', f'{EP}/voice/lines/C4a.mp3', VOICE_AT)], 'c', n)
    tmp = tempfile.mkdtemp(prefix='pop_')
    for f in range(n):
        t = f / FPS
        u = t - HOLD
        if u < RISE + 0.08:
            fr = plateB.copy().convert('RGBA')
            if u < 0:                                                   # 날개 끝이 파닥하다 쏙
                wl = av.affine(wing, (int(398 * K), int(690 * K)), 1, 1, 8 * np.sin(2 * np.pi * 7 * t))
                fr.alpha_composite(wl)
            else:
                p = min(u / RISE, 1)
                off = (1 - p) ** 2 * 260 - 26 * np.sin(np.pi * p) * (p > 0.6)  # 아래에서 올라와 살짝 넘침
                moved = head.transform(head.size, Image.AFFINE, (1, 0, 0, 0, 1, -off), Image.BICUBIC)
                m = np.asarray(moved).copy(); m[PILE_Y:, :, 3] = 0
                fr.alpha_composite(Image.fromarray(m, 'RGBA'))
            fr = fr.convert('RGB')
        else:
            fr = C.copy()
            e = env[f]
            layer = av.affine(head, pivot, 1 - 0.03 * e, 1 + 0.06 * e, 2 * e * np.sin(2 * np.pi * 2.4 * t))
            # 원래 머리 자리는 그대로 두고(통통은 늘어나는 쪽이라 원본을 덮음) 위에 얹음
            fr = fr.convert('RGBA'); fr.alpha_composite(layer); fr = fr.convert('RGB')
        amp = 9 * np.exp(-(u - RISE) * 12) if u > RISE * 0.8 else 0
        dx, dy = (np.random.uniform(-amp, amp), np.random.uniform(-amp, amp)) if amp > 0.5 else (0, 0)
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
