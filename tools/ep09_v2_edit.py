#!/usr/bin/env python3
"""ep09 v2 "부부 저녁메뉴 고민 공감 100%" 다듬기(Kling 0, 사용자 2026-10-22 "이것도 손보자" → 제안 1~6 "진행").
사용: python3 tools/ep09_v2_edit.py → edit_list.json, hf_fx.json, text_overlay.json, sfx/sfx_list.json (입력: v1 백업 *_v1.json)
 1 빨간 "피자 ✕·떡볶이 ✕·족발 ✕" 도장 → 위쪽 유리 띠 "오늘의 후보"(메뉴가 하나씩 생기고 거절되면 줄 그음). "(탈락 메뉴 n개째)" 자막은 뺌
 2 배고픔 게이지(노랑→빨강·빨간 MAX) → 유리 게이지(분홍)
 3 배달앱 큰 빨간 ✕ → 화면 회색으로 바래고 유리 알림창 "결정 실패…", 메뉴 칸 작은 ✕는 회색
 4 마지막 확대 때 오른쪽 검은 띠(이동 -230 > 한도 172) → -170
 5 "(아까)" 회상 사진이 미순 얼굴을 가림 → 오른쪽 창수 몸 쪽으로
 6 마지막 땀 흘리는 창수 동공지진 + 진동음 + 유리 알림창 "동공지진"
효과 글씨는 02a 규칙(유리 알림창). 삑 부저는 부드러운 알림음·톡으로.
"""
import json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, 'outputs/ep09')


def v1(name):
    p = os.path.join(EP, name); b = p.replace('.json', '_v1.json')
    if not os.path.exists(b):
        shutil.copy(p, b)
    return json.load(open(b))


def main():
    E = v1('edit_list.json'); F = v1('hf_fx.json'); T = v1('text_overlay.json'); X = v1('sfx/sfx_list.json')
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    from pupil_quake import quake
    starts, t = {}, 0.0
    for c in E['cuts']:
        starts[c['cut']] = t; t += c['len']
    END = t
    # 6: 마지막 컷을 클립(멈추기 전) + 멈춘 프레임(눈만 떨림) 정지 컷으로
    FZ = F['cuts']['09']['freeze']['at']; L9 = next(c['len'] for c in E['cuts'] if c['cut'] == '09')
    q9 = quake('outputs/ep09/quake/f9.png', [(630, 910, 700, 990), (780, 905, 860, 990)], os.path.join(EP, 'quake'), 'f9', 0.5, 0.9, 6)
    cuts = []
    for c in E['cuts']:
        if c['cut'] == '09':
            cuts += [dict(c, len=FZ), {'cut': '09f', 'kind': 'still', 'source_cut': 's9', 'image': q9[0], 'in': 0, 'len': round(L9 - FZ, 3), 'time_card': None}]
        else:
            cuts.append(c)
    E['cuts'] = cuts; E['history'] = E.get('history', []) + ['2026-10-22 v2: 효과 글씨 유리 스타일·검은 띠·회상 위치·동공지진(Kling 0)']
    json.dump(E, open(os.path.join(EP, 'edit_list.json'), 'w'), ensure_ascii=False, indent=1)

    C = F['cuts']
    C['01']['gauge'] = dict(C['01']['gauge'], glass=True)                                           # 2
    st3 = [s['at'] for s in C['03'].pop('stamps')]                                                  # 1: 거절 순간(v1 도장 시각)
    L3 = next(c['len'] for c in cuts if c['cut'] == '03'); a3 = starts['03']
    ask = lambda txt: next(s['start'] for s in T['subtitles'] if s['text'] == txt) - a3            # 창수가 메뉴를 말한 순간
    C['03']['chips'] = {'at': 0.0, 'dur': L3, 'y': 0.035, 'title': '오늘의 후보',
                        'items': [{'text': '치킨', 'at': 0.0, 'strike_at': 0.15},
                                  {'text': '피자', 'at': round(ask('피자?'), 3), 'strike_at': st3[0]},
                                  {'text': '떡볶이', 'at': round(ask('떡볶이?'), 3), 'strike_at': st3[1]},
                                  {'text': '족발', 'at': round(ask('…족발?'), 3), 'strike_at': st3[2]}]}
    stamps4 = C['04'].pop('stamps'); big = max(stamps4, key=lambda s: s.get('size', 0))           # 3
    L4 = next(c['len'] for c in cuts if c['cut'] == '04')
    C['04']['stamps'] = [dict(s, color='#8A8F98') for s in stamps4 if s is not big]
    C['04']['tint'] = {'at': big['at'], 'dur': round(L4 - big['at'], 3), 'color': 'rgba(170,170,170,0.65)', 'fade': 0.3}
    C['04']['toasts'] = [{'at': round(big['at'] + 0.05, 3), 'dur': round(L4 - big['at'] - 0.05, 3), 'text': '결정 실패…', 'y': 0.5}]
    C['08']['flashback'] = dict(C['08']['flashback'], x=0.79, y=0.42, w=0.36)                        # 5
    C.pop('09')                                                                                      # 4·6
    C['09f'] = {'puppet': {'bg': q9[0], 'src_width': 1080, 'layers': q9[1]},
                'cam': {'from': 1.0, 'to': 1.32, 'pan_x': [0, -170]}, 'drift': None,
                'toasts': [{'at': 0.5, 'dur': 1.0, 'text': '동공지진', 'y': 0.72}]}
    F['note'] = 'ep09 v2: 유리 효과 글씨(후보 띠·게이지·결정 실패), 검은 띠 수정, 회상 위치, 동공지진'
    json.dump(F, open(os.path.join(EP, 'hf_fx.json'), 'w'), ensure_ascii=False, indent=1)

    T['subtitles'] = [s for s in T['subtitles'] if not s['text'].startswith('(탈락 메뉴')]           # 1: 후보 띠와 같은 내용
    json.dump(T, open(os.path.join(EP, 'text_overlay.json'), 'w'), ensure_ascii=False, indent=1)

    POP, TAP, QK = 'outputs/ep05/sfx/el/ui_pop.mp3', 'outputs/ep05/sfx/el/ui_tap.mp3', 'outputs/ep02/sfx/el/pupil_quake.mp3'
    items = []
    for it in X['items']:
        q = {k: v for k, v in it.items() if k not in ('gain', 'measured_lufs', 'measured_file')}
        if it['name'] in ('buzz0', 'buzz1', 'buzz2'):
            q.update(file=POP, len=0.6, target_lufs=-22)        # 삑 → 부드러운 알림음
        elif it['name'] in ('buzz4_0', 'buzz4_1', 'buzz4_2'):
            q.update(file=TAP, len=0.5, target_lufs=-22)
        elif it['name'] == 'buzz4_3':
            q.update(file=POP, len=0.6, target_lufs=-19)
        items.append(q)
    items += [{'name': 'chicken_strike', 'file': POP, 'at': round(a3 + 0.15, 3), 'len': 0.6, 'target_lufs': -26, 'fade_out': 0.05},
              {'name': 'quake', 'file': QK, 'at': round(starts['09'] + FZ + 0.5, 3), 'len': 1.0, 'target_lufs': -20, 'fade_out': 0.2}]
    X['items'] = items; X['note'] = 'ep09 v2: 삑 부저 → 알림음·톡, 동공지진 진동음'
    json.dump(X, open(os.path.join(EP, 'sfx/sfx_list.json'), 'w'), ensure_ascii=False, indent=1)
    print('끝', round(END, 2), '| 후보 띠', C['03']['chips']['items'])


if __name__ == '__main__':
    main()
