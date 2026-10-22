#!/usr/bin/env python3
"""ep05 v2 헬스장 간 우리 미순이 — 고급 편집(Kling 0, 사용자 2026-10-22: "운동 안 하고 사진 찍는 거에 집중하는 느낌, 효과음·효과 연출 제대로").
사용: python3 tools/ep05_v2_edit.py → a·d 클립, 뷰파인더 그림, edit_list.json, hf_fx.json, sfx/sfx_list.json, voice_profile ep05
- A 포즈(뷰파인더 + 초점) → 찰칵(플래시·정지 0.6s·폴라로이드 "1장") → 덤벨 툭 + 유리 알림창 "운동 끝!"(1.4배 빠르게) → 창수에게 총총(1.3배)
- B 폰 화면: 핀치 확대로 얼굴 검사 → 유리 알림창 "↺ 다시 찍기" + 톡 누름
- C 갸웃(v1.1 퍼펫 그대로 — 바닥 덤벨 레이어 포함, 덤벨 사라짐 사고 방지)
- D 후다닥 돌아가(1.4배 + 집중선) 덤벨 집고 같은 포즈 → 뷰파인더 → 찰칵 → 폴라로이드 "2장" + "운동 0회 · 사진 2장"
- 소리: 새 배경음(ElevenLabs 음악), 효과음 ElevenLabs(DSLR 셔터·덤벨 툭·총총·핀치·알림·톡·후다닥·헬스장 소리) + 기존 톡·반짝.
"""
import json, os, re, subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, 'outputs/ep05'); FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS, TOP, WIN = 1080, 1920, 24, 576, 768
EL = 'outputs/ep05/sfx/el/'
PINK, GRAY, GOLD = '#FF6FA8', '#8A8F98', '#F2A900'
FACE_A = (0.62, 0.30)      # 포즈 때 미순 얼굴(창 비율)
FACE_PHONE = (0.5, 0.36)   # 폰 화면 속 미순 얼굴(창 비율)


def frames(f):
    return int(re.findall(r'frame=\s*(\d+)', subprocess.run([FF, '-i', f, '-map', '0:v', '-f', 'null', '-'], capture_output=True, text=True).stderr)[-1])


def build(name, src, parts):
    """클립 조각(속도 조절·멈춤) 이어 붙이기 → outputs/ep05/<name>/clip_v1.mp4. 반환: 조각별 (시작, 길이) — 실제 프레임 수로 잼."""
    d = os.path.join(EP, name); os.makedirs(os.path.join(d, 'parts'), exist_ok=True)
    files, spans, t = [], [], 0.0
    for i, (kind, *a) in enumerate(parts):
        f = os.path.join(d, f'parts/p{i}.mp4')
        if kind == 'seg':   # 빠르게(속도>1)는 프레임을 건너뜀
            vf = f'trim={a[0]}:{a[1]},setpts=(PTS-STARTPTS)/{a[2]}'
            subprocess.run([FF, '-y', '-v', 'error', '-i', os.path.join(EP, src), '-an', '-vf', vf, '-r', str(FPS), '-c:v', 'libx264', '-crf', '15', '-pix_fmt', 'yuv420p', f], check=True)
        else:               # 앞 조각 마지막 프레임 멈춤
            png = f.replace('.mp4', '.png')
            subprocess.run([FF, '-y', '-v', 'error', '-sseof', '-0.05', '-i', files[-1], '-frames:v', '1', '-update', '1', png], check=True)
            subprocess.run([FF, '-y', '-v', 'error', '-loop', '1', '-i', png, '-t', f'{a[0]:.3f}', '-r', str(FPS), '-c:v', 'libx264', '-crf', '15', '-pix_fmt', 'yuv420p', '-vf', 'scale=716:1284', f], check=True)
        n = frames(f); spans.append((round(t, 3), round(n / FPS, 3))); t += n / FPS; files.append(f)
    lst = os.path.join(d, 'parts/list.txt'); open(lst, 'w').write(''.join(f"file '{f}'\n" for f in files))
    subprocess.run([FF, '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c:v', 'libx264', '-crf', '15', '-pix_fmt', 'yuv420p', os.path.join(d, 'clip_v1.mp4')], check=True)
    return spans, round(t, 3)


def viewfinder():
    """카메라 뷰파인더 덮개(창 1080x768): 네 귀퉁이 꺾쇠 + REC 빨간 점 + 배터리."""
    im = Image.new('RGBA', (W, WIN), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c, a, w = 46, 90, 7
    for x, y, sx, sy in [(c, c, 1, 1), (W - c, c, -1, 1), (c, WIN - c, 1, -1), (W - c, WIN - c, -1, -1)]:
        d.line([(x, y), (x + sx * a, y)], fill='white', width=w); d.line([(x, y), (x, y + sy * a)], fill='white', width=w)
    f = ImageFont.truetype(os.path.join(ROOT, 'assets/fonts/NotoSansKR-Variable.ttf'), 40)
    try:
        f.set_variation_by_axes([800])
    except Exception:
        pass
    d.ellipse([c + 30, c + 28, c + 58, c + 56], fill='#FF3B30'); d.text((c + 70, c + 18), 'REC', font=f, fill='white')
    bx = W - c - 130; d.rounded_rectangle([bx, c + 26, bx + 80, c + 60], radius=6, outline='white', width=4)
    d.rectangle([bx + 82, c + 36, bx + 88, c + 50], fill='white'); d.rectangle([bx + 8, c + 33, bx + 60, c + 53], fill='white')
    p = os.path.join(EP, 'ref/viewfinder.png'); os.makedirs(os.path.dirname(p), exist_ok=True); im.save(p)
    return os.path.relpath(p, ROOT)


def main():
    a, LA = build('a', '02/clip_v1.mp4', [('seg', 0.3, 1.38, 1), ('hold', 0.6), ('seg', 1.38, 2.9, 1.4), ('seg', 2.9, 4.6, 1.3)])
    dd, LD = build('d', '05/clip_v1.mp4', [('seg', 0.2, 1.6, 1.4), ('seg', 1.6, 4.38, 1), ('hold', 3.2)])   # 마지막 멈춤 1.5 → 3.2s(사용자: 운동 0회·사진 2장 더 오래)
    LB, LC = 1.8, 1.0
    TA, TB, TC, TD = 0.0, LA, LA + LB, LA + LB + LC; END = TD + LD
    shot1 = a[1][0]; drop = a[2][0] + (2.8 - 1.38) / 1.4; walk = a[3][0]
    d2 = dd[1][0]; shot2 = dd[2][0]; grip = d2 + (1.75 - 1.6); pose = d2 + (3.8 - 1.6)
    print(f'A {LA} (찰칵 {shot1:.2f}, 툭 {drop:.2f}) | B {TB:.2f}+{LB} | C {TC:.2f}+{LC} | D {TD:.2f}+{LD} (포즈 {pose:.2f}, 찰칵 {shot2:.2f}) | 끝 {END:.2f}')
    vf = viewfinder()

    still = lambda cut, src, img, L: {'cut': cut, 'kind': 'still', 'source_cut': src, 'image': img, 'in': 0, 'len': L, 'time_card': None}
    clip = lambda cut, src, L: {'cut': cut, 'kind': 'clip', 'source_cut': src, 'clip_tag': 'v1', 'in': 0.0, 'len': L, 'time_card': None}
    E = json.load(open(os.path.join(EP, 'edit_list.json')))
    E['cuts'] = [clip('01', 'a', LA), still('02', '03', 'outputs/ep05/04/start_v1.png', LB), still('03', '04', 'outputs/ep05/03/start_v1.png', LC), clip('04', 'd', LD)]
    E['history'] = E.get('history', []) + [f'2026-10-22 ep05 v2: Kling 0 고급 편집(뷰파인더·폴라로이드·운동 끝·핀치 확대·다시 찍기·운동 0회 사진 2장), {END:.1f}s']
    json.dump(E, open(os.path.join(EP, 'edit_list.json'), 'w'), ensure_ascii=False, indent=1)

    F = json.load(open(os.path.join(EP, 'hf_fx.json')))
    tilt = F['cuts']['03']                                   # v1.1 갸웃 퍼펫(덤벨 레이어 포함) 그대로
    assert any(l['id'] == 'db' for l in tilt['puppet']['layers']), '갸웃 컷에 바닥 덤벨 레이어가 없음(2026-10-19 사라짐 사고)'
    def polaroid(cut, t, at, n, x, y):
        """창수가 찍은 사진 = 포즈 잡은 미순만(창수 뒷모습 빼고) 잘라 폴라로이드로."""
        src = os.path.join(EP, f'{cut}/clip_v1.mp4'); png = os.path.join(EP, f'ref/polaroid_{n}.png')
        subprocess.run([FF, '-y', '-v', 'error', '-ss', f'{t:.3f}', '-i', src, '-frames:v', '1', '-vf', f'scale={W}:{H},crop=440:520:470:620', '-update', '1', png], check=True)
        return {'image': os.path.relpath(png, ROOT), 'raw': True, 'at': round(at, 3), 'dur': 1.4, 'label': f'찰칵! {n}장', 'w': 0.3, 'x': x, 'y': y, 'color': True}
    lab = lambda at, dur, small, text, color, y: {'at': round(at, 3), 'dur': round(dur, 3), 'small': small, 'text': text, 'color': color, 'y': y}
    F['default_still'] = {'cam': None}; F['default_clip'] = {'cam': None}
    F['cuts'] = {
        '01': {'overlays': [{'at': 0.0, 'dur': shot1 + 0.6, 'img': vf, 'focus': {'x': FACE_A[0], 'y': FACE_A[1], 'size': 230}}],
               'flash': [{'at': shot1, 'dur': 0.3, 'peak': 0.9}],
               'flashback': polaroid('a', shot1 - 0.05, shot1 + 0.08, 1, 0.2, 0.06),   # 왼쪽 위(창수 머리 쪽) — 미순 얼굴 안 가리게
               # 노란 "운동 끝!" 도장 → 유리 알림창(사용자: 노란 글씨 효과도 수정, '다시 찍기'와 같은 고급 느낌)
               'toasts': [{'at': round(drop, 3), 'dur': round(LA - drop, 3), 'text': '운동 끝!', 'y': 0.08}]},
        '02': {'moves': [{'at': 0.0, 'dur': 0.3, 'scale': 1.0, 'x': 0, 'y': 0, 'ease': 'none'},
                         {'at': 0.3, 'dur': 0.55, 'scale': 1.8, 'x': round(-(FACE_PHONE[0] * W - W / 2) * 1.8), 'y': round(-(FACE_PHONE[1] * WIN - WIN / 2) * 1.8), 'ease': 'power3.inOut'}],
               'labels': [lab(0.05, 1.0, '', '확대 검사 중...', GRAY, 0.06)],
               # 빨간 "다시!" 도장 → 폰 화면 위 유리 알림창 + 누르는 손끝(사용자: 빨간 글씨가 분위기에 안 맞음, 고급스럽게)
               'toasts': [{'at': 1.05, 'dur': LB - 1.05, 'text': '다시 찍기', 'y': 0.70}],   # ↺ 기호는 글꼴에 없어 아주 작게 나옴 → 글자만
               'taps': [{'at': 1.35, 'x': 0.5, 'y': 0.76, 'r': 80}]},
        '03': tilt,
        '04': {'speedlines': {'at': 0.0, 'dur': dd[0][1], 'cx': 0.6, 'cy': 0.45},
               'overlays': [{'at': round(pose - 0.4, 3), 'dur': round(LD - pose + 0.4, 3), 'img': vf, 'focus': {'x': FACE_A[0], 'y': FACE_A[1], 'size': 230}}],
               'flash': [{'at': round(shot2, 3), 'dur': 0.3, 'peak': 0.9}],
               'flashback': dict(polaroid('d', shot2 - 0.05, shot2 + 0.08, 2, 0.2, 0.38), dur=round(LD - shot2 - 0.08, 3)),   # 운동 0회·사진 2장 아래
               'labels': [lab(shot2 + 0.35, LD - shot2 - 0.35, '오늘', '운동 0회', GRAY, 0.08), lab(shot2 + 0.55, LD - shot2 - 0.55, '오늘', '사진 2장', PINK, 0.22)]},
    }
    F['note'] = 'ep05 v2: 사진에만 진심(뷰파인더·폴라로이드·운동 끝·다시!·운동 0회 사진 2장), Kling 0'
    json.dump(F, open(os.path.join(EP, 'hf_fx.json'), 'w'), ensure_ascii=False, indent=1)

    sf = lambda name, file, a0, ln, lufs, **k: dict(name=name, file=file, at=round(a0, 3), len=round(ln, 3), target_lufs=lufs, fade_out=k.pop('fo', 0.05), **k)
    items = [sf('bgm', 'outputs/ep05/bgm/selfie_gym.mp3', 0.0, END, -18, fade_in=0.2, fo=0.8),   # -21이면 전체 -19 LUFS(다른 편보다 작음)
             sf('gym', EL + 'gym_amb.mp3', 0.0, END, -36, loop=True, fade_in=0.3, fo=0.6),
             sf('shutter1', EL + 'dslr_shutter.mp3', shot1 - 0.03, 0.48, -13),
             sf('drop', EL + 'dumbbell_drop.mp3', drop - 0.03, 1.0, -16),
             sf('done_pop', EL + 'ui_pop.mp3', drop + 0.12, 0.6, -21),   # "운동 끝!" 알림창
             sf('steps1', EL + 'tiny_steps.mp3', walk, LA - walk + 0.1, -22, fo=0.2),
             sf('pinch', EL + 'pinch_zoom.mp3', TB + 0.3, 0.6, -20),
             sf('ui_pop', EL + 'ui_pop.mp3', TB + 1.05, 0.6, -18),   # 땡 부저 대신(유리 알림창과 맞게)
             sf('ui_tap', EL + 'ui_tap.mp3', TB + 1.35, 0.3, -20),
             sf('rush', EL + 'rewind_rush.mp3', TD - 0.05, 0.68, -19),
             sf('steps2', EL + 'tiny_steps.mp3', TD, dd[0][1] + 0.1, -21, fo=0.2),
             sf('grip', 'outputs/ep02/sfx/el/cup_set.mp3', TD + grip, 0.4, -24),
             sf('pose_pop', 'outputs/ep01/sfx/el/sparkle.mp3', TD + pose, 0.7, -22),
             sf('shutter2', EL + 'dslr_shutter.mp3', TD + shot2 - 0.03, 0.48, -13),
             sf('stats', 'outputs/ep01/sfx/el/sparkle.mp3', TD + shot2 + 0.55, 0.7, -24)]
    json.dump({'note': 'ep05 v2 효과음(ElevenLabs 7개 + 기존 톡·반짝), 배경음 selfie_gym', 'items': items},
              open(os.path.join(EP, 'sfx/sfx_list.json'), 'w'), ensure_ascii=False, indent=1)
    pp = os.path.join(ROOT, 'outputs/voice_profile.json'); P = json.load(open(pp))
    P['episodes']['ep05'].pop('bgm', None); P['episodes']['ep05']['note'] = 'ep05 v2: 대사 없음, 배경음은 sfx_list의 selfie_gym + 효과음'
    json.dump(P, open(pp, 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
