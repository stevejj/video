#!/usr/bin/env python3
"""ep18 입을 옷이 없다는 아내 — 1차 편집(0원, Kling 1클립만).
사용: python3 tools/ep18_edit.py [--tag v1] → outputs/ep18/roughcut/ep18_<tag>_silent.mp4 + voice_profile ep18.placements·bgm + sfx/sfx_list.json
     python3 tools/mix_audio.py --ep ep18 --video outputs/ep18/roughcut/ep18_<tag>_silent.mp4 --out outputs/ep18/roughcut/ep18_<tag>_main.mp4
     python3 tools/thumb_intro.py --video ..._main.mp4 --out outputs/ep18/roughcut/ep18_<tag>.mp4 --title '[[["입을 옷이 없다는","yellow"]],[["아내","white"]]]' --bg black
- 정지 이미지는 캐릭터를 ISNet으로 오려(원래 자리는 메움) 목소리 크기에 맞춰 몸 통통(talk_bob 방식).
- 2번 옷 산사태만 Kling(K1). 4번 얼굴 쑥은 tools/ep18_popup.py 결과를 그대로 씀.
- 상황 자막은 유리 알림창(02a). 제목 위쪽, 채널명 하단 1600(휴대폰 장면은 뺌).
"""
import argparse, json, os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cutout, talk_bob
from ep14_edit import text_img, chip_img, put, ease, font, W, H, FPS, FF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, 'outputs/ep18')
K = W / 768
TITLE = [[('입을 옷이 없다는', 'yellow')], [('아내', 'white')]]
CHAN_Y = 1600
MODEL = talk_bob.MODEL


def big(name):
    im = cv2.imread(os.path.join(EP, 'img', name + '.png'))
    return cv2.resize(im, (W, int(im.shape[0] * W / im.shape[1])), interpolation=cv2.INTER_LANCZOS4)


def cam(img, z, cx, cy):
    """img(1080 x ~1935)에서 z배 확대, (cx, cy) 중심으로 잘라 1080x1920."""
    ch, cw = H / z, W / z
    x0 = min(max(cx - cw / 2, 0), img.shape[1] - cw); y0 = min(max(cy - ch / 2, 0), img.shape[0] - ch)
    M = np.float32([[z, 0, -x0 * z], [0, z, -y0 * z]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


class Puppet:
    """정지 이미지에서 오린 캐릭터 한 명(또는 이불 덩어리). 원본 좌표(768 기준) 상자."""
    def __init__(self, img, box, pad=40, lo=0.15, hi=0.85):
        x0, y0, x1, y1 = [int(v * K) for v in box]
        crop = Image.fromarray(cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_BGR2RGB))
        al = np.asarray(cutout.alpha(crop, MODEL)).astype(np.float32) / 255
        al = np.clip((al - lo) / (hi - lo), 0, 1)
        self.full = np.zeros(img.shape[:2], np.float32); self.full[y0:y1, x0:x1] = al
        X0, Y0 = max(0, x0 - pad), max(0, y0 - pad); X1, Y1 = min(img.shape[1], x1 + pad), min(img.shape[0], y1 + pad)
        self.off = (X0, Y0)
        self.rgba = np.dstack([img[Y0:Y1, X0:X1], (self.full[Y0:Y1, X0:X1] * 255).astype(np.uint8)])
        ys, xs = np.where(self.full > 0.5)
        self.foot = (xs.mean() - X0, ys.max() - Y0)
        self.center = (xs.mean(), (ys.min() + ys.max()) / 2)

    def without(self, other):
        """다른 캐릭터와 겹치는 부분은 빼기(이불이 떨 때 창수 날개까지 같이 떨리던 문제, v2)."""
        self.full *= np.clip(1 - other.full * 2.0, 0, 1)
        X0, Y0 = self.off; h, w = self.rgba.shape[:2]
        self.rgba[..., 3] = (self.full[Y0:Y0 + h, X0:X0 + w] * 255).astype(np.uint8)
        return self

    def draw(self, fr, sx=1.0, sy=1.0, ang=0.0, dx=0.0, dy=0.0, pivot=None):
        px, py = pivot if pivot else self.foot
        px, py = float(px), float(py)
        M = cv2.getRotationMatrix2D((px, py), float(ang), 1.0)
        M[0, :2] *= sx; M[1, :2] *= sy
        M[0, 2] = px - (M[0, 0] * px + M[0, 1] * py) + dx; M[1, 2] = py - (M[1, 0] * px + M[1, 1] * py) + dy
        h, w = self.rgba.shape[:2]
        warped = cv2.warpAffine(self.rgba, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        X0, Y0 = self.off; a = warped[..., 3:4].astype(np.float32) / 255
        reg = fr[Y0:Y0 + h, X0:X0 + w]
        reg[:] = (reg * (1 - a) + warped[..., :3] * a).astype(np.uint8)


def plate(img, puppets):
    m = np.zeros(img.shape[:2], np.uint8)
    for p in puppets:
        m |= (p.full > 0.05).astype(np.uint8)
    m = cv2.dilate(m, np.ones((15, 15), np.uint8))
    return cv2.inpaint(img, m * 255, 9, cv2.INPAINT_TELEA)


def bob(p, fr, e, t, j=0, k=1.0):
    br = 0.008 * np.sin(2 * np.pi * 0.45 * t + j * 1.7)
    p.draw(fr, 1 - 0.025 * e * k - br * 0.5, 1 + 0.05 * e * k + br, 1.6 * e * k * np.sin(2 * np.pi * 2.2 * t + j))


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
    total = text_img([[('총 ', 'white'), ('1,075,000원', 'yellow')]], 110, stroke=11)
    base = cv2.cvtColor(np.array(base), cv2.COLOR_RGB2BGR)
    out = []
    for i in range(n):
        t = i / FPS; fr = base.copy()
        for j, c in enumerate(card_imgs):
            tj = 0.1 + j * 0.16
            if t >= tj:
                a = ease((t - tj) / 0.14); put(fr, c, W / 2, 720 + j * 178 + (1 - a) * 40, alpha=a)
        if t >= 1.15:
            a = ease((t - 1.15) / 0.2); put(fr, total, W / 2, 1650, alpha=a, scale=0.7 + 0.3 * a + 0.08 * (1 - a))
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

    # 장면 준비
    def env_for(sk, cut_list, n):
        return talk_bob.envelope([('x', LN(c), lt) for c, lt in cut_list], 'x', n)
    nfr = lambda sk: int(round(S[sk]['len'] * FPS)) + 2
    I = {k: big(v) for k, v in dict(F1='F1_v1', F2a='F2a_v1', F4b='F4b_v2', F5='F5_v1', F6='F6_v1', F7='F7_v1', F8='F8_v1',
                                     B9='B9_v2', B10='B10_v1', B11='B11_v1', B12='B12_v1').items()}
    pp = {}
    pp['S1'] = [Puppet(I['F1'], (125, 740, 315, 1095)), Puppet(I['F1'], (330, 795, 535, 1095))]
    pp['S2'] = [Puppet(I['F2a'], (200, 735, 430, 1085))]
    pp['S4b'] = [Puppet(I['F4b'], (400, 690, 745, 1255))]
    pp['S5'] = [Puppet(I['F5'], (450, 790, 720, 1230))]
    pp['S6'] = [Puppet(I['F6'], (390, 690, 720, 1075))]
    pp['S7'] = [Puppet(I['F7'], (470, 410, 768, 760))]
    pp['S8'] = [Puppet(I['F8'], (430, 790, 710, 1230))]
    pp['S9'] = [Puppet(I['B9'], (215, 585, 575, 800))]
    pp['S10'] = [Puppet(I['B10'], (340, 400, 700, 830), lo=0.45, hi=0.75)]   # v3(사용자: 토닥 장면 창수 날개가 잘림) 상자를 왼쪽으로 넓혀 이불에 얹은 날개까지
    pp['S10'].append(Puppet(I['B10'], (100, 590, 455, 835)).without(pp['S10'][0]))
    pp['S12'] = [Puppet(I['B12'], (160, 290, 600, 900))]
    plates = {k: plate(I[img], pp[k]) for k, img in (('S1', 'F1'), ('S2', 'F2a'), ('S4b', 'F4b'), ('S5', 'F5'), ('S6', 'F6'), ('S7', 'F7'),
                                                       ('S8', 'F8'), ('S9', 'B9'), ('S10', 'B10'), ('S12', 'B12'))}
    env = {
        'S1': [env_for('S1', [('C1a', 0.3)], nfr('S1')), env_for('S1', [('C1b', 1.95)], nfr('S1'))],
        'S2': [env_for('S2', [('C2', 0.12)], nfr('S2'))], 'S4b': [env_for('S4b', [('C4b', 0.15)], nfr('S4b'))],
        'S5': [env_for('S5', [('C5', 0.15)], nfr('S5'))], 'S6': [env_for('S6', [('C6', 0.15)], nfr('S6'))],
        'S8': [env_for('S8', [('C8', 0.95)], nfr('S8'))], 'S9': [env_for('S9', [('C9', 0.35)], nfr('S9'))],
        'S10': [env_for('S10', [('C10a', 0.25), ('C10b', 2.75)], nfr('S10'))], 'S12': [env_for('S12', [('C12', 0.2)], nfr('S12'))],
    }
    K1 = Clip(os.path.join(EP, 'K1/clip_v1.mp4'), t0=0.8, sp=1.4)
    # v2: Kling 끝 프레임에 남은 날개 지운 자국 → 다시 메운 F2b_nowing2를 그 자리에만 덮음(옷이 다 떨어진 뒤)
    wm = np.load(os.path.join(EP, 'img/F2b_wingmask.npy')).astype(np.float32)
    wm = cv2.GaussianBlur(cv2.dilate(cv2.resize(wm, (W, int(wm.shape[0] * K))), np.ones((13, 13), np.uint8)), (15, 15), 0)[7:7 + H, :, None]
    fix = big('F2b_nowing2')[7:7 + H]
    POP = Clip(os.path.join(EP, 'test/popup_free_v2.mp4'))
    # B11 눈물(눈 밖, 왼쪽 눈 바깥 아래): 작은 하늘색 방울이 '쏘옥' 위로 빨려 들어감
    TEAR = (246 * K, 772 * K)
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
            if sk in plates:
                fr = plates[sk].copy(); ps = pp[sk]; ev = env.get(sk)
            if sk == 'S1':
                bob(ps[0], fr, ev[0][k], lt, 0); bob(ps[1], fr, ev[1][k], lt, 1)
                z = 1.12 + 0.12 * ease(lt / s['len']); fr = cam(fr, z, W / 2, 925 * K)
            elif sk == 'S2':
                bob(ps[0], fr, ev[0][k], lt)
                shake = 0 if lt < 0.85 else 3 + 7 * (lt - 0.85) / 0.8
                fr = cam(fr, 1.04 + 0.05 * lt / s['len'], W / 2, 760 * K)
            elif sk == 'S3':
                fr = K1.at(lt); shake = 22 * np.exp(-lt * 2.2) if lt < 1.6 else 0
                src_t = 0.8 + lt * 1.4
                if src_t > 3.9:
                    a_ = wm * ease((src_t - 3.9) / 0.3)
                    fr = (fr * (1 - a_) + fix * a_).astype(np.uint8)
            elif sk == 'S4a':
                fr = POP.at(lt)
            elif sk in ('S4b', 'S5', 'S8'):
                if sk in ('S4b', 'S8'):                # v5(사용자: "그대로인데?" 창수·"저건 작아졌어" 미순 움직이지 마) 멈춘 화면 + 확대만
                    fr = I[{'S4b': 'F4b', 'S8': 'F8'}[sk]].copy()
                else:
                    ps[0].draw(fr, 1 - 0.025 * ev[0][k], 1 + 0.05 * ev[0][k], 1.6 * ev[0][k] * np.sin(2 * np.pi * 2.2 * lt))
                z0 = {'S4b': 1.18, 'S5': 1.15, 'S8': 1.12}[sk]
                fr = cam(fr, z0 + 0.07 * ease(lt / s['len']), ps[0].center[0] - 40, ps[0].center[1] - 60)
            elif sk == 'S6':                           # v4(사용자: 우글거림) 멈춘 화면 + 확대만
                fr = I['F6'].copy()
                bump = 0.03 * np.exp(-(lt - 1.15) * 10) if lt >= 1.15 else 0
                fr = cam(fr, 1.15 + bump + 0.05 * lt / s['len'], ps[0].center[0] - 60, ps[0].center[1] + 20)
            elif sk == 'S7':                           # 날개로 가디건 쓰다듬기(만지작)
                ang = 5 * np.sin(2 * np.pi * 1.6 * lt) * min(1, lt / 0.3)
                ps[0].draw(fr, 1, 1, ang, dx=-6 * np.sin(2 * np.pi * 1.6 * lt), pivot=(ps[0].rgba.shape[1] - 10, ps[0].rgba.shape[0] * 0.55))
                fr = cam(fr, 1.0 + 0.1 * ease(lt / s['len']), W / 2, 820 * K)
            elif sk == 'S9':                           # 이불 덩어리 덜덜 + 말할 때 크게
                e = ev[0][k]; tr = 0.6 + 1.6 * e
                ps[0].draw(fr, 1 + 0.02 * e, 1 + 0.04 * e, tr * np.sin(2 * np.pi * 9 * lt), dx=tr * 1.5 * np.sin(2 * np.pi * 7 * lt))
                fr = cam(fr, 1.1 + 0.06 * lt / s['len'], ps[0].center[0], ps[0].center[1] - 80)
            elif sk == 'S10':
                stop = 2.75 + 0.32                         # "우리 패딩"의 '패딩'에서 떨림이 딱 멈춤
                tr = 1.2 if lt < stop else 0
                pk = 0.04 * max(0, np.sin(np.pi * ((lt - 0.15) / 0.25))) if 0.15 <= lt < 0.4 or 1.6 <= lt < 1.85 else 0
                ps[1].draw(fr, 1 - pk, 1 + pk, tr * np.sin(2 * np.pi * 9 * lt), dx=tr * 1.5 * np.sin(2 * np.pi * 7 * lt))
                ps[0].draw(fr)                              # v4(사용자: 손 움직이지 마) 창수는 가만히, 이불 위에 그림
                z = 1.1 + 0.06 * lt / s['len'] + (0.08 * ease((lt - stop) / 0.15) if lt >= stop else 0)
                fr = cam(fr, z, 395 * K, 640 * K)
            elif sk == 'S11':
                fr = I['B11'].copy()
                if 0.6 <= lt < 1.25:                   # 눈물 방울: 눈가 밖에서 '쏘옥' 위로 빨려 들어감
                    q = (lt - 0.6) / 0.65; r = 11 * (1 - 0.8 * ease(q)); y = TEAR[1] + 18 - 30 * ease(q)
                    cv2.ellipse(fr, (int(TEAR[0]), int(y)), (int(r * 0.75), int(r)), 0, 0, 360, (250, 220, 170), -1, cv2.LINE_AA)
                    cv2.circle(fr, (int(TEAR[0] - r * 0.25), int(y - r * 0.3)), max(1, int(r * 0.25)), (255, 255, 255), -1, cv2.LINE_AA)
                z = 1.05 if lt < 0.12 else 1.05 + 0.4 * ease((lt - 0.12) / 0.12)
                fr = cam(fr, z, 300 * K, 735 * K)
            elif sk == 'S12':
                bob(ps[0], fr, ev[0][k], lt)
                fr = cam(fr, 1.32 + 0.06 * lt / s['len'], 385 * K, 590 * K)
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
                        subc[key] = text_img([[(sb['text'], sb['sp'])]], 70, stroke=9)
                    im_ = subc[key]; put(fr, im_, W / 2, H - 430 - im_.shape[0] / 2)
            if tt > total - 0.4:
                fr = (fr * max(0, (total - tt) / 0.4)).astype(np.uint8)
            pr.stdin.write(fr.tobytes())
    pr.stdin.close(); pr.wait()
    print(f'{len(segs)}장면 {total:.2f}s → {os.path.relpath(out, ROOT)}')


if __name__ == '__main__':
    main()
