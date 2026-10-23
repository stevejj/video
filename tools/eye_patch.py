#!/usr/bin/env python3
"""눈 붙이기(0원): Kling 클립에서 눈이 감기거나 윙크처럼 바뀐 구간을 첫 프레임의 눈으로 덮는다.
ep14 C2: "눈을 가늘게" 지시에 미순이 한쪽 눈을 더 감아 윙크처럼 됨 → 사용자 "Kling 안 쓰고 무료로 고칠 수 있지 않아?"
사용: python3 tools/eye_patch.py IN.mp4 OUT.mp4 --head x0,y0,x1,y1 --eye x,y --eye x,y [--r 38,34] [--t0 0 --t1 99]
- --ref-t: 눈을 가져올 프레임 시각(초). --head·--eye 좌표도 이 프레임 기준.
- --head: 그 프레임의 머리 상자(따라가기용, 눈 포함 가능). 매 프레임 주변 ±40px에서 템플릿 매칭으로 머리 이동을 찾음.
- --eye: 첫 프레임 눈동자 중심(여러 개). 그 주변 타원(--r 가로,세로 반지름)을 첫 프레임에서 오려 이동만큼 옮겨 붙임, 가장자리 8px 흐리게.
- 부리·볼터치는 건드리지 않음(타원이 눈 둘레만). 눈 깜빡임도 사라짐(대신 눈 크기·모양이 첫 프레임 그대로).
- 소리는 원본 그대로 복사.
"""
import argparse, os, subprocess, tempfile
import numpy as np, cv2, imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('dst')
    ap.add_argument('--head', required=True); ap.add_argument('--eye', action='append', required=True)
    ap.add_argument('--r', default='38,34'); ap.add_argument('--ref-t', type=float, default=0); ap.add_argument('--t0', type=float, default=0); ap.add_argument('--t1', type=float, default=1e9)
    a = ap.parse_args()
    cap = cv2.VideoCapture(a.src); fps = cap.get(cv2.CAP_PROP_FPS)
    cap.set(cv2.CAP_PROP_POS_MSEC, a.ref_t * 1000); _, f0 = cap.read()   # 눈을 가져올 프레임(기본 첫 프레임). C7: 첫 프레임이 실눈이라 2.08s
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0); ok, frame = cap.read(); H, W = f0.shape[:2]
    x0, y0, x1, y1 = map(int, a.head.split(',')); tpl = cv2.cvtColor(f0[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
    rx, ry = map(int, a.r.split(','))
    mask = np.zeros((H, W), np.float32)
    for e in a.eye:
        ex, ey = map(int, e.split(',')); cv2.ellipse(mask, (ex, ey), (rx, ry), 0, 0, 360, 1.0, -1)
    mask = cv2.GaussianBlur(mask, (0, 0), 8)[..., None]
    tmp = tempfile.mkdtemp(); out = cv2.VideoWriter(os.path.join(tmp, 'v.mp4'), cv2.VideoWriter_fourcc(*'mp4v'), fps, (W, H))
    n, S = 0, 40
    while ok:
        t = n / fps
        if a.t0 <= t <= a.t1:
            g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            sx0, sy0 = max(0, x0 - S), max(0, y0 - S)
            r = cv2.matchTemplate(g[sy0:min(H, y1 + S), sx0:min(W, x1 + S)], tpl, cv2.TM_CCOEFF_NORMED)
            _, _, _, (mx, my) = cv2.minMaxLoc(r); dx, dy = sx0 + mx - x0, sy0 + my - y0
            M = np.float32([[1, 0, dx], [0, 1, dy]])
            src = cv2.warpAffine(f0, M, (W, H), borderMode=cv2.BORDER_REPLICATE)
            mk = cv2.warpAffine(mask, M, (W, H))[..., None]
            frame = (frame * (1 - mk) + src * mk).astype(np.uint8)
        out.write(frame); ok, frame = cap.read(); n += 1
    out.release()
    subprocess.run([FF, '-y', '-loglevel', 'error', '-i', os.path.join(tmp, 'v.mp4'), '-i', a.src, '-map', '0:v', '-map', '1:a?',
                    '-c:v', 'libx264', '-crf', '17', '-pix_fmt', 'yuv420p', '-c:a', 'copy', a.dst], check=True)
    print(f'{n}프레임, 눈 {len(a.eye)}개 붙임 → {a.dst}')


if __name__ == '__main__':
    main()
