#!/usr/bin/env python3
"""키프레임 눈 크기 검사(0원). ep08 K9·ep09 K3: 감정·연출 단어 때문에 이미지 모델이 눈을 작게·반쯤 감게 바꿈(사용자가 발견).
사용: python3 tools/eye_check.py --ref REF.png IMG.png [IMG2.png ...] [--min 0.75]
- 둥글고 아주 어두운 덩어리(눈동자)를 찾아 크기(면적)를 잼. 이미지는 1080x1920으로 맞춘 뒤 측정.
- 각 이미지의 눈을 왼쪽→오른쪽으로 정렬해 REF의 같은 순서 눈과 면적 비교. 비율이 --min 미만이거나 개수가 다르면 ✗.
- REF는 같은 에피소드에서 사람이 확인한 이미지(보통 K1). 인물 크기가 다른 컷(클로즈업 등)은 REF를 그 컷과 비슷한 구도로.
"""
import argparse, sys
import cv2
import numpy as np


def eyes(path):
    im = cv2.resize(cv2.imread(path), (1080, 1920))
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(g, 45, 255, cv2.THRESH_BINARY_INV)
    th = cv2.morphologyEx(th, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(th)
    out = []
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if not (250 < a < 9000) or not (0.6 < w / max(h, 1) < 1.6):
            continue
        fill = a / (np.pi * (w / 2) * (h / 2))  # 원·타원이면 1 근처(폰·리모컨 같은 사각형은 제외)
        if fill > 0.75 and 0.3 * 1920 - 150 < y < 0.7 * 1920 + 150:
            out.append((int(cen[i][0]), int(cen[i][1]), int(a)))
    return sorted(out)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ref', required=True); ap.add_argument('imgs', nargs='+'); ap.add_argument('--min', type=float, default=0.75)
    a = ap.parse_args()
    R = eyes(a.ref); print(f'기준 {a.ref}: 눈 {len(R)}개 면적 {[e[2] for e in R]}')
    bad = 0
    for p in a.imgs:
        E = eyes(p)
        if len(E) != len(R):
            print(f'△ {p}: 눈 {len(E)}개(기준 {len(R)}개) {[e[2] for e in E]} → 개수가 달라 비교 못 함, 눈으로 확인'); continue
        r = [round(e[2] / q[2], 2) for e, q in zip(E, R)]
        ok = min(r) >= a.min
        bad += not ok
        print(f'{"✓" if ok else "✗"} {p}: 면적 비율 {r}' + ('' if ok else f' < {a.min} → 눈이 작아짐(편집으로 기준 눈 옮기기 또는 재생성)'))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
