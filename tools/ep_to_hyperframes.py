#!/usr/bin/env python3
"""edit_list/band_offsets/text_overlay(+hf_fx)에서 HyperFrames 구성(index.html)을 생성한다.
사용: python3 tools/ep_to_hyperframes.py --ep ep01 --out outputs/ep01/hf
렌더: (HYPERFRAMES_FFMPEG_PATH/FFPROBE_PATH 설정 후) npx hyperframes@latest render <out> --fps 24 -o <mp4>
오디오는 v10 ffmpeg 믹스를 그대로 mux한다(tools/hf_render.sh).
"""
import argparse, json, os, shutil, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ep', default='ep01')
    ap.add_argument('--out', default=None)
    ap.add_argument('--edit', default=None)
    a = ap.parse_args()
    ep = a.ep
    out = a.out or os.path.join(ROOT, f'outputs/{ep}/hf')
    os.makedirs(os.path.join(out, 'media'), exist_ok=True)
    E = json.load(open(a.edit or os.path.join(ROOT, f'outputs/{ep}/edit_list.json')))
    B = json.load(open(os.path.join(ROOT, f'outputs/{ep}/band_offsets.json')))
    T = json.load(open(os.path.join(ROOT, f'outputs/{ep}/text_overlay.json')))
    FX = json.load(open(os.path.join(ROOT, f'outputs/{ep}/hf_fx.json')))
    W, H = E['canvas']; fps = E['fps']
    top, win = E['band']['top_px'], E['band']['window_px']
    fade = E['fade_out_before_black']
    shutil.copy(os.path.join(ROOT, 'assets/fonts/NotoSansKR-Variable.ttf'), os.path.join(out, 'media/NotoSansKR.ttf'))
    gs = os.path.join(ROOT, 'assets/vendor/gsap.min.js')
    if os.path.exists(gs):
        shutil.copy(gs, os.path.join(out, 'gsap.min.js'))

    media_html, tl = [], []
    t = 0.0; total = 0.0
    cuts_info = []
    for c in E['cuts']:
        L = float(c['len'])
        if c['kind'] == 'black':
            t += L; continue
        src_cut = c.get('source_cut', c['cut'])
        off = B['per_cut_top'].get(src_cut, B['default_top']) / 100.0
        offy = off * H  # 프레임을 1080x1920으로 본 뒤 창에 들어가는 구간의 시작
        cid = 'c' + c['cut'].replace('-', '_')
        fx = dict(FX['default_still'] if c['kind'] == 'still' else FX['default_clip'])
        fx.update(FX['cuts'].get(c['cut'], {}))
        pp = fx.get('puppet')
        if pp:
            S = W / pp['src_width']
            shutil.copy(os.path.join(ROOT, pp['bg']), os.path.join(out, f'media/{src_cut}_bg.png'))
            el = f'<img id="{cid}-v" src="media/{src_cut}_bg.png" data-start="{t:.3f}" data-duration="{L:.3f}" />'
            for ly in pp['layers']:
                shutil.copy(os.path.join(ROOT, ly['img']), os.path.join(out, f'media/{src_cut}_{ly["id"]}.png'))
                x, y, w, h = [v * S for v in ly['box']]
                origin = ly.get('origin') or f'{(ly["pivot"][0] - ly["box"][0]) * S:.1f}px {(ly["pivot"][1] - ly["box"][1]) * S:.1f}px'
                el += (f'<img id="{cid}-{ly["id"]}" class="layer" src="media/{src_cut}_{ly["id"]}.png" data-start="{t:.3f}" data-duration="{L:.3f}" '
                       f'style="left:{x:.1f}px; top:{y:.1f}px; width:{w:.1f}px; height:{h:.1f}px; transform-origin:{origin};" />')
                if ly.get('init'):
                    tl.append(f'tl.set("#{cid}-{ly["id"]}", {json.dumps(ly["init"])}, 0);')
                for k in ly.get('keys', []):
                    props = {kk: v for kk, v in k.items() if kk not in ('t', 'dur', 'ease')}
                    tl.append(f'tl.to("#{cid}-{ly["id"]}", {{...{json.dumps(props)}, duration: {k["dur"]}, ease: "{k.get("ease", "none")}"}}, {t + k["t"]:.3f});')
            import random
            tp = pp.get('taps'); rnd = random.Random(tp['seed']) if tp else None; tt = tp['from'] if tp else 1e9; i = 0
            while tp and tt < tp['to']:
                ly = pp['layers'][i % len(pp['layers'])]; d = rnd.choice(tp['dur'])
                tl.append(f'tl.to("#{cid}-{ly["id"]}", {{rotation: {ly["rot"]}, y: {ly["lift"]}, duration: {d}, ease: "power2.out"}}, {t + tt:.3f});')
                tl.append(f'tl.to("#{cid}-{ly["id"]}", {{rotation: 0, y: 0, duration: {d + 0.03:.2f}, ease: "power2.in"}}, {t + tt + d:.3f});')
                tt += rnd.choice(tp['gap']); i += 1
        elif c['kind'] == 'clip':
            src = os.path.join(ROOT, f'outputs/{ep}/{src_cut}/clip_v1.mp4'); dst = f'media/{src_cut}.mp4'
            shutil.copy(src, os.path.join(out, dst))
            el = (f'<video id="{cid}-v" src="{dst}" data-start="{t:.3f}" data-duration="{L:.3f}" '
                  f'data-media-start="{float(c.get("in", 0)):.3f}" muted></video>')
        else:
            src = os.path.join(ROOT, f'outputs/{ep}/{src_cut}/start_v1.png'); dst = f'media/{src_cut}.png'
            shutil.copy(src, os.path.join(out, dst))
            el = f'<img id="{cid}-v" src="{dst}" data-start="{t:.3f}" data-duration="{L:.3f}" />'
        # 래퍼는 타이밍 없음(video_nested_in_timed_element 회피). transform-origin = 창 중심
        media_html.append(f'<div class="frame" id="{cid}" style="top:{-offy:.1f}px; transform-origin: 540px {offy + win / 2:.1f}px;">{el}</div>')
        # 카메라
        cam = fx.get('cam')
        if cam:
            fr = dict(scale=cam['from'], x=cam.get('pan_x', [0, 0])[0], y=cam.get('pan_y', [0, 0])[0])
            to = dict(scale=cam['to'], x=cam.get('pan_x', [0, 0])[1], y=cam.get('pan_y', [0, 0])[1], duration=L, ease='none')
            tl.append(f'tl.fromTo("#{cid}", {json.dumps(fr)}, {json.dumps(to)}, {t:.3f});')
        dr = fx.get('drift')
        if dr and not fx.get('shake') and not fx.get('jitter'):
            n = max(1, int(L / dr['period'] * 2))
            for i in range(n):
                tl.append(f'tl.to("#{cid}", {{x: {dr["amp"] * (1 if i % 2 else -1):.1f}, y: {dr["amp"] * 0.6 * (1 if i % 4 < 2 else -1):.1f}, duration: {dr["period"] / 2:.2f}, ease: "sine.inOut"}}, {t + i * dr["period"] / 2:.3f});')
        p = fx.get('punch')
        if p:
            at = t + p['at']
            tl.append(f'tl.to("#{cid}", {{scale: {p["scale"]}, duration: 0.08, ease: "power3.out", overwrite: "auto"}}, {at:.3f});')
            tl.append(f'tl.to("#{cid}", {{scale: {p["settle"]}, duration: 0.35, ease: "power2.out"}}, {at + 0.08:.3f});')
        s = fx.get('shake')
        if s:
            at = t + s['at']; n = max(3, int(s['dur'] * 24))
            for i in range(n):
                amp = s['amp'] * (1 - i / n) if not s.get('grow') else s['amp'] * (0.3 + 0.7 * i / n)
                dx = amp * (1 if i % 2 == 0 else -1) * (0.8 if i % 3 else 1.0)
                dy = amp * 0.5 * (1 if i % 4 < 2 else -1)
                tl.append(f'tl.to("#{cid}", {{x: {dx:.1f}, y: {dy:.1f}, duration: {1 / 24:.4f}, ease: "none"}}, {at + i / 24:.3f});')
            tl.append(f'tl.to("#{cid}", {{x: 0, y: 0, duration: 0.08}}, {at + n / 24:.3f});')
        j = fx.get('jitter')
        if j:
            n = int((j['to'] - j['from']) * j['hz'])
            for i in range(n):
                tl.append(f'tl.to("#{cid}", {{x: {j["amp"] * (1 if i % 2 else -1):.1f}, y: {j["amp"] * 0.6 * (1 if i % 3 else -1):.1f}, duration: {1 / j["hz"]:.4f}, ease: "none"}}, {t + j["from"] + i / j["hz"]:.3f});')
            tl.append(f'tl.to("#{cid}", {{x: 0, y: 0, duration: 0.1}}, {t + j["to"]:.3f});')
        sp = fx.get('sparkle')
        if sp:
            at = t + sp['at']
            for k in range(6):
                sx = int(W * sp['cx'] + [-150, -60, 40, 130, -110, 90][k]); sy = top + win - 150 + sp.get('dy', 0) + [-120, -200, -90, -170, -40, -230][k]
                media_html.append(f'<div class="spark" id="{cid}-sp{k}" style="left:{sx}px; top:{sy}px;">✦</div>')
                d = at + 0.08 * k
                tl.append(f'tl.fromTo("#{cid}-sp{k}", {{scale: 0, opacity: 0, rotation: -30}}, {{scale: 1, opacity: 1, rotation: 20, duration: 0.25, ease: "back.out(3)"}}, {d:.3f});')
                tl.append(f'tl.to("#{cid}-sp{k}", {{scale: 0.2, opacity: 0, duration: 0.3}}, {d + sp["dur"] - 0.5:.3f});')
        # 시간 카드
        if c.get('time_card'):
            tc = FX['time_card']
            media_html.append(f'<div class="card" id="{cid}-card" data-start="{t:.3f}" data-duration="{tc["in"] + tc["hold"] + tc["out"]:.3f}">{c["time_card"]}</div>')
            tl.append(f'tl.fromTo("#{cid}-card", {{x: {tc["slide_px"]}, opacity: 0}}, {{x: 0, opacity: 1, duration: {tc["in"]}, ease: "power3.out"}}, {t:.3f});')
            tl.append(f'tl.to("#{cid}-card", {{opacity: 0, duration: {tc["out"]}}}, {t + tc["in"] + tc["hold"]:.3f});')
        cuts_info.append((c['cut'], t, L, c['kind']))
        if c['cut'] == '10-02' or (c['kind'] != 'black' and E['cuts'][E['cuts'].index(c) + 1]['kind'] == 'black' if E['cuts'].index(c) + 1 < len(E['cuts']) else False):
            media_html.append(f'<div class="blackfade" id="{cid}-fade" data-start="{t + L - fade:.3f}" data-duration="{fade:.3f}"></div>')
            tl.append(f'tl.fromTo("#{cid}-fade", {{opacity: 0}}, {{opacity: 1, duration: {fade}, ease: "none"}}, {t + L - fade:.3f});')
        t += L
    total = t

    # 자막
    st = T['subtitle_style']; sub_html = []
    SP = FX['subtitle']
    for i, sb in enumerate(T['subtitles']):
        sid = f'sub{i:02d}'; dur = sb['end'] - sb['start']
        shout = '!!' in sb['text']
        cx = W * sb.get('x', 0.5)
        posstyle = f' top:{top + 40}px; bottom:auto;' if sb.get('pos') == 'top' else ''
        sub_html.append(f'<div class="sub" id="{sid}" data-start="{sb["start"]:.3f}" data-duration="{dur:.3f}" data-cx="{cx:.0f}" style="color:{st["colors"][sb["speaker"]]};{posstyle}">{html.escape(sb["text"])}</div>')
        if shout:
            s = SP['shout']
            tl.append(f'tl.fromTo("#{sid}", {{scale: {s["from"]}, rotation: {s["rot"]}, opacity: 0}}, {{scale: {s["over"]}, rotation: 0, opacity: 1, duration: {s["dur"] * 0.6:.3f}, ease: "power3.out"}}, {sb["start"]:.3f});')
            tl.append(f'tl.to("#{sid}", {{scale: 1, duration: {s["dur"] * 0.4:.3f}, ease: "power2.inOut"}}, {sb["start"] + s["dur"] * 0.6:.3f});')
            n = int(s['shake_dur'] * 24)
            for k in range(n):
                tl.append(f'tl.to("#{sid}", {{x: {s["shake_amp"] * (1 - k / n) * (1 if k % 2 else -1):.1f}, duration: {1 / 24:.4f}, ease: "none"}}, {sb["start"] + k / 24:.3f});')
            tl.append(f'tl.to("#{sid}", {{x: 0, duration: 0.05}}, {sb["start"] + n / 24:.3f});')
        else:
            p = SP['pop']
            tl.append(f'tl.fromTo("#{sid}", {{scale: {p["from"]}, opacity: 0}}, {{scale: 1, opacity: 1, duration: {p["dur"]}, ease: "back.out(2.5)"}}, {sb["start"]:.3f});')

    ti = T['title']; ch = T['channel']
    title_html = ''.join(f'<div style="color:{ln["color"]}">{html.escape(ln["text"])}</div>' for ln in ti['lines'])
    page = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width={W}, height={H}" />
<title>{ep} v11 hyperframes</title>
<script src="gsap.min.js"></script>
<style>
  @font-face {{ font-family: "NotoKR"; src: url("media/NotoSansKR.ttf") format("truetype"); font-weight: 100 900; }}
  body {{ margin: 0; background: #000; font-family: "NotoKR", sans-serif; }}
  #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #000; }}
  #win {{ position: absolute; left: 0; top: {top}px; width: {W}px; height: {win}px; overflow: hidden; background: #000; }}
  .frame {{ position: absolute; left: 0; width: {W}px; height: {H}px; will-change: transform; }}
  .frame img.layer {{ position: absolute; width: auto; height: auto; object-fit: fill; }}
  .frame img:not(.layer), .frame video {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; display: block; }}
  #title {{ position: absolute; left: 0; width: 100%; top: {ti['center_y'] - ti['size'] - ti['line_gap'] / 2:.0f}px; text-align: center; font-size: {ti['size']}px; font-weight: {ti['weight']}; line-height: {ti['size'] + ti['line_gap']}px; }}
  #channel {{ position: absolute; left: 0; width: 100%; top: {ch['center_y'] - ch['size'] * 0.7:.0f}px; text-align: center; font-size: {ch['size']}px; font-weight: {ch['weight']}; color: {ch['color']}; opacity: {ch.get('opacity', 1)}; line-height: 1.4; }}
  .sub {{ position: absolute; bottom: {H - top - win + st['bottom_margin']}px; font-size: {st['size']}px; font-weight: {st['weight']}; white-space: nowrap; line-height: 1.25;
          -webkit-text-stroke: {st['stroke']}px {st['stroke_color']}; paint-order: stroke fill; transform-origin: 50% 100%; }}
  .card {{ position: absolute; left: 40px; top: {top + 36}px; font-size: 54px; font-weight: 700; color: #fff; text-shadow: 2px 2px 0 #000, 0 0 6px #000; line-height: 1.2; }}
  .spark {{ position: absolute; font-size: 64px; color: #FFE27A; text-shadow: 0 0 12px #FFD84A; transform-origin: 50% 50%; }}
  .blackfade {{ position: absolute; inset: 0; background: #000; }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-duration="{total:.3f}" data-fps="{fps}">
  <div id="win">
    {chr(10).join('    ' + m for m in media_html if 'class="frame"' in m or 'blackfade' in m)}
  </div>
  <div id="title">{title_html}</div>
  <div id="channel">{html.escape(ch['text'])}</div>
  {chr(10).join('  ' + m for m in media_html if 'class="card"' in m or 'class="spark"' in m)}
  {chr(10).join('  ' + s for s in sub_html)}
</div>
<script>
  // 자막 가로 위치: 중심 cx, 폭 {st['max_width']} 안으로 클램프 (조립기와 동일 규칙)
  function placeSubs() {{
    document.querySelectorAll('.sub').forEach(el => {{
      const cx = parseFloat(el.dataset.cx); const W = {W}, MW = {st['max_width']};
      let fs = {st['size']}; el.style.fontSize = fs + 'px';
      while (el.offsetWidth > MW && fs > 40) {{ fs -= 4; el.style.fontSize = fs + 'px'; }}
      const tw = el.offsetWidth;
      let x = Math.min(Math.max(cx - tw / 2, (W - MW) / 2), W - (W - MW) / 2 - tw);
      el.style.left = x + 'px';
    }});
  }}
  const tl = gsap.timeline({{ paused: true }});
  function build() {{
    placeSubs();
    {chr(10).join('    ' + x for x in tl)}
    window.__timelines["main"] = tl;
  }}
  if (document.fonts && document.fonts.ready) {{ document.fonts.ready.then(build); }} else {{ build(); }}
</script>
</body>
</html>
'''
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(page)
    json.dump({'total': total, 'cuts': cuts_info}, open(os.path.join(out, 'cuts.json'), 'w'), ensure_ascii=False, indent=1)
    print(f'wrote {out}/index.html  total {total:.2f}s  cuts {len(cuts_info)}  tweens {len(tl)}')


if __name__ == '__main__':
    main()
