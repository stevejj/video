#!/usr/bin/env python3
"""ep06 v2 댄스배틀 고급 편집(Kling 0, 사용자 2026-10-22: "Kling 없이 편집으로 고급스럽게, 카메라 기법·효과, 길이 늘려도, 노래·효과음 바꿔도").
사용: python3 tools/ep06_v2_edit.py → r1·r2·r3 클립, VS 카드, edit_list.json, band_offsets.json, hf_fx.json, text_overlay.json, sfx/sfx_list.json
- 전체 화면(골목·가로등이 보이게). 새 배경음 100BPM(ElevenLabs, bgm/battle100.mp3, 마디 2.4s).
- 0 VS 인트로(1마디): 창수·미순 사진이 양쪽에서 들어오고 VS가 쾅.
- 1 ROUND 1 미순(2마디): 클립을 0.9배로 늦춰 2마디에 맞춤, 미순 쪽으로 천천히 다가가며 박자마다 들썩.
- 2 ROUND 2 창수(2.5마디): 회전 장면 슬로모션 + 집중선 + "오~", 창수 쪽으로 다가감.
- 3 FINAL 미순(3마디): 회전 슬로모션 → 착지 순간 정지 + 플래시 + 에어혼 → 돌아선 창수 박수로 카메라 이동 + 환호, WINNER 미순.
- 라운드 바뀔 때: 휙 넘기기(화면 밀기) + 흰 플래시 + 휙 소리.
"""
import json, os, re, subprocess, sys
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, 'outputs/ep06'); FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 24
BPM, P0 = 100.0, 0.025; BEAT = 60 / BPM; BAR = BEAT * 4          # battle100.mp3 측정: 100.0BPM, 첫 박 0.025s
MODEL = '/tmp/claude-0/-home-user-video/f018d661-8ddb-51f7-8e2d-f2480d28ac5d/scratchpad/models/isnet.onnx'
MI = 'minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1'
PINK, BLUE, GOLD = '#FF6FA8', '#4F86F0', '#F2A900'
# 원본 클립(716x1284)에서 춤추는 쪽의 위치(비율)
POS = {'r1_misun': (0.56, 0.53), 'r2_changsu': (0.32, 0.55), 'r3_misun': (0.60, 0.52), 'r3_changsu': (0.30, 0.56)}


def frames(f):
    out = subprocess.run([FF, '-i', f, '-map', '0:v', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return int(re.findall(r'frame=\s*(\d+)', out)[-1])


def seg(src, t0, t1, factor, dst):
    vf = f'trim={t0}:{t1},setpts=(PTS-STARTPTS)/{factor}' + (f',{MI}' if factor != 1 else '')
    subprocess.run([FF, '-y', '-v', 'error', '-i', src, '-an', '-vf', vf, '-r', str(FPS), '-c:v', 'libx264', '-crf', '15', '-pix_fmt', 'yuv420p', dst], check=True)
    return dst


def hold(src_mp4, dur, dst, last=True):
    """앞 조각의 마지막 프레임을 dur초 멈춤."""
    png = dst.replace('.mp4', '.png')
    subprocess.run([FF, '-y', '-v', 'error', '-sseof', '-0.05', '-i', src_mp4, '-frames:v', '1', '-update', '1', png], check=True)
    subprocess.run([FF, '-y', '-v', 'error', '-loop', '1', '-i', png, '-t', f'{dur:.3f}', '-r', str(FPS), '-c:v', 'libx264', '-crf', '15', '-pix_fmt', 'yuv420p', '-vf', 'scale=716:1284', dst], check=True)
    return dst


def build(name, parts):
    """조각들을 이어 붙여 outputs/ep06/<name>/clip_v1.mp4. 반환: 조각별 (시작, 길이) — 실제 프레임 수로 잼."""
    d = os.path.join(EP, name); os.makedirs(os.path.join(d, 'parts'), exist_ok=True)
    files, spans, t = [], [], 0.0
    key = json.dumps(parts); kp = os.path.join(d, 'parts/key.json')
    same = os.path.exists(kp) and open(kp).read() == key and os.path.exists(os.path.join(d, 'clip_v1.mp4'))   # 같은 설정이면 다시 안 만듦(슬로모션이 느림)
    for i, (kind, *a) in enumerate(parts):
        f = os.path.join(d, f'parts/p{i}.mp4')
        if same:
            pass
        elif kind == 'seg':
            seg(os.path.join(EP, a[0]), a[1], a[2], a[3], f)
        else:
            hold(files[-1], a[0], f)
        n = frames(f); spans.append((round(t, 3), round(n / FPS, 3))); t += n / FPS; files.append(f)
    if same:
        return spans, round(t, 3)
    open(kp, 'w').write(key)
    lst = os.path.join(d, 'parts/list.txt'); open(lst, 'w').write(''.join(f"file '{f}'\n" for f in files))
    subprocess.run([FF, '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c:v', 'libx264', '-crf', '15', '-pix_fmt', 'yuv420p', os.path.join(d, 'clip_v1.mp4')], check=True)
    return spans, round(t, 3)


def grab(src, t, dst=None):
    p = dst or os.path.join(EP, 'ref/_grab.png')
    subprocess.run([FF, '-y', '-v', 'error', '-ss', f'{t:.3f}', '-i', os.path.join(EP, src), '-frames:v', '1', '-vf', f'scale={W}:{H}', p], check=True)
    return Image.open(p).convert('RGB')


def font(size, weight=900):
    f = ImageFont.truetype(os.path.join(ROOT, 'assets/fonts/NotoSansKR-Variable.ttf'), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def portrait(src, name, color):
    """캐릭터 고해상도 이미지 누끼 + 아래 이름(색 띠). 클립 프레임은 둘이 겹쳐 있어 깨끗이 안 잘림 → 시트 이미지 사용."""
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    from cutout import alpha
    im = Image.open(os.path.join(ROOT, src)).convert('RGB')
    a = np.asarray(alpha(im, MODEL)).copy(); a[a < 60] = 0
    ys, xs = np.where(a > 0)
    p = Image.fromarray(np.dstack([np.asarray(im), a]).astype('uint8')).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    flip = False
    if flip:
        p = p.transpose(Image.FLIP_LEFT_RIGHT)
    s = 340 / p.width; PH = int(p.height * s); p = p.resize((340, PH), Image.LANCZOS)   # 몸 폭을 같게(창수 키는 깃털만큼 더 큼 — 사용자: 크기 같게)
    cw = max(p.width, 360); out = Image.new('RGBA', (cw, PH + 130), (0, 0, 0, 0))
    glow = Image.new('RGBA', out.size, (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse([cw * 0.08, 60, cw * 0.92, PH - 20], fill=color + '90')
    out.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)))
    out.alpha_composite(p, ((cw - p.width) // 2, 0))
    d = ImageDraw.Draw(out); f = font(76); l, tt, r, b = d.textbbox((0, 0), name, font=f)
    bw = r - l + 70; bx = (cw - bw) // 2
    d.rounded_rectangle([bx, PH + 15, bx + bw, PH + 115], radius=50, fill=color)
    d.text((bx + 35 - l, PH + 65 - (b + tt) / 2), name, font=f, fill='white', stroke_width=3, stroke_fill=(0, 0, 0, 90))
    return out


def vs_card():
    """VS 인트로: 배경(골목을 흐리고 어둡게 + 왼쪽 파랑·오른쪽 분홍) + 창수·미순 사진 + VS 글자(레이어로 움직임)."""
    os.makedirs(os.path.join(EP, 'ref'), exist_ok=True)
    bg = grab('c1/clip_v1.mp4', 0.0).filter(ImageFilter.GaussianBlur(16))
    arr = np.asarray(bg).astype(float) * 0.42
    yy, xx = np.mgrid[0:H, 0:W]; left = (xx < W / 2 + (yy - H / 2) * 0.18)[..., None]
    tint = np.where(left, [40, 80, 200], [210, 60, 130]).astype(float)
    arr = np.clip(arr * 0.75 + tint * 0.35, 0, 255)
    bgi = Image.fromarray(arr.astype('uint8')); d = ImageDraw.Draw(bgi)
    d.line([(W / 2 - (H / 2) * 0.18, 0), (W / 2 + (H / 2) * 0.18, H)], fill=(255, 230, 120), width=10)
    bgp = os.path.join(EP, 'ref/vs_bg.png'); bgi.save(bgp)
    cs = portrait('assets/characters/pang-changsu/pang-changsu_3q_right.png', '창수', BLUE)   # 가운데(미순 쪽)를 봄
    ms = portrait('assets/characters/pang-misun/pang-misun_3q_left.png', '미순', PINK)
    csp, msp = os.path.join(EP, 'ref/vs_changsu.png'), os.path.join(EP, 'ref/vs_misun.png'); cs.save(csp); ms.save(msp)
    v = Image.new('RGBA', (520, 360), (0, 0, 0, 0)); dv = ImageDraw.Draw(v); f = font(300)
    dv.text((30, -40), 'VS', font=f, fill='#FFD84A', stroke_width=16, stroke_fill='#1A1A1A')
    v = v.rotate(8, expand=True, resample=Image.BICUBIC)   # VS는 얼굴 안 가리게 둘 사이 아래쪽(y 1060)
    vsp = os.path.join(EP, 'ref/vs_text.png'); v.save(vsp)
    rel = lambda p: os.path.relpath(p, ROOT)
    return rel(bgp), [
        {'id': 'cs', 'img': rel(csp), 'box': [30, 1480 - cs.height, cs.width, cs.height], 'origin': '50% 50%', 'init': {'x': -760, 'opacity': 0},
         'keys': [{'t': 0.05, 'dur': 0.32, 'x': 0, 'opacity': 1, 'ease': 'power3.out'}, {'t': 0.37, 'dur': 2.0, 'y': -12, 'ease': 'sine.inOut'}]},
        {'id': 'ms', 'img': rel(msp), 'box': [W - 30 - ms.width, 1340 - ms.height, ms.width, ms.height], 'origin': '50% 50%', 'init': {'x': 760, 'opacity': 0},
         'keys': [{'t': 0.1, 'dur': 0.32, 'x': 0, 'opacity': 1, 'ease': 'power3.out'}, {'t': 0.42, 'dur': 2.0, 'y': 12, 'ease': 'sine.inOut'}]},
        {'id': 'vs', 'img': rel(vsp), 'box': [(W - v.width) // 2, 1060, v.width, v.height], 'origin': '50% 50%', 'init': {'scale': 3.2, 'opacity': 0},
         'keys': [{'t': BEAT, 'dur': 0.14, 'scale': 1, 'opacity': 1, 'ease': 'power4.in'}, {'t': BEAT + 0.14, 'dur': 1.6, 'scale': 1.08, 'ease': 'sine.out'}]},
    ]


def cam(L, keys, beats, whip_in=True, whip_out=True, no_pulse=()):
    """카메라: keys = [(t, 배율, 볼 곳 x비율, y비율)] 사이를 박자마다 이어 가며 박자에 살짝 들썩. no_pulse = 들썩 없는 구간."""
    def at(t):
        for (t0, s0, x0, y0), (t1, s1, x1, y1) in zip(keys, keys[1:]):
            if t0 <= t <= t1:
                k = (t - t0) / max(t1 - t0, 1e-6); return s0 + (s1 - s0) * k, x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
        return keys[-1][1:]

    def xy(s, px, py):   # 그 점이 화면 가운데 쪽으로 오게(검은 테두리 안 보이게 제한)
        mx, my = (s - 1) * W / 2, (s - 1) * H / 2
        return round(max(-mx, min(mx, -s * (px * W - W / 2) * 0.85))), round(max(-my, min(my, -s * (py * H - H / 2) * 0.85)))
    mv = []; pts = sorted(set([0.0] + [b for b in beats if 0 < b < L - 0.2] + [k[0] for k in keys if 0 < k[0] < L]))
    if whip_in:
        s, px, py = at(0); x, y = xy(s, px, py)
        mv += [{'at': 0, 'dur': 0.001, 'scale': s, 'x': x + 620, 'y': y, 'ease': 'none'}, {'at': 0.001, 'dur': 0.18, 'scale': s, 'x': x, 'y': y, 'ease': 'power3.out'}]
        pts = [p for p in pts if p >= 0.2]
    for a, b in zip(pts, pts[1:] + [L - (0.14 if whip_out else 0)]):
        s0, px0, py0 = at(a); s1, px1, py1 = at(b); x1, y1 = xy(s1, px1, py1)
        pulse = a in beats and not any(u <= a < v for u, v in no_pulse)
        if pulse and b - a > 0.2:
            xp, yp = xy(s0 + 0.04, px0, py0)
            mv += [{'at': round(a, 3), 'dur': 0.05, 'scale': round(s0 + 0.04, 3), 'x': xp, 'y': yp, 'ease': 'power2.out'},
                   {'at': round(a + 0.05, 3), 'dur': round(b - a - 0.05, 3), 'scale': round(s1, 3), 'x': x1, 'y': y1, 'ease': 'power2.out'}]
        else:
            mv.append({'at': round(a, 3), 'dur': round(max(b - a, 0.01), 3), 'scale': round(s1, 3), 'x': x1, 'y': y1, 'ease': 'sine.inOut'})
    if whip_out:
        s, px, py = at(L); x, y = xy(s, px, py)
        mv.append({'at': round(L - 0.14, 3), 'dur': 0.14, 'scale': s, 'x': x - 700, 'y': y, 'ease': 'power2.in'})
    return mv


def main():
    # 클립(속도 조절은 실제 프레임 수로 재서 마디에 맞춤)
    s1, L1 = build('r1', [('seg', 'c1/clip_v1.mp4', 0, 4.333, 0.897)])
    s2, L2 = build('r2', [('seg', 'c2/clip_v1f.mp4', 0, 1.0, 1), ('seg', 'c2/clip_v1f.mp4', 1.0, 2.4, 0.557), ('seg', 'c2/clip_v1f.mp4', 2.4, 5.0, 1)])
    s3, L3 = build('r3', [('seg', 'c3/clip_v1.mp4', 0, 1.0, 1), ('seg', 'c3/clip_v1.mp4', 1.0, 2.1, 0.483), ('hold', 0.8),
                          ('seg', 'c3/clip_v1.mp4', 2.1, 5.04, 1), ('hold', 0.3)])
    L0 = round(P0 + BAR + 0.05, 3)                               # 인트로 = 1마디. 1라운드 클립이 4.75s(115프레임)라 +0.05 → 2·3라운드가 박에 딱
    T1 = L0; T2 = T1 + L1; T3 = T2 + L2; END = T3 + L3
    print(f'인트로 {L0} | R1 {T1:.2f}+{L1} | R2 {T2:.2f}+{L2} (마디 박 {P0 + 3 * BAR:.2f}) | R3 {T3:.2f}+{L3} | 끝 {END:.2f}')
    beats = lambda T, L: [round(P0 + k * BEAT - T, 3) for k in range(60) if T <= P0 + k * BEAT < T + L]

    bgp, layers = vs_card()
    clip = lambda cut, src, L: {'cut': cut, 'kind': 'clip', 'source_cut': src, 'clip_tag': 'v1', 'in': 0.0, 'len': L, 'time_card': None}
    E = {'canvas': [W, H], 'fps': FPS, 'band': {'top_px': 0, 'window_px': H}, 'still_zoom': 0.0, 'fade_out_before_black': 0.4,
         'cuts': [{'cut': '00', 'kind': 'still', 'source_cut': 'vs', 'image': bgp, 'in': 0, 'len': L0, 'time_card': None},
                  clip('01', 'r1', L1), clip('02', 'r2', L2), clip('03', 'r3', L3)],
         'history': [f'2026-10-22 ep06 v2: Kling 0 고급 편집, VS 인트로 + 3라운드, 100BPM, {END:.1f}s']}
    json.dump(E, open(os.path.join(EP, 'edit_list.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump({'band_ratio': 1.0, 'default_top': 0, 'per_cut_top': {}, 'note': 'ep06 v2: 전체 화면'}, open(os.path.join(EP, 'band_offsets.json'), 'w'), ensure_ascii=False, indent=1)

    (a2, _), (b2, lb2), _c2 = s2; (a3, _), (b3, lb3), (f3, lf3), (c3s, _), _h3 = s3
    face2 = b2 + (1.6 - 1.0) / 0.557 * (lb2 / (1.4 / 0.557))      # 창수가 정면을 보는 순간(슬로 안)
    land3 = f3                                                       # 미순 착지(정지 시작)
    c3t = lambda tc: c3s + (tc - 2.1)                                # c3 원본 시각 → r3 시각(정지 뒤)
    claps = [c3t(t) for t in (3.23, 3.48, 3.78, 4.06, 4.33, 4.65)]
    m1, c2p, m3, c3p = POS['r1_misun'], POS['r2_changsu'], POS['r3_misun'], POS['r3_changsu']   # 끝(박수)은 창수만 아니라 WINNER 미순도 보이게 둘 사이(0.45)
    lab = lambda at, dur, small, text, color: {'at': round(at, 3), 'dur': round(dur, 3), 'small': small, 'text': text, 'color': color, 'y': 0.30}
    F = json.load(open(os.path.join(ROOT, 'outputs/ep09/hf_fx.json')))
    F['default_still'] = {'cam': None}; F['default_clip'] = {'cam': None}
    F['cuts'] = {
        '00': {'puppet': {'bg': bgp, 'src_width': W, 'layers': layers},   # 느린 줌은 뺌(VS 흔들림과 x·y가 겹침)
               'flash': [{'at': BEAT, 'dur': 0.3, 'peak': 0.7}], 'shake': {'at': BEAT + 0.14, 'amp': 10, 'dur': 0.25}},
        '01': {'moves': cam(L1, [(0, 1.0, 0.5, 0.5), (L1, 1.32, *m1)], beats(T1, L1)),
               'flash': [{'at': 0.0, 'dur': 0.22, 'peak': 0.6}],
               'spotlight': {'at': 0.0, 'dur': L1, 'cx': 0.56, 'cy': 0.5, 'r': 0.42, 'dark': 0.45},
               'tint': {'at': 0.0, 'dur': L1, 'color': 'rgba(255,175,215,0.22)', 'fade': 0.3},
               'labels': [lab(0.15, 2.2, 'ROUND 1', '미순', PINK)]},
        '02': {'moves': cam(L2, [(0, 1.05, 0.5, 0.5), (b2, 1.15, *c2p), (b2 + lb2, 1.42, *c2p), (L2, 1.12, 0.45, 0.52)], beats(T2, L2), no_pulse=[(b2, b2 + lb2)]),
               'flash': [{'at': 0.0, 'dur': 0.22, 'peak': 0.6}, {'at': face2, 'dur': 0.25, 'peak': 0.35}],
               'spotlight': {'at': 0.0, 'dur': L2, 'cx': 0.4, 'cy': 0.5, 'r': 0.42, 'dark': 0.45},
               'tint': {'at': 0.0, 'dur': L2, 'color': 'rgba(150,190,255,0.24)', 'fade': 0.3},
               'speedlines': {'at': face2 - 0.1, 'dur': 0.9, 'cx': 0.42, 'cy': 0.5},
               'labels': [lab(0.15, 2.2, 'ROUND 2', '창수', BLUE)]},
        '03': {'moves': cam(L3, [(0, 1.08, 0.55, 0.5), (b3, 1.15, *m3), (land3, 1.45, *m3), (land3 + 0.1, 1.58, *m3), (land3 + lf3, 1.55, *m3),
                                  (land3 + lf3 + 0.6, 1.2, 0.45, 0.55), (L3, 1.24, 0.45, 0.55)], beats(T3, L3), whip_out=False,
                            no_pulse=[(b3, land3 + lf3 + 0.6)]),
               'flash': [{'at': 0.0, 'dur': 0.22, 'peak': 0.6}, {'at': land3, 'dur': 0.35, 'peak': 0.85}],
               'spotlight': {'at': 0.0, 'dur': land3 + lf3, 'cx': 0.58, 'cy': 0.5, 'r': 0.42, 'dark': 0.45},
               'tint': {'at': 0.0, 'dur': land3 + lf3, 'color': 'rgba(255,175,215,0.22)', 'fade': 0.3},
               'speedlines': {'at': land3, 'dur': lf3, 'cx': 0.55, 'cy': 0.48},
               'sparkle': {'at': claps[0], 'cx': 0.8, 'dur': L3 - claps[0], 'dy': -960, 'color': '#FFE27A'},   # 미순 머리 위(얼굴 안 가리게)
               'labels': [lab(0.15, 2.0, 'FINAL', '미순', PINK), dict(lab(claps[0], L3 - claps[0], 'WINNER', '미순', GOLD), x=0.52)]},
    }
    F['note'] = 'ep06 v2: VS 인트로 + 라운드별 이름표·조명·색·박자 들썩 카메라·휙 넘기기, 슬로모션·정지(Kling 0)'
    json.dump(F, open(os.path.join(EP, 'hf_fx.json'), 'w'), ensure_ascii=False, indent=1)

    T = json.load(open(os.path.join(ROOT, 'outputs/ep11/text_overlay.json')))   # 전체 화면 제목 위치·테두리
    T['title']['lines'] = [{'text': '창수와 미순', 'color': '#FFFFFF'}, {'text': '댄스배틀', 'color': '#FFD84A'}]   # v1 제목 그대로
    T['subtitles'] = []; T['note'] = 'ep06 v2: 전체 화면, 대사 없음'
    json.dump(T, open(os.path.join(EP, 'text_overlay.json'), 'w'), ensure_ascii=False, indent=1)

    EL = 'outputs/ep06/sfx/el/'
    sf = lambda name, file, a0, ln, lufs, **k: dict(name=name, file=file, at=round(a0, 3), len=round(ln, 3), target_lufs=lufs, fade_out=k.pop('fo', 0.05), **k)
    items = [sf('bgm', 'outputs/ep06/bgm/battle100.mp3', 0.0, END, -17, fo=0.9),
             sf('slide', EL + 'whoosh_fast.mp3', 0.02, 0.6, -24),
             sf('vs_hit', EL + 'impact_boom.mp3', T1 - L0 + BEAT, 1.5, -15),
             sf('whip1', EL + 'whoosh_fast.mp3', T1 - 0.16, 0.6, -21),
             sf('whip2', EL + 'whoosh_fast.mp3', T2 - 0.16, 0.6, -21),
             sf('ooh2', EL + 'crowd_ooh.mp3', T2 + face2, 1.5, -21, fo=0.3),
             sf('whip3', EL + 'whoosh_fast.mp3', T3 - 0.16, 0.6, -21),
             sf('scratch3', 'outputs/ep11/sfx/el/record_scratch.mp3', T3 - 0.05, 0.6, -20),
             sf('horn', EL + 'air_horn.mp3', T3 + land3, 1.0, -18),
             sf('ooh3', EL + 'crowd_ooh.mp3', T3 + land3 + 0.15, 1.5, -20, fo=0.3),
             sf('cheer', EL + 'crowd_cheer.mp3', T3 + claps[0], END - T3 - claps[0], -19, fo=0.8)]
    items += [dict(name=f'clap{i}', file='outputs/ep06/sfx/clap.wav', at=round(T3 + c, 3), len=0.3, gain=-8.0) for i, c in enumerate(claps)]
    json.dump({'note': 'ep06 v2 효과음(ElevenLabs 5개 + 박수 합성 + ep11 레코드 긁힘), 배경음 battle100', 'items': items},
              open(os.path.join(EP, 'sfx/sfx_list.json'), 'w'), ensure_ascii=False, indent=1)

    pp = os.path.join(ROOT, 'outputs/voice_profile.json'); P = json.load(open(pp))
    P['episodes']['ep06'].pop('bgm', None)
    P['episodes']['ep06']['note'] = 'ep06 v2: 대사 없음, 배경음은 sfx_list의 battle100(100BPM) + 효과음'
    json.dump(P, open(pp, 'w'), ensure_ascii=False, indent=1)
    print(f'정면 {face2:.2f} 착지 {land3:.2f} 박수 {[round(c, 2) for c in claps]}')


if __name__ == '__main__':
    main()
