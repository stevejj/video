#!/usr/bin/env python3
"""소품 연속성 자동 검사: 완성본에서 소품(색으로 구분)이 컷마다 기대대로 보이는지, 중간에 사라졌다 나타나지 않는지.
사용: python3 tools/check_props.py --ep ep05 --video outputs/ep05/roughcut/ep05_v1.mp4
설정: outputs/<ep>/props.json
  props.<이름>.hsv = {"h": [[lo,hi],...], "s_min", "v_min"}  (OpenCV HSV, H 0~179)
  cuts.<컷>.<이름> = {"min_px": N}  → 그 컷의 모든 프레임(플래시 제외)에서 픽셀 수 ≥ N 이어야 함
                     {"max_px": N}  → 그 컷에서는 안 보여야 함(≤ N)
컷 구간은 outputs/<ep>/hf/cuts.json(변환기가 씀)에서 읽는다. 흰 플래시 프레임(평균 밝기가 영상 중앙값 + 25 초과, 사라지는 꼬리 포함)은 건너뛴다.
추가로 컷 안에서 픽셀 수가 주변 ±0.25s 중앙값의 35% 아래로 떨어지는 프레임(순간 사라짐)을 경고한다.
실패가 하나라도 있으면 종료 코드 1.
"""
import argparse, json, os, sys
import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ep', required=True); ap.add_argument('--video', required=True)
    ap.add_argument('--cuts', default=None)
    a = ap.parse_args()
    P = json.load(open(os.path.join(ROOT, f'outputs/{a.ep}/props.json')))
    C = json.load(open(a.cuts or os.path.join(ROOT, f'outputs/{a.ep}/hf/cuts.json')))['cuts']
    y0, y1 = P.get('band', [576, 1344])
    cap = cv2.VideoCapture(a.video); fps = cap.get(cv2.CAP_PROP_FPS) or 24
    counts = {k: [] for k in P['props']}; flash = []
    while True:
        ok, f = cap.read()
        if not ok: break
        win = f[y0:y1]; hsv = cv2.cvtColor(win, cv2.COLOR_BGR2HSV)
        flash.append(win.mean())
        for k, p in P['props'].items():
            hm = np.zeros(hsv.shape[:2], bool)
            for lo, hi in p['hsv']['h']:
                hm |= (hsv[..., 0] >= lo) & (hsv[..., 0] <= hi)
            m = hm & (hsv[..., 1] >= p['hsv']['s_min']) & (hsv[..., 2] >= p['hsv']['v_min'])
            counts[k].append(int(m.sum()))
    br = np.array(flash); flash = list(br > np.median(br) + 25)  # 셔터 플래시(서서히 사라지는 꼬리 포함)
    fails = 0
    for cut, t0, L, kind in C:
        exp = P['cuts'].get(cut, {})
        i0, i1 = int(np.ceil(t0 * fps - 1e-6)), int(np.ceil((t0 + L) * fps - 1e-6))  # 프레임 시작 시각이 컷 안에 있는 것만
        for k, rule in exp.items():
            arr = np.array(counts[k][i0:i1]); ok_f = ~np.array(flash[i0:i1])
            vals = arr[ok_f]
            if not len(vals): continue
            line = f'컷 {cut} [{t0:.2f}~{t0 + L:.2f}s] {k}: 최소 {vals.min()} / 중앙 {int(np.median(vals))}'
            bad = []
            if 'min_px' in rule:
                bad = [i0 + j for j, v in enumerate(arr) if ok_f[j] and v < rule['min_px']]
            if 'max_px' in rule:
                bad = [i0 + j for j, v in enumerate(arr) if ok_f[j] and v > rule['max_px']]
            # 순간 사라짐: 주변 중앙값 대비 급락
            dips = []
            for j in range(len(arr)):
                if not ok_f[j]: continue
                nb = [arr[x] for x in range(max(0, j - 6), min(len(arr), j + 7)) if x != j and ok_f[x]]
                if nb and np.median(nb) > 1000 and arr[j] < 0.35 * np.median(nb):
                    dips.append(i0 + j)
            if bad:
                fails += 1
                print(f'✗ {line} → 기준 위반 {len(bad)}프레임 ({bad[0] / fps:.2f}~{bad[-1] / fps:.2f}s), 규칙 {rule}')
            elif dips:
                fails += 1
                print(f'✗ {line} → 순간 사라짐 {len(dips)}프레임 ({dips[0] / fps:.2f}~{dips[-1] / fps:.2f}s)')
            else:
                print(f'✓ {line}')
    print('결과:', '통과' if not fails else f'실패 {fails}건')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
