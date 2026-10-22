#!/usr/bin/env python3
"""ep11 = ep07 포장마차 클립 재사용(Kling 0) + 새 대사(맥주 광고 따라하기). 0원 조립.
사용: python3 tools/ep11_edit.py → voice/talk_track.wav, voice/s5_track.wav, edit_list.json, hf_fx.json, text_overlay.json, sfx/sfx_list.json, voice_profile ep11
- 새 대사를 원래 대사의 말소리 구간 길이에 맞춰 늘리고 줄임(0.75~1.35배). 입모양은 원래 대사 리듬 그대로.
- 마지막 장면은 원래 s5_track에서 L8 자리만 새 대사로, 뒤 웃음은 그대로.
- v2 광고 연출(사용자: "고급스러운 광고 느낌"): 색보정·비네트, 광고 카피 글씨(아래 자막 대신), 원샷 0.7배 슬로모션,
  엔딩 카드(초겨울, 포차의 계절.), 피아노 배경음 + 광고 효과음 → "이모! 여기 한잔 더요!"에서 레코드 긁힘과 함께 평소 화면으로.
"""
import json, os, re, subprocess, wave
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageEnhance, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, 'outputs/ep11'); FF = imageio_ffmpeg.get_ffmpeg_exe(); SR = 44100
# ep07 talk_track 말소리 구간(시작, 길이) — silencedetect로 잼
SLOT = {'L1': (0.23, 1.12), 'L2': (2.13, 1.27), 'L3': (4.23, 1.14), 'L4': (5.85, 0.82), 'L5': (7.93, 0.72), 'L6': (8.94, 0.31)}
L8_SLOT = (0.34, 1.29)   # s5_track 안
SLOW = 0.7               # 원샷(s2 1.45~4.9) 슬로모션 배속 → s2/clip_slow.mp4 (minterpolate)
SLOW_LEN = 4.8           # 3.45 / 0.7 ≈ 4.93 → 렌더 결과 4.83s
CARD_LEN = 2.0           # 엔딩 카드
S5_AT = 10.0 + SLOW_LEN + 3.0 + CARD_LEN   # 19.8: 현실 복귀(이모!)
D = SLOW_LEN - 3.45      # 슬로모션 때문에 캬~가 밀리는 시간
# 말하는 쪽 확대(사용자: "대사 칠 때 각각 확대, 진짜 광고처럼"). 얼굴 중심(1080x1920 프레임): 미순 (340, 980), 창수 (800, 980)
ZOOM, PUSH = 1.35, 1.40                      # 다가간 뒤 대사 동안 천천히 더 다가감
FACE_X = {'misun': 340, 'changsu': 800}
SPEAK = [('misun', 0.0, 1.85), ('changsu', 1.85, 3.95), ('misun', 3.95, 5.6), ('changsu', 5.6, 7.65), ('misun', 7.65, 8.7)]
WIDE_AT = 8.7                                # 짠은 둘이 함께 보이게 원래 화면으로


def moves():
    out = []
    for who, a, b in SPEAK:
        m = (ZOOM - 1) / 2 * 1080                # 화면 밖 검은 테두리가 안 보이는 최대 이동
        x = round(max(-m, min(m, -ZOOM * (FACE_X[who] - 540))))
        d = 0.6 if a == 0 else 0.5
        out.append({'at': max(a - 0.25, 0), 'dur': d, 'scale': ZOOM, 'x': x, 'y': 0})
        out.append({'at': max(a - 0.25, 0) + d, 'dur': round(b - 0.25 - (max(a - 0.25, 0) + d), 2), 'scale': PUSH, 'x': x, 'y': 0, 'ease': 'none'})
    out.append({'at': WIDE_AT, 'dur': 0.5, 'scale': 1.0, 'x': 0, 'y': 0})
    return out


GRADE = {'filter': 'contrast(1.14) saturate(0.9) brightness(0.93) sepia(0.15)', 'vignette': 0.6, 'shade': 0.5}


def pcm(f):
    return np.frombuffer(subprocess.run([FF, '-v', 'error', '-i', f, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout, np.float32).copy()


def dur(f):
    return float(re.search(r'Duration: \d+:\d+:([\d.]+)', subprocess.run([FF, '-i', f], capture_output=True, text=True).stderr).group(1))


def fit(src, target, dst):
    r = min(max(dur(src) / target, 0.75), 1.35)
    subprocess.run([FF, '-y', '-v', 'error', '-i', src, '-af', f'atempo={r:.3f}', '-ac', '1', '-ar', str(SR), dst], check=True)
    return r, dur(dst)


def save(x, path):
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes())


def main():
    pp = os.path.join(ROOT, 'outputs/voice_profile.json'); P = json.load(open(pp)); V = P['episodes']['ep11']
    L = {l['cut']: l for l in V['lines']}
    talk = np.zeros(int(9.6 * SR), np.float32); subs = []
    for c, (t0, ln) in SLOT.items():
        dst = os.path.join(EP, f'voice/lines/{c}_fit.wav'); r, d = fit(os.path.join(ROOT, L[c]['file']), ln, dst)
        a = pcm(dst); i = int(t0 * SR); talk[i:i + len(a)] += a[:len(talk) - i]
        subs.append((c, t0, t0 + max(d, ln) + 0.15)); print(f'{c} {r:.2f}배 → {d:.2f}s (자리 {ln}s)')
    save(talk, os.path.join(EP, 'voice/talk_track.wav'))
    dst = os.path.join(EP, 'voice/lines/L8_fit.wav'); r, d = fit(os.path.join(ROOT, L['L8']['file']), L8_SLOT[1], dst)
    s5 = pcm(os.path.join(ROOT, 'outputs/ep07/voice/s5_track.mp3')); s5[int(0.30 * SR):int(1.80 * SR)] = 0
    a = pcm(dst); i = int(L8_SLOT[0] * SR); s5[i:i + len(a)] += a[:len(s5) - i]
    save(s5, os.path.join(EP, 'voice/s5_track.wav')); print(f'L8 {r:.2f}배 → {d:.2f}s')
    subs.append(('L8', S5_AT + L8_SLOT[0], S5_AT + L8_SLOT[0] + max(d, L8_SLOT[1]) + 0.3))
    print('카피:', [(c, round(a0, 2), round(a1, 2)) for c, a0, a1 in subs])

    E7 = P['episodes']['ep07']
    V['placements'] = [{'file': 'outputs/ep11/voice/talk_track.wav', 'at': 0.0}] + \
                      [{'file': x['file'], 'at': round(x['at'] + D, 3)} for x in E7['placements'] if 'L7' in x['file']] + \
                      [{'file': 'outputs/ep11/voice/s5_track.wav', 'at': S5_AT}]
    # 광고 배경음: 피아노, 엔딩 카드 끝(레코드 긁힘)에서 뚝 끊김
    V['bgm'] = {'file': 'outputs/ep01/bgm/A_lofi_piano.mp3', 'target_lufs': -25, 'duck_db': 4, 'fade_in': 0.6, 'end_at': round(S5_AT + 0.05, 2), 'fade_out': 0.1,
                'note': 'ep11 v2 광고 연출: 광고 구간만, 현실 복귀에서 끊김'}
    json.dump(P, open(pp, 'w'), ensure_ascii=False, indent=1)
    ad_look()

    T = json.load(open(os.path.join(ROOT, 'outputs/ep07/text_overlay.json')))
    # 제목(사용자): "부부의 초겨울 / 맥주광고 따라하기", 노란색 = "맥주광고"
    T['title']['lines'] = [{'text': '부부의 초겨울', 'color': '#FFFFFF'},
                           {'spans': [{'text': '맥주광고', 'color': '#FFD84A'}, {'text': ' 따라하기', 'color': '#FFFFFF'}]}]
    # v2: 광고 구간 대사는 광고 카피(hf_fx copy)로, 아래 자막은 현실 복귀 대사만
    T['subtitles'] = [{'cut': c, 'text': L[c]['subtitle'], 'speaker': L[c]['speaker'], 'start': round(a0, 2), 'end': round(a1, 2), 'x': 0.5} for c, a0, a1 in subs if c == 'L8']
    T['note'] = 'ep11 v2: 광고 구간은 카피 글씨, 이모! 만 일반 자막'
    json.dump(T, open(os.path.join(EP, 'text_overlay.json'), 'w'), ensure_ascii=False, indent=1)
    for s in T['subtitles']:
        print(s['start'], s['end'], s['text'])



def end_card():
    """엔딩 카드 배경: 짠 순간 프레임을 흐리고 어둡게(따뜻한 빛만 남김)."""
    src = os.path.join(ROOT, 'outputs/ep07/s1/clip_v2.mp4'); dst = os.path.join(EP, 'card/end_bg.png')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    subprocess.run([FF, '-y', '-v', 'error', '-ss', '9.6', '-i', src, '-frames:v', '1', '-vf', 'scale=1080:1920', dst], check=True)
    im = Image.open(dst).convert('RGB').filter(ImageFilter.GaussianBlur(14))
    im = ImageEnhance.Brightness(ImageEnhance.Color(im).enhance(0.8)).enhance(0.45)
    im.save(dst)
    return 'outputs/ep11/card/end_bg.png'


def ad_look():
    clip = lambda cut, src, tag, i0, ln: {'cut': cut, 'kind': 'clip', 'source_cut': src, 'clip_tag': tag, 'in': i0, 'len': ln, 'time_card': None}
    E = json.load(open(os.path.join(ROOT, 'outputs/ep07/edit_list.json')))
    E['cuts'] = [clip('01', 's1', 'v2', 0.0, 10.0), clip('02', 's2', 'slow', 0.0, SLOW_LEN), clip('03', 's4', 'v1', 0.0, 3.0),
                 {'cut': '04', 'kind': 'still', 'source_cut': 'card', 'image': end_card(), 'in': 0, 'len': CARD_LEN, 'time_card': None},
                 clip('05', 's5', 'v2', 0.0, 5.0)]
    E['history'] = E.get('history', []) + [f'2026-10-21 ep11 v2 광고 연출: 대화 10.0 → 원샷 슬로 {SLOW_LEN} → 캬 3.0 → 엔딩 카드 {CARD_LEN} → 이모! 5.0 = {S5_AT + 5.0:.2f}s']
    json.dump(E, open(os.path.join(EP, 'edit_list.json'), 'w'), ensure_ascii=False, indent=1)
    B = json.load(open(os.path.join(EP, 'band_offsets.json'))); B['per_cut_top'].setdefault('card', 0)
    json.dump(B, open(os.path.join(EP, 'band_offsets.json'), 'w'), ensure_ascii=False, indent=1)

    cp = lambda at, dur, text, **k: dict(at=round(at, 2), dur=round(dur, 2), text=text, **k)
    s = {c: t0 for c, (t0, _) in SLOT.items()}
    F = json.load(open(os.path.join(ROOT, 'outputs/ep07/hf_fx.json')))
    F['cuts'] = {
        '01': {'grade': GRADE, 'moves': moves(),
               'copy': [cp(s['L1'], s['L2'] - s['L1'] - 0.15, '초겨울, 포차의 계절.'),
                        cp(s['L2'], s['L3'] - s['L2'] - 0.25, '입김마저 시원하다.'),
                        cp(s['L3'], s['L5'] - s['L3'] - 0.3, '차가운 잔에 담은', y=0.76),
                        cp(s['L4'], s['L5'] - s['L4'] - 0.3, '우리의 하루.', y=0.81),
                        cp(s['L5'], s['L6'] - s['L5'] - 0.06, '건배하라!', size=72),
                        cp(s['L6'], 10.0 - s['L6'] - 0.06, '짠!', size=104, weight=400, fade=0.3)],
               'sparkle': {'at': 9.45, 'cx': 0.5, 'dy': -490, 'dur': 0.9, 'glyph': '✦', 'color': '#FFF6D8'},
               'flash': [{'at': 9.6, 'dur': 0.3, 'peak': 0.22}]},
        '02': {'grade': GRADE, 'cam': {'from': 1.0, 'to': 1.06}},
        '03': {'grade': GRADE, 'copy': [cp(14.35 + D - 10.0 - SLOW_LEN, 1.6, '캬~', size=110, weight=300, y=0.78)]},
        '04': {'cam': {'from': 1.06, 'to': 1.0}, 'drift': None,
               'copy': [cp(0.2, CARD_LEN - 0.2, '초겨울, 포차의 계절.', y=0.5, size=76, fade=0.9),
                        cp(0.6, CARD_LEN - 0.6, 'MISOON & CHANGSU', y=0.565, size=30, weight=400, spacing=0.45, color='#E8D9B8', fade=0.8)]},
        '05': {'punch': {'at': 0.45, 'scale': 1.04, 'settle': 1.0}},   # 현실: 색보정·카피 없음
    }
    F['note'] = 'ep11 v2 광고 연출: 01~04 색보정·카피, 02 슬로모션, 04 엔딩 카드, 05 평소 화면'
    json.dump(F, open(os.path.join(EP, 'hf_fx.json'), 'w'), ensure_ascii=False, indent=1)

    E7 = json.load(open(os.path.join(ROOT, 'outputs/ep07/sfx/sfx_list.json')))['items']
    cup = next(x['file'] for x in E7 if x['name'] == 'clink'); el = 'outputs/ep11/sfx/el/'; end = S5_AT + 5.0
    sf = lambda name, file, a0, ln, lufs, **k: dict(name=name, file=file, at=round(a0, 3), len=round(ln, 2), target_lufs=lufs, fade_out=k.pop('fo', 0.05), **k)
    items = [sf('street_amb_ad', 'outputs/ep01/sfx/el/street_amb.mp3', 0.0, S5_AT, -38, loop=True, fade_in=0.3, fo=0.05),
             sf('fizz_open', el + 'beer_fizz.mp3', 0.0, 2.0, -32, fade_in=0.3, fo=0.4),
             sf('glass_clink', el + 'glass_clink.mp3', 9.55, 1.2, -18, fo=0.3),
             sf('whoosh_slow', el + 'whoosh_soft.mp3', 9.85, 1.0, -26),
             sf('fizz_slow', el + 'beer_fizz.mp3', 10.4, 2.0, -30, fade_in=0.2, fo=0.5),
             sf('mugs_down', cup, 10.0 + (13.35 - 10.0) / SLOW, 0.4, -26, fo=0.1),
             sf('whoosh_card', el + 'whoosh_soft.mp3', 10.0 + SLOW_LEN + 3.0 - 0.1, 1.0, -24),
             sf('pour_card', el + 'beer_pour.mp3', 10.0 + SLOW_LEN + 3.0 + 0.05, CARD_LEN - 0.05, -24, fo=0.1),
             sf('record_scratch', el + 'record_scratch.mp3', S5_AT - 0.05, 0.8, -15),
             sf('street_amb_real', 'outputs/ep01/sfx/el/street_amb.mp3', S5_AT, end - S5_AT, -32, loop=True, fo=0.8)]
    json.dump({'note': 'ep11 v2 광고 효과음(ElevenLabs 5개) + 현실 복귀', 'items': items}, open(os.path.join(EP, 'sfx/sfx_list.json'), 'w'), ensure_ascii=False, indent=1)
    print(f'v2: 총 {end:.2f}s, 슬로 {SLOW_LEN}s, 엔딩 카드 {CARD_LEN}s, 현실 복귀 {S5_AT}s')


if __name__ == '__main__':
    main()
