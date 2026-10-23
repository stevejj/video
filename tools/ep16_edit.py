#!/usr/bin/env python3
"""ep16 금요일 오후 5시 39분이란 편집(0원). 참고 릴스(김햄찌)처럼 검은 바탕 + 가운데 가로 영상 창 + 위 제목 2줄 + 아래 채널명.
사용: python3 tools/ep16_edit.py [--tag v1] → outputs/ep16/roughcut/ep16_<tag>_silent.mp4 + voice_profile ep16 placements·bgm + sfx/sfx_list.json
     python3 tools/mix_audio.py --ep ep16 --video outputs/ep16/roughcut/ep16_<tag>_silent.mp4 --out outputs/ep16/roughcut/ep16_<tag>.mp4
- 영상 창 안 장면은 1080x780으로 만들고(이미지·클립을 꽉 채워 자름) 검은 화면 가운데에 붙임.
- 7번 속마음: 단어마다 한 단계씩 오른쪽 눈으로 확대(참고 릴스 "언제 끝나서/언제 정리하고/언제 집에 가냐" → 눈 가득).
- 8번 꿈: ep07 포장마차 맥주(짠·원샷)를 가로로 잘라 분홍·살구빛 빛 번짐.
- 10번: 모니터 오른쪽 아래 사내 메신저 알림 "안녕하세요. 창수님..........." → 알림으로 3단계 빠른 확대 + 단계마다 진동.
- 메신저 대화는 그래픽 말풍선(미순 분홍·왼쪽, 창수 하늘색·오른쪽).
"""
import argparse, json, os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ep14_edit import font, text_img, chip_img, ease, COL, NOTO, JUA
import imageio_ffmpeg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, 'outputs/ep16'); FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 24
WW, WH, WY = 1080, 780, 570          # 영상 창 크기·위치(검은 띠 사이)
TITLE = [[('금요일 오후', 'white')], [('5시 39분이란', 'yellow')]]
K1F, K2F = 'K1b_v1.mp4', 'K2b_v1_fix.mp4'
KEY_REGION = (540, 430, 780, 640)   # 클립(1108x828)에서 흰 키보드 위 날개 끝 — 클립 받고 확인해 맞춤   # v3: 키보드 하나·거치대 모니터 밑(사용자). K2b는 볼터치 고친 파일


def taps(path, region, thr=1.6):
    """날개가 키보드를 두드리는 순간(클립 기준 초). region=(x0,y0,x1,y1) 날개 끝 부근, 아래로 내려치는 움직임 꼭대기."""
    cap = cv2.VideoCapture(path); fps = cap.get(cv2.CAP_PROP_FPS); prev = None; m = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(f[region[1]:region[3], region[0]:region[2]], cv2.COLOR_BGR2GRAY).astype(np.float32)
        m.append(0.0 if prev is None else float(np.abs(g - prev).mean())); prev = g
    m = np.convolve(np.array(m), np.ones(2) / 2, mode='same'); base = np.median(m) + 1e-6
    return [i / fps for i in range(1, len(m) - 1) if m[i] > m[i - 1] and m[i] >= m[i + 1] and m[i] > thr * base], len(m) / fps


def put(fr, rgba, cx, cy, alpha=1.0, scale=1.0):
    if scale != 1.0:
        rgba = cv2.resize(rgba, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    h, w = rgba.shape[:2]; Hh, Ww = fr.shape[:2]; x0, y0 = int(cx - w / 2), int(cy - h / 2)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(Ww, x0 + w), min(Hh, y0 + h)
    if xa >= xb or ya >= yb:
        return
    s = rgba[ya - y0:yb - y0, xa - x0:xb - x0]; a = s[..., 3:4].astype(np.float32) / 255 * alpha
    fr[ya:yb, xa:xb] = (fr[ya:yb, xa:xb] * (1 - a) + s[..., 2::-1] * a).astype(np.uint8)


def crop_win(img, s=1.0, cx=None, cy=None, ar=WW / WH):
    """원본(아무 크기)에서 창 비율로 잘라 1080x780. s=확대 배수, (cx, cy)=원본 좌표 중심."""
    h, w = img.shape[:2]
    bw = min(w, h * ar); bh = bw / ar; cw, ch = bw / s, bh / s
    cx = w / 2 if cx is None else cx; cy = h / 2 if cy is None else cy
    x0 = min(max(cx - cw / 2, 0), w - cw); y0 = min(max(cy - ch / 2, 0), h - ch)
    M = np.float32([[WW / cw, 0, -x0 * WW / cw], [0, WH / ch, -y0 * WH / ch]])
    return cv2.warpAffine(img, M, (WW, WH), flags=cv2.INTER_CUBIC)


class Clip:
    def __init__(self, path, crop=None):
        cap = cv2.VideoCapture(path); self.fps = cap.get(cv2.CAP_PROP_FPS); self.fr = []
        while True:
            ok, f = cap.read()
            if not ok:
                break
            if crop:   # (y0, y1) 세로 띠
                f = f[crop[0]:crop[1]]
            self.fr.append(crop_win(f))

    def at(self, t):
        return self.fr[max(0, min(len(self.fr) - 1, int(round(t * self.fps))))].copy()


def dream(fr, k=1.0):
    """꿈 효과: 분홍·살구빛 색 + 빛 번짐 + 밝게 날림 + 가장자리 하얗게."""
    f = fr.astype(np.float32)
    glow = cv2.GaussianBlur(f, (0, 0), 18)
    f = f * 0.55 + glow * 0.75 + 30
    tint = np.array([200, 190, 255], np.float32)       # BGR 살구분홍
    f = f * (1 - 0.28 * k) + tint * 0.28 * k
    yy, xx = np.mgrid[0:WH, 0:WW]; d = np.sqrt(((xx - WW / 2) / (WW / 2)) ** 2 + ((yy - WH / 2) / (WH / 2)) ** 2)
    v = np.clip((d - 0.55) / 0.6, 0, 1)[..., None] * k
    f = f * (1 - v) + 255 * v
    return np.clip(f, 0, 255).astype(np.uint8)


def clock_card(text):
    """참고 릴스 시계 컷: 어두운 휴대폰 잠금화면 느낌, 큰 흰 글씨."""
    fr = np.zeros((WH, WW, 3), np.uint8); fr[:] = (40, 30, 30)
    for y in range(WH):
        fr[y] = (int(48 + 30 * y / WH), int(30 + 15 * y / WH), int(34 + 10 * y / WH))
    return fr   # 시각 글씨는 그릴 때 따로(톡 튀어나오게)


def clock_text(text):
    """'(금) 오후 5:38' → 위 작은 흰 '(금) 오후', 아래 큰 노랑 시각(사용자 v1: 시계가 자막보다 눈에 안 들어옴)."""
    day, tm = text.rsplit(' ', 1)
    return text_img([[(day, 'white')], [(tm, 'yellow')]], 0, stroke=0) if False else (
        text_img([[(day, 'white')]], 70, weight=700, stroke=6), text_img([[(tm, 'yellow')]], 230, weight=900, stroke=12))


def chat_panel(msgs, t, appear):
    """메신저 화면: 위 이름표 '미순', 말풍선이 차례로(appear[i] 시각) 아래에서 톡 올라옴."""
    im = Image.new('RGB', (WW, WH), '#E9EEF3'); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, WW, 92], fill='#F7F8FA'); d.text((WW / 2, 46), '미순', font=font(40, 800), fill='#333333', anchor='mm')
    f = font(44, 700); y = 130
    shown = [(m, a) for m, a in zip(msgs, appear) if t >= a]
    if len(shown) > 4:   # 아래 괄호 자막과 안 겹치게 최근 4개만
        shown = shown[-4:]
    for (who, txt), a in shown:
        k = ease((t - a) / 0.18); ff = f; tw = d.textlength(txt, font=ff); sz = 44
        while tw + 60 > 780 and sz > 26:   # 긴 줄(ㅁㄴㅇㄹ…)은 글씨를 줄여 말풍선 안에
            sz -= 2; ff = font(sz, 700); tw = d.textlength(txt, font=ff)
        bw, bh = tw + 60, 92
        if who == 'misun':
            x0 = 40; fill = '#FFD6E4'
            d.ellipse([40, y + 6, 110, y + 76], fill='#FF9CC2'); d.text((75, y + 41), '미', font=font(30, 800), fill='white', anchor='mm'); x0 = 130
        else:
            x0 = WW - 40 - bw; fill = '#CFE3FF'
        yy = y + (1 - k) * 30
        d.rounded_rectangle([x0, yy, x0 + bw, yy + bh], radius=40, fill=fill)
        d.text((x0 + 30, yy + bh / 2), txt, font=ff, fill='#222222', anchor='lm')
        y += bh + 26
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)


def toast_img():
    """사내 메신저 알림(윈도 알림 느낌): 어두운 둥근 카드, 아이콘 + 이름 + 미리보기 첫 줄."""
    im = Image.new('RGBA', (560, 170), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 559, 169], radius=22, fill=(38, 42, 52, 245), outline=(90, 96, 110, 255), width=2)
    d.rounded_rectangle([24, 26, 84, 86], radius=14, fill='#4A7DFF'); d.text((54, 56), '사', font=font(34, 800), fill='white', anchor='mm')
    d.text((104, 30), '사내 메신저 · 방금', font=font(26, 500), fill='#A9B0BF')
    d.text((104, 70), '김OO 매니저', font=font(32, 800), fill='white')
    d.text((24, 120), '안녕하세요. 창수님...........', font=font(32, 600), fill='#E6E9EF')
    return np.array(im)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--tag', default='v1'); a = ap.parse_args()
    P = json.load(open(os.path.join(ROOT, 'outputs/voice_profile.json'))); E = P['episodes']['ep16']; L = {l['cut']: l for l in E['lines']}
    img = {k: cv2.imread(os.path.join(EP, f'img/{k}_v1.png')) for k in ('O1', 'O3', 'O4', 'O5', 'O6')}
    K1 = Clip(os.path.join(EP, 'clips/' + K1F)); K2 = Clip(os.path.join(EP, 'clips/' + K2F))
    D1 = Clip(os.path.join(ROOT, 'outputs/ep07/s1/clip_v2.mp4'), crop=(470, 990)); D2 = Clip(os.path.join(ROOT, 'outputs/ep07/s2/clip_v1.mp4'), crop=(470, 990))
    toast = toast_img()
    chat1 = [('misun', '오늘 칼퇴하닝?'), ('changsu', '웅ㅋㅋㅋㅋ'), ('misun', '맥주한잔하까?'), ('changsu', '웅ㅋㅋㅋㅋ')]
    chat2 = chat1 + [('changsu', '칼퇴는 못할거가타..ㅁㄴㅇㄹㅁㄴㅇㄹㅁㄴㅇㄹ'), ('misun', '자기야 힘내....')]
    EYE = (1520, 976)                       # O4·O5 오른쪽 눈(원본 2400x1792 좌표)
    W7 = [0.03, 0.74, 1.55]                 # 속마음 단어 시작(녹음 기준)
    TOAST_SRC = (880, 640)                  # O6(1200x896)에서 알림 중심

    segs = [
        dict(n='S1 월', k='K1', t0=0.0, len=1.5, sp=1.0, day='월'),          # v2: 사용자 "월~목 더 길게" 0.8 → 1.5s씩
        dict(n='S1 화', k='K1', t0=1.6, len=1.5, sp=1.0, day='화'),
        dict(n='S1 수', k='K1', t0=3.1, len=1.5, sp=1.2, day='수'),
        dict(n='S1 목', k='K1', t0=0.3, len=1.8, sp=1.5, day='목', cap='(불태운 월화수목)', cap_at=0.4),
        dict(n='S2 4:52', clock='(금) 오후 4:52', len=1.8),   # v3: 괄호 자막 뺌(사용자)
        dict(n='S3 척', k='K1', t0=1.0, len=2.8, sp=1.0, cap='(일하는 척 모드 ON)'),   # v2: 슬로 빼고 원래 속도
        dict(n='S4 키보드', still='O3', len=2.0, push=0.08, cap='(사실은 블루투스 키보드로)'),
        dict(n='S5a 몰래', k='K2', t0=0.0, len=2.2, cap='(미순이와 주말 작전 회의 중)'),
        dict(n='S5b 대화', chat=chat1, appear=[0.25, 1.25, 2.4, 3.4], len=4.6),
        dict(n='S6 5:38', clock='(금) 오후 5:38', len=1.6, cap='(퇴근 22분 전)'),
        dict(n='S7 속마음', still='O4', len=3.4, eye=True),
        dict(n='S8a 꿈', dclip='D1', t0=6.8, len=3.2, cap='(주말을 향한 몽상)'),
        dict(n='S8b 꿈 원샷', dclip='D2', t0=0.6, len=2.6, cap='(주말을 향한 몽상)'),
        dict(n='S9 5:39', clock='(금) 오후 5:39', len=1.3),
        dict(n='S10 알림', toast=True, len=2.8, cap='(띠링)'),
        dict(n='S11 끄아', still='O5', len=2.4, scream=True),
        dict(n='S12 엔딩', chat=chat2, appear=[-1, -1, -1, -1, 0.3, 2.0], len=4.6, cap='(금요일 오후 5시 39분이란)', cap_at=3.0),
    ]
    t = 0.0
    for s in segs:
        s['at'] = round(t, 3); t += s['len']
    total = round(t, 3); S = {s['n'].split()[0] + ('' if s['n'].split()[0] not in ('S1', 'S8a', 'S8b', 'S5a', 'S5b') else s['n'].split()[1]): s for s in segs}
    S = {s['n']: s for s in segs}

    # 소리
    pl, sfx, subs = [], [], []
    TAPS, _ = taps(os.path.join(EP, 'clips/' + K1F), KEY_REGION); TAPS2, _ = taps(os.path.join(EP, 'clips/' + K2F), KEY_REGION)
    print('두드림', len(TAPS), [round(x, 2) for x in TAPS][:12], '/', len(TAPS2))
    s7 = S['S7 속마음']; at7 = s7['at'] + 0.35
    pl.append({'file': L['7']['file'], 'at': round(at7, 3)})
    words = ['(제발...)', '(제발... 조용히...)', '(제발... 조용히... 넘어가자....)']
    for i, w in enumerate(words):
        subs.append(dict(text=w, sp='changsu', t0=at7 + W7[i], t1=(at7 + W7[i + 1]) if i < 2 else s7['at'] + s7['len']))
    s11 = S['S11 끄아']; pl.append({'file': L['11']['file'], 'at': round(s11['at'] + 0.25, 3)})

    def fx(name, file, at, ln, lufs, **k):
        sfx.append(dict(name=name, file=file, at=round(at, 3), len=ln, target_lufs=lufs, **k))
    el = 'outputs/ep16/sfx/el/'
    fx('office_amb', el + 'office_amb.mp3', 0, S['S8a 꿈']['at'], -38, loop=True, fade_in=0.3, fade_out=0.3)
    fx('office_amb2', el + 'office_amb.mp3', S['S9 5:39']['at'], total - S['S9 5:39']['at'], -38, loop=True, fade_out=0.6)
    for k in ('S1 월', 'S1 화', 'S1 수', 'S1 목'):
        sg = S[k]
        for j, tp in enumerate(TAPS):
            ot = (tp - sg['t0']) / sg.get('sp', 1.0)
            if 0 <= ot < sg['len']:
                fx(f'key_{k}_{j}', el + 'key_click.mp3', sg['at'] + ot, 0.3, -24 + 1.5 * ('월화수목'.index(k[-1])))
        fx('pop_' + k, 'outputs/ep05/sfx/el/ui_pop.mp3', S[k]['at'], 0.4, -26)
    for k in ('S2 4:52', 'S6 5:38', 'S9 5:39'):
        fx('whoosh_' + k, 'outputs/ep11/sfx/el/whoosh_soft.mp3', S[k]['at'] - 0.12, 0.8, -24)
        fx('tick_' + k, el + 'clock_tick.mp3', S[k]['at'] + 0.05, 1.0, -18)
    for k, tl, lu in (('S3 척', TAPS, -30), ('S5a 몰래', TAPS2, -30)):
        sg = S[k]
        for j, tp in enumerate(tl):
            ot = (tp - sg['t0']) / sg.get('sp', 1.0)
            if 0 <= ot < sg['len']:
                fx(f'key_{k}_{j}', el + 'key_click.mp3', sg['at'] + ot, 0.3, lu)
    for i, x in enumerate(S['S5b 대화']['appear']):
        fx(f'msg_{i}', el + 'msg_ping.mp3', S['S5b 대화']['at'] + x, 0.5, -22)
    fx('dream_in', el + 'dream_whoosh.mp3', S['S8a 꿈']['at'] - 0.3, 1.5, -24)
    fx('dream_music', 'outputs/ep16/bgm/dream.mp3', S['S8a 꿈']['at'], S['S9 5:39']['at'] - S['S8a 꿈']['at'], -24, fade_in=0.4, fade_out=0.15)
    fx('scratch', 'outputs/ep11/sfx/el/record_scratch.mp3', S['S9 5:39']['at'] - 0.05, 0.8, -18)
    st = S['S10 알림']; TZ = [0.35, 0.95, 1.4, 1.8]   # 알림 뜸, 확대 1·2·3
    fx('work_ping', el + 'work_ping.mp3', st['at'] + TZ[0], 0.8, -18)
    for i, z in enumerate(TZ[1:]):
        fx(f'vib_{i}', el + 'phone_vibrate.mp3', st['at'] + z, 0.6, -20 + 2 * i)
        fx(f'hit_{i}', 'outputs/ep09/sfx/el/dramatic_hit.mp3', st['at'] + z, 0.9, -24 + 3 * i, fade_out=0.3)
    fx('hit_scream', 'outputs/ep09/sfx/el/dramatic_hit.mp3', s11['at'], 0.9, -17, fade_out=0.3)
    for i, x in enumerate(S['S12 엔딩']['appear']):
        if x >= 0:
            fx(f'msg_end{i}', el + 'msg_ping.mp3', S['S12 엔딩']['at'] + x, 0.5, -22)
    E['placements'] = pl
    E['bgm'] = {'file': 'outputs/ep16/bgm/friday_calm.mp3', 'target_lufs': -28, 'duck_db': 6, 'fade_in': 0.5, 'end_at': round(S['S8a 꿈']['at'] - 0.2, 2), 'fade_out': 0.6}
    E['edit'] = {'tag': a.tag, 'total': total, 'segments': [{k: v for k, v in s.items() if k not in ('chat', 'appear')} for s in segs]}
    json.dump(P, open(os.path.join(ROOT, 'outputs/voice_profile.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump({'note': f'ep16 {a.tag} (tools/ep16_edit.py)', 'items': sfx}, open(os.path.join(EP, 'sfx/sfx_list.json'), 'w'), ensure_ascii=False, indent=1)

    # 글씨
    title = text_img(TITLE, 100, stroke=0); chan = text_img([[('지독한 미순', 'white')]], 56, weight=800, stroke=0)
    cache = {}

    def txt(key, fn):
        if key not in cache:
            cache[key] = fn()
        return cache[key]
    nf = int(round(total * FPS)); os.makedirs(os.path.join(EP, 'roughcut'), exist_ok=True)
    out = os.path.join(EP, f'roughcut/ep16_{a.tag}_silent.mp4')
    pr = subprocess.Popen([FF, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    canvas0 = np.zeros((H, W, 3), np.uint8); put(canvas0, title, W / 2, 330); put(canvas0, chan, W / 2, WY + WH + 90)
    clips = {'K1': K1, 'K2': K2, 'D1': D1, 'D2': D2}
    for s in segs:
        n0, n1 = int(round(s['at'] * FPS)), int(round((s['at'] + s['len']) * FPS))
        for fi in range(n0, min(n1, nf)):
            tt = fi / FPS; lt = tt - s['at']; shake = (0, 0)
            if s.get('k'):
                win = clips[s['k']].at(s['t0'] + lt * s.get('sp', 1.0))
            elif s.get('dclip'):
                win = dream(clips[s['dclip']].at(s['t0'] + lt), k=min(1.0, 0.4 + lt / 0.4))
            elif s.get('clock'):   # v3: 원래(v1) 시계 스타일로(사용자: 괄호 자막 빼면 원래 스타일이 괜찮음). 노랑 큰 글씨(v2, clock_text)는 안 씀
                win = txt(('clockbg', 0), lambda: clock_card('')).copy()
                put(win, txt(('clock1', s['clock']), lambda: text_img([[(s['clock'], 'white')]], 120, weight=300, stroke=0)), WW / 2, WH / 2 - 30)
            elif s.get('chat'):
                win = chat_panel(s['chat'], lt, s['appear'])
            elif s.get('eye'):   # 속마음: 단어마다 오른쪽 눈으로 한 단계씩
                lv = sum(1 for w in W7 if lt >= 0.35 + w); steps = [1.0, 1.7, 3.0, 5.2]
                sc = steps[lv] if lv == 0 else steps[lv - 1] + (steps[lv] - steps[lv - 1]) * ease((lt - 0.35 - W7[lv - 1]) / 0.16)
                cx = 1200 + (EYE[0] - 1200) * min(1, (sc - 1) / 2); cy = 896 + (EYE[1] - 896) * min(1, (sc - 1) / 2)
                win = crop_win(img['O4'], sc, cx, cy)
                if lv and lt - 0.35 - W7[lv - 1] < 0.12:
                    shake = ([8, -6, 4][min(int((lt - 0.35 - W7[lv - 1]) * FPS), 2)], 0)
            elif s.get('toast'):   # 모니터 + 알림: 뜸 → 3단계 확대 + 진동
                base = img['O6'].copy(); ta = ease((lt - TZ[0]) / 0.2) if lt >= TZ[0] else 0
                if ta > 0:
                    tw = int(330 * (0.9 + 0.1 * ta)); ti = cv2.resize(toast, (tw, int(tw * toast.shape[0] / toast.shape[1])), interpolation=cv2.INTER_AREA)
                    put(base, ti, TOAST_SRC[0] + (1 - ta) * 40, TOAST_SRC[1], alpha=ta)
                lv = sum(1 for z in TZ[1:] if lt >= z); steps = [1.0, 1.7, 2.4, 3.1]   # 마지막에도 알림 전체가 보이게
                sc = steps[lv] if lv == 0 else steps[lv - 1] + (steps[lv] - steps[lv - 1]) * ease((lt - TZ[lv]) / 0.1)
                k_ = min(1, (sc - 1) / 1.5); win = crop_win(base, sc, 600 + (TOAST_SRC[0] - 600) * k_, 448 + (TOAST_SRC[1] - 448) * k_)
                if lv and lt - TZ[lv] < 0.35:   # 진동: 빠르게 좌우 떨림
                    j = int((lt - TZ[lv]) * FPS); shake = ([14, -14, 11, -11, 8, -8, 5, -5, 2][min(j, 8)] * (0.7 + 0.3 * lv), 0)
            elif s.get('scream'):
                sc = 1.6 + 1.2 * ease(lt / 0.25); win = crop_win(img['O5'], sc, 1215, 1050)
                if lt < 1.6:
                    j = int(lt * FPS); shake = (12 * np.sin(j * 2.3), 8 * np.cos(j * 3.1))
                red = np.zeros_like(win); red[:] = (40, 40, 220)
                yy, xx = np.mgrid[0:WH, 0:WW]; v = np.clip((np.sqrt(((xx - WW / 2) / (WW / 2)) ** 2 + ((yy - WH / 2) / (WH / 2)) ** 2) - 0.6) / 0.6, 0, 1)[..., None] * 0.55
                win = (win * (1 - v) + red * v).astype(np.uint8)
            else:
                push = 1.0 + s.get('push', 0) * lt / s['len']; win = crop_win(img[s['still']], push)
            if shake != (0, 0):
                win = cv2.warpAffine(win, np.float32([[1, 0, shake[0]], [0, 1, shake[1]]]), (WW, WH), borderMode=cv2.BORDER_REPLICATE)
            # 창 안 글씨
            if s.get('day'):
                put(win, txt(('day', s['day']), lambda: chip_img(s['day'], 84)), WW / 2, 110, alpha=ease(lt / 0.08), scale=1.0 + 0.3 * (1 - ease(lt / 0.12)))
            if s.get('cap') and lt >= s.get('cap_at', 0):
                cimg = txt(('cap', s['cap']), lambda: text_img([[(s['cap'], 'white')]], 46, weight=700, stroke=6))
                put(win, cimg, WW / 2, WH - 60, alpha=ease((lt - s.get('cap_at', 0)) / 0.15))
            for sb in subs:
                if sb['t0'] <= tt < sb['t1']:
                    put(win, txt(('sub', sb['text']), lambda: text_img([[(sb['text'], sb['sp'])]], 52, stroke=7)), WW / 2, WH - 60)
            if s.get('scream') and lt >= 0.25:
                put(win, txt('scream', lambda: text_img([[('끄아아아아아아!!!', 'changsu')]], 96, stroke=10)), WW / 2 + shake[0], WH - 90, scale=1.0 + 0.15 * (1 - ease((lt - 0.25) / 0.2)))
            fr = canvas0.copy(); fr[WY:WY + WH] = win
            if tt > total - 0.4:
                fr = (fr * max(0, (total - tt) / 0.4)).astype(np.uint8)
            pr.stdin.write(fr.tobytes())
    pr.stdin.close(); pr.wait()
    print(f'{len(segs)}장면 {total:.2f}s → {os.path.relpath(out, ROOT)}')
    for s in segs:
        print(f"  {s['at']:6.2f}s {s['len']:4.1f}s {s['n']}")


if __name__ == '__main__':
    main()
