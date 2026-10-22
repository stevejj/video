#!/usr/bin/env python3
"""얼굴 따라가기(무료): 첫 프레임의 얼굴 상자를 본으로 잡고, 매 프레임 주변을 찾아(템플릿 매칭) 얼굴 중심을 기록한다.
사용(모듈): from face_track import track → [[t(클립 기준), x, y], ...] (1080x1920 프레임 좌표)
쓰임: 핀 조명이 얼굴을 따라다니게(ep09 v2 "치킨은 너무 많이 먹었어" — 사용자: 얼굴이 벗어나도 조명이 그대로라 어색).
"""
import subprocess
import numpy as np
import cv2
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()


def track(clip, t0, t1, box, search=120, step=2, smooth=5):
    """box = (x0, y0, x1, y1) 첫 프레임(t0)의 얼굴 상자. step 프레임마다 기록, 이동 평균으로 떨림 줄임."""
    w, h = 1080, 1920
    raw = subprocess.run([FF, '-v', 'error', '-ss', f'{t0:.3f}', '-t', f'{t1 - t0:.3f}', '-i', clip, '-vf', f'scale={w}:{h}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'],
                         capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w)
    x0, y0, x1, y1 = box; tpl = fr[0, y0:y1, x0:x1]; tw, th = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; pts = []
    for i in range(0, len(fr), step):
        sx0, sy0 = int(max(0, cx - tw / 2 - search)), int(max(0, cy - th / 2 - search))
        reg = fr[i, sy0:int(min(h, cy + th / 2 + search)), sx0:int(min(w, cx + tw / 2 + search))]
        r = cv2.matchTemplate(reg, tpl, cv2.TM_CCOEFF_NORMED); _, _, _, mx = cv2.minMaxLoc(r)
        cx, cy = sx0 + mx[0] + tw / 2, sy0 + mx[1] + th / 2
        pts.append([round(i / 24, 3), cx, cy])
    a = np.array(pts); k = smooth
    if len(a) > k:
        for j in (1, 2):
            a[:, j] = np.convolve(np.pad(a[:, j], (k // 2, k // 2), mode='edge'), np.ones(k) / k, 'valid')
    return [[round(float(t + t0), 3), round(float(x)), round(float(y))] for t, x, y in a]
