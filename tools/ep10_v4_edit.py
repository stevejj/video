#!/usr/bin/env python3
"""ep10 v4 방구배틀(0원 편집, Kling 없음): 서로 등 돌리고 잠(K4 한 장, K5 없음 — 사용자). 눈은 끝까지 감음.
사용: python3 tools/ep10_v4_edit.py → edit_list.json, hf_fx.json, text_overlay.json, sfx/sfx_list.json (+ voice_profile ep10 빈 대사)
- 이불 움직임: 이미지에서 이불 부분(왼쪽 미순·오른쪽 창수)을 가장자리 부드럽게 잘라 레이어로 올림.
  숨쉬기 = 세로로 1.5% 오르내림, 방귀 = 등이 맞닿은 가운데 쪽이 들썩, 뒤척임 = 좌우로 꿈틀.
- 박자(사용자 2026-10-22: "방구 비트가 음악 비트를 따라하는 게 메인", 참고 = 리센느 LOVE ATTACK 하이라이트 릴스):
  배경음 = 새 112BPM 댄스 비트(`bgm/beat112.mp3`, ElevenLabs, 처음부터 나옴, 원곡은 쓰지 않음).
  방귀 = 참고 릴스에서 뽑은 북 패턴(16분음표 자리 2·3·4·7 | 8·11·12·14 = 킥·스네어)을 따라함.
  앞 반 마디는 미순(높은 뽀옹), 뒤 반 마디는 창수(낮은 뿌웅)가 받아침. 1마디 = 카운트, 2마디 = 4분음표 주고받기, 3~7마디 = 패턴, 8마디 첫 박 = 대방출.
- 귀뚜라미 소리 없음, 이불 소리는 아주 약하게(사용자 2026-10-22).
- 효과음 시작 시각 보정: 파일 앞의 무음만큼 일찍 놓음(ONSET, 미순 방귀 0.06s·이불 0.6s 늦게 들리던 싱크 문제).
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, 'outputs/ep10')
W, H, TOP, WIN = 1080, 1920, 0.30, 768
BPM, P0 = 112.0, 0.025         # beat112.mp3 측정: 112.0BPM, 북 소리 시작(에너지 급상승) 기준 첫 박 0.025s
BEAT = 60 / BPM; S16 = BEAT / 4; BAR = BEAT * 4
PAT = {'misun': [2, 3, 4, 7], 'changsu': [8, 11, 12, 14]}   # 참고 릴스 북 패턴(킥 2·3·7·8·11·14 + 스네어 4·12)
ONSET = {'fart_misun.mp3': 0.06, 'fart_changsu.mp3': 0.0, 'fart_finale.mp3': 0.0, 'duvet_rustle.mp3': 0.6}
EL = 'outputs/ep10/sfx/el/'
# 이불 조각(1080x1920 기준): 위쪽은 잠옷 깃 바로 아래부터, 가운데서 살짝 겹침
DUVET = {'dl': (0, 975, 560, 425), 'dr': (520, 975, 560, 425)}
SEAM_X = (0.46, 0.54)    # 방귀 구름 시작(창 비율 x): 미순 쪽·창수 쪽, 등이 맞닿은 가운데
PUFF_Y = 0.70
STIR = 0.7               # 창수 뒤척임(처음, 아주 약한 이불 소리)


def grid(bar, slot):
    return round(P0 + (bar - 1) * BAR + slot * S16, 3)


def hits():
    """(시각, 누구, 세기). 1마디: 3·4박 카운트, 2마디: 4분음표 주고받기, 3~7마디: 참고 패턴, 7마디 끝 16분 필인."""
    h = [(grid(1, 8), 'misun', 1.0), (grid(1, 12), 'changsu', 1.0)]
    h += [(grid(2, s_), 'misun' if s_ in (0, 8) else 'changsu', 1.0) for s_ in (0, 4, 8, 12)]
    for bar in range(3, 8):
        for who in ('misun', 'changsu'):
            h += [(grid(bar, s_), who, 0.8) for s_ in PAT[who] if not (bar == 7 and s_ == 14)]
    h += [(grid(7, s_), 'misun' if s_ % 2 else 'changsu', 0.7) for s_ in (13, 14, 15)]
    return sorted(h)


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
    return [{'t': round(t, 3), 'dur': 0.05, 'y': round(-8 * big, 1), 'rotation': r, 'ease': 'power2.out'},
            {'t': round(t + 0.05, 3), 'dur': 0.08, 'y': 0, 'rotation': 0, 'ease': 'power2.in'}]   # 16분음표(0.134s) 안에 끝


def puppet(bg, layers, keys):
    return {'bg': bg, 'src_width': W, 'layers': [
        {'id': k, 'img': layers[k], 'box': list(DUVET[k]), 'origin': '0% 100%' if k == 'dl' else '100% 100%', 'keys': keys[k]} for k in DUVET]}


def main():
    b4 = bg_1080('outputs/ep10/04/start_v1.png', 'k4'); l4 = duvet_layers(b4, 'k4')

    H_ = hits(); finale = grid(8, 0)
    L1 = round(finale + 4.5, 2); total = L1   # K5 없이 K4 한 장으로 끝까지(사용자)
    E = {'canvas': [W, H], 'fps': 24, 'band': {'top_px': int(TOP * H), 'window_px': WIN}, 'still_zoom': 0.0, 'fade_out_before_black': 0.4,
         'cuts': [{'cut': '01', 'kind': 'still', 'source_cut': '04', 'image': b4, 'in': 0, 'len': L1, 'time_card': None}],
         'history': [f'2026-10-22 ep10 v4: 등 돌리고 방구배틀 {total:.1f}s, 112BPM 비트 따라 방귀, 눈 감은 채, 이불 움직임, 귀뚜라미 없음, K5 없음, Kling 0']}
    json.dump(E, open(os.path.join(EP, 'edit_list.json'), 'w'), ensure_ascii=False, indent=1)

    side = {'misun': 'dl', 'changsu': 'dr'}
    k1 = {'dl': breathe(L1, 3.0, 0.015), 'dr': breathe(L1, 3.4, 0.015, 0.8)}
    k1['dr'] += [{'t': STIR + i * 0.16, 'dur': 0.16, 'x': [4, -3, 2, 0][i], 'ease': 'sine.inOut'} for i in range(4)]
    for t, who, g in H_:
        k1[side[who]] += bump(t, side[who], g * (1.0 if who == 'misun' else 1.3))
    for s_ in ('dl', 'dr'):
        k1[s_] += bump(finale, s_, 2.0)

    pf = lambda t, who, size, dur, **k: dict(at=round(t, 3), x=SEAM_X[0] if who == 'misun' else SEAM_X[1], y=PUFF_Y, size=size, dur=dur, rise=k.pop('rise', 50), **k)
    puffs = [pf(t, who, int((150 if who == 'misun' else 180) * (1.2 if g == 1.0 else 1.0)), 0.5 if g == 1.0 else 0.38, alpha=0.7) for t, who, g in H_]
    puffs += [pf(finale, 'misun', 460, 1.6, rise=90, alpha=0.6), pf(finale + 0.05, 'changsu', 460, 1.6, rise=90, alpha=0.6),
              dict(at=round(finale + 0.35, 2), x=0.5, y=0.6, size=900, dur=2.4, rise=40, alpha=0.45)]
    gm = ghost(b4, (60, 640, 560, 1000), 'misun'); gc = ghost(b4, (520, 600, 1020, 1000), 'changsu')
    F = json.load(open(os.path.join(ROOT, 'outputs/ep09/hf_fx.json')))
    F['default_still'] = {'cam': None}; F['default_clip'] = {'cam': None}
    F['cuts'] = {
        '01': {'puppet': puppet(b4, l4, k1), 'puffs': puffs,
               'tint': {'at': finale + 0.2, 'dur': L1 - finale - 0.2, 'color': 'rgba(120,200,70,0.55)', 'fade': 0.3},
               'ghosts': [{'img': 'outputs/ep10/ref/ghost_v4_misun.png', 'src_width': W, 'box': gm, 'at': finale + 0.9, 'dur': L1 - finale - 0.9, 'rise': 150, 'opacity': 0.6},
                          {'img': 'outputs/ep10/ref/ghost_v4_changsu.png', 'src_width': W, 'box': gc, 'at': finale + 1.0, 'dur': L1 - finale - 1.0, 'rise': 150, 'opacity': 0.6}]},
    }
    F['note'] = 'ep10 v4: 등 돌림 + 112BPM 비트 따라 방귀 구름 + 이불 움직임(숨쉬기·들썩·뒤척임) + 초록 필터 + 영혼 둘, 고정 카메라, K5 없음'
    json.dump(F, open(os.path.join(EP, 'hf_fx.json'), 'w'), ensure_ascii=False, indent=1)

    T = json.load(open(os.path.join(ROOT, 'outputs/ep09/text_overlay.json')))
    T['title']['lines'] = [{'spans': [{'text': '현실부부 ', 'color': '#FFFFFF'}, {'text': '방구배틀', 'color': '#FFD84A'}]}, {'text': '공감 100%', 'color': '#FFFFFF'}]
    T['subtitles'] = []
    T['note'] = 'ep10: 자막 없음, 제목·채널명만'
    json.dump(T, open(os.path.join(EP, 'text_overlay.json'), 'w'), ensure_ascii=False, indent=1)

    sf = lambda name, file, a0, ln, lufs, **k: dict(name=name, file=file, at=round(a0 - ONSET.get(os.path.basename(file), 0), 3), len=round(ln, 3), target_lufs=lufs, fade_out=k.pop('fo', 0.03), **k)
    items = [sf('bgm', 'outputs/ep10/bgm/beat112.mp3', 0.0, finale + 0.06, -21, fo=0.06),
             sf('stir', EL + 'duvet_rustle.mp3', STIR, 0.7, -42, fo=0.3)]                    # 아주 약하게
    for i, (t, who, g) in enumerate(H_):
        f = 'fart_misun.mp3' if who == 'misun' else 'fart_changsu.mp3'
        nxt = H_[i + 1][0] if i + 1 < len(H_) else finale
        items.append(sf(f'h{i:02d}_{who}', EL + f, t, min(0.3, nxt - t + 0.05), (-18 if who == 'misun' else -17) + (1 if g == 1.0 else 0)))
    items += [sf('finale', EL + 'fart_finale.mp3', finale, 3.0, -15, fo=0.4),
              sf('dun', 'outputs/ep09/sfx/el/dun_sting.mp3', finale + 1.0, 1.4, -19)]
    json.dump({'note': 'ep10 v4 방구배틀 효과음(112BPM 비트 따라함, 귀뚜라미 없음, 이불 소리 아주 약하게)', 'items': items}, open(os.path.join(EP, 'sfx/sfx_list.json'), 'w'), ensure_ascii=False, indent=1)

    pp = os.path.join(ROOT, 'outputs/voice_profile.json'); P = json.load(open(pp))
    P['episodes'].setdefault('ep10', {})
    P['episodes']['ep10'].update({'lines': [], 'placements': [], 'note': 'ep10 방구배틀: 대사 없음, 효과음만(배경음도 sfx_list의 칩튠)'})
    P['episodes']['ep10'].pop('bgm', None)
    json.dump(P, open(pp, 'w'), ensure_ascii=False, indent=1)
    print(f'ep10 v4: {total:.2f}s, 방귀 {len(H_)}번, 대방출 {finale}s, 영혼 상자 {gm} {gc}')


if __name__ == '__main__':
    main()
