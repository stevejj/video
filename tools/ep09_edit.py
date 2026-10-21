#!/usr/bin/env python3
"""ep09 편집 구성 생성(0원): 애니매틱(키프레임 정지) / 완성(Kling 클립) 공통.
사용: python3 tools/ep09_edit.py --mode animatic|final  → edit_list(_animatic).json, hf_fx(_animatic).json, text_overlay.json, sfx_list.json, placements
- 장면 시작 = 앞 장면 길이 누적, 대사 = 장면 트랙(voice/scenes/sN.mp3)을 장면 시작에 배치.
- 자막 = 장면 시작 + 대사 scene_at, 길이 = len_file.
- 4장면은 폰 화면 그래픽(K1 흐림 + 폰 + 메뉴 타일, PIL로 합성).
- 효과(기획안 01): 1 게이지, 2 핀 조명·펀치·줌, 3 탈락 도장, 4 메뉴 ✕, 5 영혼 탈출·푸른 필터, 6 집중선, 7 반짝, 8 흑백 회상(6장면 "난 안 먹을 거야"), 9 정지 화면.
"""
import argparse, json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, 'outputs/ep09')
W, H, TOP = 1080, 1920, 0.30          # 30/40/30 띠: 창 = y 576~1344
WIN = 768
LENS = {'s1': 5.0, 's2': 5.0, 's3': 5.5, 's4': 3.5, 's5': 5.0, 's6': 4.5, 's7': 3.5, 's8': 6.0, 's9': 4.5}
BAND = {'s5': 28, 's7': 36}           # 장면별 띠 위치(%) — 이미지 확인 결과(K5 머리, K7 상자)
IMG = {'03': 'start_v2.png'}   # K3 v2: 눈이 작아져 K2 눈을 옮겨 붙인 수정본(사용자 발견, 0원)
TILES = [('🍚', '한식'), ('🥟', '중식'), ('🍣', '일식'), ('🍗', '치킨'), ('🍕', '피자'), ('🍢', '분식')]


def font(size):
    return ImageFont.truetype(os.path.join(ROOT, 'assets/fonts/NotoSansKR-Variable.ttf'), size)


def phone_graphic():
    """4장면: K1을 흐리게 깔고 가운데 폰(배달앱 느낌, 글자·로고는 일반 단어만) + 메뉴 타일 2x3. 타일 중심(창 비율)을 돌려줌."""
    bg = Image.open(os.path.join(EP, '01/start_v1.png')).convert('RGB').resize((W, H)).filter(ImageFilter.GaussianBlur(18))
    bg = Image.eval(bg, lambda v: int(v * 0.72))
    d = ImageDraw.Draw(bg)
    pw, ph = 470, 700; px, py = (W - pw) // 2, int(TOP * H) + (WIN - ph) // 2
    d.rounded_rectangle([px - 14, py - 14, px + pw + 14, py + ph + 14], 56, fill=(25, 25, 28))
    d.rounded_rectangle([px, py, px + pw, py + ph], 44, fill=(250, 248, 244))
    d.text((px + pw / 2, py + 62), '오늘 뭐 먹지?', font=font(44), fill=(40, 40, 40), anchor='mm')
    try:
        emo = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)
    except OSError:
        emo = None
    centers = []
    tw, th = 190, 168
    for i, (e, name) in enumerate(TILES):
        cx = px + pw / 2 + (-1 if i % 2 == 0 else 1) * (tw / 2 + 10); cy = py + 190 + (i // 2) * (th + 18)
        d.rounded_rectangle([cx - tw / 2, cy - th / 2, cx + tw / 2, cy + th / 2], 28, fill=(255, 236, 214))
        if emo:
            g = Image.new('RGBA', (140, 140), (0, 0, 0, 0)); ImageDraw.Draw(g).text((70, 70), e, font=emo, anchor='mm', embedded_color=True)
            g = g.resize((80, 80)); bg.paste(g, (int(cx - 40), int(cy - 66)), g)
        d.text((cx, cy + 46), name, font=font(40), fill=(60, 50, 40), anchor='mm')
        centers.append((cx / W, (cy - TOP * H) / WIN))
    os.makedirs(os.path.join(EP, '04'), exist_ok=True)
    bg.save(os.path.join(EP, '04/start_v1.png'))
    return centers


def phone_app():
    """4장면(무료 업그레이드, 사용자 2026-10-21): 배달앱처럼 보이는 폰 화면.
    레이어 3장: bg(흐린 거실) / list(가게 카드 세로 목록, 스크롤) / overlay(흐린 거실 + 폰 테두리 + 상단 고정 영역, 목록 창만 투명).
    가게 이름은 일반 단어만(실제 브랜드 없음). 반환: 칩 중심·화면 중심(창 비율), 목록 레이어 상자."""
    bg = Image.open(os.path.join(EP, '01/start_v1.png')).convert('RGB').resize((W, H)).filter(ImageFilter.GaussianBlur(18))
    bg = Image.eval(bg, lambda v: int(v * 0.70))
    pw, ph = 450, 640; px, py = (W - pw) // 2, int(TOP * H) + 112   # 위쪽 상황 자막(창 위 40~135px) 아래로
    LV = 252                                   # 목록 창 시작(화면 안 y)
    try:
        emo = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)
    except OSError:
        emo = None

    def emoji(img, e, cx, cy, size):
        if not emo:
            return
        g = Image.new('RGBA', (140, 140), (0, 0, 0, 0)); ImageDraw.Draw(g).text((70, 70), e, font=emo, anchor='mm', embedded_color=True)
        g = g.resize((size, size)); img.paste(g, (int(cx - size / 2), int(cy - size / 2)), g)

    # overlay: 흐린 거실 + 폰 테두리 + 화면 상단(상태바·검색·칩·제목)
    ov = bg.convert('RGBA'); d = ImageDraw.Draw(ov)
    d.rounded_rectangle([px - 16, py - 16, px + pw + 16, py + ph + 16], 60, fill=(22, 22, 26, 255))
    d.rounded_rectangle([px, py, px + pw, py + ph], 46, fill=(250, 248, 244, 255))
    d.text((px + 34, py + 24), '19:37', font=font(24), fill=(30, 30, 30), anchor='lm')
    d.rounded_rectangle([px + pw - 70, py + 15, px + pw - 30, py + 33], 5, outline=(30, 30, 30), width=3)
    d.rectangle([px + pw - 67, py + 18, px + pw - 42, py + 30], fill=(30, 30, 30))
    d.rounded_rectangle([px + 18, py + 52, px + pw - 18, py + 118], 33, fill=(238, 236, 232))
    emoji(ov, '🔍', px + 52, py + 85, 30)
    d.text((px + 76, py + 85), '오늘 뭐 먹지?', font=font(28), fill=(120, 116, 110), anchor='lm')
    chips = ['한식', '중식', '일식', '치킨', '피자']; cw, gap = 80, 7; x0 = px + (pw - (5 * cw + 4 * gap)) / 2; centers = []
    for i, c in enumerate(chips):
        cx0 = x0 + i * (cw + gap)
        d.rounded_rectangle([cx0, py + 134, cx0 + cw, py + 186], 26, fill=(255, 226, 196))
        d.text((cx0 + cw / 2, py + 160), c, font=font(26), fill=(70, 50, 30), anchor='mm')
        centers.append(((cx0 + cw / 2) / W, (py + 160 - TOP * H) / WIN))
    d.text((px + 24, py + 222), '지금 많이 찾는 가게', font=font(28), fill=(40, 40, 40), anchor='lm')
    hole = Image.new('L', (W, H), 255)
    ImageDraw.Draw(hole).rounded_rectangle([px, py + LV, px + pw, py + ph], 46, fill=0)
    ImageDraw.Draw(hole).rectangle([px, py + LV, px + pw, py + LV + 60], fill=0)
    ov.putalpha(hole)

    # list: 가게 카드 12개
    shops = [('🍗', '바삭치킨 연구소', '4.9', '25'), ('🍕', '화덕피자 공방', '4.8', '30'), ('🍚', '엄마손 백반', '4.7', '20'),
             ('🍜', '짬뽕 한 그릇', '4.8', '35'), ('🍣', '초밥 한 점', '4.9', '40'), ('🍢', '동네 떡볶이', '4.6', '20'),
             ('🍖', '족발 야시장', '4.8', '45'), ('🍲', '국밥 한 상', '4.7', '25'), ('🍔', '수제버거 집', '4.6', '30'),
             ('🥗', '샐러드 가게', '4.5', '25'), ('🌶', '마라탕 가게', '4.7', '35'), ('🍛', '돈까스 키친', '4.8', '30')]
    ch, cg = 150, 12; lh = len(shops) * (ch + cg) + 40
    lst = Image.new('RGBA', (pw, lh), (250, 248, 244, 255)); ld = ImageDraw.Draw(lst)
    for i, (e, name, star, mins) in enumerate(shops):
        y = 8 + i * (ch + cg)
        ld.rounded_rectangle([14, y, pw - 14, y + ch], 22, fill=(255, 255, 255, 255), outline=(232, 228, 222), width=2)
        ld.rounded_rectangle([28, y + 15, 148, y + 135], 18, fill=(255, 236, 214))
        emoji(lst, e, 88, y + 75, 78)
        ld.text((168, y + 42), name, font=font(32), fill=(30, 30, 30), anchor='lm')
        ld.text((168, y + 86), f'★ {star}  ·  배달 {mins}분', font=font(25), fill=(120, 110, 100), anchor='lm')
        ld.text((168, y + 120), '배달팁 무료', font=font(22), fill=(80, 150, 120), anchor='lm')
    os.makedirs(os.path.join(EP, '04'), exist_ok=True); os.makedirs(os.path.join(EP, 'ref'), exist_ok=True)
    bg.save(os.path.join(EP, '04/start_v1.png'))
    lst.save(os.path.join(EP, 'ref/app_list.png')); ov.save(os.path.join(EP, 'ref/app_overlay.png'))
    return dict(chips=centers, screen=((px + pw / 2) / W, (py + ph * 0.6 - TOP * H) / WIN), list_box=[px, py + LV, pw, lh], list_h=lh, view_h=ph - LV)


def ghost_cut():
    """5장면 영혼 탈출: K5 창수 누끼(ISNet, 0원)."""
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    from cutout import alpha
    im = Image.open(os.path.join(EP, '05/start_v1.png')).convert('RGB').resize((W, H))
    a = np.asarray(alpha(im.crop((100, 420, 1080, 1560)), '/tmp/claude-0/-home-user-video/f018d661-8ddb-51f7-8e2d-f2480d28ac5d/scratchpad/models/isnet.onnx')).copy()
    a[a < 70] = 0
    rgba = np.dstack([np.asarray(im.crop((100, 420, 1080, 1560))), a])
    ys, xs = np.where(a > 0); b = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    out = os.path.join(EP, 'ref/ghost_changsu.png')
    Image.fromarray(rgba.astype('uint8')).crop(b).save(out)
    return [int(100 + b[0]), int(420 + b[1]), int(b[2] - b[0]), int(b[3] - b[1])]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--mode', choices=['animatic', 'final'], default='animatic')
    a = ap.parse_args(); anim = a.mode == 'animatic'
    P = json.load(open(os.path.join(ROOT, 'outputs/voice_profile.json'))); V = P['episodes']['ep09']
    order = ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9']
    st = {}; t = 0.0
    for s in order:
        st[s] = round(t, 3); t += LENS[s]
    total = round(t, 3)
    app = phone_app(); gbox = ghost_cut()

    # 편집표
    cuts = []
    for i, s in enumerate(order):
        n = s[1:].zfill(2)
        if anim or s == 's4':
            cuts.append({'cut': n, 'kind': 'still', 'source_cut': s, 'image': f'outputs/ep09/{n}/{IMG.get(n, "start_v1.png")}', 'in': 0, 'len': LENS[s], 'time_card': None})
        else:
            cuts.append({'cut': n, 'kind': 'clip', 'source_cut': s, 'clip_tag': 'v1', 'in': 0.0, 'len': LENS[s], 'time_card': None})
    E = {'canvas': [W, H], 'fps': 24, 'band': {'top_px': int(TOP * H), 'window_px': WIN}, 'still_zoom': 0.0, 'fade_out_before_black': 0.4,
         'cuts': cuts, 'history': [f'2026-10-21 ep09 {a.mode} v1: 9장면 {total}s, 효과 9곳(기획안 01)']}
    json.dump(E, open(os.path.join(EP, f'edit_list{"_animatic" if anim else ""}.json'), 'w'), ensure_ascii=False, indent=1)
    B = json.load(open(os.path.join(EP, 'band_offsets.json'))); B['per_cut_top'].update(BAND)
    json.dump(B, open(os.path.join(EP, 'band_offsets.json'), 'w'), ensure_ascii=False, indent=1)

    # 대사 배치·자막
    V['placements'] = [{'file': V['scenes'][s]['file'], 'at': st[s]} for s in order]
    V['bgm']['end_at'] = total
    json.dump(P, open(os.path.join(ROOT, 'outputs/voice_profile.json'), 'w'), ensure_ascii=False, indent=1)
    L = {l['cut']: l for l in V['lines']}
    at = lambda c: st['s' + ''.join(ch for ch in c if ch.isdigit())] + L[c]['scene_at']
    subs = []
    for c, l in L.items():
        sb = {'cut': c, 'text': l['subtitle'], 'speaker': l['speaker'], 'start': round(at(c), 2), 'end': round(at(c) + l['len_file'] + 0.05, 2), 'x': 0.5}
        if c == '2b':
            sb.update(color='#FFD84A', size=84)
        subs.append(sb)
    cap = lambda text, a0, a1: {'cut': 'cap', 'text': text, 'speaker': 'sfx', 'start': round(a0, 2), 'end': round(a1, 2), 'x': 0.5, 'pos': 'top'}
    pyeong = at('2b') + 0.55  # 강조 순간 "너무 많이" (v2: 2b "치킨은 너무 많이 먹었어")
    subs += [cap('(저녁 7시)', st['s1'] + 0.2, st['s1'] + 2.0),
             cap('(이번 주 치킨 3번 먹음)', pyeong + 0.1, st['s3']),
             cap('(탈락 메뉴 2개째)', at('3b'), at('3d')), cap('(탈락 메뉴 3개째)', at('3d'), at('3f')), cap('(탈락 메뉴 4개째)', at('3f'), st['s4']),
             cap('(배달앱 30분째 스크롤)', st['s4'] + 0.1, st['s5']),
             cap('(결국 처음 메뉴)', at('6a') + 0.6, st['s7']),
             cap('(40분 뒤, 치킨 도착)', st['s7'] + 0.1, st['s8']),
             cap('(이번 주 치킨 4번째)', at('8c'), st['s9']),
             cap('(내일도 시작)', at('9') + 2.1, total)]
    T = json.load(open(os.path.join(ROOT, 'outputs/ep08/text_overlay.json')))
    T['title']['lines'] = [{'text': '남자 여자', 'color': '#FFFFFF'}, {'text': '"아무거나" 공감 100%', 'color': '#FFD84A'}]
    T['subtitles'] = sorted(subs, key=lambda x: x['start'])
    T['note'] = 'ep09: 자막 = 장면 시작 + 대사 scene_at(tools/ep09_edit.py)'
    json.dump(T, open(os.path.join(EP, 'text_overlay.json'), 'w'), ensure_ascii=False, indent=1)

    # 효과(장면 안 상대 시각)
    rel = lambda c: L[c]['scene_at']
    F = json.load(open(os.path.join(ROOT, 'outputs/ep08/hf_fx_animatic.json')))
    if not anim:
        F['default_still'] = F['default_still']  # 4장면 그래픽만 정지
    F['default_clip'] = {'cam': None}
    tile_t = [rel('4a') + 0.05, rel('4a') + 0.55, rel('4a') + 1.05]
    F['cuts'] = {
        '01': {'gauge': {'at': rel('1b') + 0.2, 'dur': LENS['s1'] - rel('1b') - 0.2, 'label': '배고픔', 'fill': 1.0, 'y': 0.2}},
        '02': {'cam': {'from': 1.0, 'to': 1.16, 'pan_x': [0, -130]}, 'punch': {'at': pyeong - st['s2'], 'scale': 1.22, 'settle': 1.18},
               'spotlight': {'at': pyeong - st['s2'] - 0.05, 'dur': LENS['s2'] - (pyeong - st['s2']) + 0.05, 'cx': 0.66, 'cy': 0.45, 'r': 0.27, 'dark': 0.78}},
        '03': {'stamps': [{'at': rel('3b'), 'x': 0.26, 'y': 0.34, 'text': '피자 ✕', 'size': 96, 'w': 330, 'rot': -10},
                          {'at': rel('3d'), 'x': 0.74, 'y': 0.30, 'text': '떡볶이 ✕', 'size': 96, 'w': 380, 'rot': 8},
                          {'at': rel('3f') + 0.3, 'x': 0.5, 'y': 0.68, 'text': '족발 ✕', 'size': 96, 'w': 330, 'rot': -6}]},
        '04': {'cam': {'from': 1.0, 'to': 1.04}, 'drift': {'amp': 4, 'period': 0.5},
               'puppet': {'bg': 'outputs/ep09/04/start_v1.png', 'src_width': W, 'layers': [
                   {'id': 'list', 'img': 'outputs/ep09/ref/app_list.png', 'box': app['list_box'], 'origin': '0px 0px',
                    'keys': [{'t': rel('4b') - 0.1, 'dur': 1.3, 'y': -(app['list_h'] - app['view_h'] - 60), 'ease': 'power2.inOut'}]},
                   {'id': 'ov', 'img': 'outputs/ep09/ref/app_overlay.png', 'box': [0, 0, W, H], 'origin': '0px 0px', 'keys': []}]},
               'taps': [{'at': tt, 'x': app['chips'][k][0], 'y': app['chips'][k][1], 'r': 60} for k, tt in enumerate(tile_t)]
               + [{'at': rel('4b') - 0.15, 'x': 0.55, 'y': 0.82, 'r': 80}],
               'stamps': [{'at': tt + 0.12, 'x': app['chips'][k][0], 'y': app['chips'][k][1], 'size': 76} for k, tt in enumerate(tile_t)]
               + [{'at': rel('4b') + 1.25, 'x': app['screen'][0], 'y': app['screen'][1], 'size': 300, 'rot': -8}]},
        '05': {'tint': {'at': 0.4, 'dur': LENS['s5'] - 0.4, 'color': 'rgba(110,150,235,0.55)', 'fade': 0.8},
               'ghost': {'img': 'outputs/ep09/ref/ghost_changsu.png', 'src_width': W, 'box': gbox, 'at': rel('5a') + 1.2, 'dur': LENS['s5'] - rel('5a') - 1.2, 'rise': 280, 'opacity': 0.45}},
        '06': {'speedlines': {'at': rel('6a'), 'dur': 1.4, 'cx': 0.3, 'cy': 0.5}, 'punch': {'at': rel('6a'), 'scale': 1.08, 'settle': 1.04}},
        '07': {'sparkle': {'at': rel('7') + 0.1, 'cx': 0.5, 'dur': 1.6, 'dy': 40}},
        '08': {'flashback': {'cut': 's6', 'image': 'outputs/ep09/06/start_v1.png', 't': rel('6b') + 0.3, 'top': TOP, 'at': rel('8b') + L['8b']['len_file'] - 0.2, 'dur': 1.1, 'label': '(아까)', 'w': 0.5, 'y': 0.08}},
        '09': {'freeze': {'at': rel('9') + 2.0, 'zoom': 1.32, 'x': -230}},
    }
    if anim:  # 정지 화면은 애니매틱에선 이미 정지 → 줌·패닝만
        F['cuts']['09']['freeze'] = {'at': rel('9') + 2.0, 'zoom': 1.32, 'x': -230}
    F['note'] = f'ep09 {a.mode}: 효과 9곳(하트 제외 — 사용자)'
    json.dump(F, open(os.path.join(EP, f'hf_fx{"_animatic" if anim else ""}.json'), 'w'), ensure_ascii=False, indent=1)

    # 효과음
    sf = lambda name, file, a0, ln, lufs, **k: dict(name=name, file=file, at=round(a0, 2), len=ln, target_lufs=lufs, fade_out=0.1, **k)
    el = 'outputs/ep09/sfx/el/'
    X = {'note': f'ep09 {a.mode} 효과음', 'items': [
        sf('stomach_growl', el + 'stomach_growl.mp3', st['s1'] + rel('1b') + 0.2, 1.4, -24),
        sf('dramatic_hit', el + 'dramatic_hit.mp3', pyeong - 0.05, 1.4, -20),
        sf('bang', 'outputs/ep02/sfx/el/charger_drop.mp3', pyeong, 0.5, -20, gain=12.0),
        *[sf(f'buzz{k}', el + 'wrong_buzzer.mp3', st['s3'] + x, 0.6, -24) for k, x in enumerate([rel('3b'), rel('3d'), rel('3f') + 0.3])],
        *[sf(f'buzz4_{k}', el + 'wrong_buzzer.mp3', st['s4'] + x, 0.5, -26) for k, x in enumerate([tt + 0.12 for tt in tile_t] + [rel('4b') + 1.25])],
        sf('doorbell', el + 'doorbell.mp3', st['s7'] + 0.1, 1.4, -22),
        sf('sparkle', 'outputs/ep01/sfx/el/sparkle.mp3', st['s7'] + rel('7') + 0.1, 0.8, -26),
        sf('flashback', el + 'flashback_chime.mp3', st['s8'] + rel('8b') + L['8b']['len_file'] - 0.25, 1.1, -22),
        sf('dun', el + 'dun_sting.mp3', st['s9'] + rel('9') + 2.0, 1.4, -20),
    ]}
    os.makedirs(os.path.join(EP, 'sfx'), exist_ok=True)
    json.dump(X, open(os.path.join(EP, 'sfx/sfx_list.json'), 'w'), ensure_ascii=False, indent=1)
    print(f'ep09 {a.mode}: {total}s, 장면 시작', st, '\n유령 상자', gbox, '칩', [(round(x, 2), round(y, 2)) for x, y in app['chips']])


if __name__ == '__main__':
    main()
