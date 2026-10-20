#!/usr/bin/env python3
"""ep08 완성본 편집 구성 생성(0원): Kling 9장면 → edit_list.json, voice_profile placements, text_overlay.json, sfx_list.json, hf_fx.json.
사용: python3 tools/ep08_edit.py  → 이후 ep_to_hyperframes.py · hyperframes render · mix_audio.py
- 장면 길이 = 대사 끝 + 여유, 끝부분 멈춘 프레임(qa_clip)과 S7 거품 흘러내림(4.0s~)은 잘라냄.
- 대사는 우리 녹음(장면 트랙)을 그대로 쓰되, S6은 Kling이 "창수야!"를 0.65s 늦게 다시 만들어 입모양이 그 소리에 맞으므로 클립 소리를 씀.
- 자막은 애니매틱 타임라인(장면 시작 0,6,11,…)의 장면 안 상대 시각을 새 장면 시작으로 옮김.
"""
import json, os, shutil, subprocess
import imageio_ffmpeg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, 'outputs/ep08')
FF = imageio_ffmpeg.get_ffmpeg_exe()

# (장면, 클립 태그, in, len, 음성 트랙 시작 이동[s]) — 이동이 음수면 트랙을 장면 시작보다 앞당김(앞부분은 무음)
SCENES = [
    ('s1', 'v1', 0.0, 5.55, 0.0),   # 대사 끝 5.49, 5.58~ 멈춤
    ('s2', 'v1', 0.0, 4.9, 0.0),    # 대사 끝 4.67
    ('s3', 'v1', 0.0, 4.6, 0.0),    # 대사 끝 4.24, 4.96 멈춤
    ('s4', 'v1', 0.0, 4.9, 0.0),    # 대사 끝 4.72
    ('s5', 'v1', 0.0, 3.04, 0.0),   # 클립 3.04s(대사 끝 3.09 → 다음 장면 첫 0.05s로 넘어감, S6 앞은 무음)
    ('s6', 'v1', 0.0, 4.4, 0.0),    # 클립 소리: 창수야 3.09~4.06
    ('s7', 'v1_fix', 0.0, 4.0, -0.4),  # 4.0s~ 거품 흘러내림 → 대사(2.8~4.18)를 0.4s 앞당김
    ('s8', 'v1', 0.0, 4.0, 0.0),    # 대사 끝 3.61, 4.92 멈춤
    ('s9', 'v1', 0.0, 5.8, 0.0),    # 대사 끝 5.65, 5.83 멈춤
]
OLD_START = {'s1': 0, 's2': 6.0, 's3': 11.0, 's4': 16.0, 's5': 21.0, 's6': 24.5, 's7': 29.5, 's8': 34.5, 's9': 39.5}
OLD_LEN = {'s1': 6.0, 's2': 5.0, 's3': 5.0, 's4': 5.0, 's5': 3.5, 's6': 5.0, 's7': 5.0, 's8': 5.0, 's9': 6.0}


def s6_clip_voice():
    """S6 클립 소리를 대사 트랙으로: 앞 2초(같은 녹음)의 크기를 우리 녹음에 맞춤."""
    import numpy as np
    def pcm(f):
        r = subprocess.run([FF, '-v', 'error', '-i', f, '-ac', '1', '-ar', '44100', '-f', 'f32le', '-'], capture_output=True).stdout
        return np.frombuffer(r, np.float32)
    c = pcm(os.path.join(EP, 's6/clip_v1.mp4')); r = pcm(os.path.join(EP, 'voice/scenes/s6.mp3'))
    n = 2 * 44100
    db = 20 * np.log10(np.sqrt(np.mean(r[:n] ** 2)) / np.sqrt(np.mean(c[:n] ** 2)))
    out = os.path.join(EP, 'voice/scenes/s6_clip.mp3')
    subprocess.run([FF, '-y', '-v', 'error', '-i', os.path.join(EP, 's6/clip_v1.mp4'), '-vn', '-ac', '1', '-ar', '44100',
                    '-af', f'volume={db:.2f}dB', '-b:a', '128k', out], check=True)
    print(f'S6 클립 소리 → {out} ({db:+.1f}dB)')
    return 'outputs/ep08/voice/scenes/s6_clip.mp3'


def main():
    starts = {}; t = 0.0; cuts = []
    for i, (s, tag, cin, L, _) in enumerate(SCENES):
        starts[s] = t
        cuts.append({'cut': f'{i + 1:02d}', 'kind': 'clip', 'source_cut': s, 'clip_tag': tag, 'in': cin, 'len': L, 'time_card': None})
        t += L
    total = round(t, 3)
    # 변환기는 band_offsets를 source_cut(s1~s9)으로 찾음 → 이미지 단계의 컷 번호(01~09) 값을 그대로 옮겨 둠
    bp = os.path.join(EP, 'band_offsets.json'); B = json.load(open(bp))
    for i, (s, *_r) in enumerate(SCENES):
        k = f'{i + 1:02d}'
        if k in B['per_cut_top']:
            B['per_cut_top'].setdefault(s, B['per_cut_top'][k])
    json.dump(B, open(bp, 'w'), ensure_ascii=False, indent=1)
    E =json.load(open(os.path.join(EP, 'edit_list_animatic.json')))
    E['cuts'] = cuts
    E['history'] = E.get('history', []) + [f'2026-10-20 완성 v1: Kling 9장면 {total}s (끝 멈춤·S7 거품 흘러내림 잘라냄)']
    json.dump(E, open(os.path.join(EP, 'edit_list.json'), 'w'), ensure_ascii=False, indent=1)

    # 대사 배치
    pp = os.path.join(ROOT, 'outputs/voice_profile.json'); P = json.load(open(pp)); V = P['episodes']['ep08']
    if 'placements_animatic' not in V:
        V['placements_animatic'] = V['placements']
    s6 = s6_clip_voice()
    V['placements'] = []
    for s, _, _, _, sh in SCENES:
        f = s6 if s == 's6' else f'outputs/ep08/voice/scenes/{s}.mp3'
        V['placements'].append({'file': f, 'at': round(max(0.0, starts[s] + sh), 3)})
    V['bgm']['end_at'] = total
    json.dump(P, open(pp, 'w'), ensure_ascii=False, indent=1)

    # 자막: 장면 안 상대 시각을 옮김
    tp = os.path.join(EP, 'text_overlay.json'); T = json.load(open(tp))
    ap = os.path.join(EP, 'text_overlay_animatic.json')
    if not os.path.exists(ap):
        shutil.copy(tp, ap)
    T0 = json.load(open(ap))
    shift = {s: sh for s, _, _, _, sh in SCENES}
    subs = []
    for it in T0['subtitles']:
        s = max((k for k in OLD_START if OLD_START[k] <= it['start'] + 1e-6), key=lambda k: OLD_START[k])
        rel0, rel1 = it['start'] - OLD_START[s], it['end'] - OLD_START[s]
        if it['cut'] != 'cap':
            rel0 += shift[s]; rel1 += shift[s]
        if it['cut'] == '6c':  # 클립 소리 기준(Kling 재타이밍)
            rel0, rel1 = 3.09, 4.3
        L = dict((sc, ln) for sc, _, _, ln, _ in SCENES)[s]
        n = dict(it); n['start'] = round(starts[s] + max(0.0, rel0), 2); n['end'] = round(starts[s] + min(rel1, L), 2)
        subs.append(n)
    T['subtitles'] = subs
    T['note'] = '완성 v1: 자막 시각 = 새 장면 시작 + 장면 안 상대 시각(애니매틱판은 text_overlay_animatic.json)'
    json.dump(T, open(tp, 'w'), ensure_ascii=False, indent=1)

    # 효과음
    xp = os.path.join(EP, 'sfx/sfx_list.json'); X = json.load(open(xp))
    keep = {it['name']: it for it in X['items']}
    X['note'] = 'ep08 완성 v1: 기상 보잉 + 드라이기 + 화난 쿵 + 샤워 + 정장 반짝'
    X['items'] = [
        dict(keep['wake_boing'], at=starts['s1'] + 0.15),
        {'name': 'hair_dryer', 'file': 'outputs/ep08/sfx/el/hair_dryer.mp3', 'at': starts['s2'], 'len': 4.9, 'target_lufs': -33,
         'loop': True, 'fade_in': 0.2, 'fade_out': 0.4},
        dict(keep['angry_hit'], at=round(starts['s6'] + 3.09, 2)),
        {'name': 'shower', 'file': 'outputs/ep08/sfx/el/shower.mp3', 'at': starts['s7'], 'len': 4.0, 'target_lufs': -31,
         'loop': True, 'fade_in': 0.15, 'fade_out': 0.3},
        dict(keep['suit_sparkle'], at=round(starts['s8'] + 0.1, 2)),
    ]
    json.dump(X, open(xp, 'w'), ensure_ascii=False, indent=1)

    # 화면 효과: 클립은 카메라 고정, 창수야에 흔들림, 정장 등장 펀치
    F = json.load(open(os.path.join(EP, 'hf_fx_animatic.json')))
    F['note'] = 'ep08 완성 v1: Kling 클립(카메라 고정) + 창수야 흔들림 + 정장 펀치'
    F['cuts'] = {'06': {'shake': {'at': 3.09, 'amp': 8, 'dur': 0.4}}, '08': {'punch': {'at': 0.1, 'scale': 1.06, 'settle': 1.03}}}
    json.dump(F, open(os.path.join(EP, 'hf_fx.json'), 'w'), ensure_ascii=False, indent=1)
    print(f'완성 v1 구성: {total}s, 장면 시작', {k: round(v, 2) for k, v in starts.items()})


if __name__ == '__main__':
    main()
