#!/usr/bin/env python3
"""동공지진(무료): 멈춘 프레임에서 검은 눈만 레이어로 떼고, 원래 자리는 주변 털색으로 메운 배경판을 만든다.
사용(모듈): from pupil_quake import quake → (배경판 경로, puppet layers)
- 눈 찾기: 지정 상자 안에서 어두운(밝기 < thr) 가장 큰 덩어리. 하이라이트(흰 점)도 포함되게 구멍 메움.
- 레이어 움직임: 좌우로 빠르게 덜덜(amp px, 0.04s 간격) + 살짝 위아래. 두 눈은 반대 위상.
"""
import os
import numpy as np
import cv2
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def quake(frame_png, boxes, out_dir, tag, at, dur, amp, thr=70, pad=4):
    im = np.asarray(Image.open(os.path.join(ROOT, frame_png)).convert('RGB')).copy()
    lum = im.mean(2); allm = np.zeros(lum.shape, np.uint8); layers = []
    for k, (x0, y0, x1, y1) in enumerate(boxes):
        reg = (lum[y0:y1, x0:x1] < thr).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(reg)
        i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        m = (lab == i).astype(np.uint8) * 255
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))                 # 하이라이트 구멍 메움
        cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); m[:] = 0; cv2.drawContours(m, cs, -1, 255, -1)
        m = cv2.dilate(m, np.ones((2 * pad + 1, 2 * pad + 1), np.uint8))
        full = np.zeros(lum.shape, np.uint8); full[y0:y1, x0:x1] = m; allm |= full
        ys, xs = np.where(full > 0); bx = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        a = cv2.GaussianBlur(full, (5, 5), 0)[bx[1]:bx[3], bx[0]:bx[2]]
        p = os.path.join(out_dir, f'{tag}_eye{k}.png')
        Image.fromarray(np.dstack([im[bx[1]:bx[3], bx[0]:bx[2]], a])).save(p)
        sgn = 1 if k % 2 == 0 else -1; keys = []; t = at
        while t < at + dur:
            j = len(keys)
            keys.append({'t': round(t, 3), 'dur': 0.04, 'x': sgn * amp * (1 if j % 2 == 0 else -1) * (0.7 if j % 3 == 0 else 1.0),
                         'y': round(amp * 0.25 * (1 if j % 4 < 2 else -1), 1), 'ease': 'none'})
            t += 0.04
        keys.append({'t': round(at + dur, 3), 'dur': 0.08, 'x': 0, 'y': 0, 'ease': 'power2.out'})
        layers.append({'id': f'eye{k}', 'img': os.path.relpath(p, ROOT), 'box': [int(bx[0]), int(bx[1]), int(bx[2] - bx[0]), int(bx[3] - bx[1])],
                       'origin': '50% 50%', 'keys': keys})
    bg = cv2.inpaint(im, cv2.dilate(allm, np.ones((5, 5), np.uint8)), 9, cv2.INPAINT_TELEA)   # 눈 자리를 털색으로
    bp = os.path.join(out_dir, f'{tag}_bg.png'); Image.fromarray(bg).save(bp)
    return os.path.relpath(bp, ROOT), layers
