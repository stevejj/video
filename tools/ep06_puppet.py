#!/usr/bin/env python3
"""ep06 퍼펫 재료(무료 애니매틱·Kling 실패 대비): K1에서 창수·미순을 오려내고, 둘이 빠진 배경판을 만든다.
plate = K1 - 창수 - 미순 (붐박스는 남김 → 붐박스 레이어 불필요, 08 F8)
"""
import json, os, subprocess, sys
import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'outputs/ep06/puppet')
K1 = os.path.join(ROOT, 'outputs/ep06/01/start_v1.png')
CUTS = {  # id: (박스, 추가 인자) — 창수는 어두워서 추론용만 밝힘, 미순은 날개 알파 강화
    'changsu': ((20, 500, 330, 1040), ['--gamma', '0.45']),
    'misun': ((300, 580, 588, 930), ['--boost', '0.5']),
}
BOOMBOX = (560, 812, 740, 965)


def main():
    os.makedirs(OUT, exist_ok=True)
    meta = {'src_width': 768, 'note': '배경판에서 지운 소품은 레이어로 다시 얹을 것(08 F8)', 'removed_props': {'plate': ['changsu', 'misun']}}
    k1 = cv2.imread(K1); masks = {}
    for k, (box, extra) in CUTS.items():
        full = os.path.join(OUT, f'{k}_full.png'); mk = os.path.join(OUT, f'{k}_mask.png')
        subprocess.run([sys.executable, os.path.join(ROOT, 'tools/cutout.py'), '--img', K1, '--box', *map(str, box),
                        '--out', full, '--mask-out', mk, *extra], check=True)
        im = Image.open(full); a = np.asarray(im.getchannel('A')).copy()
        if k == 'misun':  # 붐박스 조각 제거(붐박스 박스 안 노란색·아래쪽)
            hsv = cv2.cvtColor(k1, cv2.COLOR_BGR2HSV)
            yellow = (hsv[..., 0] >= 15) & (hsv[..., 0] <= 35) & (hsv[..., 1] > 120)
            x0, y0, x1, y1 = BOOMBOX; inb = np.zeros_like(yellow); inb[y0:y1, x0:x1] = True
            low = np.zeros_like(yellow); low[835:y1, 560:x1] = True
            a[(inb & yellow) | low] = 0
        im.putalpha(Image.fromarray(a))
        bb = Image.fromarray(a).point(lambda v: 255 if v > 8 else 0).getbbox()
        im.crop(bb).save(os.path.join(OUT, f'{k}.png'))
        meta[k] = {'box': [bb[0], bb[1], bb[2] - bb[0], bb[3] - bb[1]]}
        masks[k] = a > 30
        os.remove(full); Image.fromarray(a).save(mk)
    ker = np.ones((7, 7), np.uint8)
    hole = cv2.dilate((masks['changsu'] | masks['misun']).astype(np.uint8), ker, iterations=3) > 0
    plate = k1.copy(); H, W = hole.shape
    # 1) 미순 뒤 벽돌: 오른쪽 190px 벽돌 복사(붐박스·구멍은 피함), 바닥(y>=880)은 아래 바닥 결. 창수 자리는 2)에서 inpaint
    bx0, by0, bx1, by1 = BOOMBOX; boom = np.zeros_like(hole); boom[by0:by1, bx0:bx1] = True
    ys, xs = np.nonzero(hole)
    order = np.argsort(-ys)  # 아래부터 채워서 위쪽 복사원이 먼저 채워지게
    done = ~hole.copy()
    for y, x in zip(ys[order], xs[order]):
        if x < 300:  # 창수 자리: 그림자 띠가 반복되므로 복사하지 않고 inpaint(거의 항상 창수가 가림)
            continue
        if y < 880:
            sx, sy = x + 190, y
        else:
            sx, sy = x, y + 120
        if sx < W and sy < H and done[sy, sx] and not boom[sy, sx]:
            plate[y, x] = plate[sy, sx]; done[y, x] = True
    # 2) 남은 곳·경계만 inpaint(붐박스 색이 번지지 않게 붐박스도 잠시 '모름'으로)
    rest = (~done) | (cv2.dilate(hole.astype(np.uint8), ker, iterations=1).astype(bool) & ~cv2.erode(hole.astype(np.uint8), ker, iterations=1).astype(bool))
    plate = cv2.inpaint(plate, ((rest | boom) * 255).astype(np.uint8), 5, cv2.INPAINT_TELEA)
    plate[boom & ~hole] = k1[boom & ~hole]
    cv2.imwrite(os.path.join(OUT, 'plate.png'), plate)
    json.dump(meta, open(os.path.join(OUT, 'meta.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == '__main__':
    main()
