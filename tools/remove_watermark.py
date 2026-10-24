"""캐릭터 시트 우하단 Gemini 별 워터마크 제거.

사용: python3 tools/remove_watermark.py
입력: assets/characters/original/<name>_sheet_original.png
출력: assets/characters/<name>/<name>_sheet_clean.png 및 각도별 크롭
"""
from pathlib import Path
import numpy as np, cv2
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent / "assets" / "characters"
SPARKLE_REGIONS = [(1225, 1280, 625, 680, 14), (1285, 1350, 660, 750, 10)]  # y0,y1,x0,x1,threshold
CROPS = {
    "face_front": (40, 175, 450, 1060),
    "body_front": (480, 150, 760, 485),
    "body_side": (480, 515, 760, 860),
    "body_back": (470, 905, 760, 1250),
}


def sparkle_masks(im):
    mask = np.zeros(im.shape[:2], np.uint8)
    big = np.zeros_like(mask)
    for i, (y0, y1, x0, x1, thr) in enumerate(SPARKLE_REGIONS):
        g = cv2.cvtColor(im[y0:y1, x0:x1], cv2.COLOR_RGB2GRAY)
        d = g.astype(int) - cv2.medianBlur(g, 41).astype(int)
        m = np.zeros(g.shape, np.uint8)
        m[d > thr] = 255
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        n, lab, stats, _ = cv2.connectedComponentsWithStats(m)
        for k in range(1, n):
            if stats[k, cv2.CC_STAT_AREA] > 60:
                mask[y0:y1, x0:x1][lab == k] = 255
                if i == 0:
                    big[y0:y1, x0:x1][lab == k] = 255
    return mask, big


def clean(name):
    im = np.array(Image.open(ROOT / "original" / f"{name}_sheet_original.png").convert("RGB"))
    mask, big = sparkle_masks(im)
    core = cv2.erode(big, np.ones((3, 3), np.uint8)) > 0
    # 큰 별: 순수 배경 행(1254~1262)에서 오버레이 알파를 채널별로 추정한 뒤 역산
    sel = np.zeros_like(core)
    sel[1254:1263, :] = True
    sel &= core
    ref = im[1254:1263, 676:690].reshape(-1, 3).astype(float).mean(axis=0)
    alpha = np.median((im[sel].astype(float) - ref) / (255 - ref), axis=0)
    out = im.astype(float)
    out[core] = np.clip((out[core] - alpha * 255) / (1 - alpha), 0, 255)
    out = out.astype(np.uint8)
    # 나머지(작은 별 2개 + 큰 별 경계)는 인페인팅
    inp = cv2.dilate(mask, np.ones((3, 3), np.uint8))
    inp[core] = 0
    out = cv2.inpaint(cv2.cvtColor(out, cv2.COLOR_RGB2BGR), inp, 3, cv2.INPAINT_TELEA)
    out = Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))
    dst = ROOT / name
    dst.mkdir(exist_ok=True)
    out.save(dst / f"{name}_sheet_clean.png")
    for k, box in CROPS.items():
        out.crop(box).save(dst / f"{name}_{k}.png")
    print(name, "alpha", alpha.round(3))


if __name__ == "__main__":
    for n in ["pang-misun", "pang-changsu"]:
        clean(n)
