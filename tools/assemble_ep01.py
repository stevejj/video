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
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype(FONT, 54)
    d0 = ImageDraw.Draw(Image.new('RGBA', (10, 10)))
    x0, y0, x1, y1 = d0.textbbox((0, 0), text, font=font)
    pad = 14
    im = Image.new('RGBA', (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), (0, 0, 0, 140))
    ImageDraw.Draw(im).text((pad - x0, pad - y0), text, font=font, fill=(255, 255, 255, 255))
    im.save(path)


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
    a = ap.parse_args()

    E = json.load(open(EDIT)); B = json.load(open(BAND))
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
        segs.append(seg)
        print(f'{c["cut"]:6s} {c["kind"]:5s} {L:4.1f}s  ok', flush=True)

    lst = os.path.join(tmp, 'list.txt')
    with open(lst, 'w') as f:
        for s in segs:
            f.write(f"file '{s}'\n")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
         '-pix_fmt', 'yuv420p', '-movflags', '+faststart', a.out])
    shutil.rmtree(tmp, ignore_errors=True)
    print('완료:', a.out)


if __name__ == '__main__':
    main()
