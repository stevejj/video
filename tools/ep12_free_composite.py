#!/usr/bin/env python3
"""ep12 무료 합성(0원): 상어 구경 사진(로컬 전용)에 미순·창수 뒷모습을 붙이고 말풍선.
사용: python3 tools/ep12_free_composite.py → outputs/ep12/01/free_v2.png, free_compare.jpg (둘 다 로컬 전용)
- 캐릭터 뒷모습 시트에서 ISNet으로 누끼 → 크기·위치 → 사진 햇빛에 맞춰 밝기·선명도·입자 조정.
- v2(사용자): 휴대폰 뺌(나란히 서서 구경하는 뒷모습), 미순·창수가 확실히 보이게 크게, 말풍선(미순 아주 연한 분홍, 창수 아주 연한 파랑).
- 워터마크(언론사 표시)는 지우지 않음: 저작권 표시 제거는 저작권법상 금지.
- 결과는 2배(1600px)로 키워 말풍선 글씨를 선명하게.
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, 'outputs/ep12')
MODEL = '/tmp/claude-0/-home-user-video/f018d661-8ddb-51f7-8e2d-f2480d28ac5d/scratchpad/models/isnet.onnx'
# (참조, 아래 중심 x, 발 y, 키 px) — 원본 800x657 기준, 아이 태운 아저씨 오른쪽 앞(벙거지 모자 분 앞)
PLACE = [('assets/characters/pang-misun/pang-misun_body_back.png', 292, 712, 236),
         ('assets/characters/pang-changsu/pang-changsu_body_back.png', 462, 716, 246)]   # 오른쪽 아래 언론사 표시(x 575~785)를 가리지 않는 자리   # v2: 카메라에 가장 가까운 앞쪽이라 크게 — 머리·어깨가 확실히 보이고 아래는 사진 밖으로 잘림
S2 = 2                                                                            # 결과 배율
FONT = os.path.join(ROOT, 'assets/fonts/NotoSansKR-Variable.ttf')
# 말풍선(1x 좌표): 글, 중심, 색, 꼬리 끝(머리 위)
BUBBLES = [('쟤가 부캉이야?', (235, 335), '#FFE6EF', (285, 478)),
           ('웅! 다시 돌아왔다는뎅', (545, 392), '#E4F0FF', (462, 468))]


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


def bubble(img, text, c, color, tip):
    """둥근 말풍선 + 꼬리(머리 쪽), 연한 색 + 아주 얇은 회색 테두리 + 옅은 그림자."""
    d = ImageDraw.Draw(img); f = ImageFont.truetype(FONT, 30 * S2)
    try:
        f.set_variation_by_axes([800])
    except Exception:
        pass
    l, t, r, b = d.textbbox((0, 0), text, font=f); tw, th = r - l, b - t
    px, py = 28 * S2, 18 * S2; cx, cy = c[0] * S2, c[1] * S2
    box = [cx - tw / 2 - px, cy - th / 2 - py, cx + tw / 2 + px, cy + th / 2 + py]
    tx, ty = tip[0] * S2, tip[1] * S2
    bx = min(max(tx, box[0] + 40 * S2), box[2] - 40 * S2)
    tail = [(bx - 16 * S2, box[3] - 4), (bx + 16 * S2, box[3] - 4), (tx, ty)]
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    ds.rounded_rectangle([v + 4 * S2 for v in box], radius=36 * S2, fill=(0, 0, 0, 70)); ds.polygon([(x + 4 * S2, y + 4 * S2) for x, y in tail], fill=(0, 0, 0, 70))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6 * S2)))
    d.polygon(tail, fill=color, outline=(150, 150, 160), width=2 * S2)
    d.rounded_rectangle(box, radius=36 * S2, fill=color, outline=(150, 150, 160), width=2 * S2)
    d.polygon([(tail[0][0] + 3 * S2, tail[0][1] - 3 * S2), (tail[1][0] - 3 * S2, tail[1][1] - 3 * S2), (tx, ty - 6 * S2)], fill=color)  # 꼬리와 풍선 이음새 지움
    d.text((cx - tw / 2 - l, cy - th / 2 - t), text, font=f, fill=(55, 55, 65))


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
    out = base.convert('RGB')
    # 사진처럼: 아주 약한 흐림 + 입자 → 2배로 키운 뒤 말풍선(글씨 선명)
    arr = np.asarray(out.filter(ImageFilter.GaussianBlur(0.35))).astype(float)
    arr += np.random.default_rng(1).normal(0, 2.2, arr.shape)
    out = Image.fromarray(np.clip(arr, 0, 255).astype('uint8')).resize((W * S2, H * S2), Image.LANCZOS).convert('RGBA')
    for text, c, color, tip in BUBBLES:
        bubble(out, text, c, color, tip)
    out = out.convert('RGB')
    os.makedirs(os.path.join(EP, '01'), exist_ok=True)
    out.save(os.path.join(EP, '01/free_v2.png'))
    cmp_ = Image.new('RGB', (W * 2 + 10, H), 'white'); cmp_.paste(photo, (0, 0)); cmp_.paste(out.resize((W, H), Image.LANCZOS), (W + 10, 0))
    cmp_.save(os.path.join(EP, '01/free_compare.jpg'), quality=88)
    print('ok', os.path.join(EP, '01/free_v2.png'), out.size)


if __name__ == '__main__':
    main()
