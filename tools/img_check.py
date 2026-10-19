#!/usr/bin/env python3
"""키프레임 이미지 검수 보조(0원): 영상에 실제로 보이는 띠 크롭 + 창수 볼터치 검사.
사용: python3 tools/img_check.py IMG [--top 30] [--full]  → 같은 폴더에 <이름>_band.jpg
--full 이면 전체 화면(ep07식)으로 보고 크롭하지 않음.
"""
import argparse, os, sys
import cv2
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('img'); ap.add_argument('--top', type=float, default=30); ap.add_argument('--full', action='store_true')
    a = ap.parse_args()
    im = Image.open(a.img).convert('RGB').resize((1080, 1920))
    band = im if a.full else im.crop((0, int(1920 * a.top / 100), 1080, int(1920 * (a.top + 40) / 100)))
    out = os.path.splitext(a.img)[0] + '_band.jpg'; band.save(out, quality=88)
    import qa_clip
    px = qa_clip.changsu_blush(cv2.imread(a.img))
    print(f'band: {out}  창수 볼터치 {px}px', '✓' if px <= 126 else '✗')


if __name__ == '__main__':
    main()
