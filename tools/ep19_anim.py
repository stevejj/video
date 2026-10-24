#!/usr/bin/env python3
"""ep19 무료 애니매틱(0원) 조립.
사용: python tools/ep19_anim.py [--tag v1] [--skip-clips] [--only-json]
1) 말하는 컷: talk_bob(몸 통통) 클립 → outputs/ep19/<cut>/clip_v1.mp4
2) 속마음 줄: 약한 동굴 울림(cave_light, ep14 방식) → outputs/ep19/voice/lines/<id>_rev.mp3
3) edit_list / band_offsets / text_overlay / hf_fx / voice placements / sfx_list 작성
4) ep_to_hyperframes → HyperFrames lint·render → mix_audio(배경음 없음) → outputs/ep19/roughcut/ep19_animatic_<tag>.mp4
규칙: 02c M18(속마음 = 리버브 + 그 캐릭터로 푸시인), 02a §11 띠 30/40/30, 유리 알림창, 폰 전 컷 가슴.
"""
import argparse, json, os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import imageio_ffmpeg
import pupil_quake

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF = imageio_ffmpeg.get_ffmpeg_exe()
EP = 'ep19'; O = f'outputs/{EP}'; IMG = f'{O}/img'; VL = f'{O}/voice/lines'
SR = 44100
HF_BIN = os.path.join(ROOT, 'external/hf-cli/node_modules/.bin/hyperframes' + ('.cmd' if os.name == 'nt' else ''))
MODEL = os.environ.get('ISNET_MODEL') or os.path.join(os.environ.get('LOCALAPPDATA', ''), r'Temp\claude\C--Users-ljste-OneDrive-------video\52137cd4-6604-41fd-9aea-217127389d20\scratchpad\models\isnet.onnx')

COL = {'changsu': '#8FB0E8', 'misun': '#FF9CC2'}
TAIL = 0.4
# 효과음 재사용(새 생성 없음)
SFX = {
    'ping': 'outputs/ep16/sfx/el/msg_ping.mp3', 'pop': 'outputs/ep05/sfx/el/ui_pop.mp3', 'gulp': 'outputs/ep11/sfx/el/gulp.mp3',
    'dream': 'outputs/ep16/sfx/el/dream_whoosh.mp3', 'sparkle': 'outputs/ep01/sfx/el/sparkle.mp3', 'quake': 'outputs/ep02/sfx/el/pupil_quake.mp3',
    'vibrate': 'outputs/ep16/sfx/el/phone_vibrate.mp3',
}
TWO = {'changsu': '40,430,384,1000', 'misun': '384,430,740,1000'}
ONE = '0,300,768,1150'

# 컷 정의. lines: (화자, 줄ID, 시작 오프셋, 속마음?)  sub_x: 자막 가로 중심(0~1)
CUTS = [
    dict(cut='01', img=f'{IMG}/B0_v2.png', still=True, lines=[('misun', 'L01', 0.3, False)], sub_x=0.5, fx={'drift': {'amp': 4, 'period': 2.4}, 'punch': {'at': 0.3, 'scale': 1.03, 'settle': 1.0}}),  # 2026-10-24 사용자: 첫 장면 미순 움직이지 말 것(정지)
    dict(cut='02', img=f'{IMG}/C03_v1.png', still=True, dur=0.9, lines=[], sfx=[('ping', 0.1, -16)], fx={'punch': {'at': 0.1, 'scale': 1.05, 'settle': 1.02}}),
    dict(cut='03', img=f'{IMG}/C03_v1.png', still=True, dur=3.0, lines=[],
         fx={'cam': {'from': 1.02, 'to': 1.05},
             'bubbles': [{'at': 0.2, 'dur': 2.6, 'side': 'in', 'text': '야 토요일에 치맥 ㄱ?', 'x': 0.03, 'y': 0.04, 'size': 48},
                         {'at': 1.5, 'dur': 1.3, 'side': 'in', 'text': '오랜만에 함 보자', 'x': 0.03, 'y': 0.20, 'size': 48}]},
         sfx=[('ping', 0.2, -18), ('ping', 1.5, -20)]),
    dict(cut='04', img=f'{IMG}/C03_v1.png', still=True, lines=[('changsu', 'L04', 0.3, True)], sub_x=0.5, fx={'cam': {'from': 1.0, 'to': 1.08}}),
    dict(cut='05', img='outputs/ep07/c1/start_v1.png', still=True, dur=1.6, lines=[], sub_x=0.5,
         fx={'cam': {'from': 1.0, 'to': 1.06}, 'tint': {'at': 0.0, 'dur': 1.6, 'color': 'rgba(255,160,185,0.45)', 'fade': 0.25}},
         sfx=[('dream', 0.0, -20), ('gulp', 0.45, -16)], sfx_sub=('꿀꺽', 0.45, 0.8)),
    dict(cut='06', img=f'{IMG}/C06_v1.png', still=True, lines=[('changsu', 'L06a', 0.3, True), ('changsu', 'L06b', 3.2, True)], sub_x=0.5,
         fx={'moves': [{'at': 0.3, 'dur': 2.6, 'scale': 1.06, 'ease': 'power1.inOut'}, {'at': 3.2, 'dur': 1.7, 'scale': 1.13, 'ease': 'power1.inOut'}]}),
    dict(cut='07', img=f'{IMG}/B0_v2.png', still=True, lines=[('misun', 'L07', 0.3, False)], sub_x=0.5, fx={'drift': {'amp': 4, 'period': 2.4}, 'punch': {'at': 0.3, 'scale': 1.03, 'settle': 1.0}}),
    dict(cut='08', img=f'{IMG}/C08_pair.png', still=True, lines=[('changsu', 'L08', 0.3, False)], sub_x=0.5, fx={'drift': {'amp': 4, 'period': 2.4}, 'punch': {'at': 0.3, 'scale': 1.03, 'settle': 1.0}}),
    dict(cut='09', img=f'{IMG}/M09_pair.png', still=True, lines=[('misun', 'L09', 0.3, False)], sub_x=0.5, fx={'drift': {'amp': 4, 'period': 2.4}, 'punch': {'at': 0.3, 'scale': 1.03, 'settle': 1.0}}),
    dict(cut='10', img=f'{IMG}/C10_v1.png', still=True, lines=[('changsu', 'L10a', 0.2, True), ('changsu', 'L10b', 1.35, True)], sub_x=0.5,
         fx={'moves': [{'at': 0.2, 'dur': 0.9, 'scale': 1.07, 'ease': 'power1.inOut'}, {'at': 1.35, 'dur': 0.9, 'scale': 1.14, 'ease': 'power1.inOut'}],
             'toasts': [{'at': 1.3, 'dur': 1.3, 'text': '후....될놈될', 'y': 0.10}], 'sparkle': {'at': 1.3, 'cx': 0.5, 'dur': 1.1}},
         sfx=[('pop', 1.3, -21), ('sparkle', 1.3, -22)]),
    dict(cut='11', img=f'{IMG}/C11_tight.png', still=True, lines=[('changsu', 'L11', 0.3, False)], sub_x=0.5,
         fx={'drift': {'amp': 4, 'period': 2.4}, 'punch': {'at': 0.3, 'scale': 1.03, 'settle': 1.0}, 'toasts': [{'at': 0.25, 'dur': 1.3, 'text': '연기 시작', 'y': 0.10}]}, sfx=[('pop', 0.25, -21)]),
    dict(cut='12', img=f'{IMG}/M09_pair.png', still=True, lines=[('misun', 'L12', 0.3, False)], sub_x=0.5, fx={'drift': {'amp': 4, 'period': 2.4}, 'punch': {'at': 0.3, 'scale': 1.03, 'settle': 1.0}}),
    dict(cut='13', img=f'{IMG}/C13_v1_crop.png', still=True, lines=[('changsu', 'L13', 0.1, False)], sub_x=0.5, quake=True,
         fx={'shake': {'at': 0.1, 'dur': 0.7, 'amp': 10}}, sfx=[('quake', 0.1, -18)]),
    dict(cut='14', img=f'{IMG}/C14_v1.png', still=True, lines=[('changsu', 'L14', 0.3, False)], sub_x=0.5,
         fx={'drift': {'amp': 4, 'period': 2.4}, 'punch': {'at': 0.3, 'scale': 1.03, 'settle': 1.0}, 'toasts': [{'at': 0.3, 'dur': 1.4, 'text': '급수습', 'y': 0.10}]}, sfx=[('pop', 0.3, -21)]),  # 사용자: 창수 움직이지 말 것(몸 통통 제거)
    dict(cut='15', img=f'{IMG}/M15_pair.png', still=True, lines=[('misun', 'L15', 0.3, False)], sub_x=0.5, fx={'drift': {'amp': 4, 'period': 2.4}, 'punch': {'at': 0.3, 'scale': 1.03, 'settle': 1.0}}),
    dict(cut='16', img=f'{IMG}/C16_v1.png', still=True, lines=[('changsu', 'L16', 0.4, False)], sub_x=0.5,
         fx={'cam': {'from': 1.0, 'to': 1.0, 'pan_y': [150, 150]}, 'punch': {'at': 0.4, 'scale': 1.03, 'settle': 1.0},
             'bubbles': [{'at': 0.0, 'dur': 9, 'side': 'in', 'text': '야 토요일에 치맥 ㄱ?', 'x': 0.03, 'y': 0.03, 'size': 44, 'pop': False},
                         {'at': 0.0, 'dur': 9, 'side': 'in', 'text': '오랜만에 함 보자', 'x': 0.03, 'y': 0.17, 'size': 44, 'pop': False},
                         {'at': 0.9, 'dur': 9, 'side': 'out', 'text': '토요일 콜!!!', 'right': 0.03, 'y': 0.31, 'size': 48, 'fade': False}]},
         sfx=[('ping', 1.3, -18)]),
]
SUBS_TEXT = {  # 줄ID → 자막 표기(기획안)
    'L01': '아 이거 진짜 웃기다 ㅋㅋ', 'L04': '(치맥…)', 'L06a': '(토요일에… 자기한테 뭐라고 하지)', 'L06b': '(말할까말까말까말까할까말까)',
    'L07': '자기야.', 'L08': '응, 왜?', 'L09': '나 토요일에 친구들이랑 저녁 먹어도 돼? 좀 늦을 것 같은데.',
    'L10a': '(토요일…?)', 'L10b': '(이게 되네?)', 'L11': '아… 토요일에? 미순이 없이 나 혼자 뭐 하냐…', 'L12': '그런가? 그럼 가지 말까?',
    'L13': '어어어, 아니아니아니.', 'L14': '아니야, 재밌게 놀다 와~ 나도 그냥… 친구나 만나지 뭐.', 'L15': '그래? 그럼 나 잡는다~', 'L16': '야야야 토요일 콜!!!',
}


def dur_of(path):
    out = subprocess.run([FF, '-i', os.path.join(ROOT, path)], capture_output=True, text=True).stderr
    import re
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', out); return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])


def pcm(path):
    d = subprocess.run([FF, '-loglevel', 'error', '-i', os.path.join(ROOT, path), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(d, np.float32).copy()


def cave_light(src, dst, wet=0.22):  # 2026-10-24 사용자: 리버브 줄임(0.45→0.22)
    """ep14_voice.cave_light와 같은 처리: 동굴 IR 컨볼루션을 약하게 섞음(-3dB 뒤), 꼬리 2초."""
    from scipy.signal import fftconvolve
    x = pcm(src); ir = pcm('assets/ir/cave_big.wav'); ir /= np.sqrt((ir ** 2).sum())
    y = np.concatenate([x, np.zeros(int(2.0 * SR), np.float32)]) * 10 ** (-3 / 20)
    out = y + wet * fftconvolve(y, ir)[:len(y)]
    out = np.clip(out, -1, 1)
    raw = (out * 32767).astype('<i2').tobytes()
    subprocess.run([FF, '-y', '-loglevel', 'error', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'libmp3lame', '-q:a', '2', os.path.join(ROOT, dst)], input=raw, check=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--tag', default='v1'); ap.add_argument('--skip-clips', action='store_true'); ap.add_argument('--only-json', action='store_true')
    a = ap.parse_args()
    P = json.load(open(os.path.join(ROOT, 'outputs/voice_profile.json'), encoding='utf-8'))
    LEN = {l['cut']: l['len'] for l in P['episodes'][EP]['lines']}

    # 1) 컷 길이·타임라인
    t = 0.0; subs = []; places = []; sfx_items = []; edit_cuts = []; fx_cuts = {}
    for c in CUTS:
        end_voice = max([at + LEN[lid] for _, lid, at, _ in c['lines']] + [0.0])
        L = round(max(c.get('dur', 0.0), end_voice + TAIL if c['lines'] else 0.0), 3)
        c['L'] = L; c['t'] = round(t, 3)
        for sp, lid, at, inner in c['lines']:
            f = f'{VL}/{lid}.mp3'
            if inner:
                rf = f'{VL}/{lid}_rev.mp3'
                if not a.only_json and not os.path.exists(os.path.join(ROOT, rf)):
                    cave_light(f, rf)
                f = rf
            places.append({'file': f, 'at': round(t + at, 3), 'line': lid, 'inner': inner})
            col = COL[sp] + ('CC' if inner else '')
            subs.append({'start': round(t + at, 3), 'end': round(t + at + LEN[lid] + 0.25, 3), 'speaker': sp, 'text': SUBS_TEXT[lid], 'x': c.get('sub_x', 0.5), 'color': col})
        if c.get('sfx_sub'):
            txt, at, d = c['sfx_sub']
            subs.append({'start': round(t + at, 3), 'end': round(t + at + d, 3), 'speaker': 'sfx', 'text': txt, 'x': 0.5, 'size': 52})
        for name, at, lufs in c.get('sfx', []):
            sfx_items.append({'name': f'{c["cut"]}_{name}', 'file': SFX[name], 'at': round(t + at, 3), 'len': round(min(dur_of(SFX[name]), 2.5), 3), 'target_lufs': lufs, 'fade_out': 0.05})
        if c.get('still'):
            edit_cuts.append({'cut': c['cut'], 'kind': 'still', 'image': c['img'], 'in': 0, 'len': L, 'time_card': None})
        else:
            edit_cuts.append({'cut': c['cut'], 'kind': 'clip', 'source_cut': c['cut'], 'clip_tag': 'v1', 'in': 0.0, 'len': L, 'time_card': None})
        fx = dict(c.get('fx', {}))
        for bb in fx.get('bubbles', []):
            bb['dur'] = round(min(bb['dur'], L - bb['at']), 3)
        if c.get('quake'):
            os.makedirs(os.path.join(ROOT, O, '13'), exist_ok=True)
            bg, layers = pupil_quake.quake(c['img'], [(95, 640, 240, 790), (350, 640, 500, 790)], os.path.join(ROOT, O, '13'), 'quake', 0.1, 0.7, 7)
            fx['puppet'] = {'src_width': 768, 'bg': bg, 'layers': layers}
        fx_cuts[c['cut']] = fx
        t += L
    total = round(t, 3)
    print(f'컷 {len(CUTS)} · 총 {total:.1f}s')

    # 2) JSON
    edit = {'canvas': [1080, 1920], 'fps': 24, 'band': {'top_px': 576, 'window_px': 768}, 'still_zoom': 0.0, 'fade_out_before_black': 0.4, 'cuts': edit_cuts,
            'history': [f'2026-10-24 애니매틱 {a.tag}: 정지 16컷 + 몸 통통 9 + 속마음 리버브·푸시인, Kling 0원, {total:.1f}s']}
    json.dump(edit, open(os.path.join(ROOT, O, 'edit_list.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump({'band_ratio': 0.4, 'default_top': 30, 'per_cut_top': {}, 'note': 'ep19: 전 컷 30(얼굴 y≈0.45)'}, open(os.path.join(ROOT, O, 'band_offsets.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    text = {'title': {'lines': [{'text': '남편이 친구들 약속', 'color': '#FFFFFF'}, {'text': '허락받는 법', 'color': '#FFD84A'}], 'size': 104, 'weight': 800, 'center_y': 400, 'line_gap': 18},
            'channel': {'text': '지독한 미순', 'color': '#FFFFFF', 'size': 52, 'weight': 700, 'center_y': 1420, 'opacity': 0.9},
            'subtitle_style': {'size': 74, 'weight': 800, 'stroke': 9, 'stroke_color': '#111111', 'bottom_margin': 46, 'max_width': 1000, 'colors': {**COL, 'sfx': '#FFFFFF'}},
            'note': 'ep19: 제목 노랑 "허락받는 법"(사용자 확정). 속마음 자막 = 괄호 + 화자 색 80%', 'subtitles': subs}
    json.dump(text, open(os.path.join(ROOT, O, 'text_overlay.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    fxj = {'note': f'ep19 애니매틱 {a.tag}: 속마음 = 리버브 + 푸시인(M18), 알림창, 동공지진(13)', 'default_still': {'cam': None}, 'default_clip': {'cam': None}, 'cuts': fx_cuts,
           'subtitle': {'pop': {'from': 0.6, 'dur': 0.14}, 'shout': {'from': 0.3, 'over': 1.18, 'dur': 0.22, 'shake_amp': 7, 'shake_dur': 0.3, 'rot': -2}},
           'time_card': {'slide_px': -60, 'in': 0.25, 'hold': 1.2, 'out': 0.25}}
    json.dump(fxj, open(os.path.join(ROOT, O, 'hf_fx.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    P['episodes'][EP]['placements'] = places
    json.dump(P, open(os.path.join(ROOT, 'outputs/voice_profile.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.makedirs(os.path.join(ROOT, O, 'sfx'), exist_ok=True)
    json.dump({'note': 'ep19 애니매틱: 효과음 전부 기존 재사용(새 생성 0)', 'items': sfx_items}, open(os.path.join(ROOT, O, 'sfx/sfx_list.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if a.only_json:
        return

    # 3) talk_bob 클립
    if not a.skip_clips:
        env = dict(os.environ, ISNET_MODEL=MODEL)
        for c in CUTS:
            if c.get('still'):
                continue
            out = os.path.join(ROOT, O, c['cut'], 'clip_v1.mp4'); os.makedirs(os.path.dirname(out), exist_ok=True)
            if os.path.exists(out):
                continue
            cmd = [sys.executable, os.path.join(ROOT, 'tools/talk_bob.py'), '--img', os.path.join(ROOT, c['img']), '--out', out, '--dur', str(c['L']), '--push', '1.0']
            for who, box in c['bob'].items():
                cmd += ['--char', f'{who}:{box}']
            for sp, lid, at, inner in c['lines']:
                cmd += ['--line', f'{sp}:{VL}/{lid}.mp3:{at}']  # 상대 경로(윈도우 드라이브 콜론 충돌 회피)
            print('talk_bob', c['cut'], flush=True)
            subprocess.run(cmd, check=True, env=env, cwd=ROOT)

    # 4) 변환 → 렌더 → 믹스
    hf = os.path.join(ROOT, O, 'hf')
    subprocess.run([sys.executable, '-X', 'utf8', os.path.join(ROOT, 'tools/ep_to_hyperframes.py'), '--ep', EP, '--out', hf], check=True, env=dict(os.environ, PYTHONUTF8='1'))
    r = subprocess.run([HF_BIN, 'lint', hf], capture_output=True, text=True); print(r.stdout[-600:])
    vid = os.path.join(hf, f'render_{a.tag}_video.mp4')
    subprocess.run([HF_BIN, 'render', hf, '--fps', '24', '-o', vid, '--quiet'], check=True)
    os.makedirs(os.path.join(ROOT, O, 'roughcut'), exist_ok=True)
    final = os.path.join(ROOT, O, 'roughcut', f'{EP}_animatic_{a.tag}.mp4')
    subprocess.run([sys.executable, '-X', 'utf8', os.path.join(ROOT, 'tools/mix_audio.py'), '--ep', EP, '--video', vid, '--out', final, '--no-bgm'], check=True, env=dict(os.environ, PYTHONUTF8='1'))
    print('완료', final)


if __name__ == '__main__':
    main()
