#!/usr/bin/env python3
"""ep12 무료 합성(0원): 상어 구경 사진(로컬 전용)에 미순·창수 뒷모습을 붙임.
사용: python3 tools/ep12_free_composite.py → outputs/ep12/01/free_v1.png, free_compare.jpg (둘 다 로컬 전용)
- 캐릭터 뒷모습 시트에서 ISNet으로 누끼 → 크기·위치 → 사진 햇빛에 맞춰 밝기·색·선명도·입자 조정.
- 땅 그림자(타원 흐림) + 휴대폰(사진 속 상어 부분을 화면으로) 머리 높이에 듦.
- 한계: 휴대폰을 든 날개 자세·고개 돌린 옆얼굴 참조 이미지가 없어 뒷모습 그대로(유료 생성이면 가능).
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, 'outputs/ep12')
MODEL = '/tmp/claude-0/-home-user-video/f018d661-8ddb-51f7-8e2d-f2480d28ac5d/scratchpad/models/isnet.onnx'
# (참조, 아래 중심 x, 발 y, 키 px) — 원본 800x657 기준, 아이 태운 아저씨 오른쪽 앞(벙거지 모자 분 앞)
PLACE = [('assets/characters/pang-misun/pang-misun_body_back.png', 445, 668, 118),
         ('assets/characters/pang-changsu/pang-changsu_body_back.png', 522, 670, 126)]   # v1(150·162px)은 어른만큼 커 보임
SHARK = (150, 120, 720, 260)   # 휴대폰 화면에 넣을 상어 부분


def cut(path):
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    from cutout import alpha
    im = Image.open(os.path.join(ROOT, path)).convert('RGB')
    a = np.asarray(alpha(im, MODEL)).copy(); a[a < 40] = 0
    a = np.asarray(Image.fromarray(a).filter(ImageFilter.MinFilter(3)))   # 가장자리 배경색 테두리 제거
    ys, xs = np.where(a > 0)
    rgba = Image.fromarray(np.dstack([np.asarray(im), a]).astype('uint8'))
    return rgba.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def sunlit(p):
    """정오 햇빛: 위쪽 밝게·아래쪽 살짝 어둡게, 대비·채도는 사진처럼."""
    rgb = p.convert('RGB'); a = p.getchannel('A')
    rgb = ImageEnhance.Contrast(rgb).enhance(1.08)
    w, h = rgb.size; g = np.linspace(1.08, 0.85, h)[:, None, None]
    arr = np.clip(np.asarray(rgb).astype(float) * g, 0, 255)    # v1은 따뜻한 색을 더해 회색 털이 베이지로 보임 → 색 그대로
    out = Image.fromarray(arr.astype('uint8')); out.putalpha(a.filter(ImageFilter.GaussianBlur(0.8)))
    return out


def phone(photo, w):
    """휴대폰(검은 테두리 + 상어 화면), 위에서 내려다본 살짝 기운 모습."""
    h = int(w * 1.9); ph = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(ph)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=w // 6, fill=(25, 25, 28, 255))
    scr = photo.crop(SHARK).resize((h - 8, w - 8)).rotate(90, expand=True)   # 가로로 찍는 화면을 세로 폰에
    ph.paste(scr, (4, 4))
    return ph


def main():
    photo = Image.open(os.path.join(EP, 'ref/source_photo.jpg')).convert('RGB')
    base = photo.convert('RGBA'); W, H = photo.size
    sh = Image.new('L', (W, H), 0); d = ImageDraw.Draw(sh)
    layers = []
    for ref, cx, fy, ht in PLACE:
        p = cut(ref); s = ht / p.height; p = p.resize((int(p.width * s), ht), Image.LANCZOS)
        p = sunlit(p); x, y = int(cx - p.width / 2), int(fy - ht)
        d.ellipse([x + p.width * 0.15, fy - 14, x + p.width * 0.95, fy + 10], fill=120)   # 땅 그림자(해가 거의 위에서)
        layers.append((p, x, y))
    base.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, 255)).copy() if False else Image.composite(
        Image.new('RGBA', (W, H), (20, 25, 25, 255)), Image.new('RGBA', (W, H), (0, 0, 0, 0)), sh.filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * 0.5))))
    for p, x, y in layers:
        base.alpha_composite(p, (x, y))
    # 휴대폰: 머리 앞쪽 위로 든 모습(뒤에서 보면 머리 위·옆으로 화면이 보임)
    for (p, x, y), dx in zip(layers, (-0.32, 0.30)):   # 머리 옆 위쪽(창수 깃털 안 가리게)
        ph = phone(photo, 22).rotate(-10 if dx < 0 else 8, expand=True, resample=Image.BICUBIC)
        base.alpha_composite(ph, (int(x + p.width * (0.5 + dx) - ph.width / 2), y - ph.height + 14))
    out = base.convert('RGB')
    # 사진처럼: 아주 약한 흐림 + 입자 + JPEG 한 번
    arr = np.asarray(out.filter(ImageFilter.GaussianBlur(0.35))).astype(float)
    arr += np.random.default_rng(1).normal(0, 2.2, arr.shape)
    out = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))
    os.makedirs(os.path.join(EP, '01'), exist_ok=True)
    tmp = os.path.join(EP, '01/free_v1.jpg'); out.save(tmp, quality=90)
    Image.open(tmp).save(os.path.join(EP, '01/free_v1.png'))
    cmp_ = Image.new('RGB', (W * 2 + 10, H), 'white'); cmp_.paste(photo, (0, 0)); cmp_.paste(Image.open(tmp), (W + 10, 0))
    cmp_.save(os.path.join(EP, '01/free_compare.jpg'), quality=88)
    print('ok', os.path.join(EP, '01/free_v1.png'))


if __name__ == '__main__':
    main()
