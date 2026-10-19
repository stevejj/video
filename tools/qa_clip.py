#!/usr/bin/env python3
"""생성 영상 자동 검사(F10 관문). Kling 클립을 받을 때마다, 완성본을 보낼 때마다 실행. 실패면 종료 코드 1.
사용: python3 tools/qa_clip.py VIDEO [--band y0,y1] [--ep epXX --cuts cuts.json]
검사
 1. 창수 볼터치: 창수(진한 청회색 털 덩어리) 윤곽 안의 분홍 픽셀 — ep06 C2 결함
 2. 멈춘 프레임: 2프레임 이상 연속으로 같은 화면 — 렌더 시 seek 실패
 3. 소품 연속성: --ep 를 주면 outputs/<ep>/props.json 기준(check_props.py와 같은 규칙) — ep05 덤벨 사라짐
"""
import argparse, json, os, subprocess, sys
import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_URL = 'https://github.com/danielgatis/rembg/releases/download/v0.0.0/isnet-general-use.onnx'


def ensure_model(path):
    """ISNet 모델이 없으면(컨테이너 초기화 등) 받아 둔다."""
    import os, urllib.request
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        print('ISNet 모델 내려받는 중:', path); urllib.request.urlretrieve(MODEL_URL, path)
    return path


_SESS = None


def penguins_mask(f):
    """ISNet으로 펭귄(전경)만 — 저녁 조명에서 바닥도 파랗게 보여 색만으로는 창수를 못 가름."""
    global _SESS
    import onnxruntime as ort
    if _SESS is None:
        _SESS = ort.InferenceSession(ensure_model('/tmp/claude-0/-home-user-video/f018d661-8ddb-51f7-8e2d-f2480d28ac5d/scratchpad/models/isnet.onnx'), providers=['CPUExecutionProvider'])
    x = cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2RGB), (1024, 1024)).astype(np.float32) / 255.0 - 0.5
    o = _SESS.run(None, {_SESS.get_inputs()[0].name: x.transpose(2, 0, 1)[None]})[0][0, 0]
    o = (o - o.min()) / (o.max() - o.min() + 1e-8)
    return cv2.resize(o, (f.shape[1], f.shape[0])) > 0.5


def changsu_blush(f):
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV); h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    peng = penguins_mask(f)
    # 창수 털: 펭귄 안에서 진한 청회색(미순은 밝은 은회색·채도 낮음)
    blue = (peng & (h >= 100) & (h <= 130) & (s > 50) & (v < 170)).astype(np.uint8)
    blue = cv2.morphologyEx(blue, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    blue = cv2.morphologyEx(blue, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(blue)
    if n < 2: return 0
    k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    if st[k, cv2.CC_STAT_AREA] < 0.005 * blue.size: return 0
    cnt, _ = cv2.findContours((lab == k).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    hull = np.zeros_like(blue); cv2.drawContours(hull, [cv2.convexHull(max(cnt, key=cv2.contourArea))], -1, 1, -1)
    b, g, r = [f[..., i].astype(np.int16) for i in range(3)]
    pink = (r - g > 25) & (b - g > -5) & (r > 130)  # 분홍(빨강>초록, 파랑≥초록) — 주황 부리(파랑<초록)는 제외
    return int((pink & peng & (hull > 0)).sum())


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('video'); ap.add_argument('--band'); ap.add_argument('--ep'); ap.add_argument('--cuts')
    ap.add_argument('--blush-px', type=int, default=None, help='창수 볼터치 기준 픽셀(기본: 화면 넓이의 0.012%)')
    a = ap.parse_args()
    cap = cv2.VideoCapture(a.video); fps = cap.get(cv2.CAP_PROP_FPS) or 24
    y0, y1 = map(int, a.band.split(',')) if a.band else (None, None)
    blush, diffs = [], []; prev = None; shape = None
    while True:
        ok, f = cap.read()
        if not ok: break
        if y0 is not None: f = f[y0:y1]
        shape = f.shape
        blush.append(changsu_blush(f) if len(diffs) % 2 == 0 else (blush[-1] if blush else 0))  # 2프레임마다(속도)
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.int16)
        if prev is not None: diffs.append(float(np.abs(g - prev).mean()))
        prev = g
    area = shape[0] * shape[1]; thr = a.blush_px or int(area * 0.00012)
    fails = 0
    bad = [i for i, c in enumerate(blush) if c > thr]
    if bad:
        fails += 1; print(f'✗ 창수 볼터치 의심 {len(bad)}프레임 ({bad[0] / fps:.2f}~{bad[-1] / fps:.2f}s), 최대 {max(blush)}px > 기준 {thr}px')
    else:
        print(f'✓ 창수 볼터치 없음 (최대 {max(blush)}px ≤ {thr}px)')
    z = [d < 0.05 for d in diffs]  # 2프레임 이상 연속으로 같은 화면 = 멈춤(클립 끝 1프레임 중복은 무해)
    fr = [i + 1 for i in range(len(z) - 1) if z[i] and z[i + 1]]
    if fr:
        fails += 1; print(f'✗ 멈춘 프레임 {len(fr)}개: {[round(i / fps, 2) for i in fr[:10]]}')
    else:
        print('✓ 멈춘 프레임 없음')
    if a.ep:
        cmd = [sys.executable, os.path.join(ROOT, 'tools/check_props.py'), '--ep', a.ep, '--video', a.video] + (['--cuts', a.cuts] if a.cuts else [])
        r = subprocess.run(cmd); fails += r.returncode != 0
    print('결과:', '통과' if not fails else f'실패 {fails}건 → 사용자에게 보내기 전에 고치거나, 결함을 먼저 보고')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
