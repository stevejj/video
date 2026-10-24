#!/usr/bin/env python3
"""영상 맨 앞에 썸네일 화면 붙이기(2026-10-23 사용자: 썸네일처럼 가운데 제목 + 채널명으로 시작).
- black: 검은 배경 + 가운데 제목·채널명을 hold초 보여 주고 영상 시작(ep11 맥주광고, ep06 댄스배틀).
- blur : 첫 장면을 흐리게 깐 배경 + 가운데 제목·채널명 → trans초 동안 글씨는 흐려지며 사라지고 장면은 다시 선명해지며
         영상 첫 화면으로 이어짐(ep14 인형뽑기). --bg-img = 글씨 없는 첫 장면(없으면 영상 첫 프레임).
소리는 붙인 길이만큼 뒤로 밀림(앞은 무음). 글씨 모양은 영상 제목과 같은 Noto Sans KR 굵게 + 검은 테두리(ep14_edit.text_img).
사용: python3 tools/thumb_intro.py --video IN.mp4 --out OUT.mp4 --title '[[["맥주광고","yellow"],[" 따라하기","white"]]]' [--bg blur --bg-img PNG --trans 0.7] [--hold 1.2]
"""
import argparse, json, os, subprocess, sys
import numpy as np
import cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from ep14_edit import text_img, ease
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 24
CHANNEL = '지독한 미순'


def overlay(frame, rgba, cx, cy, alpha=1.0, blur=0.0, scale=1.0):
    if scale != 1.0:
        rgba = cv2.resize(rgba, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    if blur > 0.3:
        pad = int(blur * 3) + 2
        rgba = cv2.copyMakeBorder(rgba, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
        rgba = cv2.GaussianBlur(rgba, (0, 0), blur)
    h, w = rgba.shape[:2]; x0, y0 = int(cx - w / 2), int(cy - h / 2)
    fx0, fy0, fx1, fy1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if fx1 <= fx0 or fy1 <= fy0:
        return
    src = rgba[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0].astype(np.float32)
    a = src[..., 3:4] / 255.0 * alpha
    rgb = src[..., [2, 1, 0]]          # text_img는 RGBA, 프레임은 BGR
    frame[fy0:fy1, fx0:fx1] = (frame[fy0:fy1, fx0:fx1] * (1 - a) + rgb * a).astype(np.uint8)


def first_frame(video):
    raw = subprocess.run([FF, '-v', 'error', '-i', video, '-frames:v', '1', '-vf', f'scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W, 3).copy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--video', required=True); ap.add_argument('--out', required=True); ap.add_argument('--title', required=True)
    ap.add_argument('--bg', choices=['black', 'blur'], default='black'); ap.add_argument('--bg-img')
    ap.add_argument('--hold', type=float, default=1.2); ap.add_argument('--trans', type=float, default=0.7)
    ap.add_argument('--size', type=int, default=120); ap.add_argument('--chan-size', type=int, default=58)
    a = ap.parse_args()
    lines = json.loads(a.title)
    title = text_img([[(t, c) for t, c in ln] for ln in lines], a.size, stroke=11)
    chan = text_img([[(CHANNEL, 'white')]], a.chan_size, weight=700, stroke=6)
    gap = 26; th, ch = title.shape[0], chan.shape[0]
    top = H / 2 - (th + gap + ch) / 2
    ty, cy = top + th / 2, top + th + gap + ch / 2

    v0 = first_frame(a.video)
    if a.bg == 'black':
        base = np.zeros((H, W, 3), np.uint8); trans = 0.0
    else:
        clean = cv2.resize(cv2.imread(a.bg_img), (W, H), interpolation=cv2.INTER_CUBIC) if a.bg_img else v0
        trans = a.trans
    n_hold, n_tr = int(round(a.hold * FPS)), int(round(trans * FPS))
    tmp = a.out + '.intro.mp4'
    enc = subprocess.Popen([FF, '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    SIG = 26.0   # 배경 흐림 정도
    for i in range(n_hold + n_tr):
        if a.bg == 'black':
            fr = base.copy(); overlay(fr, title, W / 2, ty); overlay(fr, chan, W / 2, cy)
        else:
            p = 0.0 if i < n_hold else ease((i - n_hold + 1) / max(1, n_tr))          # 0 → 1: 다시 선명해짐
            bg = cv2.addWeighted(clean, 1 - p, v0, p, 0)                                 # 글씨 없는 장면 → 영상 첫 화면(위 제목 포함)
            s = SIG * (1 - p)
            if s > 0.4:
                bg = cv2.GaussianBlur(bg, (0, 0), s)
            fr = (bg.astype(np.float32) * (0.72 + 0.28 * p)).astype(np.uint8)          # 글씨가 잘 보이게 살짝 어둡게 → 원래 밝기
            q = 0.0 if i < n_hold else ease((i - n_hold + 1) / max(1, n_tr * 0.65))      # 글씨: 흐려지며 사라짐
            if q < 0.999:
                overlay(fr, title, W / 2, ty, alpha=1 - q, blur=14 * q, scale=1 + 0.06 * q)
                overlay(fr, chan, W / 2, cy, alpha=1 - q, blur=10 * q, scale=1 + 0.06 * q)
        enc.stdin.write(fr.tobytes())
    enc.stdin.close(); enc.wait()
    d = (n_hold + n_tr) / FPS
    # 이어 붙이기: 영상은 그대로 뒤에, 소리는 d초 뒤로(앞은 무음)
    subprocess.run([FF, '-y', '-v', 'error', '-i', tmp, '-i', a.video, '-filter_complex',
                    f'[0:v]fps={FPS},format=yuv420p,setsar=1[a];[1:v]scale={W}:{H},fps={FPS},format=yuv420p,setsar=1[b];[a][b]concat=n=2:v=1:a=0[v];'
                    f'[1:a]adelay={int(d * 1000)}:all=1,apad=pad_dur=0[au]',
                    '-map', '[v]', '-map', '[au]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k',
                    '-shortest', a.out], check=True)
    os.remove(tmp)
    print('완료', os.path.relpath(a.out, ROOT), f'앞에 {d:.2f}s 붙임')


if __name__ == '__main__':
    main()
