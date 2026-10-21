#!/usr/bin/env python3
"""ep09 편집 구성 생성(0원): 애니매틱(키프레임 정지) / 완성(Kling 클립) 공통.
사용: python3 tools/ep09_edit.py --mode animatic|final  → edit_list(_animatic).json, hf_fx(_animatic).json, text_overlay.json, sfx_list.json, placements
- 장면 시작 = 앞 장면 길이 누적, 대사 = 장면 트랙(voice/scenes/sN.mp3)을 장면 시작에 배치.
- 자막 = 장면 시작 + 대사 scene_at, 길이 = len_file.
- 4장면은 폰 화면 그래픽(K1 흐림 + 폰 + 메뉴 타일, PIL로 합성).
- 효과(기획안 01): 1 게이지, 2 핀 조명·펀치·줌, 3 탈락 도장, 4 메뉴 ✕, 5 영혼 탈출·푸른 필터, 6 집중선, 7 반짝, 8 흑백 회상, 9 정지 화면.
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
    tiles = phone_graphic(); gbox = ghost_cut()

    # 편집표
    cuts = []
    for i, s in enumerate(order):
        n = s[1:].zfill(2)
        if anim or s == 's4':
            cuts.append({'cut': n, 'kind': 'still', 'source_cut': s, 'image': f'outputs/ep09/{n}/start_v1.png', 'in': 0, 'len': LENS[s], 'time_card': None})
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
    pyeong = at('2b') + 1.58  # "평생!" (트랙 2.68s - 2b 시작 1.1s)
    subs += [cap('(저녁 7시)', st['s1'] + 0.2, st['s1'] + 2.0),
             cap('(치킨 끊은 지 0일차)', pyeong + 0.1, st['s3']),
             cap('(탈락 메뉴 2개째)', at('3b'), at('3d')), cap('(탈락 메뉴 3개째)', at('3d'), at('3f')), cap('(탈락 메뉴 4개째)', at('3f'), st['s4']),
             cap('(배달앱 30분째 스크롤)', st['s4'] + 0.1, st['s5']),
             cap('(결국 처음 메뉴)', at('6a') + 0.6, st['s7']),
             cap('(40분 뒤, 치킨 도착)', st['s7'] + 0.1, st['s8']),
             cap('(치킨 끊은 지 40분째)', at('8b'), st['s9']),
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
        '04': {'cam': {'from': 1.0, 'to': 1.04}, 'drift': {'amp': 5, 'period': 0.5},
               'stamps': [{'at': tt, 'x': tiles[k][0], 'y': tiles[k][1], 'size': 150} for k, tt in enumerate(tile_t)]
               + [{'at': rel('4b') + 0.1, 'x': tiles[k][0], 'y': tiles[k][1], 'size': 150} for k in (3, 4, 5)]},
        '05': {'tint': {'at': 0.4, 'dur': LENS['s5'] - 0.4, 'color': 'rgba(110,150,235,0.55)', 'fade': 0.8},
               'ghost': {'img': 'outputs/ep09/ref/ghost_changsu.png', 'src_width': W, 'box': gbox, 'at': rel('5a') + 1.2, 'dur': LENS['s5'] - rel('5a') - 1.2, 'rise': 280, 'opacity': 0.45}},
        '06': {'speedlines': {'at': rel('6a'), 'dur': 1.4, 'cx': 0.3, 'cy': 0.5}, 'punch': {'at': rel('6a'), 'scale': 1.08, 'settle': 1.04}},
        '07': {'sparkle': {'at': rel('7') + 0.1, 'cx': 0.5, 'dur': 1.6, 'dy': 40}},
        '08': {'flashback': {'cut': 's2', 'image': 'outputs/ep09/02/start_v1.png', 't': pyeong - st['s2'], 'top': TOP, 'at': rel('8a') + L['8a']['len_file'] - 0.2, 'dur': 1.1, 'label': '(아까)', 'w': 0.5, 'y': 0.08}},
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
        *[sf(f'buzz4_{k}', el + 'wrong_buzzer.mp3', st['s4'] + x, 0.5, -26) for k, x in enumerate(tile_t + [rel('4b') + 0.1])],
        sf('doorbell', el + 'doorbell.mp3', st['s7'] + 0.1, 1.4, -22),
        sf('sparkle', 'outputs/ep01/sfx/el/sparkle.mp3', st['s7'] + rel('7') + 0.1, 0.8, -26),
        sf('flashback', el + 'flashback_chime.mp3', st['s8'] + rel('8a') + L['8a']['len_file'] - 0.25, 1.1, -22),
        sf('dun', el + 'dun_sting.mp3', st['s9'] + rel('9') + 2.0, 1.4, -20),
    ]}
    os.makedirs(os.path.join(EP, 'sfx'), exist_ok=True)
    json.dump(X, open(os.path.join(EP, 'sfx/sfx_list.json'), 'w'), ensure_ascii=False, indent=1)
    print(f'ep09 {a.mode}: {total}s, 장면 시작', st, '\n유령 상자', gbox, '타일', [(round(x, 2), round(y, 2)) for x, y in tiles])


if __name__ == '__main__':
    main()
