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
# v12(2026-10-23 사용자 ②): 짠 순간 속도 조절 — 잔이 닿기 직전 9.30~9.80s(원본)를 0.25배로, 앞뒤는 원래 속도 → s1/clip_ramp.mp4
RAMP_A, RAMP_B, RAMP_SP = 9.30, 9.80, 0.25
EXTRA = round((RAMP_B - RAMP_A) * (1 / RAMP_SP - 1), 3)   # 1.5s 늘어남
CUT1 = 10.0 + EXTRA      # 대화+짠 장면 길이
CARD_LEN = 2.6           # 엔딩 카드(v12 ④: 캔 치익 → 따르는 소리가 들어가게 2.0 → 2.6)
S5_AT = CUT1 + SLOW_LEN + 3.0 + CARD_LEN   # 현실 복귀(이모!)
CARD_AT = CUT1 + SLOW_LEN + 3.0
WARNING = '지나친 음주는 다음 날 미순이의 잔소리를 부릅니다.'   # v12 ④: 실제 광고 아래 작은 경고문 패러디


def rt(t):
    """원본 s1 시각 → 속도 조절 뒤 시각."""
    return t if t <= RAMP_A else (RAMP_A + (t - RAMP_A) / RAMP_SP if t <= RAMP_B else t + EXTRA)
D = SLOW_LEN - 3.45      # 슬로모션 때문에 캬~가 밀리는 시간
# 광고 목소리(v4, 사용자: "목소리는 그대로, 광고 연기 톤 느낌"): 1~6번만, 7번(이모!)은 원래 소리
AD_EQ = 'highpass=f=70,equalizer=f=150:t=q:w=1:g=4,equalizer=f=400:t=q:w=1.2:g=-2,equalizer=f=3500:t=q:w=1:g=3,acompressor=threshold=-22dB:ratio=3.5:attack=5:release=120:makeup=2'
REVERB = {'pre': 0.04, 'decay': 0.25, 'wet': 0.4, 'band': [300, 6000]}   # 짧은 방 울림, 말소리 전체(ad_voice)
# 말하는 쪽 확대(사용자: "대사 칠 때 각각 확대, 진짜 광고처럼"). 얼굴 중심(1080x1920 프레임): 미순 (340, 980), 창수 (800, 980)
ZOOM, PUSH = 1.6, 1.68                       # v4(사용자: "더 세게, 스피드하게 왔다갔다"): 빠르게 확 다가간 뒤 대사 동안 천천히 더
FACE_X = {'misun': 340, 'changsu': 800}
ORDER = [('misun', 'L1'), ('changsu', 'L2'), ('misun', 'L3'), ('changsu', 'L4'), ('misun', 'L5')]
CHAN_Y = 1600   # v9(2026-10-23 사용자): 본 영상 채널명은 하단(썸네일 시작 화면에선 가운데)
COPY_Y = 0.70   # v10(사용자: 카피가 채널명을 가림): 광고 카피 자리 0.78~0.81 → 0.70~0.75(채널명 1600px 위로 약 100px 띄움)
WIDE_AT = 8.75                               # 짠은 둘이 함께 보이게 원래 화면으로
BEAT = 0.45                                  # v5(사용자: "전환이 급하다, 확대 속도는 좋아"): 앞 대사 끝과 다음 대사 사이 가운데서 넘어가
                                             # 다음 사람이 말하기 전 0.25~0.45초 머무름(대사 직전 0.12초 전환 → 급해 보였음)


def moves():
    out = []; m = (ZOOM - 1) / 2 * 1080       # 화면 밖 검은 테두리가 안 보이는 최대 이동
    for i, (who, c) in enumerate(ORDER):
        st = SLOT[c][0]
        if i == 0:
            a0 = 0.0
        else:
            prev_end = sum(SLOT[ORDER[i - 1][1]])
            a0 = round(st - min(BEAT, (st - prev_end) / 2), 2)
        end = WIDE_AT if i == len(ORDER) - 1 else None
        x = round(max(-m, min(m, -ZOOM * (FACE_X[who] - 540)))); d = 0.2
        out.append({'at': a0, 'dur': d, 'scale': ZOOM, 'x': x, 'y': 0, 'ease': 'power3.out'})
        out.append({'at': round(a0 + d, 2), 'scale': PUSH, 'x': x, 'y': 0, 'ease': 'none', 'end': end})
    for k in range(1, len(out) - 1, 2):       # 천천히 다가가기는 다음 전환 직전까지
        out[k]['dur'] = round(out[k + 1]['at'] - out[k]['at'], 2)
    out[-1]['dur'] = round(WIDE_AT - out[-1]['at'], 2)
    for o in out:
        o.pop('end', None)
    out.append({'at': WIDE_AT, 'dur': 0.25, 'scale': 1.0, 'x': 0, 'y': 0, 'ease': 'power3.out'})
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


def ad_voice(x):
    """광고 내레이션 느낌(목소리는 그대로): 저음 따뜻하게·발음 또렷하게·압축(가까이서 말하는 소리) + 말소리 전체에 짧은 방 울림.
    - v4처럼 울림을 말 끝에만 붙이면 이어짐이 어색함(사용자) → v5는 끊김 없이 계속 깔고,
    - 발음 뭉개짐 방지: 울림 시작을 40ms 늦추고(자음 먼저 들림), 울림에서 저음(<300Hz)·고음(>6kHz)을 뺌.
      울림이 길거나(0.3s+) 일찍 오면(30ms) 받아쓰기 "포차 → 푸차"(2026-10-22 비교)."""
    from scipy.signal import fftconvolve, butter, sosfilt
    dry = os.path.join(EP, 'voice/talk_track_dry.wav')
    y = np.frombuffer(subprocess.run([FF, '-v', 'error', '-i', dry, '-af', AD_EQ, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout, np.float32).copy()[:len(x)]
    rms = lambda a: np.sqrt((a[np.abs(a) > 1e-4] ** 2).mean())
    y *= rms(x) / rms(y)
    R = REVERB; rng = np.random.default_rng(3); n = int(R['decay'] * 5 * SR); tt = np.arange(n) / SR
    ir = np.concatenate([np.zeros(int(R['pre'] * SR)), rng.standard_normal(n) * np.exp(-tt / R['decay'])]); ir /= np.sqrt((ir ** 2).sum())
    wet = sosfilt(butter(2, R['band'], 'bandpass', fs=SR, output='sos'), fftconvolve(y, ir)[:len(y)])
    out = y + R['wet'] * wet
    return out / max(1.0, np.abs(out).max() / 0.97)


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
    save(talk, os.path.join(EP, 'voice/talk_track_dry.wav'))
    save(ad_voice(talk), os.path.join(EP, 'voice/talk_track.wav'))
    dst = os.path.join(EP, 'voice/lines/L8_fit.wav'); r, d = fit(os.path.join(ROOT, L['L8']['file']), L8_SLOT[1], dst)
    s5 = pcm(os.path.join(ROOT, 'outputs/ep07/voice/s5_track.mp3')); s5[int(0.30 * SR):int(1.80 * SR)] = 0
    a = pcm(dst); i = int(L8_SLOT[0] * SR); s5[i:i + len(a)] += a[:len(s5) - i]
    save(s5, os.path.join(EP, 'voice/s5_track.wav')); print(f'L8 {r:.2f}배 → {d:.2f}s')
    subs.append(('L8', S5_AT + L8_SLOT[0], S5_AT + L8_SLOT[0] + max(d, L8_SLOT[1]) + 0.3))
    print('카피:', [(c, round(a0, 2), round(a1, 2)) for c, a0, a1 in subs])

    E7 = P['episodes']['ep07']
    V['placements'] = [{'file': 'outputs/ep11/voice/talk_track.wav', 'at': 0.0}] + \
                      [{'file': x['file'], 'at': round(x['at'] + D + EXTRA, 3)} for x in E7['placements'] if 'L7' in x['file']] + \
                      [{'file': 'outputs/ep11/voice/s5_track.wav', 'at': S5_AT}]
    # 광고 배경음: 피아노, 엔딩 카드 끝(레코드 긁힘)에서 뚝 끊김
    V['bgm'] = {'file': 'outputs/ep01/bgm/A_lofi_piano.mp3', 'target_lufs': -25, 'duck_db': 4, 'fade_in': 0.6, 'end_at': round(S5_AT + 0.05, 2), 'fade_out': 0.1,
                # v12 ①: 소리가 주인공인 순간엔 배경음을 내림(짠 슬로, 꿀꺽, 엔딩 카드 캔·따르기)
                'dips': [{'at': round(rt(RAMP_A), 2), 'len': round(rt(RAMP_B) - rt(RAMP_A) + 0.3, 2), 'db': -5},
                         {'at': round(CUT1 + 1.15, 2), 'len': 3.2, 'db': -6},
                         {'at': round(CARD_AT, 2), 'len': CARD_LEN, 'db': -9}],
                'note': 'ep11 v2 광고 연출: 광고 구간만, 현실 복귀에서 끊김 / v12 소리 주인공 구간 내림'}
    json.dump(P, open(pp, 'w'), ensure_ascii=False, indent=1)
    ad_look()

    T = json.load(open(os.path.join(ROOT, 'outputs/ep07/text_overlay.json')))
    # 제목(사용자 2026-10-22 재정정): "초겨울 포차의 계절 / 맥주광고 따라하기", 노란색 = "맥주광고"
    # v11(2026-10-23 사용자): 시작 화면과 같은 한 줄 "맥주광고 따라하기"(노란색 = 맥주광고)
    T['title']['lines'] = [{'spans': [{'text': '맥주광고', 'color': '#FFD84A'}, {'text': ' 따라하기', 'color': '#FFFFFF'}]}]
    # v2: 광고 구간 대사는 광고 카피(hf_fx copy)로, 아래 자막은 현실 복귀 대사만
    T['subtitles'] = [{'cut': c, 'text': L[c]['subtitle'], 'speaker': L[c]['speaker'], 'start': round(a0, 2), 'end': round(a1, 2), 'x': 0.5} for c, a0, a1 in subs if c == 'L8']
    T['channel']['center_y'] = CHAN_Y
    T['note'] = 'ep11 v2: 광고 구간은 카피 글씨, 이모! 만 일반 자막 / v9: 채널명 하단'
    json.dump(T, open(os.path.join(EP, 'text_overlay.json'), 'w'), ensure_ascii=False, indent=1)
    for s in T['subtitles']:
        print(s['start'], s['end'], s['text'])



def end_card():
    """엔딩 카드 배경: 짠 순간 프레임을 흐리고 어둡게(따뜻한 빛만 남김).
    v12 ④(실제 광고 마지막 화면처럼): 가운데에 '제품 사진' = 짠 순간 잔 두 개를 선명하게 잘라 둥근 모서리 + 그림자로 올림."""
    from PIL import ImageDraw
    src = os.path.join(ROOT, 'outputs/ep07/s1/clip_v2.mp4'); dst = os.path.join(EP, 'card/end_bg.png')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    raw = os.path.join(EP, 'card/clink_raw.png')
    subprocess.run([FF, '-y', '-v', 'error', '-ss', '9.5', '-i', src, '-frames:v', '1', '-vf', 'scale=1080:1920', raw], check=True)
    full = Image.open(raw).convert('RGB')
    im = full.filter(ImageFilter.GaussianBlur(14))
    im = ImageEnhance.Brightness(ImageEnhance.Color(im).enhance(0.8)).enhance(0.45)
    S_, cx, cy = 520, 560, 1100                      # 잔 두 개(x 440~680, y 1020~1240)와 웃는 얼굴이 들어가는 정사각형
    shot = full.crop((cx - S_ // 2, cy - S_ // 2 - 60, cx + S_ // 2, cy + S_ // 2 - 60))
    shot = ImageEnhance.Contrast(ImageEnhance.Brightness(shot).enhance(1.05)).enhance(1.06)
    m = Image.new('L', shot.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, S_ - 1, S_ - 1], radius=44, fill=255)
    px, py = (1080 - S_) // 2, 1210 - S_ - 40          # 슬로건(0.63 = 1210px) 위
    sh = Image.new('L', (1080, 1920), 0); ImageDraw.Draw(sh).rounded_rectangle([px, py + 18, px + S_, py + S_ + 18], radius=44, fill=170)
    sh = sh.filter(ImageFilter.GaussianBlur(26)); im = Image.composite(Image.new('RGB', im.size, (0, 0, 0)), im, sh)
    im.paste(shot, (px, py), m)
    ImageDraw.Draw(im).rounded_rectangle([px, py, px + S_ - 1, py + S_ - 1], radius=44, outline=(242, 228, 200), width=2)
    im.save(dst)
    return 'outputs/ep11/card/end_bg.png'


def ramp_clip():
    """v12 ②: s1 대화+짠 클립에서 잔이 닿기 직전 RAMP_A~RAMP_B만 RAMP_SP배로(움직임 보간), 앞뒤 원래 속도 → s1/clip_ramp.mp4."""
    src = os.path.join(EP, 's1/clip_v2.mp4'); dst = os.path.join(EP, 's1/clip_ramp.mp4')
    if os.path.exists(dst) and os.path.getmtime(dst) > os.path.getmtime(__file__):
        return
    fc = (f'[0:v]trim=0:{RAMP_A},setpts=PTS-STARTPTS[a];'
          # 보간 필터가 끝 프레임을 버려 짧아짐(1.71s) → 입력을 0.1s 더 받고 출력을 정확한 길이로 자름
          f'[0:v]trim={RAMP_A}:{RAMP_B + 0.1},setpts=(PTS-STARTPTS)/{RAMP_SP},minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:vsbmc=1,'
          f'trim=duration={(RAMP_B - RAMP_A) / RAMP_SP:.3f},setpts=PTS-STARTPTS[b];'
          f'[0:v]trim={RAMP_B},setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0,fps=24,format=yuv420p[v]')
    subprocess.run([FF, '-y', '-v', 'error', '-i', src, '-filter_complex', fc, '-map', '[v]', '-c:v', 'libx264', '-crf', '15', '-preset', 'medium', dst], check=True)
    print('속도 조절 클립', os.path.relpath(dst, ROOT), f'{dur(dst):.2f}s')


def ad_look():
    clip = lambda cut, src, tag, i0, ln: {'cut': cut, 'kind': 'clip', 'source_cut': src, 'clip_tag': tag, 'in': i0, 'len': ln, 'time_card': None}
    E = json.load(open(os.path.join(ROOT, 'outputs/ep07/edit_list.json')))
    ramp_clip()
    E['cuts'] = [clip('01', 's1', 'ramp', 0.0, CUT1), clip('02', 's2', 'slow', 0.0, SLOW_LEN), clip('03', 's4', 'v1', 0.0, 3.0),
                 {'cut': '04', 'kind': 'still', 'source_cut': 'card', 'image': end_card(), 'in': 0, 'len': CARD_LEN, 'time_card': None},
                 clip('05', 's5', 'v2', 0.0, 5.0)]
    E['history'] = E.get('history', []) + [f'2026-10-23 ep11 v12: 대화+짠(속도 조절) {CUT1} → 원샷 슬로 {SLOW_LEN} → 캬 3.0 → 엔딩 카드 {CARD_LEN} → 이모! 5.0 = {S5_AT + 5.0:.2f}s']
    json.dump(E, open(os.path.join(EP, 'edit_list.json'), 'w'), ensure_ascii=False, indent=1)
    B = json.load(open(os.path.join(EP, 'band_offsets.json'))); B['per_cut_top'].setdefault('card', 0)
    json.dump(B, open(os.path.join(EP, 'band_offsets.json'), 'w'), ensure_ascii=False, indent=1)

    cp = lambda at, dur, text, **k: dict(at=round(at, 2), dur=round(dur, 2), text=text, **{'y': COPY_Y, **k})
    s = {c: t0 for c, (t0, _) in SLOT.items()}
    sw = [m['at'] for m in moves() if m['scale'] == ZOOM]   # 카메라 전환 시각
    F = json.load(open(os.path.join(ROOT, 'outputs/ep07/hf_fx.json')))
    F['cuts'] = {
        '01': {'grade': GRADE, 'moves': moves(),
               # 카피는 카메라가 다음 사람으로 넘어갈 때 함께 사라짐(v5: 앞 카피가 다음 사람 화면에 남던 것 수정)
               'copy': [cp(s['L1'], sw[1] + 0.05 - s['L1'], '초겨울, 포차의 계절.'),
                        cp(s['L2'], sw[2] + 0.05 - s['L2'], '입김마저 시원하다.'),
                        cp(s['L3'], sw[4] + 0.05 - s['L3'], '차가운 잔에 담은', y=COPY_Y),
                        cp(s['L4'], sw[4] + 0.05 - s['L4'], '우리의 하루.', y=COPY_Y + 0.05),
                        cp(s['L5'], s['L6'] - s['L5'] - 0.06, '건배하라!', size=72),
                        cp(s['L6'], CUT1 - s['L6'] - 0.06, '짠!', size=104, weight=400, fade=0.3)],
               'flash': [{'at': round(rt(9.5), 2), 'dur': 0.3, 'peak': 0.22}]},
        '02': {'grade': GRADE, 'cam': {'from': 1.0, 'to': 1.06}},
        '03': {'grade': GRADE, 'copy': [cp(14.35 + D - 10.0 - SLOW_LEN, 1.6, '캬~', size=110, weight=300, y=COPY_Y + 0.01)]},
        '04': {'cam': {'from': 1.06, 'to': 1.0}, 'drift': None,
               # v12 ④: 가운데 '제품 사진'(짠 순간)은 배경에 넣고, 아래에 슬로건·이름·작은 경고문
               'copy': [cp(0.3, CARD_LEN - 0.3, '초겨울, 포차의 계절.', y=0.63, size=72, fade=0.9),
                        cp(0.7, CARD_LEN - 0.7, 'MISOON & CHANGSU', y=0.69, size=30, weight=400, spacing=0.45, color='#E8D9B8', fade=0.8),
                        cp(0.9, CARD_LEN - 0.9, WARNING, y=0.765, size=28, weight=400, spacing=0.04, color='#B8AEA2', fade=0.6)]},
        '05': {'punch': {'at': 0.45, 'scale': 1.04, 'settle': 1.0}},   # 현실: 색보정·카피 없음
    }
    F['note'] = 'ep11 v2 광고 연출: 01~04 색보정·카피, 02 슬로모션, 04 엔딩 카드, 05 평소 화면'
    json.dump(F, open(os.path.join(EP, 'hf_fx.json'), 'w'), ensure_ascii=False, indent=1)

    E7 = json.load(open(os.path.join(ROOT, 'outputs/ep07/sfx/sfx_list.json')))['items']
    cup = next(x['file'] for x in E7 if x['name'] == 'clink'); el = 'outputs/ep11/sfx/el/'; end = S5_AT + 5.0
    sf = lambda name, file, a0, ln, lufs, **k: dict(name=name, file=file, at=round(a0, 3), len=round(ln, 2), target_lufs=lufs, fade_out=k.pop('fo', 0.05), **k)
    # v12 ①: 소리가 주인공(실제 맥주 광고처럼 가까이서 들리는 소리) — 대사와 겹치지 않는 자리만(짠 슬로, 원샷 꿀꺽, 엔딩 카드)
    items = [sf('street_amb_ad', 'outputs/ep01/sfx/el/street_amb.mp3', 0.0, S5_AT, -38, loop=True, fade_in=0.3, fo=0.05),
             sf('fizz_open', el + 'beer_fizz.mp3', 0.0, 2.0, -32, fade_in=0.3, fo=0.4),
             sf('whoosh_slow', el + 'whoosh_soft.mp3', rt(RAMP_A) - 0.05, 1.0, -26),   # '짠!'(8.94~9.25s) 끝난 뒤
             sf('glass_clink', el + 'glass_clink.mp3', rt(9.47), 1.6, -17, fo=0.4),
             sf('gulp1', el + 'gulp.mp3', CUT1 + 1.3, 1.6, -22, fo=0.1),
             sf('gulp2', el + 'gulp.mp3', CUT1 + 2.7, 1.6, -25, fo=0.2),
             sf('fizz_slow', el + 'beer_fizz.mp3', 10.4 + EXTRA, 2.0, -32, fade_in=0.2, fo=0.5),
             sf('mugs_down', cup, CUT1 + (13.35 - 10.0) / SLOW, 0.4, -26, fo=0.1),
             sf('whoosh_card', el + 'whoosh_soft.mp3', CARD_AT - 0.1, 1.0, -26),
             sf('can_open', el + 'can_open.mp3', CARD_AT + 0.1, 1.0, -18, fo=0.2),
             sf('pour_card', el + 'beer_pour.mp3', CARD_AT + 0.75, CARD_LEN - 0.8, -20, fade_in=0.05, fo=0.15),
             sf('record_scratch', el + 'record_scratch.mp3', S5_AT - 0.05, 0.8, -15),
             sf('street_amb_real', 'outputs/ep01/sfx/el/street_amb.mp3', S5_AT, end - S5_AT, -32, loop=True, fo=0.8)]
    json.dump({'note': 'ep11 v2 광고 효과음(ElevenLabs 5개) + 현실 복귀', 'items': items}, open(os.path.join(EP, 'sfx/sfx_list.json'), 'w'), ensure_ascii=False, indent=1)
    print(f'v2: 총 {end:.2f}s, 슬로 {SLOW_LEN}s, 엔딩 카드 {CARD_LEN}s, 현실 복귀 {S5_AT}s')


if __name__ == '__main__':
    main()
