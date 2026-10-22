#!/usr/bin/env python3
"""ep12 무료 합성(0원): 상어 구경 장면(남의 사진, 로컬 전용)에 미순·창수 뒷모습을 붙이고 말풍선.
사용: python3 tools/ep12_free_composite.py [--scene reel|photo] → outputs/ep12/01/free_<scene>.png, compare_<scene>.jpg (로컬 전용)
- 캐릭터 뒷모습 시트에서 ISNet으로 누끼 → 크기·위치 → 햇빛에 맞춰 밝기·선명도·입자, 해 반대쪽으로 땅 그림자.
- v2(사용자): 휴대폰 뺌(나란히 서서 구경하는 뒷모습), 미순·창수가 확실히 보이게, 말풍선(미순 분홍, 창수 파랑).
- v3(사용자): 사진을 릴스 캡처(부캉이 산책로)로 바꿈. 말풍선은 더 연하고 둥글게, 뾰족한 꼬리 대신 작은 동그라미,
  글씨체 Jua(귀여운 둥근 글씨, OFL 무료).
- 릴스 캡처의 인스타 화면 요소(상태바·뒤로가기·오른쪽 버튼·계정명·음악)는 영상 내용이 아니라서 잘라내고 9:16으로.
  원작자 표시는 캡션에 적기를 권함. 사진 자체의 워터마크·저작권 표시는 지우지 않음(저작권법상 금지).
"""
import argparse, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, 'outputs/ep12')
MODEL = '/tmp/claude-0/-home-user-video/f018d661-8ddb-51f7-8e2d-f2480d28ac5d/scratchpad/models/isnet.onnx'
REFS = {'back': ('assets/characters/pang-misun/pang-misun_body_back.png', 'assets/characters/pang-changsu/pang-changsu_body_back.png'),
        'right': ('assets/characters/pang-misun/pang-misun_3q_right.png', 'assets/characters/pang-changsu/pang-changsu_3q_right.png')}   # 3/4 오른쪽 보기
LINES = {'misun': '쟤가 부캉이야?', 'changsu': '웅! 다시 돌아왔다는뎅'}
COLOR = {'misun': '#FFF1F6', 'changsu': '#EEF5FF'}      # 아주 연한 분홍·파랑
SCENES = {
    # 원본 좌표: place = (누구, 아래 중심 x, 발 y, 키), sun = 그림자 방향(-1 왼쪽), crop = 결과로 쓸 영역, inpaint = 지울 화면 요소 상자
    # 결과 좌표: bubble = (누구, 풍선 중심, 동그라미 끝 = 머리 위)
    # v4(사용자: "부캉이를 바라보며 서 있게, 시선은 상어로"): 상어가 오른쪽 아래 → 오른쪽을 보는 3/4 모습(얼굴도 보임)
    'reel': dict(src='ref/source_reel.png', crop=(0, 0, 1010, 1796), out_w=1080, sun=-1, pose='right', tilt=-7,   # 오른쪽 아래(상어)로 고개를 살짝 숙임
                 # 걸어가던 두 사람 앞(발 y 510보다 앞)에 서서 그 둘을 가림. 더 앞에 있는 사람(난간 파란 셔츠·여자)은 다시 위로 올림
                 # v5(사용자: "사람처럼 옆으로 나란히"): 같은 발 높이, 어깨가 거의 닿게. 발은 난간 안쪽(이 높이에서 난간 x≈230)
                 place=[('misun', 92, 524, 192), ('changsu', 200, 524, 202)],
                 front=[(140, 385, 255, 615), (35, 455, 185, 735)],
                 inpaint=[(90, 215, 140, 288), (110, 50, 320, 120), (830, 50, 1030, 120)],   # 인스타 뒤로가기·시각·신호/배터리
                 bubble=[('misun', (290, 150), (100, 345)), ('changsu', (660, 470), (250, 352))]),
    'photo': dict(src='ref/source_photo.jpg', crop=(0, 0, 800, 657), out_w=1600, sun=0, pose='back',
                  place=[('misun', 292, 712, 236), ('changsu', 462, 716, 246)],   # 오른쪽 아래 언론사 표시를 가리지 않는 자리
                  inpaint=[], front=[],
                  bubble=[('misun', (470, 670), (570, 956)), ('changsu', (1090, 784), (924, 936))]),
}


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
    """한낮 햇빛: 위쪽 밝게·아래쪽 살짝 어둡게(색은 그대로 — 따뜻한 색을 더하면 회색 털이 베이지로 보임)."""
    rgb = ImageEnhance.Color(ImageEnhance.Contrast(p.convert("RGB")).enhance(1.08)).enhance(0.75); a = p.getchannel("A")   # 시트의 누런 기 빼서 은회색으로(볼터치는 남게)
    g = np.linspace(1.08, 0.85, rgb.height)[:, None, None]
    out = Image.fromarray(np.clip(np.asarray(rgb).astype(float) * g, 0, 255).astype('uint8'))
    out.putalpha(a.filter(ImageFilter.GaussianBlur(0.8)))
    return out


def bubble(img, who, c, tip, scale):
    """둥근 알약 말풍선(아주 연한 색, 테두리 없음, 옅은 그림자) + 말하는 쪽으로 작아지는 동그라미 3개."""
    f = ImageFont.truetype(os.path.join(ROOT, 'assets/fonts/Jua-Regular.ttf'), int(46 * scale))
    d = ImageDraw.Draw(img); text = LINES[who]
    l, t, r, b = d.textbbox((0, 0), text, font=f); tw, th = r - l, b - t
    px, py = 34 * scale, 22 * scale; cx, cy = c
    box = [cx - tw / 2 - px, cy - th / 2 - py, cx + tw / 2 + px, cy + th / 2 + py]; hh = box[3] - box[1]
    if box[0] <= tip[0] <= box[2] or tip[1] > box[3]:     # 머리가 아래쪽: 풍선 아래 가장자리에서 출발
        sx, sy = min(max(tip[0], box[0] + hh / 2), box[2] - hh / 2), box[3]
    else:                                                  # 머리가 옆쪽: 풍선 옆 가장자리에서 출발
        sx, sy = (box[0] if tip[0] < box[0] else box[2]), cy
    dots = [(sx + (tip[0] - sx) * k, sy + (tip[1] - sy) * k, (15 - 4 * i) * scale) for i, k in enumerate((0.35, 0.65, 0.9))]
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh); o = 3 * scale
    ds.rounded_rectangle([v + o for v in box], radius=hh / 2, fill=(0, 0, 0, 45))
    for x, y, r_ in dots:
        ds.ellipse([x - r_ + o, y - r_ + o, x + r_ + o, y + r_ + o], fill=(0, 0, 0, 45))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5 * scale)))
    d.rounded_rectangle(box, radius=hh / 2, fill=COLOR[who])
    for x, y, r_ in dots:
        d.ellipse([x - r_, y - r_, x + r_, y + r_], fill=COLOR[who])
    d.text((cx - tw / 2 - l, cy - th / 2 - t), text, font=f, fill=(92, 78, 82))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--scene', default='reel'); a = ap.parse_args()
    S = SCENES[a.scene]
    photo = Image.open(os.path.join(EP, S['src'])).convert('RGB')
    if S['inpaint']:   # 인스타 화면 요소(사진 내용 아님)만 주변으로 메움
        import cv2
        arr = np.asarray(photo).copy(); m = np.zeros(arr.shape[:2], np.uint8)
        for x0, y0, x1, y1 in S['inpaint']:
            reg = arr[y0:y1, x0:x1].min(2) > 232; m[y0:y1, x0:x1][reg] = 255   # 흰 화면 요소만(밝은 회색 바닥 타일은 남김)
        m = cv2.dilate(m, np.ones((5, 5), np.uint8))
        photo = Image.fromarray(cv2.inpaint(arr, m, 5, cv2.INPAINT_TELEA))
    base = photo.convert('RGBA'); W, H = photo.size
    sh = Image.new('L', (W, H), 0); d = ImageDraw.Draw(sh); layers = []
    for who, cx, fy, ht in sorted(S['place'], key=lambda p: p[2]):     # 먼 쪽(위)부터 그림
        p = cut(REFS[S['pose']][0 if who == 'misun' else 1])
        if S.get('tilt'):
            p = p.rotate(S['tilt'], expand=True, resample=Image.BICUBIC)
        s = ht / p.height
        p = sunlit(p.resize((int(p.width * s), ht), Image.LANCZOS)); x, y = int(cx - p.width / 2), int(fy - ht)
        off = S['sun'] * p.width * 0.45
        d.ellipse([x + p.width * 0.1 + off, fy - 12, x + p.width * 0.9 + off, fy + 10], fill=120)
        layers.append((p, x, y))
    shadow = sh.filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * 0.7))   # 발밑이 떠 보이지 않게 조금 진하게
    base.alpha_composite(Image.composite(Image.new('RGBA', (W, H), (20, 25, 25, 255)), Image.new('RGBA', (W, H), (0, 0, 0, 0)), shadow))
    for p, x, y in layers:
        base.alpha_composite(p, (x, y))
    for x0, y0, x1, y1 in S['front']:   # 미순·창수보다 카메라에 가까운 사람은 다시 앞으로
        sys.path.insert(0, os.path.join(ROOT, 'tools'))
        from cutout import alpha
        reg = photo.crop((x0, y0, x1, y1)); m = alpha(reg, MODEL).point(lambda v: 255 if v > 150 else 0)   # 반투명 테두리가 미순·창수 위에 푸른 얼룩을 남김 → 확실한 부분만
        r_ = reg.convert('RGBA'); r_.putalpha(m.filter(ImageFilter.GaussianBlur(0.7))); base.alpha_composite(r_, (x0, y0))
    out = base.convert('RGB').crop(S['crop'])
    arr = np.asarray(out.filter(ImageFilter.GaussianBlur(0.35))).astype(float)
    arr += np.random.default_rng(1).normal(0, 2.2, arr.shape)
    k = S['out_w'] / out.width
    out = Image.fromarray(np.clip(arr, 0, 255).astype('uint8')).resize((S['out_w'], round(out.height * k)), Image.LANCZOS).convert('RGBA')
    for who, c, tip in S['bubble']:
        bubble(out, who, c, tip, S['out_w'] / 1080)
    out = out.convert('RGB')
    os.makedirs(os.path.join(EP, '01'), exist_ok=True)
    out.save(os.path.join(EP, f'01/free_{a.scene}.png'))
    src = photo.crop(S['crop']).resize(out.size)
    cmp_ = Image.new('RGB', (out.width * 2 + 20, out.height), 'white'); cmp_.paste(src, (0, 0)); cmp_.paste(out, (out.width + 20, 0))
    cmp_.resize((cmp_.width // 2, cmp_.height // 2)).save(os.path.join(EP, f'01/compare_{a.scene}.jpg'), quality=88)
    print('ok', os.path.join(EP, f'01/free_{a.scene}.png'), out.size)


if __name__ == '__main__':
    main()
