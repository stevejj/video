#!/usr/bin/env python3
"""ep17 미순이의 감정 변화속도 편집(0원). 참고 릴스 Ddm8_Phv9zq처럼 세로 꽉 찬 고정 화면 + 위 제목 + 가운데 아래 대사 자막.
사용: python3 tools/ep17_edit.py [--tag v1] → outputs/ep17/roughcut/ep17_<tag>_silent.mp4 + voice_profile ep17 placements·bgm + sfx/sfx_list.json
     python3 tools/mix_audio.py --ep ep17 --video outputs/ep17/roughcut/ep17_<tag>_silent.mp4 --out outputs/ep17/roughcut/ep17_<tag>.mp4
- 장면 = 대사 한 줄(또는 두 줄). 그림 E1 달달 / E2 버럭 / E3 쉰내 / E5 엔딩, 3·5번은 Kling K3·K5.
- 달달: 분홍빛 + 하트가 피어오름 + 귀여운 배경음. 버럭: 배경음 뚝(dips) + 쿵 + 화면 톡 확대·흔들림 + 차가운 색.
- 말하는 쪽은 목소리 크기에 맞춰 그쪽으로 아주 살짝 통통(부리 움직임 대신, 사용자 2026-10-23).
"""
import argparse, json, os, subprocess, sys
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ep14_edit import text_img, ease
import imageio_ffmpeg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, 'outputs/ep17'); FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 24
TITLE = [[('POV', 'white')], [('미순이의 감정 변화속도', 'yellow')]]
SUB_Y = 1590
SPK_X = {'misun': 0.66, 'changsu': 0.35}   # 그림 폭 비율, 말하는 쪽 중심
FACE_Y = 0.50                              # 두 얼굴 높이(그림 높이 비율)
BASE = (1.25, 0.5, 0.56)                   # 기본 화면: 두 펭귄이 작게 보여서 1.25배, 조금 아래 중심(v1)
# 그림마다 펭귄 크기가 달라 컷이 튐 → 그림별 기본 화면(배수, 중심 x, 중심 y)으로 E1 크기에 맞춤(v1 검수)
FRAME = {'E1': (1.25, 0.5, 0.56), 'E2': (1.56, 0.52, 0.55), 'E3': (1.45, 0.52, 0.55), 'E5': (1.25, 0.5, 0.56), 'K3': (1.2, 0.5, 0.56), 'K5': (1.12, 0.5, 0.56)}
K3F, K5F = 'K3_v1.mp4', 'K5_v1_fix.mp4'   # K5: 1.5s 뒤 미순 반대쪽 날개 끝이 남색으로 보여 지움(0원)
CLIP_T0 = {'K3': 1.3, 'K5': 1.8}           # 16칸 검수: K3 1.3s부터 머리 기댐(앞은 눈 동그래짐), K5 1.0~1.3s 날개 남색 → 1.8s부터

# 장면: (이름, 그림/클립, 감정, 대사 컷들, 확대 목표)
BEATS = [
    ('1 편안', 'E1', 'sweet', ['m1', 'c1'], None),
    ('2 핸드폰만', 'E2', 'cold', ['m2'], None),
    ('3 못살아', 'K3', 'sweet', ['m3'], None),
    ('4 쉰내', 'E3', 'cold', ['m4'], None),
    ('5 귀여워', 'K5', 'sweet', ['m5'], None),
    ('6 못알아들어', 'E2', 'cold', ['m6'], None),
    ('7 여보', 'E1', 'sweet', ['m7', 'c7'], 'misun'),
    ('8 입이뚫렸는데', 'E2', 'cold', ['m8'], 'misun'),
    ('9 잘못했어', 'E5', 'none', ['c9'], 'changsu'),
    ('10 귀여워', 'E1', 'sweet', ['m10'], None),
]


def put(fr, rgba, cx, cy, alpha=1.0, scale=1.0):
    if scale != 1.0:
        rgba = cv2.resize(rgba, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    h, w = rgba.shape[:2]; x0, y0 = int(cx - w / 2), int(cy - h / 2)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if xa >= xb or ya >= yb:
        return
    s = rgba[ya - y0:yb - y0, xa - x0:xb - x0]; a = s[..., 3:4].astype(np.float32) / 255 * alpha
    fr[ya:yb, xa:xb] = (fr[ya:yb, xa:xb] * (1 - a) + s[..., 2::-1] * a).astype(np.uint8)


def view(img, s=1.0, fx=0.5, fy=0.5):
    """그림을 1080x1920으로, s배 확대, (fx, fy)=확대 중심(비율)."""
    h, w = img.shape[:2]; cw, ch = w / s, h / s
    x0 = min(max(fx * w - cw / 2, 0), w - cw); y0 = min(max(fy * h - ch / 2, 0), h - ch)
    M = np.float32([[W / cw, 0, -x0 * W / cw], [0, H / ch, -y0 * H / ch]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC)


def env(path):
    """목소리 크기(0~1) 프레임별."""
    d = subprocess.run([FF, '-loglevel', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'], capture_output=True).stdout
    x = np.frombuffer(d, np.float32); hop = 16000 // FPS
    r = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x), hop)])
    return np.clip(r / (np.percentile(r, 95) + 1e-6), 0, 1)


def heart_img(size, col=(255, 120, 170)):
    im = np.zeros((size, size, 4), np.uint8); t = np.linspace(0, 2 * np.pi, 200)
    x = 16 * np.sin(t) ** 3; y = -(13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t))
    pts = np.stack([(x / 34 + 0.5) * size, (y / 34 + 0.52) * size], 1).astype(np.int32)
    cv2.fillPoly(im, [pts], (col[2], col[1], col[0], 235), cv2.LINE_AA)
    return im[..., [2, 1, 0, 3]]


def tone(fr, mood, k):
    f = fr.astype(np.float32)
    if mood == 'sweet':   # 분홍빛 + 살짝 뽀얗게
        f = f * (1 - 0.12 * k) + np.array([215, 190, 255], np.float32) * 0.12 * k
    elif mood == 'cold':  # 채도 낮추고 푸르게
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY).astype(np.float32)[..., None]
        f = f * (1 - 0.45 * k) + g * 0.45 * k; f = f * np.array([1.06, 1.0, 0.93]) - 6 * k
    return np.clip(f, 0, 255).astype(np.uint8)


class Clip:
    def __init__(self, path):
        cap = cv2.VideoCapture(path); self.fps = cap.get(cv2.CAP_PROP_FPS) or 24; self.fr = []
        while True:
            ok, f = cap.read()
            if not ok:
                break
            self.fr.append(f)

    def at(self, t):
        return self.fr[max(0, min(len(self.fr) - 1, int(round(t * self.fps))))]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--tag', default='v1'); a = ap.parse_args()
    P = json.load(open(os.path.join(ROOT, 'outputs/voice_profile.json'))); E = P['episodes']['ep17']; L = {l['cut']: l for l in E['lines']}
    img = {k: cv2.imread(os.path.join(EP, f'img/{k}_v1.png')) for k in ('E1', 'E2', 'E3', 'E5')}
    clips = {}
    for k, fn in (('K3', K3F), ('K5', K5F)):
        p = os.path.join(EP, 'clips/' + fn)
        clips[k] = Clip(p) if os.path.exists(p) else None
    # 시간표: 대사를 이어 붙이고 장면 사이 쉼
    GAP = {'sweet': 0.35, 'cold': 0.25, 'none': 0.6}
    t = 0.3; segs = []; pl = []; subs = []
    for name, src, mood, cuts, zoom in BEATS:
        s0 = t - 0.3 if not segs else segs[-1]['end']
        lines = []
        for c in cuts:
            l = L[c]; lines.append(dict(cut=c, at=round(t, 3), len=l['len'], sp=l['speaker'], text=l['subtitle'], file=l['file']))
            pl.append({'file': l['file'], 'at': round(t, 3)}); t += l['len'] + 0.25
        t += GAP[mood]
        segs.append(dict(n=name, src=src, mood=mood, lines=lines, zoom=zoom, at=round(s0, 3), end=round(t - 0.3, 3)))
    segs[-1]['end'] = round(segs[-1]['end'] + 1.2, 3)
    total = segs[-1]['end']
    for s in segs:
        s['len'] = round(s['end'] - s['at'], 3)
    envs = {ln['cut']: env(os.path.join(ROOT, ln['file'])) for s in segs for ln in s['lines']}

    # 소리
    sfx = []
    def fx(name, file, at, ln, lufs, **k):
        sfx.append(dict(name=name, file=file, at=round(at, 3), len=ln, target_lufs=lufs, **k))
    dips = []
    for s in segs:
        if s['mood'] == 'cold':
            fx('hit_' + s['n'], 'outputs/ep09/sfx/el/dramatic_hit.mp3', s['at'], 0.9, -20, fade_out=0.3)
            dips.append({'at': round(s['at'], 2), 'len': round(s['len'], 2), 'db': -40})
        elif s['mood'] == 'none':
            fx('scratch', 'outputs/ep11/sfx/el/record_scratch.mp3', s['at'] - 0.05, 0.8, -22)
            dips.append({'at': round(s['at'], 2), 'len': round(s['len'], 2), 'db': -40})
        else:
            fx('sparkle_' + s['n'], 'outputs/ep01/sfx/el/sparkle.mp3', s['at'], 1.0, -26)
    E['placements'] = pl
    E['bgm'] = {'file': 'outputs/ep17/bgm/sweet.mp3', 'target_lufs': -26, 'duck_db': 6, 'fade_in': 0.2, 'end_at': round(total, 2), 'fade_out': 0.6, 'dips': dips}
    E['edit'] = {'tag': a.tag, 'total': total, 'segments': [{k: v for k, v in s.items() if k != 'lines'} for s in segs]}
    json.dump(P, open(os.path.join(ROOT, 'outputs/voice_profile.json'), 'w'), ensure_ascii=False, indent=1)
    os.makedirs(os.path.join(EP, 'sfx'), exist_ok=True)
    json.dump({'note': f'ep17 {a.tag} (tools/ep17_edit.py)', 'items': sfx}, open(os.path.join(EP, 'sfx/sfx_list.json'), 'w'), ensure_ascii=False, indent=1)

    title = text_img(TITLE, 96, stroke=9); chan = text_img([[('지독한 미순', 'white')]], 50, weight=800, stroke=6)
    hearts = [heart_img(s) for s in (60, 80, 100)]
    rng = np.random.default_rng(4); HP = [(rng.uniform(0.08, 0.92), rng.uniform(0, 1), rng.integers(3), rng.uniform(0.6, 1.2)) for i in range(12)]   # 하트는 머리 위 띠(제목 아래~머리 위)에서만 — 얼굴 가리지 않게
    cache = {}
    nf = int(round(total * FPS)); os.makedirs(os.path.join(EP, 'roughcut'), exist_ok=True)
    out = os.path.join(EP, f'roughcut/ep17_{a.tag}_silent.mp4')
    pr = subprocess.Popen([FF, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for s in segs:
        n0, n1 = int(round(s['at'] * FPS)), int(round(s['end'] * FPS))
        for fi in range(n0, min(n1, nf)):
            tt = fi / FPS; lt = tt - s['at']
            if s['src'] in clips:
                c = clips[s['src']]; src = c.at(lt + CLIP_T0[s['src']]) if c is not None else img['E1']
            else:
                src = img[s['src']]
            # 말하는 쪽 + 목소리 크기
            spk, e = None, 0.0
            for ln in s['lines']:
                k = int((tt - ln['at']) * FPS)
                if 0 <= k < len(envs[ln['cut']]):
                    spk, e = ln['sp'], float(envs[ln['cut']][k])
            sc, fx_, fy_ = FRAME[s['src']]
            if s['mood'] == 'cold':   # 톡 확대(버럭 순간)
                sc = 1.0 + 0.1 * ease(lt / 0.08)
            if s['zoom']:
                zk = ease(min(1, lt / 0.5)); sc = sc + (0.35 if s['zoom'] == 'changsu' else 0.22) * zk
                fx_ = fx_ + (SPK_X[s['zoom']] - fx_) * zk; fy_ = FRAME[s['src']][2] + (FACE_Y - FRAME[s['src']][2]) * zk
            if spk and s['src'] not in clips:   # 통통: 말하는 쪽으로 아주 살짝
                sc += 0.018 * e; fx_ += (SPK_X[spk] - 0.5) * 0.06
            fr = view(src, sc, fx_, fy_)
            if s['mood'] == 'cold' and lt < 0.22:
                j = int(lt * FPS); fr = cv2.warpAffine(fr, np.float32([[1, 0, [16, -14, 10, -8, 5, -3][min(j, 5)]], [0, 1, 0]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
            fr = tone(fr, s['mood'], min(1.0, lt / 0.12))
            if s['mood'] == 'sweet':   # 하트가 아래에서 피어오름
                for hx, ph, hi, sp in HP:
                    u = (lt * 0.35 * sp + ph) % 1.0
                    put(fr, hearts[hi], hx * W + 30 * np.sin(u * 6 + ph * 9), H * (0.33 - 0.19 * u), alpha=min(1, u * 5) * (1 - u) * 0.85)
            put(fr, title, W / 2, 250); put(fr, chan, W / 2, 1820)
            for ln in s['lines']:
                if ln['at'] - 0.05 <= tt < (ln['at'] + ln['len'] + 0.35 if ln is not s['lines'][-1] else s['end']):
                    key = ('sub', ln['cut'])
                    if key not in cache:
                        parts = [x.strip() + ('?' if i < ln['text'].count('? ') else '') for i, x in enumerate(ln['text'].split('? '))]   # 물음표 두 문장은 두 줄
                        cache[key] = text_img([[(x, ln['sp'])] for x in parts], 64, stroke=8, maxw=1000)
                    pop = 1.0 + 0.12 * (1 - ease((tt - ln['at'] + 0.05) / 0.12))
                    put(fr, cache[key], W / 2, SUB_Y, scale=pop)
            if tt > total - 0.4:
                fr = (fr * max(0, (total - tt) / 0.4)).astype(np.uint8)
            pr.stdin.write(fr.tobytes())
    pr.stdin.close(); pr.wait()
    print(f'{len(segs)}장면 {total:.2f}s → {os.path.relpath(out, ROOT)}')
    for s in segs:
        print(f"  {s['at']:6.2f}s {s['len']:4.1f}s {s['mood']:5s} {s['n']}")


if __name__ == '__main__':
    main()
