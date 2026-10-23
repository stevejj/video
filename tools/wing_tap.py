#!/usr/bin/env python3
"""키보드 클로즈업 그림(O3c)에서 아래쪽 날개 끝 두 개를 떼어 번갈아 살짝 들었다 놓아 '타닥타닥' 영상을 만든다. 0원(Kling 대신).
사용: python3 tools/wing_tap.py --img outputs/ep16/img/O3c_v1.png --out OUT.mp4 --dur 5 --rate 7
쉬는 자세 = 원본. 누를 때 날개가 화면 안쪽(위)으로 조금 움직임 → 원본 키보드를 덮기만 하므로 빈 자리 생기지 않음.
타격 시각을 OUT.taps.json 으로 남김(편집에서 key_click 배치).
"""
import argparse, json, subprocess
import cv2
import numpy as np
import imageio_ffmpeg


def wing_masks(img, ytop=680):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, sat, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    m = ((h >= 98) & (h <= 128) & (sat > 30) & (v < 175)).astype(np.uint8); m[:ytop] = 0  # 파란 회색 털만(흰 키보드·나무 책상 제외)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    out = []
    for i in range(1, n):
        if st[i, 4] > 8000:
            k = (lab == i).astype(np.uint8)
            cs, _ = cv2.findContours(k, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            f = np.zeros_like(k); cv2.drawContours(f, cs, -1, 1, -1)
            out.append((st[i, 0] + st[i, 2] / 2, f))
    return [f for _, f in sorted(out, key=lambda x: x[0])]


class Tapper:
    """그림 하나에서 원하는 시각의 '타닥타닥' 프레임을 바로 만든다(편집 도구에서 직접 사용). taps=[(초, 0왼/1오른)]."""
    def __init__(self, img, dur=60, rate=7, lift=22, seed=3):
        self.base = img.astype(np.float32); self.H, self.W = img.shape[:2]; self.lift = lift
        self.masks = wing_masks(img)
        assert len(self.masks) == 2, f'날개 {len(self.masks)}개 검출'
        self.soft = [cv2.GaussianBlur(m.astype(np.float32), (7, 7), 0)[..., None] for m in self.masks]
        self.anchor = []
        for m in self.masks:
            ys, xs = np.nonzero(m); self.anchor.append((xs.mean(), ys.max()))
        rng = np.random.default_rng(seed); self.taps = []; t = 0.15; side = 0
        while t < dur - 0.1:
            self.taps.append((round(t, 3), side)); side = 1 - side if rng.random() < 0.8 else side
            t += (1 / rate) * rng.uniform(0.7, 1.3)

    def frame(self, tt, active=True):
        fr = self.base.copy()
        if not active:
            return fr.astype(np.uint8)
        for s in (0, 1):
            # 타격: 0.03s 만에 안쪽으로, 0.09s 동안 돌아옴
            d = 0.0
            for tp, sd in self.taps:
                if sd != s or tp > tt:
                    continue
                x = tt - tp
                if x < 0.03: d = max(d, x / 0.03)
                elif x < 0.12: d = max(d, 1 - (x - 0.03) / 0.09)
            if d <= 0:
                continue
            dy = -self.lift * d; dx = (6 if s == 0 else -6) * d; sc = 1 - 0.03 * d; cx, cy = self.anchor[s]
            M = np.float32([[sc, 0, (1 - sc) * cx + dx], [0, sc, (1 - sc) * cy + dy]])
            wimg = cv2.warpAffine(self.base, M, (self.W, self.H), borderMode=cv2.BORDER_REPLICATE)
            wm = cv2.warpAffine(self.soft[s], M, (self.W, self.H))[..., None]
            # 쉬는 자세 = 원본이고 누를 때 안쪽(위)으로만 가므로 원본 날개 위에 덮기만 함(빈 자리 없음)
            fr = fr * (1 - wm) + wimg * wm
        return np.clip(fr, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--img'); ap.add_argument('--out'); ap.add_argument('--dur', type=float, default=5)
    ap.add_argument('--rate', type=float, default=7, help='초당 타격 수(두 날개 합)'); ap.add_argument('--lift', type=float, default=22)
    ap.add_argument('--fps', type=int, default=30); ap.add_argument('--seed', type=int, default=3)
    a = ap.parse_args()
    img = cv2.imread(a.img); H, W = img.shape[:2]
    tp = Tapper(img, a.dur, a.rate, a.lift, a.seed)
    p = subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}',
                          '-r', str(a.fps), '-i', '-', '-c:v', 'libx264', '-crf', '14', '-pix_fmt', 'yuv420p', a.out], stdin=subprocess.PIPE)
    for fi in range(int(a.dur * a.fps)):
        p.stdin.write(tp.frame(fi / a.fps).tobytes())
    p.stdin.close(); p.wait()
    json.dump([t for t, _ in tp.taps], open(a.out.rsplit('.', 1)[0] + '.taps.json', 'w'))
    print('taps', len(tp.taps))


if __name__ == '__main__':
    main()
