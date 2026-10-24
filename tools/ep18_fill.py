#!/usr/bin/env python3
"""ep18 옷 더미 꼭대기에 옷 3벌 더 얹기(0원) — 사용자 v10·v11.
사용: python3 tools/ep18_fill.py → outputs/ep18/img/<원본>_fill.png
- v10: 날개 지운 자리(F2b_nowing2, 선반 아래 어둡게 번진 곳)를 노랑 티·분홍 가디건·회색 비니로 덮음 → F2b_fill.
- v11(사용자: "창수 튀어나온 다음에도 그렇게 채워 / 여기를 가리라는 거야"): 얼굴 쑥(F4a) 머리 오른쪽, 선반 아래 어둡게 비어 보이는 곳을 옷으로 채움.
  (v11에 F4b·F5·F6·F8 꼭대기를 잘못 짚어 x 300에 얹었다가 산더미가 이상해져 뺐음 → v14에서 자국 자리(405, 665)에 다시 얹음)
- 옷 조각은 F2b 바닥 옷을 ISNet으로 오린 것(outputs/ep18/sprites). 좌표는 768 기준.
"""
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'outputs/ep18/img')
SP = os.path.join(ROOT, 'outputs/ep18/sprites')
TOP = [('shirt_y', 0.95, 8, True, -33, -10), ('cardi', 1.05, -6, False, 3, 3), ('beanie', 0.6, -12, False, 15, -33)]   # 꼭대기 기준 상대 위치
JOBS = {
    'F2b_nowing2': [(405, 665)],                       # 날개 지운 자리
    # v14(사용자 동그라미): 이 장면들은 F2b_nowing을 참조해 만들어져 같은 자리(선반 아래)에 날개 지운 자국이 그대로 옮겨져 있음 → 같은 위치에 같은 옷
    'F4b_v2': [(405, 692)], 'F5_v1': [(405, 692)], 'F6_v1': [(405, 692)], 'F8_v1': [(405, 692)],   # 이 장면들은 더미 윗선이 조금 낮음
}
SIDES = [('shirt_y', 0.95, -10, False, 505, 690), ('cardi', 1.0, 8, False, 468, 700), ('beanie', 0.55, -8, False, 470, 655)]   # F4a: 머리 오른쪽 선반 아래 빈 곳을 옷으로 채움


def sprite(name, sc, rot, flip):
    s = Image.open(os.path.join(SP, name + '.png')); s = s.crop(s.getbbox())
    if flip:
        s = s.transpose(Image.FLIP_LEFT_RIGHT)
    s = s.resize((int(s.width * sc), int(s.height * sc)), Image.LANCZOS).rotate(rot, expand=True, resample=Image.BICUBIC)
    a = np.asarray(s).copy(); al = a[..., 3].astype(np.float32) / 255
    a[..., 3] = (np.clip((al - 0.25) / 0.5, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(a)


def put_all(im, items):
    k = im.width / 768
    for name, sc, rot, flip, x, y in items:
        s = sprite(name, sc * k, rot, flip)
        im.alpha_composite(s, (int(x * k - s.width / 2), int(y * k - s.height / 2)))
    return im


def main():
    for src, peaks in JOBS.items():
        im = Image.open(os.path.join(IMG, src + '.png')).convert('RGBA')
        for px, py in peaks:
            im = put_all(im, [(n, sc, r, f, px + dx, py + dy) for n, sc, r, f, dx, dy in TOP])
        out = 'F2b_fill' if src == 'F2b_nowing2' else src + '_fill'
        im.convert('RGB').save(os.path.join(IMG, out + '.png')); print(out)
    im = put_all(Image.open(os.path.join(IMG, 'F4a_v1.png')).convert('RGBA'), SIDES)
    im.convert('RGB').save(os.path.join(IMG, 'F4a_v1_fill.png')); print('F4a_v1_fill')


if __name__ == '__main__':
    main()
