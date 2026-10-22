#!/usr/bin/env python3
"""ep10 v4 방구배틀(0원 편집, Kling 없음): 서로 등 돌리고 잠(K4) → 대방출 뒤 둘 다 눈 질끈(K5). 눈은 끝까지 감음.
사용: python3 tools/ep10_v4_edit.py [--k5 PATH] → edit_list.json, hf_fx.json, text_overlay.json, sfx/sfx_list.json (+ voice_profile ep10 빈 대사)
- 이불 움직임: 이미지에서 이불 부분(왼쪽 미순·오른쪽 창수)을 가장자리 부드럽게 잘라 레이어로 올림.
  숨쉬기 = 세로로 1.5% 오르내림, 방귀 = 등이 맞닿은 가운데 쪽이 들썩, 뒤척임 = 좌우로 꿈틀.
- 박자: 칩튠 F(84.5BPM, 한 박 0.71s, 첫 박 0.31s). 주고받기 4번 → 8분음표 12번 → 16분음표 12번 → 대방출.
- 귀뚜라미 소리 없음(사용자 2026-10-22).
"""
import argparse, json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, 'outputs/ep10')
W, H, TOP, WIN = 1080, 1920, 0.30, 768
BEAT, PHASE = 0.71, 0.31
MUSIC_AT = 7.9
EL = 'outputs/ep10/sfx/el/'
# 이불 조각(1080x1920 기준): 위쪽은 잠옷 깃 바로 아래부터, 가운데서 살짝 겹침
DUVET = {'dl': (0, 975, 560, 425), 'dr': (520, 975, 560, 425)}
SEAM_X = (0.46, 0.54)    # 방귀 구름 시작(창 비율 x): 미순 쪽·창수 쪽, 등이 맞닿은 가운데
PUFF_Y = 0.70
PRE = [(3.0, 'misun', 'fart_misun.mp3', -20), (5.0, 'changsu', 'fart_changsu.mp3', -17),
       (6.3, 'misun', 'fart_misun.mp3', -21), (7.0, 'changsu', 'fart_changsu.mp3', -18)]   # 음악 전 주고받기
STIR = 4.2               # 창수 뒤척임(미순 첫 방귀에)


def bg_1080(src, name):
    """원본(768x1376)을 1080x1920으로 맞춰 저장(레이어 좌표와 화면이 정확히 같게)."""
    dst = os.path.join(EP, f'ref/{name}_1080.png')
    Image.open(os.path.join(ROOT, src)).convert('RGB').resize((W, H), Image.LANCZOS).save(dst)
    return os.path.relpath(dst, ROOT)


def duvet_layers(bg, tag):
    """이불 조각 레이어(가장자리 40px 부드럽게)."""
    im = Image.open(os.path.join(ROOT, bg)).convert('RGB'); out = {}
    for k, (x, y, w, h) in DUVET.items():
        m = Image.new('L', (w, h), 0); f = 40
        ImageDraw.Draw(m).rounded_rectangle([f, f, w - f, h + 200], radius=60, fill=255)   # 아래쪽은 창 밖이라 열어 둠
        m = m.filter(ImageFilter.GaussianBlur(f / 2))
        p = im.crop((x, y, x + w, y + h)); p.putalpha(m)
        f_ = os.path.join(EP, f'ref/{tag}_{k}.png'); p.save(f_); out[k] = os.path.relpath(f_, ROOT)
    return out


def ghost(src, box, name):
    """머리 누끼(ISNet) → 영혼 레이어."""
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    from cutout import alpha
    im = Image.open(os.path.join(ROOT, src)).convert('RGB').crop(box)
    a = np.asarray(alpha(im, '/tmp/claude-0/-home-user-video/f018d661-8ddb-51f7-8e2d-f2480d28ac5d/scratchpad/models/isnet.onnx')).copy(); a[a < 80] = 0
    ys, xs = np.where(a > 0); b = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    Image.fromarray(np.dstack([np.asarray(im), a]).astype('uint8')).crop(b).save(os.path.join(EP, f'ref/ghost_v4_{name}.png'))
    return [int(box[0] + b[0]), int(box[1] + b[1]), int(b[2] - b[0]), int(b[3] - b[1])]


def breathe(L, period, amp, phase=0.0):
    ks = []; t = phase
    while t < L:
        ks.append({'t': round(t, 3), 'dur': round(min(period / 2, L - t), 3), 'scaleY': 1 + amp, 'ease': 'sine.inOut'})
        t += period / 2
        if t < L:
            ks.append({'t': round(t, 3), 'dur': round(min(period / 2, L - t), 3), 'scaleY': 1.0, 'ease': 'sine.inOut'})
        t += period / 2
    return ks


def bump(t, side, big=1.0):
    """방귀: 가운데 쪽이 위로 들썩(왼쪽 조각은 반시계, 오른쪽은 시계 방향)."""
    r = (-1.4 if side == 'dl' else 1.4) * big
    return [{'t': round(t, 3), 'dur': 0.06, 'y': round(-8 * big, 1), 'rotation': r, 'ease': 'power2.out'},
            {'t': round(t + 0.06, 3), 'dur': 0.12, 'y': 0, 'rotation': 0, 'ease': 'power2.in'}]


def puppet(bg, layers, keys):
    return {'bg': bg, 'src_width': W, 'layers': [
        {'id': k, 'img': layers[k], 'box': list(DUVET[k]), 'origin': '0% 100%' if k == 'dl' else '100% 100%', 'keys': keys[k]} for k in DUVET]}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--k5', default='outputs/ep10/05/start_v1.png'); a = ap.parse_args()
    k5 = a.k5 if os.path.exists(os.path.join(ROOT, a.k5)) else 'outputs/ep10/04/start_v1.png'   # K5 전에는 K4로 미리 보기
    b4 = bg_1080('outputs/ep10/04/start_v1.png', 'k4'); b5 = bg_1080(k5, 'k5')
    l4 = duvet_layers(b4, 'k4'); l5 = duvet_layers(b5, 'k5')

    # 박자
    t0 = MUSIC_AT + PHASE + BEAT
    hits = [t0 + i * BEAT / 2 for i in range(12)]
    t1 = hits[-1] + BEAT / 2
    hits += [t1 + i * BEAT / 4 for i in range(12)]
    finale = round(hits[-1] + BEAT / 2, 2)
    battle = [(round(h, 3), 'misun' if i % 2 == 0 else 'changsu') for i, h in enumerate(hits)]
    L1 = round(finale + 0.5, 2); L2 = 4.5; total = L1 + L2

    E = {'canvas': [W, H], 'fps': 24, 'band': {'top_px': int(TOP * H), 'window_px': WIN}, 'still_zoom': 0.0, 'fade_out_before_black': 0.4,
         'cuts': [{'cut': '01', 'kind': 'still', 'source_cut': '04', 'image': b4, 'in': 0, 'len': L1, 'time_card': None},
                  {'cut': '02', 'kind': 'still', 'source_cut': '05', 'image': b5, 'in': 0, 'len': L2, 'time_card': None}],
         'history': [f'2026-10-22 ep10 v4: 등 돌리고 방구배틀 {total:.1f}s, 눈 감은 채, 이불 움직임, 귀뚜라미 없음, Kling 0']}
    json.dump(E, open(os.path.join(EP, 'edit_list.json'), 'w'), ensure_ascii=False, indent=1)

    side = {'misun': 'dl', 'changsu': 'dr'}
    k1 = {'dl': breathe(L1, 3.0, 0.015), 'dr': breathe(L1, 3.4, 0.015, 0.8)}
    for t, who, _, _ in PRE:
        k1[side[who]] += bump(t, side[who], 1.0 if who == 'misun' else 1.4)
    k1['dr'] += [{'t': STIR + i * 0.16, 'dur': 0.16, 'x': [5, -4, 3, 0][i], 'ease': 'sine.inOut'} for i in range(4)]
    for h, who in battle:
        k1[side[who]] += bump(h, side[who], 0.8 if h < t1 else 0.6)
    for s in ('dl', 'dr'):
        k1[s] += bump(finale, s, 2.0)
    k2 = {'dl': breathe(L2, 3.0, 0.012), 'dr': breathe(L2, 3.4, 0.012, 0.8)}

    pf = lambda t, who, size, dur, **k: dict(at=round(t, 3), x=SEAM_X[0] if who == 'misun' else SEAM_X[1], y=PUFF_Y, size=size, dur=dur, rise=k.pop('rise', 50), **k)
    puffs = [pf(t, who, 200 if who == 'misun' else 280, 0.9, rise=70, alpha=0.75) for t, who, _, _ in PRE]
    puffs += [pf(h, who, 150 if h < t1 else 130, 0.55 if h < t1 else 0.4) for h, who in battle]
    puffs += [pf(finale, 'misun', 460, 1.6, rise=90, alpha=0.6), pf(finale + 0.05, 'changsu', 460, 1.6, rise=90, alpha=0.6),
              dict(at=round(finale + 0.35, 2), x=0.5, y=0.6, size=900, dur=2.4, rise=40, alpha=0.45)]
    gm = ghost(b5, (60, 640, 560, 1000), 'misun'); gc = ghost(b5, (520, 600, 1020, 1000), 'changsu')
    F = json.load(open(os.path.join(ROOT, 'outputs/ep09/hf_fx.json')))
    F['default_still'] = {'cam': None}; F['default_clip'] = {'cam': None}
    F['cuts'] = {
        '01': {'puppet': puppet(b4, l4, k1), 'puffs': puffs,
               'tint': {'at': finale + 0.2, 'dur': L1 - finale - 0.2, 'color': 'rgba(120,200,70,0.55)', 'fade': 0.3}},
        '02': {'puppet': puppet(b5, l5, k2), 'tint': {'at': 0.0, 'dur': L2, 'color': 'rgba(120,200,70,0.55)', 'fade': 0.01},
               'puffs': [dict(at=0.0, x=0.5, y=0.6, size=900, dur=2.0, rise=40, alpha=0.35)],
               'ghosts': [{'img': 'outputs/ep10/ref/ghost_v4_misun.png', 'src_width': W, 'box': gm, 'at': 0.5, 'dur': L2 - 0.5, 'rise': 150, 'opacity': 0.6},
                          {'img': 'outputs/ep10/ref/ghost_v4_changsu.png', 'src_width': W, 'box': gc, 'at': 0.6, 'dur': L2 - 0.6, 'rise': 150, 'opacity': 0.6}]},
    }
    F['note'] = 'ep10 v4: 등 돌림 + 이불 움직임(숨쉬기·들썩·뒤척임) + 방귀 구름 + 초록 필터 + 영혼 둘, 고정 카메라'
    json.dump(F, open(os.path.join(EP, 'hf_fx.json'), 'w'), ensure_ascii=False, indent=1)

    T = json.load(open(os.path.join(ROOT, 'outputs/ep09/text_overlay.json')))
    T['title']['lines'] = [{'spans': [{'text': '현실부부 ', 'color': '#FFFFFF'}, {'text': '방구배틀', 'color': '#FFD84A'}]}, {'text': '공감 100%', 'color': '#FFFFFF'}]
    T['subtitles'] = []
    T['note'] = 'ep10: 자막 없음, 제목·채널명만'
    json.dump(T, open(os.path.join(EP, 'text_overlay.json'), 'w'), ensure_ascii=False, indent=1)

    sf = lambda name, file, a0, ln, lufs, **k: dict(name=name, file=file, at=round(a0, 3), len=ln, target_lufs=lufs, fade_out=k.pop('fo', 0.05), **k)
    items = [sf('shift', EL + 'duvet_rustle.mp3', 1.2, 1.2, -32, fade_in=0.2, fo=0.4)]
    items += [sf(f'pre{i}_{who}', EL + f, t, 0.9, lufs) for i, (t, who, f, lufs) in enumerate(PRE)]
    items += [sf('stir', EL + 'duvet_rustle.mp3', STIR, 0.8, -27, fo=0.3),
              sf('bell', EL + 'boxing_bell.mp3', MUSIC_AT - 0.25, 1.4, -19),
              sf('chiptune', 'outputs/ep01/bgm/F_soft_chiptune.mp3', MUSIC_AT, round(finale - MUSIC_AT + 0.05, 2), -24, fade_in=0.1, fo=0.12)]
    for i, (h, who) in enumerate(battle):
        f = 'fart_misun.mp3' if who == 'misun' else 'fart_changsu.mp3'
        items.append(sf(f'b{i:02d}_{who}', EL + f, h, 0.32 if h < t1 else 0.17, -21 if who == 'misun' else -19))
    items += [sf('finale', EL + 'fart_finale.mp3', finale, 3.0, -16, fo=0.4),
              sf('dun', 'outputs/ep09/sfx/el/dun_sting.mp3', L1, 1.4, -19)]
    json.dump({'note': 'ep10 v4 방구배틀 효과음(귀뚜라미 없음, 박자: 칩튠 84.5BPM)', 'items': items}, open(os.path.join(EP, 'sfx/sfx_list.json'), 'w'), ensure_ascii=False, indent=1)

    pp = os.path.join(ROOT, 'outputs/voice_profile.json'); P = json.load(open(pp))
    P['episodes'].setdefault('ep10', {})
    P['episodes']['ep10'].update({'lines': [], 'placements': [], 'note': 'ep10 방구배틀: 대사 없음, 효과음만(배경음도 sfx_list의 칩튠)'})
    P['episodes']['ep10'].pop('bgm', None)
    json.dump(P, open(pp, 'w'), ensure_ascii=False, indent=1)
    print(f'ep10 v4: {total:.2f}s (K4 {L1} + K5 {L2}), 배틀 {len(battle)}번, 대방출 {finale}s, K5={k5}, 영혼 상자 {gm} {gc}')


if __name__ == '__main__':
    main()
