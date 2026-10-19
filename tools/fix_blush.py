#!/usr/bin/env python3
"""클립 일부 프레임·영역에서 분홍 볼터치를 지운다(창수는 볼터치 없음 — 정체성 규칙). 0원 후처리.
사용: python3 tools/fix_blush.py --clip IN.mp4 --out OUT.mp4 --frames 28-52 --region x0,y0,x1,y1
분홍(H 150~179·0~8, S>35, V>110) 픽셀의 채도를 주변 털·얼굴 수준으로 낮춘다(부드러운 마스크). 영역 밖·지정 프레임 밖은 그대로.
"""
import argparse, subprocess
import cv2
import numpy as np
import imageio_ffmpeg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--clip'); ap.add_argument('--out'); ap.add_argument('--frames'); ap.add_argument('--region')
    a = ap.parse_args()
    f0, f1 = map(int, a.frames.split('-')); x0, y0, x1, y1 = map(int, a.region.split(','))
    cap = cv2.VideoCapture(a.clip); fps = cap.get(cv2.CAP_PROP_FPS); W = int(cap.get(3)); H = int(cap.get(4))
    p = subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}',
                          '-r', str(fps), '-i', '-', '-c:v', 'libx264', '-crf', '14', '-pix_fmt', 'yuv420p', a.out], stdin=subprocess.PIPE)
    i = 0; changed = 0
    while True:
        ok, f = cap.read()
        if not ok: break
        if f0 <= i <= f1:
            roi = f[y0:y1, x0:x1]; hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV).astype(np.float32)
            h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
            pink = (((h >= 150) | (h <= 8)) & (s > 35) & (v > 110)).astype(np.float32)
            m = cv2.GaussianBlur(cv2.dilate(pink, np.ones((5, 5), np.uint8)), (15, 15), 0)
            hsv[..., 1] = s * (1 - 0.85 * m)
            f[y0:y1, x0:x1] = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR); changed += int(pink.sum())
        p.stdin.write(f.tobytes()); i += 1
    p.stdin.close(); p.wait(); print('frames', i, 'pink px fixed', changed)


if __name__ == '__main__':
    main()
