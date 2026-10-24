#!/usr/bin/env python3
"""ep18 입을 옷이 없다는 아내 — 1차 편집(0원, Kling 1클립만).
사용: python3 tools/ep18_edit.py [--tag v1] → outputs/ep18/roughcut/ep18_<tag>_silent.mp4 + voice_profile ep18.placements·bgm + sfx/sfx_list.json
     python3 tools/mix_audio.py --ep ep18 --video outputs/ep18/roughcut/ep18_<tag>_silent.mp4 --out outputs/ep18/roughcut/ep18_<tag>_main.mp4
     python3 tools/thumb_intro.py --video ..._main.mp4 --out outputs/ep18/roughcut/ep18_<tag>.mp4 --title '[[["입을 옷이 없다는","yellow"]],[["아내","white"]]]' --bg black
- v6(사용자): 캐릭터·배경을 오려 움직이지 않음(몸·머리 통통, 이불 덜덜, 날개 만지작 모두 뺌 — 지운 자국이 보여서).
  움직임은 카메라로만: 밀어 들어가기, 말하는 쪽으로 옮기기, 확대 펀치, 흔들림. 마지막 동공지진(눈 둘레만 약하게)은 유지.
- 2번 옷 산사태만 Kling(K1). 4번 얼굴은 옷 더미 → 얼굴 나온 화면으로 바뀌며 확대 펀치.
- 상황 자막은 유리 알림창(02a). 제목 위쪽, 채널명 하단 1600(휴대폰 장면은 뺌).
"""
import argparse, json, os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import talk_bob
from ep14_edit import text_img, chip_img, put, ease, font, W, H, FPS, FF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, 'outputs/ep18')
K = W / 768
TITLE = [[('입을 옷이 없다는', 'yellow')], [('아내', 'white')]]
CHAN_Y = 1600


def big(name):
    im = cv2.imread(os.path.join(EP, 'img', name + '.png'))
    return cv2.resize(im, (W, int(im.shape[0] * W / im.shape[1])), interpolation=cv2.INTER_LANCZOS4)


def cam(img, z, cx, cy):
    """img(1080 x ~1935)에서 z배 확대, (cx, cy) 중심으로 잘라 1080x1920."""
    ch, cw = H / z, W / z
    x0 = min(max(cx - cw / 2, 0), img.shape[1] - cw); y0 = min(max(cy - ch / 2, 0), img.shape[0] - ch)
    M = np.float32([[z, 0, -x0 * z], [0, z, -y0 * z]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def dust(fr, t, cx, cy, n=26, seed=5):
    """옷이 쏟아진 뒤 먼지 구름: 더미 표면에 뭉게뭉게 덩어리가 피어올라 덮고, '뽁' 뒤에 걷힘. t = 시작 뒤 초, (cx, cy) = 더미 꼭대기."""
    if t < 0 or t > 2.4:
        return fr
    rng = np.random.default_rng(seed); ov = np.zeros(fr.shape[:2], np.float32)
    grow = 0.55 + 0.45 * ease(t / 0.6)
    for i in range(n):
        u = rng.uniform(0, 1); side = rng.uniform(-1, 1)
        x = cx + side * (60 + 330 * u); y = cy + 40 + 560 * u * abs(side) * 0.8 + rng.uniform(-40, 60) - 45 * t   # 더미 비탈을 따라
        r = rng.uniform(55, 115) * grow
        cv2.circle(ov, (int(x), int(y)), int(r), 1.0, -1, cv2.LINE_AA)
    ov = cv2.GaussianBlur(ov, (0, 0), 16)
    a = np.clip(ov * 1.2, 0, 1) * 0.45 * (1 - ease((t - 1.6) / 0.8))   # v9(사용자): 더 옅게
    shade = 0.9 + 0.1 * cv2.GaussianBlur(ov, (0, 0), 40)          # 가운데가 조금 밝게(입체감)
    col = np.array([222, 230, 238], np.float32)[None, None] * np.clip(shade, 0, 1.05)[..., None]
    return (fr * (1 - a[..., None]) + col * a[..., None]).astype(np.uint8)


class Clip:
    def __init__(self, path, t0=0.0, sp=1.0):
        cap = cv2.VideoCapture(path); self.fps = cap.get(cv2.CAP_PROP_FPS); self.fr = []
        while True:
            ok, f = cap.read()
            if not ok:
                break
            self.fr.append(cv2.resize(f, (W, H), interpolation=cv2.INTER_CUBIC))
        self.t0, self.sp = t0, sp

    def at(self, lt):
        i = int(round((self.t0 + lt * self.sp) * self.fps))
        return self.fr[max(0, min(len(self.fr) - 1, i))].copy()


def phone_cart(n):
    """12번 반전: 휴대폰 쇼핑앱 장바구니 — 패딩 5벌이 톡톡 담겨 있고 총액이 쿵."""
    items = [('롱패딩 (핑크)', '289,000원', (255, 182, 206)), ('숏패딩 (아이보리)', '239,000원', (246, 238, 222)),
             ('경량패딩', '129,000원', (198, 216, 238)), ('패딩 조끼 (민트)', '99,000원', (196, 236, 222)), ('롱패딩 (블랙)', '319,000원', (90, 90, 96))]
    base = Image.new('RGB', (W, H), (250, 247, 249)); d = ImageDraw.Draw(base)
    d.rectangle([0, 0, W, 610], fill=(255, 236, 243))
    d.text((W / 2, 560), '장바구니 (5)', font=font(60, 800), fill='#5A4A52', anchor='mm')
    card_imgs = []
    for name, price, col in items:
        c = Image.new('RGBA', (960, 160), (0, 0, 0, 0)); cd = ImageDraw.Draw(c)
        cd.rounded_rectangle([0, 0, 959, 159], radius=32, fill=(255, 255, 255, 255), outline=(236, 226, 232), width=3)
        cd.rounded_rectangle([24, 18, 148, 142], radius=22, fill=col)
        cd.polygon([(86, 34), (124, 56), (114, 128), (58, 128), (48, 56)], fill=tuple(max(0, v - 25) for v in col))   # 패딩 모양 단순 그림
        cd.text((180, 48), name, font=font(44, 700), fill='#333333')
        cd.text((180, 112), price, font=font(40, 800), fill='#FF5C9A')
        cd.rounded_rectangle([860, 55, 910, 105], radius=10, fill='#FF9CC2'); cd.text((885, 80), '✓', font=font(34, 800), fill='white', anchor='mm')
        card_imgs.append(np.array(c))
    total = text_img([[('총 ', 'white'), ('1,075,000원', 'yellow')]], 88, stroke=9)   # v11(사용자: 밑에 잘림) 작게
    base = cv2.cvtColor(np.array(base), cv2.COLOR_RGB2BGR)
    out = []
    for i in range(n):
        t = i / FPS; fr = base.copy()
        for j, c in enumerate(card_imgs):
            tj = 0.1 + j * 0.16
            if t >= tj:
                a = ease((t - tj) / 0.14); put(fr, c, W / 2, 720 + j * 178 + (1 - a) * 40, alpha=a)
        if t >= 1.15:
            a = ease((t - 1.15) / 0.2); put(fr, total, W / 2, 1585, alpha=a, scale=0.7 + 0.3 * a + 0.08 * (1 - a))
        out.append(fr)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--tag', default='v1'); a = ap.parse_args()
    P = json.load(open(os.path.join(ROOT, 'outputs/voice_profile.json'))); E = P['episodes']['ep18']; L = {l['cut']: l for l in E['lines']}
    LN = lambda c: os.path.join(ROOT, L[c]['file'])
    # C9는 이불 속이라 먹먹하게(0원 필터)
    muf = os.path.join(EP, 'voice/lines/C9_muffled.mp3')
    if not os.path.exists(muf):
        subprocess.run([FF, '-y', '-v', 'error', '-i', LN('C9'), '-af', 'lowpass=f=1500,volume=1.6', muf], check=True)

    segs = [
        dict(n='S1 옷장 앞', len=4.0),
        dict(n='S2 손잡이', len=1.65),
        dict(n='S3 산사태', len=3.0),
        dict(n='S4a 얼굴 쑥', len=3.0),
        dict(n='S4b 작년 거', len=2.6),
        dict(n='S5 정리해 봐', len=2.3),
        dict(n='S6 버리고', len=2.0),
        dict(n='S7 아까운데', len=2.6),
        dict(n='S8 1시간 뒤', len=3.2, chip=('1시간 뒤', 0.0, 0.95)),
        dict(n='S9 미워', len=2.3),
        dict(n='S10 달래기', len=4.5),
        dict(n='S11 정말', len=1.9),
        dict(n='S12 담아놨지롱', len=2.2),
        dict(n='S12b 장바구니', len=2.3, phone=True),
        dict(n='S13 동공지진', len=2.8),
    ]
    t = 0.0
    for s in segs:
        s['at'] = round(t, 3); t += s['len']
    total = round(t, 3); S = {s['n'].split()[0]: s for s in segs}

    # 대사(장면 안 시각)
    VO = [('S1', 'C1a', 0.3, 'changsu'), ('S1', 'C1b', 1.95, 'misun'), ('S2', 'C2', 0.12, 'changsu'), ('S4a', 'C4a', 1.15, 'changsu'),
          ('S4b', 'C4b', 0.15, 'misun'), ('S5', 'C5', 0.15, 'changsu'), ('S6', 'C6', 0.15, 'misun'), ('S7', 'C7', 0.35, 'misun'),
          ('S8', 'C8', 0.95, 'changsu'), ('S9', 'C9', 0.35, 'misun'), ('S10', 'C10a', 0.25, 'changsu'), ('S10', 'C10b', 2.75, 'changsu'),
          ('S11', 'C11', 0.3, 'misun'), ('S12', 'C12', 0.2, 'misun')]
    pl, subs = [], []
    for sk, cut, lt, sp in VO:
        at = S[sk]['at'] + lt; f = L[cut]['file'] if cut != 'C9' else os.path.relpath(muf, ROOT)
        pl.append({'file': f, 'at': round(at, 3)})
        subs.append(dict(text=L[cut]['subtitle'], sp=sp, t0=at, t1=at + L[cut]['len'] + 0.25))
    # S2 대사가 S3(산사태)까지 이어지면 자막도 그대로
    sfx = []

    def fx(name, file, at, ln, lufs, **k):
        sfx.append(dict(name=name, file=file, at=round(at, 3), len=ln, target_lufs=lufs, **k))
    el = 'outputs/ep18/sfx/el/'
    fx('door_rattle', el + 'door_rattle.mp3', S['S2']['at'] + 0.85, 0.8, -26)
    fx('avalanche', el + 'clothes_avalanche.mp3', S['S3']['at'] + 0.1, 2.0, -18, fade_out=0.3)
    fx('pop_up', el + 'pop_up.mp3', S['S4a']['at'] + 0.55, 0.6, -20)
    fx('whoosh_4b', el + 'whoosh.mp3', S['S4b']['at'] - 0.12, 0.5, -30)
    fx('thud', el + 'box_thud.mp3', S['S6']['at'] + 1.15, 0.6, -20)
    fx('sparkle_7', el + 'sparkle.mp3', S['S7']['at'] + 1.1, 0.8, -30)
    fx('whoosh_8', el + 'whoosh.mp3', S['S8']['at'] - 0.1, 0.5, -28)
    fx('rustle_9', el + 'blanket_rustle.mp3', S['S9']['at'] + 0.05, 1.5, -24, fade_out=0.3)
    fx('poke_1', el + 'poke.mp3', S['S10']['at'] + 0.15, 0.5, -24)
    fx('rustle_10', el + 'blanket_rustle.mp3', S['S10']['at'] + 0.5, 1.5, -28, fade_out=0.3)
    fx('poke_2', el + 'poke.mp3', S['S10']['at'] + 1.6, 0.5, -26)
    fx('sparkle_11', el + 'sparkle.mp3', S['S11']['at'] + 0.12, 0.8, -22)
    fx('whoosh_12b', el + 'whoosh.mp3', S['S12b']['at'] - 0.1, 0.5, -26)
    for j in range(5):
        fx(f'ding_{j}', el + 'phone_ding.mp3', S['S12b']['at'] + 0.1 + j * 0.16, 0.5, -26)
    fx('vibrate', el + 'phone_vibrate.mp3', S['S13']['at'] + 0.1, 1.5, -22, fade_out=0.3)
    fx('shock', el + 'shock_hit.mp3', S['S13']['at'] + 0.05, 1.2, -19, fade_out=0.3)

    E['placements'] = pl
    E['bgm'] = {'file': 'outputs/ep18/bgm/cozy_comedy.mp3', 'target_lufs': -28, 'duck_db': 6, 'fade_in': 0.4, 'end_at': total, 'fade_out': 1.0,
                'dips': [{'at': round(S['S3']['at'], 2), 'len': 2.4, 'db': -8}, {'at': round(S['S13']['at'], 2), 'len': S['S13']['len'] + 0.1, 'db': -18}]}
    E['edit'] = {'tag': a.tag, 'total': total, 'segments': segs}
    json.dump(P, open(os.path.join(ROOT, 'outputs/voice_profile.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump({'note': f'ep18 {a.tag} (tools/ep18_edit.py가 만듦)', 'items': sfx}, open(os.path.join(EP, 'sfx/sfx_list.json'), 'w'), ensure_ascii=False, indent=1)

    # 장면 준비 — v6(사용자): 캐릭터·배경을 오려 움직이지 않음(지운 자국 안 나오게). 움직임은 카메라로만(밀기·옮기기·확대 펀치·흔들림).
    nfr = lambda sk: int(round(S[sk]['len'] * FPS)) + 2
    I = {k: big(v) for k, v in dict(F1='F1_v1', F2a='F2a_v1', F2b='F2b_fill', F4a='F4a_v1_fill', F4b='F4b_v2', F5='F5_v1', F6='F6_v1', F7='F7_v1',
                                     F8='F8_v1', B9='B9_v2', B10='B10_v1', B11='B11_v1', B12='B12_v1').items()}
    voice9 = talk_bob.envelope([('x', LN('C9'), 0.35)], 'x', nfr('S9'))      # 9번: 목소리 크기만큼 카메라가 들썩
    K1 = Clip(os.path.join(EP, 'K1/clip_v1.mp4'), t0=0.8, sp=1.4)
    # Kling 끝 프레임과 같은 구도의 날개 지운 더미(시작·끝 프레임처럼 위아래 7px 잘림)
    fix = big('F2b_fill')[7:7 + H]   # v10(사용자): 날개 지운 자리 위에 옷을 더 쌓아 가림

    def punch(lt, t0, z0, z1, d=0.12):
        return z0 if lt < t0 else z0 + (z1 - z0) * ease((lt - t0) / d)

    # B13 동공지진
    b13 = cv2.imread(os.path.join(EP, 'img/B13_v1.png')); s13 = W / b13.shape[1]
    lum = b13.mean(2); eyes = []
    for (x0, y0, x1, y1) in ((300, 1150, 640, 1500), (900, 1150, 1240, 1500)):
        reg = (lum[y0:y1, x0:x1] < 60).astype(np.uint8)
        n_, lab, st, _ = cv2.connectedComponentsWithStats(reg); i_ = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        m = (lab == i_).astype(np.uint8) * 255; m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
        cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); m[:] = 0; cv2.drawContours(m, cs, -1, 255, -1)
        m = cv2.dilate(m, np.ones((9, 9), np.uint8)); full = np.zeros(lum.shape, np.uint8); full[y0:y1, x0:x1] = m; eyes.append(full)
    eye_c = []
    for m in eyes:
        ys, xs = np.where(m > 0); eye_c.append((xs.mean(), ys.mean(), max(np.ptp(xs), np.ptp(ys)) / 2))

    title = text_img(TITLE, 92, stroke=10); chan = text_img([[('지독한 미순', 'white')]], 52, weight=700, stroke=6)
    chips, subc = {}, {}
    cart = phone_cart(nfr('S12b'))
    nf = int(round(total * FPS))
    os.makedirs(os.path.join(EP, 'roughcut'), exist_ok=True); out = os.path.join(EP, f'roughcut/ep18_{a.tag}_silent.mp4')
    pr = subprocess.Popen([FF, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    rng = np.random.default_rng(3)
    for s in segs:
        sk = s['n'].split()[0]; n0, n1 = int(round(s['at'] * FPS)), int(round((s['at'] + s['len']) * FPS))
        for fi in range(n0, min(n1, nf)):
            tt = fi / FPS; lt = tt - s['at']; k = fi - n0; shake = 0
            if sk == 'S1':                             # 말하는 쪽으로 카메라 옮김 → "없어!"에서 확대 펀치
                x = 220 + (432 - 220) * ease((lt - 1.75) / 0.35) if lt >= 1.75 else 220
                z = punch(lt, 3.15, 1.25 + 0.04 * lt / s['len'], 1.45)
                fr = cam(I['F1'], z, x * K, 935 * K)
            elif sk == 'S2':                           # 손잡이 쪽으로 밀어 들어감 + 문 덜컹 흔들림
                fr = cam(I['F2a'], 1.05 + 0.12 * ease(lt / s['len']), 330 * K, 820 * K)
                shake = 0 if lt < 0.85 else 3 + 7 * (lt - 0.85) / 0.8
            elif sk == 'S3':
                fr = K1.at(lt); shake = 22 * np.exp(-lt * 2.2) if lt < 1.6 else 0
                src_t = 0.8 + lt * 1.4
                if src_t > 3.9:                        # v7(사용자: 옷 더미 맨 위가 우글거림) Kling 끝부분은 날개 지운 더미 그림으로 화면 전체를 넘겨 멈춤
                    a_ = ease((src_t - 3.9) / 0.35)
                    fr = (fr * (1 - a_) + fix * a_).astype(np.uint8)
                fr = dust(fr, lt - 1.75, 383 * K, 690 * K - 7)
            elif sk == 'S4a':                          # 옷 더미 → 뽁! 얼굴 나온 화면으로 바뀌며 확대 펀치
                if lt < 0.55:
                    fr = cam(I['F2b'], 1.0 + 0.03 * lt, W / 2, 900 * K); shake = 2 if lt > 0.25 else 0
                    fr = dust(fr, lt + S['S3']['len'] - 1.75, 383 * K, 690 * K - 7)
                else:
                    z = punch(lt, 0.55, 1.0, 1.22, 0.1) + 0.06 * max(0, lt - 0.7) / 2.3
                    fr = cam(I['F4a'], z, 383 * K, 760 * K); shake = 9 * np.exp(-(lt - 0.55) * 12)
                    fr = dust(fr, lt + S['S3']['len'] - 1.75, W / 2, 1100)
            elif sk in ('S4b', 'S5', 'S6', 'S8'):
                img, cx, cy, z0 = {'S4b': ('F4b', 575, 960, 1.5), 'S5': ('F5', 585, 1000, 1.15), 'S6': ('F6', 540, 900, 1.15), 'S8': ('F8', 566, 960, 1.8)}[sk]   # v7: 4b 미순·8 창수 크게(v8 사용자: 창수 더 크게)
                z = z0 + 0.08 * ease(lt / s['len'])
                if sk == 'S6':                         # 툭: 카메라가 살짝 튐
                    z += 0.035 * np.exp(-(lt - 1.15) * 10) if lt >= 1.15 else 0
                if sk == 'S8':                         # 하…: 천천히 더 밀어 들어감
                    z = z0 + 0.25 * ease((lt - 0.95) / 1.6) if lt >= 0.95 else z0
                fr = cam(I[img], z, cx * K, cy * K)
            elif sk == 'S7':                           # 가디건 클로즈업: 천천히 밀며 날개 쪽으로
                fr = cam(I['F7'], 1.0 + 0.12 * ease(lt / s['len']), (384 + 120 * ease(lt / s['len'])) * K, 640 * K)
            elif sk == 'S9':                           # 이불 김밥: 말할 때 카메라가 들썩
                e = voice9[k]; shake = 1.5 + 7 * e
                fr = cam(I['B9'], 1.15 + 0.08 * ease(lt / s['len']), 395 * K, 690 * K)
            elif sk == 'S10':                          # 천천히 밀다가 "우리 패딩"의 '패딩'에서 이불 쪽으로 확대 펀치
                stop = 2.75 + 0.32
                z = punch(lt, stop, 1.1 + 0.05 * lt / s['len'], 1.35, 0.12)
                cx = 395 if lt < stop else 395 - 120 * ease((lt - stop) / 0.12)
                fr = cam(I['B10'], z, cx * K, 680 * K)
            elif sk == 'S11':                          # 정말?!: 미순 얼굴로 확대 펀치
                fr = cam(I['B11'], punch(lt, 0.12, 1.05, 1.45), 300 * K, 735 * K)
            elif sk == 'S12':
                fr = cam(I['B12'], 1.32 + 0.08 * ease(lt / s['len']), 385 * K, 590 * K)
            elif sk == 'S12b':
                fr = cart[k].copy()
            elif sk == 'S13':
                im = b13.copy()
                if 0.2 <= lt < 2.2:
                    jj = int((lt - 0.2) / 0.05); amp = 7 * (0.6 if jj % 3 == 0 else 1.0)
                    for j, (ex, ey, er) in enumerate(eye_c):
                        dx = (1 if j == 0 else -1) * amp * (1 if jj % 2 == 0 else -1); dy = amp * 0.3 * (1 if jj % 4 < 2 else -1)
                        R = int(er * 2.2); x0_, y0_ = int(ex - R), int(ey - R)
                        yy, xx = np.mgrid[0:2 * R, 0:2 * R].astype(np.float32)
                        g = np.exp(-((xx - R) ** 2 + (yy - R) ** 2) / (2 * (er * 1.05) ** 2)).astype(np.float32)
                        sub = im[y0_:y0_ + 2 * R, x0_:x0_ + 2 * R].copy()
                        im[y0_:y0_ + 2 * R, x0_:x0_ + 2 * R] = cv2.remap(sub, xx - dx * g, yy - dy * g, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
                im = cv2.resize(im, (W, int(im.shape[0] * s13)), interpolation=cv2.INTER_AREA)
                z = 1.0 if lt < 0.2 else (1.25 if lt < 0.9 else 1.6)
                if 0.2 <= lt < 0.32:
                    z = 1.0 + 0.25 * ease((lt - 0.2) / 0.12)
                elif 0.9 <= lt < 1.02:
                    z = 1.25 + 0.35 * ease((lt - 0.9) / 0.12)
                fr = cam(im, z, W / 2, 1320 * s13)
                shake = 3 if 0.2 <= lt < 2.2 else 0
            if shake > 0.5:
                fr = cv2.warpAffine(fr, np.float32([[1, 0, rng.uniform(-shake, shake)], [0, 1, rng.uniform(-shake, shake)]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
            for key in ('chip', 'chip2'):
                if s.get(key) and s[key][1] <= lt < s[key][2]:
                    txt, c0, c1 = s[key]
                    if txt not in chips:
                        chips[txt] = chip_img(txt, 66)
                    a_ = ease((lt - c0) / 0.15) * min(1, (c1 - lt) / 0.15)
                    put(fr, chips[txt], W / 2, 640, alpha=a_, scale=0.9 + 0.1 * ease((lt - c0) / 0.15))
            put(fr, title, W / 2, 360)
            if not s.get('phone'):
                put(fr, chan, W / 2, CHAN_Y)
            for sb in subs:
                if sb['t0'] <= tt < sb['t1']:
                    key = (sb['text'], sb['sp'])
                    if key not in subc:
                        subc[key] = text_img([[(sb['text'].replace('…', '...'), sb['sp'])]], 70, stroke=9)   # v12(사용자): 말줄임은 가운데 점(…) 말고 아래 점(...)
                    im_ = subc[key]; put(fr, im_, W / 2, H - 430 - im_.shape[0] / 2)
            if tt > total - 0.4:
                fr = (fr * max(0, (total - tt) / 0.4)).astype(np.uint8)
            pr.stdin.write(fr.tobytes())
    pr.stdin.close(); pr.wait()
    print(f'{len(segs)}장면 {total:.2f}s → {os.path.relpath(out, ROOT)}')


if __name__ == '__main__':
    main()
