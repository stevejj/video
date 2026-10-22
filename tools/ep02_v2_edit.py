#!/usr/bin/env python3
"""ep02 v2 "오늘도 좀줘 좀줘 좀줘" 다듬기(Kling 0, 사용자 2026-10-22: "어색한 부분 다 손봐, Kling만 안 쓰면 진행").
사용: python3 tools/ep02_v2_edit.py → edit_list.json, hf_fx.json, text_overlay.json, sfx/sfx_list.json, voice_profile ep02 placements·bgm
입력: v1 설정 백업(*_v1.json, voice_v1.json). v1 시각은 컷 기준으로 새 시각에 옮기고(컷 안 위치 유지), 고친 곳만 따로 지정.
고친 곳(제안 1~11):
 1·2 창수 "응."(03·14컷)을 부리가 벌어지는 순간으로, 두 컷 길이 +0.3·+0.5
 3·7 "흐음.."(속마음)은 부리 닫힌 부분만(03 클립 0~1.7s) + 더 가까이 천천히 다가가 다른 장면처럼
 4·5 "그 리모컨 좀 줘"(v1 "이모컨"으로 들림)·"자기야아아아"(길게) 다시 녹음(voice_gen)
 6 베개 요청: 정지 2.0s → 앞 클립 끝 0.5s 더 쓰고 정지 1.5s
 8 커피 장면 들어갈 때 플래시 + 휙
 9 리모컨 강조: 노란 점선·화살표 → 리모컨만 밝게 + 유리 알림창 "리모컨: 바로 옆"
 10 결말: 미순이 리모컨을 스스로 집은 뒤 1.8s 멈춤 + 창수 멍한 얼굴로 다가감 + "…………." 길게 + 암전
 11 리모컨 집는 소리·이불 부스럭, 배경음 서서히 끝
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, 'outputs/ep02')
L1 = lambda f: json.load(open(os.path.join(EP, f)))


def main():
    E1 = L1('edit_list_v1.json'); F1 = L1('hf_fx_v1.json'); T1 = L1('text_overlay_v1.json'); X1 = L1('sfx/sfx_list_v1.json'); V1 = L1('voice_v1.json')
    # 새 컷(컷 id → in, len). 나머지는 v1 그대로
    NEW = {'03': (0.8, 1.8), '04': (0.5, 2.5), '05': (0, 1.5), '10': (0.0, 1.7), '14': (0.5, 2.0), '15': (0.5, 2.35)}
    # 재미 효과(사용자 2026-10-22 "동공지진 같은 재미, 추천 조합 A+C+E, 진동음"): 멈춘 프레임에서 눈만 떼어 덜덜(pupil_quake)
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    from pupil_quake import quake
    q14 = quake('outputs/ep02/quake/f14.png', [(370, 850, 520, 1010), (770, 850, 890, 1000)], os.path.join(EP, 'quake'), 'f14', 0.08, 0.8, 7)   # 14컷 첫 프레임
    q15 = quake('outputs/ep02/quake/f15.png', [(280, 870, 340, 925), (350, 875, 377, 912)], os.path.join(EP, 'quake'), 'f15', 0.7, 0.9, 3)     # 결말 멈춤 프레임(15 클립 2.85s)
    INS = {'14': ('before', {'cut': '14q', 'kind': 'still', 'source_cut': '14', 'image': q14[0], 'in': 0, 'len': 1.0, 'time_card': None}),
           '15': ('after', {'cut': '15f', 'kind': 'still', 'source_cut': '15', 'image': q15[0], 'in': 0, 'len': 1.85, 'time_card': None})}
    s1, t = {}, 0.0
    for c in E1['cuts']:
        s1[c['cut']] = (t, c.get('in', 0), c['len']); t += c['len']
    cuts, s2, t = [], {}, 0.0
    for c in E1['cuts']:
        c = dict(c)
        if c['cut'] in NEW:
            c['in'], c['len'] = NEW[c['cut']]
        if c['cut'] == '13':   # 9: UI 인서트 → 같은 그림의 정지 컷(효과는 hf_fx)
            c = {'cut': '13', 'kind': 'still', 'source_cut': '13', 'image': 'outputs/ep02/11/end_v1.png', 'in': 0, 'len': c['len'], 'time_card': None}
        seq = [c]
        if c['cut'] in INS:
            seq = [INS[c['cut']][1], c] if INS[c['cut']][0] == 'before' else [c, INS[c['cut']][1]]
        for c in seq:
            s2[c['cut']] = (t, c.get('in', 0), c['len']); cuts.append(c); t += c['len']
    cuts.append({'cut': '16', 'kind': 'black', 'len': 0.6, 'time_card': None}); END = round(t + 0.6, 3)

    def move(x):
        """v1 시각 → 새 시각(같은 컷 안 같은 순간)."""
        for k, (a, i1, ln) in s1.items():
            if a <= x < a + ln + 1e-6:
                b, i2, _ = s2[k]; return round(b + (x - a) + (i1 - i2), 3)
        return round(x, 3)
    st = lambda k: s2[k][0]

    E = dict(E1); E['cuts'] = cuts
    E['history'] = E1.get('history', []) + [f'2026-10-22 v2: 어색한 곳 11개 다듬기(Kling 0), {END}s']
    json.dump(E, open(os.path.join(EP, 'edit_list.json'), 'w'), ensure_ascii=False, indent=1)

    F = dict(F1); F['cuts'] = dict(F1['cuts'])
    F['cuts']['05'] = {'cam': {'from': 1.0, 'to': 1.05}}
    F['cuts']['09'] = dict(F1['cuts'].get('09', {}), flash=[{'at': 0.0, 'dur': 0.2, 'peak': 0.45}])
    F['cuts']['10'] = {'cam': {'from': 1.2, 'to': 1.34}}                       # 3·7: 03컷과 다르게 더 가까이 천천히
    F['cuts']['13'] = {'cam': {'from': 1.0, 'to': 1.1},
                       'spotlight': {'at': 0.1, 'dur': 1.4, 'cx': 0.8, 'cy': 0.68, 'r': 0.16, 'dark': 0.6},
                       'toasts': [{'at': 0.25, 'dur': 1.25, 'text': '리모컨: 바로 옆', 'y': 0.2}]}   # 위 심부름 횟수와 안 겹치게
    pp = lambda q: {'bg': q[0], 'src_width': 1080, 'layers': q[1]}
    F['cuts']['14q'] = {'puppet': pp(q14), 'shake': {'at': 0.08, 'amp': 4, 'dur': 0.8},                       # A: 동공지진
                        'toasts': [{'at': 0.12, 'dur': 0.85, 'text': '동공지진', 'y': 0.72}]}
    F['cuts']['15'] = {'sparkle': {'at': 1.3, 'cx': 0.58, 'dur': 1.0, 'dy': -250, 'color': '#FFE27A'}}       # E: 미순이 집은 리모컨 반짝
    F['cuts']['15f'] = {'puppet': pp(q15), 'cam': {'from': 1.0, 'to': 1.28, 'pan_x': [0, 160]}, 'drift': None}   # 기본 흔들림(drift)이 x를 덮어써 다가가기가 약해짐 → 끔            # 10·E: 멈춤 → 창수 쪽으로 다가가며 동공지진 한 번 더
    F['note'] = 'ep02 v2: 응 입모양 맞춤, 흐음 장면 차별화, 리모컨 강조(조명+유리 알림창), 결말 멈춤·암전'
    json.dump(F, open(os.path.join(EP, 'hf_fx.json'), 'w'), ensure_ascii=False, indent=1)

    P = json.load(open(os.path.join(ROOT, 'outputs/voice_profile.json'))); VP = P['episodes']['ep02']
    lines = {l['cut']: l for l in VP['lines']}
    over = {'03': st('03') + 1.07, '14': st('14') + 1.4, '05': st('04') + 2.0, '10': st('10') + 0.4, '15': st('15') + 0.1}   # 1·2·6·3·5
    pl = []
    for p in V1['placements']:
        q = dict(p); q['at'] = round(over.get(p['key'], move(p['at'])), 3)
        if p['key'] in lines:
            q['len'] = lines[p['key']].get('len_file', q['len'])
        pl.append(q)
    VP['placements'] = pl
    VP['bgm'] = dict(V1['bgm'], end_at=END - 0.3, fade_out=1.6, tempo_from=move(V1['bgm']['tempo_from']), dip_at=move(V1['bgm']['dip_at']))
    json.dump(P, open(os.path.join(ROOT, 'outputs/voice_profile.json'), 'w'), ensure_ascii=False, indent=1)
    at = {p['key']: p for p in pl}
    # C: 심부름 횟수(왼쪽 위 유리 알림창) — 창수가 "응." 할 때마다 1→5회, 마지막엔 앉은 시간 0초
    ks = ['03', '06', '07b', '09b', '14']; cnt = []
    for i, k in enumerate(ks):
        a0 = at[k]['at'] - st('01'); a1 = (at[ks[i + 1]]['at'] if i + 1 < len(ks) else st('15f')) - st('01')
        cnt.append({'at': round(a0, 3), 'dur': round(a1 - a0, 3), 'text': f'심부름 {i + 1}회', 'y': 0.025, 'align': 'left', 'size': 46})
    cnt.append({'at': round(st('15f'), 3), 'dur': round(END - 0.6 - st('15f'), 3), 'text': '심부름 5회 · 앉은 시간 0초', 'y': 0.025, 'align': 'left', 'size': 46})
    F['cuts']['01'] = dict(F['cuts'].get('01', {}), toasts=cnt)
    json.dump(F, open(os.path.join(EP, 'hf_fx.json'), 'w'), ensure_ascii=False, indent=1)

    T = dict(T1); subs = []
    for sb in T1['subtitles']:
        s = dict(sb); d = sb['end'] - sb['start']
        key = {'자기야 설거지한 김에 물좀줘': '02', '자기야 일어난 김에 베개좀줘': '05', '자기야 가는 김에 커피좀줘': '07', '자기야 숨쉬는 김에 충전기좀줘': '09',
               '흐음..': '10', '자기야 앉은 김에 리모컨좀줘': '12', '자기야아아아아아아아': '15'}.get(sb['text'])
        if key:
            s['start'] = at[key]['at']; s['end'] = round(s['start'] + (d if key == '10' else max(d, at[key]['len']) + 0.05), 3)   # 10(흐음) 파일은 뒤에 무음이 길어 v1 길이 유지
        elif sb['text'] == '응.':
            k = min(['03', '06', '07b', '09b', '14'], key=lambda k: abs(move(V1['placements'][[p['key'] for p in V1['placements']].index(k)]['at']) - move(sb['start'])))
            s['start'] = round(at[k]['at'] - 0.05, 3); s['end'] = round(s['start'] + d, 3)
        elif sb['text'].startswith('…'):
            s['start'] = round(st('15') + 2.2, 3); s['end'] = round(END - 0.7, 3)   # 10: 길게(15f 멈춤까지)
        else:
            s['start'] = move(sb['start']); s['end'] = move(sb['end'])
        if key == '12':
            s['text'] = '자기야 앉은 김에 그 리모컨좀줘'                                  # 4: 다시 녹음한 대사에 맞춤
        subs.append(s)
    subs.sort(key=lambda s: s['start'])
    for a, b in zip(subs, subs[1:]):   # 같은 자리 자막 겹침 방지
        if b['start'] < a['end'] and (a.get('pos') == b.get('pos')):
            a['end'] = round(b['start'] - 0.02, 3)
    T['subtitles'] = subs; T['note'] = 'v2: 자막 시각 = 새 음성 배치'
    # 제목(2026-10-22 사용자): "남편이 소파에 못 앉는 이유", 노란색 = "못 앉는 이유"
    T['title'] = dict(T1['title'], lines=[{'text': '남편이 소파에', 'color': '#FFFFFF'}, {'text': '못 앉는 이유', 'color': '#FFD84A'}])
    json.dump(T, open(os.path.join(EP, 'text_overlay.json'), 'w'), ensure_ascii=False, indent=1)

    items = []
    for it in X1['items']:
        q = dict(it); q['at'] = move(it['at'])
        if it['name'] == 'tv_amb':
            q['len'] = END
        items.append(q)
    sf = lambda name, file, a0, ln, lufs, **k: dict(name=name, file=file, at=round(a0, 3), len=ln, target_lufs=lufs, fade_out=k.pop('fo', 0.05), **k)
    items += [sf('whoosh_09', 'outputs/ep06/sfx/el/whoosh_fast.mp3', st('09') - 0.12, 0.6, -24),           # 8
              sf('toast_pop', 'outputs/ep05/sfx/el/ui_pop.mp3', st('13') + 0.25, 0.6, -21),               # 9
              sf('blanket', 'outputs/ep10/sfx/el/duvet_rustle.mp3', st('15') + 0.6, 1.0, -30, fo=0.3),      # 11
              sf('remote_grab', 'outputs/ep02/sfx/el/cup_set.mp3', st('15') + 1.3, 0.4, -27),
              sf('quake1', 'outputs/ep02/sfx/el/pupil_quake.mp3', st('14q') + 0.08, 0.95, -18, fo=0.15),     # A 진동음
              sf('quake2', 'outputs/ep02/sfx/el/pupil_quake.mp3', st('15f') + 0.7, 1.0, -20, fo=0.2)]
    items += [sf(f'count{i + 1}', 'outputs/ep05/sfx/el/ui_pop.mp3', c['at'] + st('01'), 0.6, -27) for i, c in enumerate(cnt)]   # C 숫자 올라갈 때
    json.dump({'note': 'ep02 v2 효과음(v1 + 휙·알림·이불·리모컨)', 'items': items}, open(os.path.join(EP, 'sfx/sfx_list.json'), 'w'), ensure_ascii=False, indent=1)
    print('끝', END, '| 컷 시작', {k: round(v[0], 2) for k, v in s2.items()})
    for s in subs:
        print(f"  {s['start']:6.2f}-{s['end']:6.2f} {s['text']}")


if __name__ == '__main__':
    main()
