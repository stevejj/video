#!/usr/bin/env python3
"""ep01 가편집본 조립.
사용: python3 tools/assemble_ep01.py [--out outputs/ep01/roughcut/ep01_roughcut_v1.mp4] [--no-cards]

- outputs/ep01/edit_list.json 의 컷 순서·편집창·길이·시간 카드
- outputs/ep01/band_offsets.json 의 컷별 세로 오프셋(검은 띠 레이아웃)
- 클립: 편집창으로 자르고, 가로 1080으로 확대 후 40% 창(768px)만 잘라 캔버스 22% 위치에 배치
- 정지 컷: 같은 창을 잘라 1→1+zoom 느린 줌
- 시간 카드: 창 왼쪽 위에 1.2초 (타이틀·자막·채널명은 이 단계에서 넣지 않음)
"""
import argparse, json, os, subprocess, sys, tempfile, shutil
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, 'assets/fonts/NotoSansKR-Variable.ttf')
EDIT = os.path.join(ROOT, 'outputs/ep01/edit_list.json')
BAND = os.path.join(ROOT, 'outputs/ep01/band_offsets.json')


def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode:
        sys.stderr.write(r.stderr[-3000:])
        raise SystemExit(f'ffmpeg 실패: {" ".join(cmd[:6])}...')


def card_png(text, path):
    """시간 카드 PNG(반투명 검은 상자 + 흰 글자). ffmpeg 빌드에 drawtext가 없어 overlay로 얹는다."""
    from PIL import Image, ImageDraw
    font = _font(54, 700)
    d0 = ImageDraw.Draw(Image.new('RGBA', (10, 10)))
    x0, y0, x1, y1 = d0.textbbox((0, 0), text, font=font)
    pad = 14
    im = Image.new('RGBA', (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), (0, 0, 0, 140))
    ImageDraw.Draw(im).text((pad - x0, pad - y0), text, font=font, fill=(255, 255, 255, 255))
    im.save(path)


def _font(size, weight):
    from PIL import ImageFont
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def _hex(c, a=255):
    c = c.lstrip('#'); return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), a)


def render_text_layers(T, W, H, top_px, win, tmp):
    """제목·채널명(항상) PNG 1장 + 자막별 PNG. 전부 캔버스 크기 RGBA."""
    from PIL import Image, ImageDraw
    base = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(base)
    t = T['title']; f = _font(t['size'], t['weight'])
    boxes = [d.textbbox((0, 0), ln['text'], font=f) for ln in t['lines']]
    hs = [b[3] - b[1] for b in boxes]; total = sum(hs) + t['line_gap'] * (len(hs) - 1)
    y = t['center_y'] - total / 2
    for ln, b, h in zip(t['lines'], boxes, hs):
        x = (W - (b[2] - b[0])) / 2 - b[0]
        d.text((x, y - b[1]), ln['text'], font=f, fill=_hex(ln['color']))
        y += h + t['line_gap']
    ch = T['channel']; f = _font(ch['size'], ch['weight'])
    b = d.textbbox((0, 0), ch['text'], font=f)
    d.text(((W - (b[2] - b[0])) / 2 - b[0], ch['center_y'] - (b[3] - b[1]) / 2 - b[1]), ch['text'], font=f,
           fill=_hex(ch['color'], int(255 * ch.get('opacity', 1))))
    static = os.path.join(tmp, 'text_static.png'); base.save(static)
    st = T['subtitle_style']; subs = []
    for i, sb in enumerate(T['subtitles']):
        size = st['size']
        while True:
            f = _font(size, st['weight'])
            im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            b = d.textbbox((0, 0), sb['text'], font=f, stroke_width=st['stroke'])
            if b[2] - b[0] <= st['max_width'] or size <= 40:
                break
            size -= 4
        tw, th = b[2] - b[0], b[3] - b[1]
        cx = W * sb['x']; x = min(max(cx - tw / 2, (W - st['max_width']) / 2), W - (W - st['max_width']) / 2 - tw)
        y = top_px + win - st['bottom_margin'] - th
        pad = 6
        im = Image.new('RGBA', (tw + 2 * pad, th + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.text((pad - b[0], pad - b[1]), sb['text'], font=f, fill=_hex(st['colors'][sb['speaker']]),
               stroke_width=st['stroke'], stroke_fill=_hex(st['stroke_color']))
        path = os.path.join(tmp, f'sub_{i:02d}.png'); im.save(path)
        subs.append((path, sb['start'], sb['end'], int(x - pad + im.width / 2), int(y - pad + im.height / 2), sb.get('pop', T.get('subtitle_style', {}).get('pop', True))))
    return static, subs


def apply_fx(seg_in, seg_out, fx_list, L, fps, W, H, top_px, win):
    """02c M4·M7 편집 효과(크레딧 0). 창 영역만 잘라 효과 적용 후 다시 캔버스에 배치.
    fx 항목: {"type":"zoom_punch","at":1.0,"amount":0.10,"dur":0.12}  순간 확대 후 유지
             {"type":"pushin","amount":0.05}                          컷 전체에 걸쳐 느린 확대
             {"type":"shake","at":1.0,"dur":0.35,"px":10}             흔들림
    """
    chain = [f"[0:v]crop={W}:{win}:0:{top_px},scale={W * 2}:{win * 2}:flags=lanczos"]
    zexpr = '1'
    for fx in fx_list:
        t = fx['type']
        if t == 'zoom_punch':
            a, t0, d = fx.get('amount', 0.10), fx['at'], fx.get('dur', 0.12)
            zexpr += f"+{a}*min(1,max(0,(on/{fps}-{t0})/{d}))"
        elif t == 'pushin':
            zexpr += f"+{fx.get('amount', 0.05)}*on/{max(1, int(L * fps))}"
    if zexpr != '1':
        chain.append(f"zoompan=z='{zexpr}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W * 2}x{win * 2}:fps={fps}")
    for fx in fx_list:
        if fx['type'] == 'shake':
            a, t0, d = fx.get('px', 10) * 2, fx['at'], fx.get('dur', 0.35)
            chain.append(f"crop=w=iw-{2 * a}:h=ih-{2 * a}:x='{a}+{a}*sin(t*97)*between(t,{t0},{t0 + d})':y='{a}+{a}*cos(t*83)*between(t,{t0},{t0 + d})'")
    chain.append(f"scale={W}:{win}:flags=lanczos,pad={W}:{H}:0:{top_px}:black,format=yuv420p[out]")
    run([FF, '-y', '-i', seg_in, '-filter_complex', ','.join(chain), '-map', '[out]', '-r', str(fps), '-t', str(L),
         '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', seg_out])


def still_zoom_segment(src, off, W, H, win, top_px, zoom, nfr, fps, card_path, fade, seg):
    import cv2, numpy as np
    im = cv2.imread(src)
    sc = W / im.shape[1]
    im = cv2.resize(im, (W, int(round(im.shape[0] * sc))), interpolation=cv2.INTER_AREA)
    y0 = int(im.shape[0] * off)
    y0 = max(0, min(y0, im.shape[0] - win))
    card = None
    if card_path:
        c = cv2.imread(card_path, cv2.IMREAD_UNCHANGED)
        card = (c[:, :, :3].astype(np.float32), c[:, :, 3:4].astype(np.float32) / 255.0)
    cx, cy = W / 2.0, y0 + win / 2.0
    p = subprocess.Popen([FF, '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
                          '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', seg],
                         stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    canvas = np.zeros((H, W, 3), np.uint8)
    for k in range(nfr):
        z = 1.0 + zoom * k / max(1, nfr - 1)
        # 창 중심을 고정한 채 z배 확대 → 창 좌표계로 이동
        M = np.array([[z, 0, (1 - z) * cx], [0, z, (1 - z) * cy - y0]], np.float32)
        win_img = cv2.warpAffine(im, M, (W, win), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        if card is not None and k < int(1.2 * fps):
            rgb, a = card; h, w = rgb.shape[:2]; x, y = 40, 36
            roi = win_img[y:y + h, x:x + w].astype(np.float32)
            win_img[y:y + h, x:x + w] = (roi * (1 - a) + rgb * a).astype(np.uint8)
        if fade and k >= nfr - int(fade * fps):
            g = (nfr - 1 - k) / max(1, int(fade * fps))
            win_img = (win_img.astype(np.float32) * g).astype(np.uint8)
        canvas[:] = 0
        canvas[top_px:top_px + win] = win_img
        p.stdin.write(canvas.tobytes())
    p.stdin.close(); err = p.stderr.read().decode(); p.wait()
    if p.returncode:
        sys.stderr.write(err[-2000:]); raise SystemExit('still 렌더 실패: ' + src)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(ROOT, 'outputs/ep01/roughcut/ep01_roughcut_v1.mp4'))
    ap.add_argument('--no-cards', action='store_true')
    ap.add_argument('--no-fx', action='store_true', help='edit_list cuts[*].fx 편집 효과 끄기')
    ap.add_argument('--edit', default=None, help='edit_list.json 경로(기본 outputs/<ep>/edit_list.json)')
    ap.add_argument('--voice', action='store_true', help='outputs/voice_profile.json 의 대사를 시작 시각에 배치해 오디오 트랙 추가')
    ap.add_argument('--ep', default='ep01')
    ap.add_argument('--voice-v7', action='store_true', help='lines[*].file_v7(화자별 배속·속마음 톤 후처리본) 사용')
    ap.add_argument('--text', action='store_true', help='outputs/<ep>/text_overlay.json 의 제목·채널명·자막을 얹음')
    ap.add_argument('--bgm', action='store_true', help='voice_profile episodes[ep].bgm 배경음 삽입(대사 더킹)')
    ap.add_argument('--sfx', action='store_true', help='outputs/<ep>/sfx/sfx_list.json 의 효과음을 배치')
    a = ap.parse_args()

    E = json.load(open(a.edit or EDIT)); B = json.load(open(BAND))
    W, H = E['canvas']; fps = E['fps']
    top_px, win = E['band']['top_px'], E['band']['window_px']
    zoom = E['still_zoom']; fade = E['fade_out_before_black']
    tmp = tempfile.mkdtemp(prefix='ep01_asm_')
    segs = []
    cuts = E['cuts']
    for i, c in enumerate(cuts):
        seg = os.path.join(tmp, f'{i:02d}_{c["cut"]}.mp4')
        L = c['len']
        card_in = []; card = ''
        if c.get('time_card') and not a.no_cards:
            cp = os.path.join(tmp, f'card_{i:02d}.png'); card_png(c['time_card'], cp)
            card_in = ['-i', cp]
            card = f"[v0];[v0][1:v]overlay=40:{top_px + 36}:enable='lt(t,1.2)'"
        pad = f"pad={W}:{H}:0:{top_px}:black"
        next_black = i + 1 < len(cuts) and cuts[i + 1]['kind'] == 'black'
        fadef = f",fade=t=out:st={L - fade}:d={fade}" if next_black else ''
        if c['kind'] == 'black':
            run([FF, '-y', '-f', 'lavfi', '-i', f'color=c=black:s={W}x{H}:r={fps}', '-t', str(L),
                 '-pix_fmt', 'yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', seg])
        else:
            src_cut = c['source_cut']
            off = B['per_cut_top'].get(src_cut, B['default_top']) / 100.0
            if c['kind'] == 'clip':
                src = os.path.join(ROOT, f'outputs/ep01/{src_cut}/clip_v1.mp4')
                # 클립 716x1284 → 가로 1080 → 세로 1620 ; 창 y = off*1620
                vf = (f"[0:v]scale={W}:-2,crop={W}:{win}:0:'floor(ih*{off:.4f})',fps={fps},"
                      f"{pad}{card}{fadef},format=yuv420p[out]")
                run([FF, '-y', '-ss', str(c['in']), '-t', str(L), '-i', src, *card_in, '-filter_complex', vf,
                     '-map', '[out]', '-an', '-t', str(L),
                     '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', seg])
            else:
                src = os.path.join(ROOT, f'outputs/ep01/{src_cut}/start_v1.png')
                nfr = int(round(L * fps))
                # 정지: zoompan은 정수 반올림으로 덜컥거려서(프레임간 0.2↔4.7 교차) OpenCV 서브픽셀 워프로 직접 렌더링
                still_zoom_segment(src, off, W, H, win, top_px, zoom, nfr, fps,
                                   card_in[1] if card_in else None, fade if next_black else 0, seg)
        if c.get('fx') and not a.no_fx:
            seg_fx = seg.replace('.mp4', '_fx.mp4'); apply_fx(seg, seg_fx, c['fx'], L, fps, W, H, top_px, win); seg = seg_fx
        segs.append(seg)
        print(f'{c["cut"]:6s} {c["kind"]:5s} {L:4.1f}s  ok' + (f"  fx={[f['type'] for f in c['fx']]}" if c.get('fx') and not a.no_fx else ''), flush=True)

    lst = os.path.join(tmp, 'list.txt')
    with open(lst, 'w') as f:
        for s in segs:
            f.write(f"file '{s}'\n")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    video = a.out if not (a.voice or a.sfx or a.text) else os.path.join(tmp, 'video_only.mp4')
    run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
         '-pix_fmt', 'yuv420p', '-movflags', '+faststart', video])
    if a.text:
        T = json.load(open(os.path.join(ROOT, f'outputs/{a.ep}/text_overlay.json')))
        static, subs = render_text_layers(T, W, H, top_px, win, tmp)
        ins = ['-i', video, '-i', static]; fc = ['[0:v][1:v]overlay=0:0[v1]']
        for k, (pth, st_, en, cx, cy, pop) in enumerate(subs):
            ins += ['-i', pth]
            if pop:
                # 팝업: 0.12초 동안 0.6→1.0 확대(살짝 1.06 오버슈트) 후 고정. 중심 고정 오버레이
                sc = f"min(1.0\\,0.6+(t-{st_})/0.12*0.46)"
                fc.append(f"[{k + 2}:v]scale=w='iw*{sc}':h='ih*{sc}':eval=frame[s{k}]")
                fc.append(f"[v{k + 1}][s{k}]overlay=x='{cx}-w/2':y='{cy}-h/2':enable='between(t,{st_},{en})'[v{k + 2}]")
            else:
                fc.append(f"[v{k + 1}][{k + 2}:v]overlay=x='{cx}-w/2':y='{cy}-h/2':enable='between(t,{st_},{en})'[v{k + 2}]")
        texted = os.path.join(tmp, 'video_text.mp4')
        last = f'[v{len(subs) + 1}]'
        fc[-1] = fc[-1].rsplit('[', 1)[0] + '[vout]'
        run([FF, '-y', *ins, '-filter_complex', ';'.join(fc), '-map', '[vout]', '-c:v', 'libx264', '-preset', 'medium',
             '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', texted])
        print(f'글자: 제목·채널명 + 자막 {len(subs)}개')
        if not (a.voice or a.sfx):
            shutil.copy(texted, a.out)
        video = texted
    if a.voice or a.sfx or a.bgm:
        total = sum(c['len'] for c in cuts)
        inputs = ['-i', video]; fc = []; n = 0; voice_labels = []
        if a.voice:
            P = json.load(open(os.path.join(ROOT, 'outputs/voice_profile.json')))
            seen = set()
            for l in P['episodes'][a.ep]['lines']:
                f = l.get('file_v7') if a.voice_v7 else l.get('file')
                if not f or f in seen or 'at' not in l:
                    continue
                seen.add(f); n += 1; inputs += ['-i', os.path.join(ROOT, f)]
                fc.append(f"[{n}:a]aresample=44100,aformat=channel_layouts=mono,adelay={int(l['at'] * 1000)}[a{n}]"); voice_labels.append(f'a{n}')
            print(f'음성 {len(seen)}개')
        if a.sfx:
            X = json.load(open(os.path.join(ROOT, f'outputs/{a.ep}/sfx/sfx_list.json')))
            for it in X['items']:
                n += 1; inputs += ['-i', os.path.join(ROOT, it['file'])]
                chain = "aresample=44100,aformat=channel_layouts=mono"
                if it.get('loop'):
                    chain += ",aloop=loop=-1:size=44100*60"
                chain += f",atrim=0:{it['len']},asetpts=PTS-STARTPTS"
                if it.get('fade_in'):
                    chain += f",afade=t=in:st=0:d={it['fade_in']}"
                if it.get('fade_out'):
                    chain += f",afade=t=out:st={it['len'] - it['fade_out']}:d={it['fade_out']}"
                chain += f",volume={it['gain']}dB,adelay={int(it['at'] * 1000)}"
                fc.append(f"[{n}:a]{chain}[a{n}]")
            print(f"효과음 {len(X['items'])}개")
        labels = [f'a{i}' for i in range(1, n + 1)]
        if a.bgm:
            P = json.load(open(os.path.join(ROOT, 'outputs/voice_profile.json')))
            B = P['episodes'][a.ep].get('bgm')
            if B:
                import re as _re
                bf = os.path.join(ROOT, B['file'])
                meas = subprocess.run([FF, '-i', bf, '-af', 'loudnorm=print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
                cur = float(json.loads(_re.search(r'\{.*\}', meas, _re.S).group(0))['input_i'])
                gain = B['target_lufs'] - cur
                end = B['end_at']; n += 1; inputs += ['-i', bf]
                fc.append(f"[{n}:a]aresample=44100,aformat=channel_layouts=mono,aloop=loop=-1:size=44100*120,atrim=0:{end},asetpts=PTS-STARTPTS,"
                          f"volume={gain:.2f}dB,afade=t=in:st=0:d={B['fade_in']},afade=t=out:st={end - B['fade_out']}:d={B['fade_out']}[bgm_raw]")
                if voice_labels:
                    # 대사 합을 사이드체인으로 배경음 더킹
                    fc.append(''.join(f'[{v}]' for v in voice_labels) + f"amix=inputs={len(voice_labels)}:normalize=0,apad=whole_dur={total},asplit[vsum][vsc]")
                    ratio = 1 + B['duck_db'] / 3.0
                    fc.append(f"[bgm_raw][vsc]sidechaincompress=threshold=0.02:ratio={ratio:.2f}:attack=30:release=400:makeup=1[bgm]")
                    labels = [x for x in labels if x not in voice_labels] + ['vsum', 'bgm']
                else:
                    labels.append('bgm_raw')
                print(f"배경음 {os.path.basename(bf)} gain {gain:+.1f}dB, {end}s까지")
        fc.append(''.join(f'[{x}]' for x in labels) + f"amix=inputs={len(labels)}:normalize=0,apad=whole_dur={total},alimiter=limit=0.85:level=false[mix]")
        run([FF, '-y', *inputs, '-filter_complex', ';'.join(fc), '-map', '0:v', '-map', '[mix]', '-c:v', 'copy',
             '-c:a', 'aac', '-b:a', '160k', '-t', str(total), '-movflags', '+faststart', a.out])
    shutil.rmtree(tmp, ignore_errors=True)
    print('완료:', a.out)


if __name__ == '__main__':
    main()
