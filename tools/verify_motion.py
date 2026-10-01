#!/usr/bin/env python3
"""02c M9 — 조립본의 '정지 초' 검사. 1초 창마다 영상 창(또는 전체) 프레임 변화량을 재서 임계값 미만인 초를 나열한다.
사용: python3 tools/verify_motion.py <mp4> [--win 576,768] [--thresh 1.5] [--edit outputs/ep01/edit_list.json]
- --win top,height : 검은 띠 레이아웃의 영상 창(기본 576,768). 자막·카드 등 글자 영역은 포함(글자 팝업도 '변화'로 인정).
- 변화량 = 프레임 간 "10 이상 변한 픽셀 비율(%)"의 1초 안 최대값(그레이, 1/4 축소, 블러). 컷 경계 프레임은 제외.
  ep01 실측: 2% 줌 정지 컷 0.0~1.9, 걷기·고개 돌리기 2~6, 자막 팝업 4~8. 기본 임계값 1.0.
"""
import argparse, json, sys
import cv2, numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video'); ap.add_argument('--win', default='576,768'); ap.add_argument('--thresh', type=float, default=1.0)
    ap.add_argument('--edit', default=None, help='edit_list.json: 정지 초가 어느 컷인지 표시')
    a = ap.parse_args()
    top, h = map(int, a.win.split(','))
    c = cv2.VideoCapture(a.video); fps = c.get(5); n = int(c.get(7)); dur = n / fps
    cuts = []
    if a.edit:
        E = json.load(open(a.edit)); t = 0
        for x in E['cuts']:
            cuts.append((t, t + x['len'], x['cut'])); t += x['len']
    bounds = set(int(round(t0 * fps)) for t0, _, _ in cuts)
    prev = None; sec_max = {}
    i = 0
    while True:
        ok, f = c.read()
        if not ok:
            break
        g = cv2.cvtColor(f[top:top + h], cv2.COLOR_BGR2GRAY)
        g = cv2.resize(g, (g.shape[1] // 4, g.shape[0] // 4)).astype(np.float32); g = cv2.GaussianBlur(g, (5, 5), 0)
        if prev is not None and not any(abs(i - b) <= 1 for b in bounds):
            s = int(i / fps); frac = float((np.abs(g - prev) > 10).mean()) * 100
            sec_max[s] = max(sec_max.get(s, 0.0), frac)
        prev = g; i += 1
    sec_sum = sec_max
    still = []
    for s in sorted(sec_sum):
        v = sec_sum[s]
        if v < a.thresh:
            cut = next((nm for t0, t1, nm in cuts if t0 <= s < t1), '?')
            still.append((s, round(v, 2), cut))
    total = len(sec_sum)
    print(f'{a.video}: {dur:.1f}s, 1초 창 {total}개, 정지(변화 < {a.thresh}) {len(still)}초 = {len(still) / total * 100:.0f}%')
    by_cut = {}
    for s, v, cut in still:
        by_cut.setdefault(cut, []).append(s)
    for cut, secs in by_cut.items():
        print(f'  {cut:6s} {len(secs)}초  ({secs[0]}~{secs[-1]}s)')
    return 0 if not still else 1


if __name__ == '__main__':
    sys.exit(main())
