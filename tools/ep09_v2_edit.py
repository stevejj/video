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
v2.1(사용자): 동공지진은 얼굴로 확 다가가서, "(아까)" 흑백 사진 더 길게, "왔다 왔다" 별(반짝이) 빼기,
 "결정 실패" 더 오래(앱 컷 +0.9s, 뒤 시각 전부 +0.9s).
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
    pp_ = os.path.join(ROOT, 'outputs/voice_profile.json'); P = json.load(open(pp_)); VP = P['episodes']['ep09']
    vb = os.path.join(EP, 'voice_v1.json')
    if not os.path.exists(vb):
        json.dump({'placements': VP['placements'], 'bgm': VP['bgm']}, open(vb, 'w'), ensure_ascii=False, indent=1)
    V1 = json.load(open(vb))
    FAIL, EXT = 2.75, 0.9          # "결정 실패" 시각(앱 컷 안, "다 별로~" 끝난 직후)·앱 컷 연장
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    from pupil_quake import quake
    starts, t = {}, 0.0
    for c in E['cuts']:
        starts[c['cut']] = t; t += c['len']
    SH0 = starts['05']                                         # 이 시각 이후는 전부 EXT만큼 뒤로
    sh = lambda x: round(x + (EXT if x >= SH0 - 1e-6 else 0), 3)
    END = t + EXT
    # 6: 마지막 컷을 클립(멈추기 전) + 멈춘 프레임(눈만 떨림) 정지 컷으로
    FZ = F['cuts']['09']['freeze']['at']; L9 = next(c['len'] for c in E['cuts'] if c['cut'] == '09')
    q9 = quake('outputs/ep09/quake/f9.png', [(630, 910, 700, 990), (780, 905, 860, 990)], os.path.join(EP, 'quake'), 'f9', 0.95, 1.0, 6)
    cuts = []
    for c in E['cuts']:
        if c['cut'] == '04':
            c = dict(c, len=round(c['len'] + EXT, 3))
        if c['cut'] == '09':
            cuts += [dict(c, len=FZ), {'cut': '09f', 'kind': 'still', 'source_cut': 's9', 'image': q9[0], 'in': 0, 'len': round(L9 - FZ, 3), 'time_card': None}]
        else:
            cuts.append(c)
    E['cuts'] = cuts; E['history'] = E.get('history', []) + ['2026-10-22 v2: 효과 글씨 유리 스타일·검은 띠·회상 위치·동공지진(Kling 0)']
    json.dump(E, open(os.path.join(EP, 'edit_list.json'), 'w'), ensure_ascii=False, indent=1)

    C = F['cuts']
    C['01']['gauge'] = dict(C['01']['gauge'], glass=True)                                           # 2
    # v2.3(사용자: 핀 조명이 미순 얼굴을 따라가게): 고정 원 → 얼굴 추적(tools/face_track.py, 클립 2.3~4.45s) + 프레임 안(카메라와 같이)
    sp = C['02'].pop('spotlight')
    from face_track import track
    tp = os.path.join(EP, 'ref/misun_face_track_s2.json')
    if not os.path.exists(tp):
        json.dump(track(os.path.join(EP, 's2/clip_v1.mp4'), 2.3, 4.45, (610, 800, 840, 1010)), open(tp, 'w'))
    C['02']['spot_track'] = {'at': sp['at'], 'dur': sp['dur'], 'r': 250, 'dark': sp.get('dark', 0.75), 'pts': json.load(open(tp))}
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
    C['04']['tint'] = {'at': FAIL, 'dur': round(L4 - FAIL, 3), 'color': 'rgba(170,170,170,0.65)', 'fade': 0.3}
    C['04']['toasts'] = [{'at': FAIL + 0.05, 'dur': round(L4 - FAIL - 0.05, 3), 'text': '결정 실패…', 'y': 0.5}]   # v2.1: 약 1.6s 보임
    C['08']['flashback'] = dict(C['08']['flashback'], x=0.79, y=0.42, w=0.36, dur=2.0)               # 5 + v2.1: 1.1 → 2.0s
    C.pop('07', None)                                                                                # v2.1: "왔다 왔다" 별(반짝이) 뺌
    C.pop('09')                                                                                      # 4·6
    # v2.2(사용자: "동공지진은 2단계에 걸쳐 확대"): 0.3s 1단계(1.45배) → 0.75s 2단계(2.1배) → 0.95s부터 눈 떨림. 얼굴 중심(1080x1920) ≈ (745, 1000)
    fx_, fy_ = 745, 1000
    def at_(z):   # 그 배율에서 얼굴이 가운데 쪽으로 오게(검은 테두리 안 보이게 제한)
        mx, my = (z - 1) * 540, (z - 1) * 384
        return round(max(-mx, min(mx, -z * (fx_ - 540) * 0.95))), round(max(-my, min(my, -z * (fy_ - 960) * 0.95)))
    (x1, y1), (x2, y2) = at_(1.45), at_(2.1)
    L9f = round(L9 - FZ, 3)
    C['09f'] = {'puppet': {'bg': q9[0], 'src_width': 1080, 'layers': q9[1]}, 'cam': None, 'drift': None,
                'moves': [{'at': 0.0, 'dur': 0.3, 'scale': 1.0, 'x': 0, 'y': 0, 'ease': 'none'},
                          {'at': 0.3, 'dur': 0.15, 'scale': 1.45, 'x': x1, 'y': y1, 'ease': 'power3.out'},
                          {'at': 0.45, 'dur': 0.3, 'scale': 1.48, 'x': x1, 'y': y1, 'ease': 'none'},
                          {'at': 0.75, 'dur': 0.15, 'scale': 2.1, 'x': x2, 'y': y2, 'ease': 'power3.out'},
                          {'at': 0.9, 'dur': round(L9f - 0.9, 3), 'scale': 2.15, 'x': x2, 'y': y2, 'ease': 'none'}],
                'toasts': [{'at': 0.95, 'dur': round(L9f - 0.95, 3), 'text': '동공지진', 'y': 0.72}]}
    F['note'] = 'ep09 v2: 유리 효과 글씨(후보 띠·게이지·결정 실패), 검은 띠 수정, 회상 위치, 동공지진'
    json.dump(F, open(os.path.join(EP, 'hf_fx.json'), 'w'), ensure_ascii=False, indent=1)

    T['subtitles'] = [dict(s, start=sh(s['start']), end=sh(s['end'])) for s in T['subtitles'] if not s['text'].startswith('(탈락 메뉴')]   # 1: 후보 띠와 같은 내용
    # v2.4(사용자): 6a "알았어! 그냥 치킨 시킨다!" → "나 그럼 치킨 먹어도 돼?" 다시 녹음(voice_gen seed 7) → S6 클립 소리 다시 만들고 자막 교체
    from ep09_edit import final_tracks, S6A
    final_tracks(VP['lines']); l6a = next(l for l in VP['lines'] if l['cut'] == '6a')
    T['subtitles'] = [dict(s, text=l6a['subtitle'], end=round(s['start'] + l6a['len_file'] / S6A['tempo'] + 0.05, 2)) if s['cut'] == '6a' else s for s in T['subtitles']]
    VP['placements'] = [dict(p, at=sh(p['at'])) for p in V1['placements']]
    VP['bgm'] = dict(V1['bgm'], end_at=round(V1['bgm']['end_at'] + EXT, 3))
    json.dump(P, open(pp_, 'w'), ensure_ascii=False, indent=1)
    json.dump(T, open(os.path.join(EP, 'text_overlay.json'), 'w'), ensure_ascii=False, indent=1)

    POP, TAP, QK = 'outputs/ep05/sfx/el/ui_pop.mp3', 'outputs/ep05/sfx/el/ui_tap.mp3', 'outputs/ep02/sfx/el/pupil_quake.mp3'
    items = []
    for it in X['items']:
        q = {k: v for k, v in it.items() if k not in ('gain', 'measured_lufs', 'measured_file')}
        q['at'] = sh(it['at'])
        if it['name'] == 'sparkle':
            continue                                            # v2.1: "왔다 왔다" 별 소리도 뺌
        if it['name'] in ('buzz0', 'buzz1', 'buzz2'):
            q.update(file=POP, len=0.6, target_lufs=-22)        # 삑 → 부드러운 알림음
        elif it['name'] in ('buzz4_0', 'buzz4_1', 'buzz4_2'):
            q.update(file=TAP, len=0.5, target_lufs=-22)
        elif it['name'] == 'buzz4_3':
            q.update(file=POP, len=0.6, target_lufs=-19, at=round(starts['04'] + FAIL, 3))
        items.append(q)
    items += [{'name': 'chicken_strike', 'file': POP, 'at': round(a3 + 0.15, 3), 'len': 0.6, 'target_lufs': -26, 'fade_out': 0.05},
              {'name': 'zoom1', 'file': 'outputs/ep06/sfx/el/whoosh_fast.mp3', 'at': round(sh(starts['09']) + FZ + 0.22, 3), 'len': 0.5, 'target_lufs': -24, 'fade_out': 0.05},
              {'name': 'zoom2', 'file': 'outputs/ep06/sfx/el/whoosh_fast.mp3', 'at': round(sh(starts['09']) + FZ + 0.67, 3), 'len': 0.5, 'target_lufs': -21, 'fade_out': 0.05},
              {'name': 'quake', 'file': QK, 'at': round(sh(starts['09']) + FZ + 0.95, 3), 'len': 1.0, 'target_lufs': -20, 'fade_out': 0.2}]
    X['items'] = items; X['note'] = 'ep09 v2: 삑 부저 → 알림음·톡, 동공지진 진동음'
    json.dump(X, open(os.path.join(EP, 'sfx/sfx_list.json'), 'w'), ensure_ascii=False, indent=1)
    print('끝', round(END, 2), '| 후보 띠', C['03']['chips']['items'])


if __name__ == '__main__':
    main()
