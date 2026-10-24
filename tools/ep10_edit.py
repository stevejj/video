#!/usr/bin/env python3
"""ep10 방구배틀 편집 구성(0원, Kling 없음): 정지 이미지 3장 + 효과(방귀 구름·도장·집중선·흔들림·초록 필터·영혼 둘) + 효과음 비트.
사용: python3 tools/ep10_edit.py → edit_list.json, hf_fx.json, text_overlay.json, sfx/sfx_list.json (+ voice_profile ep10 빈 대사)
박자: 배경 칩튠 F(84.5BPM, 한 박 0.71s, 첫 박 0.31s). 배틀 = 8분음표 교대 → 16분음표로 빨라짐 → 마지막 박에 동시 대방출.
"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, 'outputs/ep10')
W, H, TOP, WIN = 1080, 1920, 0.30, 768
BEAT, PHASE = 0.71, 0.31
MUSIC_AT = 4.3                       # 칩튠 시작(K3 + ROUND 1 직후)
MISUN, CHANGSU = (0.32, 0.74), (0.68, 0.74)   # 이불 속 엉덩이 위치(창 비율)
EL = 'outputs/ep10/sfx/el/'
IMG = {'02': 'start_v2.png'}   # K2 v2: 창수 눈이 너무 커서 K3 눈을 옮겨 붙임(사용자, 0원)


def ghost(box, name):
    """K3에서 머리 누끼(ISNet) → 영혼 레이어."""
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    from cutout import alpha
    im = Image.open(os.path.join(EP, '03/start_v1.png')).convert('RGB').resize((W, H)).crop(box)
    a = np.asarray(alpha(im, '/tmp/claude-0/-home-user-video/f018d661-8ddb-51f7-8e2d-f2480d28ac5d/scratchpad/models/isnet.onnx')).copy(); a[a < 80] = 0
    ys, xs = np.where(a > 0); b = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    os.makedirs(os.path.join(EP, 'ref'), exist_ok=True)
    Image.fromarray(np.dstack([np.asarray(im), a]).astype('uint8')).crop(b).save(os.path.join(EP, f'ref/ghost_{name}.png'))
    return [int(box[0] + b[0]), int(box[1] + b[1]), int(b[2] - b[0]), int(b[3] - b[1])]


def main():
    cuts = [('01', 2.0), ('02', 2.0), ('03', 10.0)]
    E = {'canvas': [W, H], 'fps': 24, 'band': {'top_px': int(TOP * H), 'window_px': WIN}, 'still_zoom': 0.0, 'fade_out_before_black': 0.4,
         'cuts': [{'cut': c, 'kind': 'still', 'source_cut': c, 'image': f'outputs/ep10/{c}/{IMG.get(c, "start_v1.png")}', 'in': 0, 'len': L, 'time_card': None} for c, L in cuts],
         'history': ['2026-10-21 ep10 v1: 방구배틀 14s, Kling 0']}
    json.dump(E, open(os.path.join(EP, 'edit_list.json'), 'w'), ensure_ascii=False, indent=1)

    # 배틀 박자(절대 시각): 첫 박자 이후 8분음표 8번 → 16분음표 10번 → 다음 박에 대방출
    t0 = MUSIC_AT + PHASE + BEAT          # 5.32
    hits = [t0 + i * BEAT / 2 for i in range(8)]
    t1 = hits[-1] + BEAT / 2
    hits += [t1 + i * BEAT / 4 for i in range(10)]
    finale = round(hits[-1] + BEAT / 4 + BEAT / 4, 2)   # 다음 8분 자리
    K3 = 4.0
    rel = lambda t: round(t - K3, 3)
    battle = [(round(h, 3), 'misun' if i % 2 == 0 else 'changsu') for i, h in enumerate(hits)]

    gm = ghost((150, 620, 560, 1010), 'misun'); gc = ghost((540, 560, 940, 1010), 'changsu')
    F = json.load(open(os.path.join(ROOT, 'outputs/ep09/hf_fx.json')))
    F['default_still'] = {'cam': None}   # 원본처럼 고정 카메라(컷 사이 줌 튐 방지)
    F['default_clip'] = {'cam': None}
    F['cuts'] = {
        '01': {'puffs': [{'at': 1.0, 'x': MISUN[0], 'y': MISUN[1], 'size': 200}], 'shake': {'at': 1.0, 'amp': 2, 'dur': 0.2}},
        '02': {'puffs': [{'at': 0.7, 'x': CHANGSU[0], 'y': CHANGSU[1], 'size': 300, 'rise': 80}], 'shake': {'at': 0.7, 'amp': 2, 'dur': 0.2}},
        '03': {  # v2(사용자): ROUND 1·K.O.·집중선 뺌, 줌인·떨림 뺌(눈이 커지고 흔들려 보임) → 원본처럼 완전 고정
               'puffs': [{'at': rel(h), 'x': (MISUN if who == 'misun' else CHANGSU)[0] + (0.03 if i % 4 == 0 else -0.02),
                          'y': (MISUN if who == 'misun' else CHANGSU)[1], 'size': 150 if h < t1 else 130, 'dur': 0.55 if h < t1 else 0.4, 'rise': 50}
                         for i, (h, who) in enumerate(battle)]
               + [{'at': rel(finale), 'x': MISUN[0], 'y': 0.72, 'size': 460, 'dur': 1.6, 'rise': 90, 'alpha': 0.6},
                  {'at': rel(finale) + 0.05, 'x': CHANGSU[0], 'y': 0.72, 'size': 460, 'dur': 1.6, 'rise': 90, 'alpha': 0.6},
                  {'at': rel(finale) + 0.35, 'x': 0.5, 'y': 0.6, 'size': 900, 'dur': 2.4, 'rise': 40, 'alpha': 0.45}],
               'tint': {'at': rel(finale) + 0.2, 'dur': 14.0 - finale - 0.2, 'color': 'rgba(120,200,70,0.55)', 'fade': 0.6},
               'ghosts': [{'img': 'outputs/ep10/ref/ghost_misun.png', 'src_width': W, 'box': gm, 'at': rel(finale) + 0.8, 'dur': 14.0 - finale - 0.8, 'rise': 150, 'opacity': 0.6},
                          {'img': 'outputs/ep10/ref/ghost_changsu.png', 'src_width': W, 'box': gc, 'at': rel(finale) + 0.9, 'dur': 14.0 - finale - 0.9, 'rise': 150, 'opacity': 0.6}]},
    }
    F['note'] = 'ep10 방구배틀: v2 고정 카메라(줌·떨림 없음) + 방귀 구름 + 초록 필터 + 영혼 둘, 도장 없음'
    json.dump(F, open(os.path.join(EP, 'hf_fx.json'), 'w'), ensure_ascii=False, indent=1)

    T = json.load(open(os.path.join(ROOT, 'outputs/ep09/text_overlay.json')))
    # 제목(사용자): "현실부부 방구배틀 공감 100%", 노란색 = "방구배틀"
    T['title']['lines'] = [{'spans': [{'text': '현실부부 ', 'color': '#FFFFFF'}, {'text': '방구배틀', 'color': '#FFD84A'}]}, {'text': '공감 100%', 'color': '#FFFFFF'}]
    T['subtitles'] = []   # 대사·위쪽 자막 없음(사용자: "위쪽 자막은 일단 다 빼봐")
    T['note'] = 'ep10: 자막 없음, 제목·채널명만'
    json.dump(T, open(os.path.join(EP, 'text_overlay.json'), 'w'), ensure_ascii=False, indent=1)

    sf = lambda name, file, a0, ln, lufs, **k: dict(name=name, file=file, at=round(a0, 3), len=ln, target_lufs=lufs, fade_out=k.pop('fo', 0.05), **k)
    items = [sf('night', 'outputs/ep01/sfx/el/crickets.mp3', 0.0, 4.2, -38, loop=True, fade_in=0.3, fo=0.4),
             sf('misun_first', EL + 'fart_misun.mp3', 1.0, 0.8, -20),
             sf('changsu_answer', EL + 'fart_changsu.mp3', 2.7, 0.9, -17),
             sf('bell', EL + 'boxing_bell.mp3', 4.15, 1.4, -19),
             sf('chiptune', 'outputs/ep01/bgm/F_soft_chiptune.mp3', MUSIC_AT, round(finale - MUSIC_AT + 0.05, 2), -24, fade_in=0.1, fo=0.12)]
    for i, (h, who) in enumerate(battle):
        f = 'fart_misun.mp3' if who == 'misun' else 'fart_changsu.mp3'
        items.append(sf(f'b{i:02d}_{who}', EL + f, h, 0.32 if h < t1 else 0.17, -21 if who == 'misun' else -19))
    items += [sf('finale', EL + 'fart_finale.mp3', finale, 3.0, -16, fo=0.4),
              sf('dun', 'outputs/ep09/sfx/el/dun_sting.mp3', finale + 1.3, 1.4, -19),
              sf('night_end', 'outputs/ep01/sfx/el/crickets.mp3', finale + 2.6, round(14.0 - finale - 2.6, 2), -34, loop=True, fade_in=0.4, fo=0.3)]
    os.makedirs(os.path.join(EP, 'sfx'), exist_ok=True)
    json.dump({'note': 'ep10 방구배틀 효과음(박자: 칩튠 84.5BPM)', 'items': items}, open(os.path.join(EP, 'sfx/sfx_list.json'), 'w'), ensure_ascii=False, indent=1)

    pp = os.path.join(ROOT, 'outputs/voice_profile.json'); P = json.load(open(pp))
    P['episodes'].setdefault('ep10', {})
    P['episodes']['ep10'].update({'lines': [], 'placements': [], 'note': 'ep10 방구배틀: 대사 없음, 효과음만(배경음도 sfx_list의 칩튠)'})
    P['episodes']['ep10'].pop('bgm', None)
    json.dump(P, open(pp, 'w'), ensure_ascii=False, indent=1)
    print(f'ep10: 14.0s, 배틀 {len(battle)}번(8분 8 + 16분 10), 대방출 {finale}s, 영혼 상자 {gm} {gc}')


if __name__ == '__main__':
    main()
