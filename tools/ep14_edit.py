#!/usr/bin/env python3
"""ep14 인형뽑기 편집(0원): Kling 클립 7개 + 정지 이미지 + 휴대폰 알림 그래픽 → 무음 영상 + 소리 배치(mix_audio.py).
사용: python3 tools/ep14_edit.py [--tag v1]  → outputs/ep14/roughcut/ep14_<tag>_silent.mp4, voice_profile ep14.placements·bgm, sfx/sfx_list.json
     python3 tools/mix_audio.py --ep ep14 --video outputs/ep14/roughcut/ep14_<tag>_silent.mp4 --out outputs/ep14/roughcut/ep14_<tag>.mp4
- 화면은 OpenCV로 한 프레임씩 만들어 ffmpeg로 바로 인코딩(HyperFrames 안 씀). 글씨는 PIL(NotoSansKR 굵기 지정, 효과 글씨는 Jua).
- "나는 실패하지 않습니다" 4번 모두 단어마다 3단계 확대(사용자 2026-10-23): 나는 → 실패하지 → 않습니다, 한 단계마다 쿵 + 살짝 흔들림,
  자막도 단어가 하나씩 붙음.
- 실패 몽타주는 C3(집게)의 잡고→놓침 구간을 2배속으로, 좌우를 번갈아 뒤집어 돌려 씀. 판 수는 유리 알림창(02a 규칙) 글씨.
- 14번 휴대폰 잠금화면은 그래픽으로 직접 그림: "1,000원 결제" 알림 25개가 점점 빨리 쌓임 → "총 25,000원".
"""
import argparse, json, os, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, 'outputs/ep14'); CL = os.path.join(EP, 'clips'); FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 24
NOTO = os.path.join(ROOT, 'assets/fonts/NotoSansKR-Variable.ttf'); JUA = os.path.join(ROOT, 'assets/fonts/Jua-Regular.ttf')
COL = {'misun': '#FF9CC2', 'changsu': '#8FB0E8', 'white': '#FFFFFF', 'yellow': '#FFD84A'}
TITLE = [[('인형뽑기방이 망하지 않는 이유', 'white')], [('(계수정 빙의한 미순)', 'yellow')]]   # 제목 2줄(사용자 2026-10-23)
ZOOM_STEPS = [1.0, 1.28, 1.6, 1.95]     # 나는 / 실패하지 / 않습니다 → 3단계


def font(size, weight=800, path=NOTO):
    f = ImageFont.truetype(path, size)
    if path == NOTO:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def text_img(lines, size, weight=800, stroke=9, gap=18, path=NOTO, maxw=1000):
    """lines = [[(text, color), ...], ...] → RGBA. 폭이 maxw를 넘으면 글자 크기를 줄임."""
    while True:
        f = font(size, weight, path); d = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
        ws = [sum(d.textlength(t, font=f) for t, _ in ln) for ln in lines]
        if max(ws) <= maxw or size < 30:
            break
        size -= 4
    lh = size + gap; im = Image.new('RGBA', (int(max(ws)) + 2 * stroke + 20, lh * len(lines) + 2 * stroke + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        x = (im.width - ws[i]) / 2
        for t, c in ln:
            d.text((x, stroke + 10 + i * lh), t, font=f, fill=COL.get(c, c), stroke_width=stroke, stroke_fill='#111111'); x += d.textlength(t, font=f)
    return np.array(im)


def chip_img(text, size=58):
    """유리 알림창(02a): 흰 78% 둥근 띠 + Jua 갈색 글씨."""
    f = font(size, path=JUA); d = ImageDraw.Draw(Image.new('RGBA', (1, 1))); tw = d.textlength(text, font=f)
    im = Image.new('RGBA', (int(tw) + 80, size + 44), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=im.height // 2, fill=(255, 255, 255, 200))
    d.text((40, 16), text, font=f, fill='#5A4A52')
    return np.array(im)


def put(frame, rgba, cx, cy, alpha=1.0, scale=1.0):
    """frame(BGR)에 RGBA를 가운데 (cx, cy)로 얹음."""
    if scale != 1.0:
        rgba = cv2.resize(rgba, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    h, w = rgba.shape[:2]; x0, y0 = int(cx - w / 2), int(cy - h / 2)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if xa >= xb or ya >= yb:
        return
    s = rgba[ya - y0:yb - y0, xa - x0:xb - x0]; a = s[..., 3:4].astype(np.float32) / 255 * alpha
    frame[ya:yb, xa:xb] = (frame[ya:yb, xa:xb] * (1 - a) + s[..., 2::-1] * a).astype(np.uint8)


class Clip:
    def __init__(self, path):
        cap = cv2.VideoCapture(path); self.fps = cap.get(cv2.CAP_PROP_FPS); self.frames = []
        while True:
            ok, f = cap.read()
            if not ok:
                break
            self.frames.append(cv2.resize(f, (W, H), interpolation=cv2.INTER_CUBIC))

    def at(self, t):
        return self.frames[max(0, min(len(self.frames) - 1, int(round(t * self.fps))))].copy()


def ease(x):
    return 1 - (1 - min(1, max(0, x))) ** 3


def zoom(frame, s, cx, cy):
    if s <= 1.001:
        return frame
    cw, ch = W / s, H / s; x0 = min(max(cx - cw / 2, 0), W - cw); y0 = min(max(cy - ch / 2, 0), H - ch)
    M = np.float32([[s, 0, -x0 * s], [0, s, -y0 * s]])
    return cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_LINEAR)


def phone_frames(n, t_list, total_bg):
    """휴대폰 잠금화면: 시계 + 알림 카드(최근 4개 보이고 아래 '+N'), 끝에 '총 25,000원'."""
    bg = np.zeros((H, W, 3), np.uint8)
    for y in range(H):
        k = y / H; bg[y] = (int(70 + 40 * k), int(30 + 20 * k), int(40 + 60 * (1 - k)))   # BGR: 보라→남색
    big = text_img([[('21:47', 'white')]], 190, weight=300, stroke=0); date = text_img([[('10월 23일 목요일', 'white')]], 44, weight=500, stroke=0)
    f1, f2 = font(44, 800), font(34, 500)
    card = Image.new('RGBA', (920, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, 919, 149], radius=36, fill=(245, 245, 250, 225))
    d.ellipse([28, 35, 108, 115], fill='#FFD84A'); d.text((68, 75), '₩', font=font(46, 800), fill='#5A4A52', anchor='mm')
    d.text((132, 30), '결제 승인  1,000원', font=f1, fill='#222222'); d.text((132, 90), '인형뽑기 · 방금', font=f2, fill='#777777')
    card = np.array(card)
    total = text_img([[('총 ', 'white'), ('25,000원', 'yellow')]], 130, stroke=12)
    out = []
    for i in range(n):
        t = i / FPS; fr = bg.copy(); put(fr, big, W / 2, 730); put(fr, date, W / 2, 905)
        k = sum(1 for x in t_list if x <= t)   # 지금까지 온 알림 수
        for j in range(min(k, 4)):
            age = t - t_list[k - 1 - j]; slide = ease(age / 0.12) if j == 0 else 1.0
            y = 1020 + j * 170 - (1 - slide) * 60
            put(fr, card, W / 2, y, alpha=slide if j == 0 else (1.0 - 0.18 * j))
        if k > 4:
            put(fr, chip_img(f'+{k - 4}개 더', 44), W / 2, 1020 + 4 * 170)
        if t >= total_bg:
            a = ease((t - total_bg) / 0.25); put(fr, total, W / 2, 1300, alpha=a, scale=0.7 + 0.3 * a)
        out.append(fr)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--tag', default='v1'); a = ap.parse_args()
    P = json.load(open(os.path.join(ROOT, 'outputs/voice_profile.json'))); E = P['episodes']['ep14']; L = {l['cut']: l for l in E['lines']}
    k3 = cv2.resize(cv2.imread(os.path.join(EP, 'img/K3_v1.png')), (W, H), interpolation=cv2.INTER_CUBIC)
    k5b = cv2.resize(cv2.imread(os.path.join(EP, 'img/K5b_v1.png')), (W, H), interpolation=cv2.INTER_CUBIC)
    clips = {}

    def clip(name):
        if name not in clips:
            clips.clear(); clips[name] = Clip(os.path.join(CL, name + '.mp4'))
        return clips[name]

    # 장면 목록: (이름, 종류, 원본, 시작, 길이, 배속, 좌우뒤집기, 확대 {t단계: [..], c: (x,y)})
    FACE_C4, FACE_C7 = (652, 880), (528, 930)
    C4Z = {'steps': [0.32, 1.26, 2.32], 'c': FACE_C4}
    segs = [
        dict(n='S0 거리', src='C1_v1', t0=0.0, len=3.3),
        dict(n='S1 기계', still=True, len=1.6),
        dict(n='S2 저 오리', src='C2_v1_eyefix', t0=0.0, len=2.9),
        dict(n='S3 1판', src='C3_v1', t0=0.4, len=4.3, chip='1판', miss=4.17 - 0.4),
        dict(n='S4 실패X①', src='C4_v1', t0=0.0, len=3.9, z=C4Z),
        dict(n='S5a 2판', src='C3_v1', t0=2.6, len=1.3, sp=2.0, chip='2판', miss=(4.17 - 2.6) / 2.0),
        dict(n='S5b 3판', src='C3_v1', t0=2.6, len=1.3, sp=2.0, flip=True, chip='3판', miss=(4.17 - 2.6) / 2.0),
        dict(n='S5c 5판', src='C3_v1', t0=2.6, len=1.3, sp=2.0, chip='5판', miss=(4.17 - 2.6) / 2.0),
        dict(n='S6 실패X②', src='C4_v1', t0=0.0, len=3.9, z=C4Z),
        dict(n='S7 그만해', src='C5_v1', t0=0.6, len=2.9),
        dict(n='S8 쉿①', src='C6_v1', t0=0.6, len=2.2),
        dict(n='S9a 11판', src='C3_v1', t0=2.6, len=1.15, sp=2.2, flip=True, chip='11판', miss=(4.17 - 2.6) / 2.2),
        dict(n='S9b 15판', src='C3_v1', t0=2.6, len=1.15, sp=2.2, chip='15판', miss=(4.17 - 2.6) / 2.2),
        dict(n='S9c 19판', src='C3_v1', t0=2.6, len=1.15, sp=2.2, flip=True, chip='19판', miss=(4.17 - 2.6) / 2.2),
        dict(n='S10 쉿②', src='C6_v1', t0=1.05, len=1.6),
        dict(n='S11a 24판', src='C3_v1', t0=2.6, len=1.45, sp=2.0, chip='24판', miss=(4.17 - 2.6) / 2.0),
        dict(n='S11 실패X③', src='C4_v1', t0=0.0, len=3.9, z=C4Z),
        dict(n='S12 25판', src='C3_v1', t0=0.6, len=2.8, sp=0.82, chip='25판'),
        dict(n='S12b 성공', win=True, len=2.2, chip='25판'),
        dict(n='S13 승리', src='C7_v1_eyefix', t0=0.0, len=1.9),
        dict(n='S14 결제 알림', phone=True, len=3.9),
        dict(n='S15 실패X④', src='C7_v1_eyefix', t0=1.2, len=4.4, z={'steps': [0.82, 1.76, 2.82], 'c': FACE_C7}),
    ]
    t = 0.0
    for s in segs:
        s['at'] = round(t, 3); t += s['len']
    total = round(t, 3); S = {s['n'].split()[0]: s for s in segs}

    # 소리 배치(절대 시각)
    VL = lambda cut: L[cut]['file']
    pl, subs, sfx, dips, hits = [], [], [], [], []

    def line(cut, at, speaker, text, end=None, size=None):
        pl.append({'file': VL(cut), 'at': round(at, 3)})
        subs.append(dict(text=text, sp=speaker, t0=at, t1=end or at + L[cut]['len'] + 0.25, size=size))

    def fail_line(seg, offs):
        """실패X: 녹음은 장면 시작에 맞춤(C4: 장면 소리 c4의 0.3s 지점이 말 시작 = 클립과 같음), 자막은 단어가 붙음."""
        at0 = seg['at'] + offs[0] - 0.02; pl.append({'file': VL('v2-04'), 'at': round(at0, 3)})
        w = ['나는....', '나는.... 실패하지....', '나는.... 실패하지.... 않습니다.']; ts = [seg['at'] + o for o in offs]
        for i in range(3):
            subs.append(dict(text=w[i], sp='misun', t0=ts[i], t1=ts[i + 1] if i < 2 else ts[2] + 1.15, size=None))
            hits.append(ts[i])
        dips.append({'at': round(ts[0] - 0.3, 2), 'len': round(ts[2] - ts[0] + 1.5, 2), 'db': -14})

    line('v2-01', S['S0']['at'] + 1.2, 'misun', '우리 딱 5천 원어치만 할까?')
    line('v2-02', S['S2']['at'] + 0.3, 'misun', '저 오리.... 오늘 데려간다...')
    for k in ('S4', 'S6', 'S11'):
        fail_line(S[k], [0.32, 1.26, 2.32])
    line('v2-07', S['S7']['at'] + 0.2, 'changsu', '미순아... 그만해...')
    for k, c, cut in (('S8', 0.9, 'v2-08'), ('S10', 0.45, 'v2-10')):
        line(cut, S[k]['at'] + c - 0.05, 'misun', '조효오오옹!!!', size=96)
    fail_line(S['S15'], [0.82, 1.76, 2.82])

    def fx(name, file, at, ln, lufs, **k):
        sfx.append(dict(name=name, file=file, at=round(at, 3), len=ln, target_lufs=lufs, **k))
    el = 'outputs/ep14/sfx/el/'
    fx('street_amb', 'outputs/ep01/sfx/el/street_amb.mp3', 0, S['S1']['at'], -36, loop=True, fade_in=0.2, fade_out=0.3)
    fx('arcade_amb', el + 'arcade_amb.mp3', S['S1']['at'], S['S14']['at'] - S['S1']['at'], -36, loop=True, fade_in=0.3, fade_out=0.4)
    fx('arcade_amb_end', el + 'arcade_amb.mp3', S['S15']['at'], S['S15']['len'], -38, loop=True, fade_in=0.3, fade_out=0.6)
    fx('click_1', el + 'button_click.mp3', S['S3']['at'] + 0.05, 0.5, -24)
    fx('motor_1', el + 'claw_motor.mp3', S['S3']['at'] + 0.2, 2.5, -27, fade_out=0.3)
    fx('drop_1', el + 'plush_drop.mp3', S['S3']['at'] + (4.17 - 0.4), 0.6, -20)
    for k in ('S5a', 'S5b', 'S5c', 'S9a', 'S9b', 'S9c', 'S11a'):
        sp = S[k].get('sp', 1); fx('click_' + k, el + 'button_click.mp3', S[k]['at'], 0.5, -28)
        fx('drop_' + k, el + 'plush_drop.mp3', S[k]['at'] + (4.17 - 2.6) / sp, 0.6, -21)
        fx('whoosh_' + k, 'outputs/ep06/sfx/el/whoosh_fast.mp3' if os.path.exists(os.path.join(ROOT, 'outputs/ep06/sfx/el/whoosh_fast.mp3')) else el + 'button_click.mp3', S[k]['at'] - 0.08, 0.4, -30)
    for k, c in (('S8', 0.9), ('S10', 0.45)):
        fx('shush_' + k, el + 'shush_tap.mp3', S[k]['at'] + c, 0.5, -18)
    fx('click_25', el + 'button_click.mp3', S['S12']['at'] + 0.05, 0.5, -24)
    fx('motor_25', el + 'claw_motor.mp3', S['S12']['at'] + 0.2, 2.5, -26, fade_out=0.3)
    WIN_AT = 0.9   # 성공 장면 안에서 번쩍 시각
    fx('sparkle', el + 'success_sparkle.mp3', S['S12b']['at'] + WIN_AT - 0.05, 1.0, -20)
    fx('win', el + 'win_jingle.mp3', S['S12b']['at'] + WIN_AT, 2.5, -19, fade_out=0.4)
    fx('chute', el + 'prize_chute.mp3', S['S13']['at'] - 0.1, 0.8, -18)
    for s_ in segs:
        if s_.get('miss') is not None:   # 실패: 툭 + 와와와(꽝)
            big = s_['n'].split()[0] in ('S3', 'S11a')
            fx('womp_' + s_['n'].split()[0], el + 'fail_womp.mp3', s_['at'] + s_['miss'] + 0.05, 1.2 if big else 0.6, -22 if big else -27, fade_out=0.2)
    hit = None
    for root in ('outputs/ep09/sfx/el/dramatic_hit.mp3', 'outputs/ep08/sfx/el/dramatic_hit.mp3', 'outputs/ep05/sfx/el/impact_boom.mp3'):
        if os.path.exists(os.path.join(ROOT, root)):
            hit = root; break
    if not hit:
        import glob
        hit = os.path.relpath(sorted(glob.glob(os.path.join(ROOT, 'outputs/*/sfx/el/dramatic_hit.mp3')))[0], ROOT)
    for i, h in enumerate(hits):
        fx(f'hit_{i}', hit, h - 0.02, 0.9, [-24, -21, -18][i % 3], fade_out=0.3)
    # 휴대폰 알림: 25개, 점점 빨라짐
    ph = S['S14']; gaps = np.geomspace(0.32, 0.045, 24); ts = [0.15] + list(0.15 + np.cumsum(gaps)); total_at = ts[-1] + 0.35
    for i, x in enumerate(ts):
        fx(f'ding_{i}', el + 'pay_ding.mp3', ph['at'] + x, 0.5, -22 - (6 if i > 8 else 0))
    fx('total_hit', hit, ph['at'] + total_at, 0.9, -20, fade_out=0.3)

    E['placements'] = pl
    E['bgm'] = {'file': 'outputs/ep14/bgm/claw_comedy.mp3', 'target_lufs': -27, 'duck_db': 6, 'fade_in': 0.5, 'end_at': total, 'fade_out': 1.2, 'dips': dips}
    E['edit'] = {'tag': a.tag, 'total': total, 'segments': [{k: v for k, v in s.items() if k != 'z'} for s in segs]}
    json.dump(P, open(os.path.join(ROOT, 'outputs/voice_profile.json'), 'w'), ensure_ascii=False, indent=1)
    os.makedirs(os.path.join(EP, 'sfx'), exist_ok=True)
    json.dump({'note': f'ep14 {a.tag} 인형뽑기 (tools/ep14_edit.py가 만듦)', 'items': sfx}, open(os.path.join(EP, 'sfx/sfx_list.json'), 'w'), ensure_ascii=False, indent=1)

    # 글씨 미리 그리기
    title = text_img(TITLE, 92, stroke=10); chan = text_img([[('지독한 미순', 'white')]], 52, weight=700, stroke=6)
    sub_cache = {}

    def sub_img(sb):
        key = (sb['text'], sb['sp'], sb['size'])
        if key not in sub_cache:
            sub_cache[key] = text_img([[(sb['text'], sb['sp'])]], sb['size'] or 74, stroke=9)
        return sub_cache[key]
    chips = {}
    sign = chip_img('1판 1,000원', 64); win_txt = text_img([[('성공!!!', 'yellow')]], 150, stroke=12)
    WIN_AT = 0.9
    nf = int(round(total * FPS)); fade = 0.4
    os.makedirs(os.path.join(EP, 'roughcut'), exist_ok=True); out = os.path.join(EP, f'roughcut/ep14_{a.tag}_silent.mp4')
    pr = subprocess.Popen([FF, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    phone = None
    for s in segs:
        n0, n1 = int(round(s['at'] * FPS)), int(round((s['at'] + s['len']) * FPS))
        if s.get('phone'):
            phone = phone_frames(n1 - n0, [x for x in ts], total_at)
        for fi in range(n0, min(n1, nf)):
            tt = fi / FPS; lt = tt - s['at']
            if s.get('still'):
                fr = zoom(k3, 1.25, W / 2, 1100)   # 고정(사용자: 밀려 들어가면 기계 윗단이 채널명 뒤로 올라가 글씨가 뜨고 겹쳐 보임)
            elif s.get('phone'):
                fr = phone[fi - n0].copy()
            elif s.get('win'):   # 성공: 오리를 꽉 잡은 집게가 천천히 올라감 → 번쩍 + 반짝이 + "성공!!!"
                up = ease(lt / 1.3); fr = zoom(k5b, 1.12 + 0.06 * up, W / 2, 860 + 70 * up)   # 오리가 1150→1080으로 올라감(판 수 글씨와 안 겹치게)
            else:
                fr = clip(s['src']).at(s['t0'] + lt * s.get('sp', 1.0))
                if s.get('flip'):
                    fr = fr[:, ::-1].copy()
            if s.get('z'):
                st = s['z']['steps']; lvl = sum(1 for x in st if lt >= x)
                sc = ZOOM_STEPS[lvl] if lvl == 0 else ZOOM_STEPS[lvl - 1] + (ZOOM_STEPS[lvl] - ZOOM_STEPS[lvl - 1]) * ease((lt - st[lvl - 1]) / 0.14)
                fr = zoom(fr, sc, *s['z']['c'])
                if lvl and lt - st[lvl - 1] < 0.12:   # 쿵 할 때 살짝 흔들림
                    k = int((lt - st[lvl - 1]) * FPS); dx = [10, -8, 5][min(k, 2)] * lvl / 2
                    fr = cv2.warpAffine(fr, np.float32([[1, 0, dx], [0, 1, -dx / 2]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
            if s.get('miss') is not None and 0 <= lt - s['miss'] < 0.5:   # 실패: 놓치는 순간 화면이 회색으로 바랬다 돌아옴 + "꽝"
                k_ = 1 - (lt - s['miss']) / 0.5; g_ = cv2.cvtColor(cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
                fr = (fr * (1 - 0.8 * k_) + g_ * 0.8 * k_ * 0.75).astype(np.uint8)
            if s.get('miss') is not None and lt >= s['miss']:
                if '꽝' not in chips:
                    chips['꽝'] = chip_img('꽝!', 64)
                put(fr, chips['꽝'], W / 2, 810, alpha=ease((lt - s['miss']) / 0.1), scale=1.0 + 0.25 * (1 - ease((lt - s['miss']) / 0.15)))
            if s.get('win') and lt >= WIN_AT:
                a_ = ease((lt - WIN_AT) / 0.2); fl = max(0.0, 1 - (lt - WIN_AT) / 0.3)
                fr = (fr * (1 - 0.6 * fl) + 255 * 0.6 * fl).astype(np.uint8)
                for j, (ox, oy, r_) in enumerate(((-300, -160, 34), (290, -220, 28), (-250, 210, 24), (320, 150, 38), (0, -330, 22), (-60, 300, 20))):
                    tw = 0.6 + 0.4 * abs(np.sin((lt - WIN_AT) * 7 + j)); rr = r_ * tw * a_; cx_, cy_ = W / 2 + ox, 1080 + oy
                    pts = np.array([[cx_, cy_ - rr * 2], [cx_ + rr * 0.45, cy_ - rr * 0.45], [cx_ + rr * 2, cy_], [cx_ + rr * 0.45, cy_ + rr * 0.45],
                                    [cx_, cy_ + rr * 2], [cx_ - rr * 0.45, cy_ + rr * 0.45], [cx_ - rr * 2, cy_], [cx_ - rr * 0.45, cy_ - rr * 0.45]], np.int32)
                    cv2.fillPoly(fr, [pts], (216, 246, 255), lineType=cv2.LINE_AA)
                put(fr, win_txt, W / 2, 1420, alpha=a_, scale=0.6 + 0.4 * a_ + 0.06 * np.sin((lt - WIN_AT) * 9))
            if s['n'].startswith('S1 '):
                put(fr, sign, W / 2, 700, alpha=ease((lt - 0.15) / 0.2))
            if s.get('chip'):
                if s['chip'] not in chips:
                    chips[s['chip']] = chip_img(s['chip'], 72)
                put(fr, chips[s['chip']], W / 2, 700, alpha=ease(lt / 0.12))
            put(fr, title, W / 2, 360); put(fr, chan, W / 2, 530)
            for sb in subs:
                if sb['t0'] <= tt < sb['t1']:
                    im = sub_img(sb); put(fr, im, W / 2, H - 430 - im.shape[0] / 2)
            if tt > total - fade:
                fr = (fr * max(0, (total - tt) / fade)).astype(np.uint8)
            pr.stdin.write(fr.tobytes())
    pr.stdin.close(); pr.wait()
    print(f'{len(segs)}장면 {total:.2f}s → {os.path.relpath(out, ROOT)}')
    for s in segs:
        print(f"  {s['at']:6.2f}s {s['len']:4.1f}s {s['n']}")


if __name__ == '__main__':
    main()
