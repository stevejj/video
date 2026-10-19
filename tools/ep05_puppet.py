#!/usr/bin/env python3
"""ep05 무료 애니매틱 v2 재료: K1·K3에서 미순·바닥 덤벨을 오려내고(cutout.py), 미순 없는 배경판 2장을 만든다.
plateA = K1 구도(창수 폰 든 상태) - 미순, 바닥 덤벨 없음
plateB = K3 구도(창수 폰 내린 상태) - 미순 - 바닥 덤벨
구멍(두 장 모두 미순이 가리는 곳)은 OpenCV inpaint, 바닥 덤벨 자리는 아래쪽 바닥 결을 복사한다.
"""
import json, os, subprocess, sys
import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'outputs/ep05/puppet')
K1 = os.path.join(ROOT, 'outputs/ep05/01/start_v1.png')
K3 = os.path.join(ROOT, 'outputs/ep05/03/start_v1.png')
CUTS = {  # id: (원본, 박스)
    'misun_k1': (K1, (270, 470, 680, 880)),
    'misun_k3': (K3, (290, 470, 640, 880)),
    'dumbbells': (K3, (490, 850, 700, 960)),
}


def main():
    os.makedirs(OUT, exist_ok=True)
    meta = {'src_width': 768}
    masks = {}
    for k, (img, box) in CUTS.items():
        full = os.path.join(OUT, f'{k}_full.png'); mk = os.path.join(OUT, f'{k}_mask.png')
        if not os.path.exists(mk):
            subprocess.run([sys.executable, os.path.join(ROOT, 'tools/cutout.py'), '--img', img, '--box', *map(str, box),
                            '--out', full, '--mask-out', mk], check=True)
        im = Image.open(full); a = im.getchannel('A')
        bb = a.point(lambda v: 255 if v > 8 else 0).getbbox()
        im.crop(bb).save(os.path.join(OUT, f'{k}.png'))
        feet = a.point(lambda v: 255 if v > 128 else 0).getbbox()
        meta[k] = {'box': [bb[0], bb[1], bb[2] - bb[0], bb[3] - bb[1]], 'solid': list(feet)}
        masks[k] = np.asarray(a) > 40
        os.remove(full)
    k1 = cv2.imread(K1); k3 = cv2.imread(K3)
    ker = np.ones((7, 7), np.uint8)
    dil = lambda m, it=2: cv2.dilate(m.astype(np.uint8), ker, iterations=it) > 0
    m1, m3, md = dil(masks['misun_k1']), dil(masks['misun_k3']), dil(masks['dumbbells'], 4)
    # 바닥 덤벨 자리: 같은 높이 왼쪽(창수와 미순 사이) 바닥 결 복사 후 경계만 inpaint
    plate = k3.copy()
    near = dil(md, 8)
    b, g, r = [k3[..., i].astype(int) for i in range(3)]
    md = md | (near & (r - g > 6))  # 덤벨 주변 분홍 반사광까지 포함
    ys, xs = np.nonzero(md)
    patch = k3[ys, np.clip(xs - 180, 0, k3.shape[1] - 1)].astype(np.float32)
    ring = k3[dil(md, 3) & ~md].astype(np.float32)
    patch = (patch - patch.mean(0)) * (ring.std(0) / (patch.std(0) + 1e-6)) + ring.mean(0)  # 밝기·대비 맞춤
    plate[ys, xs] = np.clip(patch, 0, 255).astype(np.uint8)
    edge = dil(md, 1) & ~cv2.erode(md.astype(np.uint8), ker, iterations=2).astype(bool)
    plate = cv2.inpaint(plate, edge.astype(np.uint8) * 255, 4, cv2.INPAINT_TELEA)
    fill = m3 & ~m1
    plate[fill] = k1[fill]
    hole = m3 & m1
    # 구멍: 오른쪽 P px 떨어진 배경(덤벨 랙 반복 무늬)을 오른쪽→왼쪽 순서로 복사, 경계만 inpaint
    P = 80
    ys, xs = np.nonzero(hole)
    for x in sorted(set(xs.tolist()), reverse=True):
        col = ys[xs == x]
        up, fl = col[col < 745], col[col >= 745]  # 랙 높이는 옆 반복, 바닥은 아래쪽 바닥 결
        plate[up, x] = plate[up, min(x + P, plate.shape[1] - 1)]
        plate[fl, x] = plate[np.clip(fl + 130, 0, plate.shape[0] - 1), x]
    seam = dil(hole, 1) & ~cv2.erode(hole.astype(np.uint8), ker, iterations=1).astype(bool)
    plateB = cv2.inpaint(plate, seam.astype(np.uint8) * 255, 3, cv2.INPAINT_TELEA)
    cv2.imwrite(os.path.join(OUT, 'plateB.png'), plateB)
    plateA = k1.copy(); plateA[m1] = plateB[m1]
    cv2.imwrite(os.path.join(OUT, 'plateA.png'), plateA)
    json.dump(meta, open(os.path.join(OUT, 'meta.json'), 'w'), indent=1)
    print(json.dumps(meta))


if __name__ == '__main__':
    main()
