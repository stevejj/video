#!/usr/bin/env python3
"""edit_list/band_offsets/text_overlay(+hf_fx)에서 HyperFrames 구성(index.html)을 생성한다.
사용: python3 tools/ep_to_hyperframes.py --ep ep01 --out outputs/ep01/hf
렌더: (HYPERFRAMES_FFMPEG_PATH/FFPROBE_PATH 설정 후) npx hyperframes@latest render <out> --fps 24 -o <mp4>
오디오는 v10 ffmpeg 믹스를 그대로 mux한다(tools/hf_render.sh).
"""
import argparse, json, os, shutil, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def grab_frame(src, t, dst, crop_top=None, crop_h=None):
    """영상(t초)이나 이미지에서 한 프레임을 1080x1920 PNG로. crop_top·crop_h(비율)를 주면 그 띠만 잘라냄(회상 화면)."""
    import subprocess, imageio_ffmpeg
    vf = 'scale=1080:1920'
    if crop_top is not None:
        vf += f',crop=1080:{int(1920 * crop_h)}:0:{int(1920 * crop_top)}'
    args = ['-ss', f'{t:.3f}', '-i', src] if src.endswith('.mp4') else ['-i', src]
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-v', 'error', *args, '-frames:v', '1', '-vf', vf, dst], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ep', default='ep01')
    ap.add_argument('--out', default=None)
    ap.add_argument('--edit', default=None)
    ap.add_argument('--fx', default=None)
    ap.add_argument('--text', default=None)
    a = ap.parse_args()
    ep = a.ep
    out = a.out or os.path.join(ROOT, f'outputs/{ep}/hf')
    os.makedirs(os.path.join(out, 'media'), exist_ok=True)
    E = json.load(open(a.edit or os.path.join(ROOT, f'outputs/{ep}/edit_list.json')))
    B = json.load(open(os.path.join(ROOT, f'outputs/{ep}/band_offsets.json')))
    T = json.load(open(a.text or os.path.join(ROOT, f'outputs/{ep}/text_overlay.json')))
    FX = json.load(open(a.fx or os.path.join(ROOT, f'outputs/{ep}/hf_fx.json')))
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
        ui = fx.get('ui')
        if ui and c['kind'] == 'ui':
            if ui['kind'] == 'counter':
                el = (f'<div id="{cid}-v" class="uibox" data-start="{t:.3f}" data-duration="{L:.3f}">'
                      f'<div class="uilabel">{ui["label"]}</div><div class="uinum" id="{cid}-num">{ui["from"]}회차</div>'
                      f'<div class="uiclock">{ui["clock"]}</div></div>')
                tl.append(f'tl.fromTo("#{cid}-v", {{scale: 0.7, opacity: 0}}, {{scale: 1, opacity: 1, duration: 0.2, ease: "back.out(2)"}}, {t:.3f});')
                tl.append(f'tl.to("#{cid}-num", {{scale: 1.35, duration: 0.08, yoyo: true, repeat: 1, onStart: () => {{ document.getElementById("{cid}-num").textContent = "{ui["to"]}회차"; }}}}, {t + 0.6:.3f});')
            else:
                S = W / ui['src_width']
                shutil.copy(os.path.join(ROOT, ui['base']), os.path.join(out, f'media/{src_cut}_base.png'))
                cx, cy, r = ui['center'][0] * S, ui['center'][1] * S, ui['radius'] * S
                left = ui.get('arrow_side', 'right') == 'left'   # 화살표를 동그라미 왼쪽에 두고 ▶ 로 가리킴
                ax = cx - r - 20 - 70 if left else cx + r + 20
                glyph = '▶' if left else '◀'; sgn = -1 if left else 1
                el = (f'<img id="{cid}-v" src="media/{src_cut}_base.png" data-start="{t:.3f}" data-duration="{L:.3f}" />'
                      f'<div id="{cid}-ring" class="ring" data-start="{t:.3f}" data-duration="{L:.3f}" style="left:{cx - r:.0f}px; top:{cy - r:.0f}px; width:{2 * r:.0f}px; height:{2 * r:.0f}px;"></div>'
                      f'<div id="{cid}-arrow" class="arrow" data-start="{t:.3f}" data-duration="{L:.3f}" style="left:{ax:.0f}px; top:{cy - 50:.0f}px;">{glyph}</div>')
                tl.append(f'tl.fromTo("#{cid}-ring", {{scale: 2, opacity: 0}}, {{scale: 1, opacity: 1, duration: 0.25, ease: "power3.out"}}, {t + 0.1:.3f});')
                tl.append(f'tl.fromTo("#{cid}-arrow", {{x: {30 * sgn}, opacity: 0}}, {{x: 0, opacity: 1, duration: 0.2, ease: "back.out(3)"}}, {t + 0.3:.3f});')
                tl.append(f'tl.to("#{cid}-arrow", {{x: {12 * sgn}, duration: 0.25, yoyo: true, repeat: 3, ease: "sine.inOut"}}, {t + 0.5:.3f});')
                fx = dict(fx); fx['cam'] = {'from': 1.0, 'to': ui.get('zoom', 1.25)}
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
                       f'style="left:{x:.1f}px; top:{y:.1f}px; width:{w:.1f}px; height:{h:.1f}px; transform-origin:{origin};{" opacity:0;" if (ly.get("init") or {}).get("opacity") == 0 else ""}" />')   # 0초 프레임에 숨김이 안 먹는 문제(tl.set) → CSS로도 숨김
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
        elif ui and c['kind'] == 'ui':
            pass
        elif c['kind'] == 'clip':
            src = os.path.join(ROOT, f'outputs/{ep}/{src_cut}/clip_{c.get("clip_tag", "v1")}.mp4'); dst = f'media/{src_cut}.mp4'
            shutil.copy(src, os.path.join(out, dst))
            el = (f'<video id="{cid}-v" src="{dst}" data-start="{t:.3f}" data-duration="{L:.3f}" '
                  f'data-media-start="{float(c.get("in", 0)):.3f}" muted></video>')
        else:
            src = os.path.join(ROOT, c['image']) if c.get('image') else os.path.join(ROOT, f'outputs/{ep}/{src_cut}/start_v1.png'); dst = f'media/{c["cut"]}.png'
            shutil.copy(src, os.path.join(out, dst))
            el = f'<img id="{cid}-v" src="{dst}" data-start="{t:.3f}" data-duration="{L:.3f}" />'
        # 화면 안에서 카메라와 같이 움직이는 효과(정지 화면·영혼 탈출): 프레임 좌표(1080x1920)
        frame_src = src if c['kind'] == 'clip' else (os.path.join(ROOT, c['image']) if c.get('image') else None)
        fz = fx.get('freeze')
        if fz and frame_src:  # 그 순간 프레임을 이미지로 덮어 멈춘 것처럼 보이게(카메라 줌은 계속)
            png = f'media/{cid}_freeze.png'
            grab_frame(frame_src, float(c.get('in', 0)) + fz['at'] if c['kind'] == 'clip' else 0, os.path.join(out, png))
            el += f'<img id="{cid}-fz" src="{png}" data-start="{t + fz["at"]:.3f}" data-duration="{L - fz["at"]:.3f}" style="{"filter: grayscale(1);" if fz.get("gray") else ""}" />'
            if fz.get('zoom'):
                tl.append(f'tl.to("#{cid}", {{scale: {fz["zoom"]}, x: {fz.get("x", 0)}, duration: {L - fz["at"]:.3f}, ease: "power1.out", overwrite: "auto"}}, {t + fz["at"]:.3f});')
        for gi, gh in enumerate(fx.get('ghosts') or ([fx['ghost']] if fx.get('ghost') else [])):  # 영혼 탈출(여러 명 가능): 누끼 레이어가 반투명으로 떠오름
            S = W / gh['src_width']; x, y, w, h = [v * S for v in gh['box']]
            shutil.copy(os.path.join(ROOT, gh['img']), os.path.join(out, f'media/{cid}_ghost{gi}.png'))
            el += (f'<img id="{cid}-gh{gi}" class="layer" src="media/{cid}_ghost{gi}.png" data-start="{t + gh["at"]:.3f}" data-duration="{gh["dur"]:.3f}" '
                   f'style="left:{x:.1f}px; top:{y:.1f}px; width:{w:.1f}px; height:{h:.1f}px; opacity:0; filter: brightness(1.6) saturate(0.3);" />')
            tl.append(f'tl.fromTo("#{cid}-gh{gi}", {{opacity: 0, y: 0}}, {{opacity: {gh.get("opacity", 0.55)}, y: {-gh.get("rise", 260)}, duration: {gh["dur"]:.3f}, ease: "power1.out"}}, {t + gh["at"]:.3f});')
            for k in range(int(gh['dur'] / 0.4)):
                tl.append(f'tl.to("#{cid}-gh{gi}", {{x: {14 * (1 if k % 2 else -1)}, duration: 0.4, ease: "sine.inOut"}}, {t + gh["at"] + k * 0.4:.3f});')
        stk = fx.get('spot_track')
        if stk:  # 따라가는 핀 조명(ep09 v2): 프레임 안에 넣어 카메라 줌·이동과 같이 움직이고, 얼굴 추적점(face_track)을 따라감
            pts_ = stk['pts']; R = 2880; px0, py0 = pts_[0][1], pts_[0][2]; r0 = stk.get('r', 250)
            el += (f'<div class="layer spottrack" id="{cid}-stk" data-start="{t + stk["at"]:.3f}" data-duration="{stk["dur"]:.3f}" '
                   f'style="left:{px0 - R}px; top:{py0 - R}px; width:{2 * R}px; height:{2 * R}px; opacity:0; '
                   f'background: radial-gradient(circle {r0}px at 50% 50%, rgba(255,240,200,0.10) 0%, rgba(255,240,200,0.05) 70%, rgba(0,0,0,{stk.get("dark", 0.75)}) 100%);"></div>')
            tl.append(f'tl.fromTo("#{cid}-stk", {{opacity: 0}}, {{opacity: 1, duration: 0.15, ease: "power2.out"}}, {t + stk["at"]:.3f});')
            for (ta, xa, ya), (tb, xb, yb) in zip(pts_, pts_[1:]):
                if tb <= stk['at']:
                    continue
                tl.append(f'tl.to("#{cid}-stk", {{x: {xb - px0}, y: {yb - py0}, duration: {tb - max(ta, stk["at"]):.3f}, ease: "none"}}, {t + max(ta, stk["at"]):.3f});')
        # 래퍼는 타이밍 없음(video_nested_in_timed_element 회피). transform-origin = 창 중심
        for k, ov in enumerate(fx.get('overlays', [])):  # 창 전체 이미지 덮개(ep05 v2 뷰파인더): 서서히 나타났다 사라짐
            oid = f'{cid}-ov{k}'; d0 = t + ov['at']; fd = ov.get('fade', 0.15)
            shutil.copy(os.path.join(ROOT, ov['img']), os.path.join(out, f'media/{cid}_ov{k}.png'))
            media_html.append(f'<img class="winfx" id="{oid}" src="media/{cid}_ov{k}.png" data-start="{d0:.3f}" data-duration="{ov["dur"]:.3f}" style="opacity:0; z-index:4;" />')
            tl.append(f'tl.fromTo("#{oid}", {{opacity: 0}}, {{opacity: 1, duration: {fd}, ease: "power1.out"}}, {d0:.3f});')
            tl.append(f'tl.to("#{oid}", {{opacity: 0, duration: {fd}, ease: "power1.in"}}, {d0 + ov["dur"] - fd:.3f});')
            if ov.get('focus'):   # 가운데 초점 사각형이 작아지며 맞춰짐
                f_ = ov['focus']; fid = f'{oid}-f'
                media_html.append(f'<div class="winfx focusbox" id="{fid}" data-start="{d0:.3f}" data-duration="{ov["dur"]:.3f}" style="left:{f_["x"] * W - f_["size"] / 2:.0f}px; top:{f_["y"] * win - f_["size"] / 2:.0f}px; width:{f_["size"]}px; height:{f_["size"]}px; opacity:0; z-index:4;"></div>')
                tl.append(f'tl.fromTo("#{fid}", {{opacity: 0, scale: 1.6}}, {{opacity: 1, scale: 1, duration: 0.35, ease: "power3.out"}}, {d0 + 0.05:.3f});')
                tl.append(f'tl.to("#{fid}", {{borderColor: "#7CFF7C", duration: 0.05}}, {d0 + 0.45:.3f});')
                tl.append(f'tl.to("#{fid}", {{opacity: 0, duration: {fd}}}, {d0 + ov["dur"] - fd:.3f});')
        ch_ = fx.get('chips')
        if ch_:  # 후보 목록(ep09 v2 "오늘의 후보"): 유리 띠 안에 메뉴가 하나씩 생기고, 거절되면 줄이 그어지며 흐려짐(빨간 도장 대신)
            shutil.copy(os.path.join(ROOT, 'assets/fonts/Jua-Regular.ttf'), os.path.join(out, 'media/Jua.ttf'))
            cid_ = f'{cid}-ch'; d0 = t + ch_['at']
            items = ''.join(f'<span class="chip" id="{cid_}{i}"{" style=" + chr(34) + "opacity:0" + chr(34) if it["at"] > ch_["at"] + 0.01 else ""}>{html.escape(it["text"])}<i class="strike" id="{cid_}{i}s"></i></span>' for i, it in enumerate(ch_['items']))
            media_html.append(f'<div class="winfx chips" id="{cid_}" data-start="{d0:.3f}" data-duration="{ch_["dur"]:.3f}" style="top:{ch_.get("y", 0.04) * win:.0f}px; opacity:0;">'
                              f'<span class="chipsin">{"<b class=chiptitle>" + html.escape(ch_["title"]) + "</b>" if ch_.get("title") else ""}{items}</span></div>')
            tl.append(f'tl.fromTo("#{cid_}", {{opacity: 0, y: 16}}, {{opacity: 1, y: 0, duration: 0.3, ease: "power2.out"}}, {d0:.3f});')
            tl.append(f'tl.to("#{cid_}", {{opacity: 0, duration: 0.25}}, {d0 + ch_["dur"] - 0.25:.3f});')
            for i, it in enumerate(ch_['items']):
                ia = t + it['at']
                if ia > d0 + 0.01:
                    tl.append(f'tl.fromTo("#{cid_}{i}", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.25, ease: "back.out(2.2)"}}, {ia:.3f});')
                if it.get('strike_at') is not None:
                    sa = t + it['strike_at']
                    tl.append(f'tl.fromTo("#{cid_}{i}s", {{scaleX: 0}}, {{scaleX: 1, duration: 0.22, ease: "power2.out"}}, {sa:.3f});')
                    tl.append(f'tl.to("#{cid_}{i}", {{opacity: 0.45, duration: 0.25}}, {sa + 0.15:.3f});')
        for k, ts_ in enumerate(fx.get('toasts', [])):  # 유리 알림창(ep05 v2 "다시 찍기"): 반투명 흰 둥근 창이 살짝 커지며 떠오름(빨간 도장 대신 — 사용자: 분위기에 안 맞음)
            tid_ = f'{cid}-ts{k}'; d0 = t + ts_['at']
            shutil.copy(os.path.join(ROOT, 'assets/fonts/Jua-Regular.ttf'), os.path.join(out, 'media/Jua.ttf'))
            media_html.append(f'<div class="winfx toast" id="{tid_}" data-start="{d0:.3f}" data-duration="{ts_["dur"]:.3f}" '
                              f'style="left:0; width:{W}px; top:{ts_.get("y", 0.75) * win:.0f}px; opacity:0;{" text-align:left; padding-left:%dpx; box-sizing:border-box;" % ts_.get("pad", 120) if ts_.get("align") == "left" else ""}">'
                              f'<span class="toastin"{" style=%sfont-size:%dpx; padding:14px 34px 16px 30px;%s" % (chr(34), ts_["size"], chr(34)) if ts_.get("size") else ""}>'
                              f'{"<span class=toasticon>" + html.escape(ts_["icon"]) + "</span>" if ts_.get("icon") else ""}{html.escape(ts_["text"])}</span></div>')
            tl.append(f'tl.fromTo("#{tid_}", {{opacity: 0, y: 24, scale: 0.9}}, {{opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(1.7)"}}, {d0:.3f});')
            tl.append(f'tl.to("#{tid_}", {{opacity: 0, y: -10, duration: 0.25, ease: "power1.in"}}, {d0 + ts_["dur"] - 0.25:.3f});')
        for k, lb in enumerate(fx.get('labels', [])):  # 이름표(ep06 v2 댄스배틀): 둥근 색 띠가 왼쪽에서 미끄러져 들어왔다 나감
            lid = f'{cid}-lb{k}'; d0 = t + lb['at']
            media_html.append(f'<div class="winfx tagpill" id="{lid}" data-start="{d0:.3f}" data-duration="{lb["dur"]:.3f}" '
                              f'style="top:{lb.get("y", 0.75) * win:.0f}px; left:{lb.get("x", 0.06) * W:.0f}px; background:{lb.get("color", "#FF7EB3")}; opacity:0;">'
                              f'<span class="tagsmall">{html.escape(lb.get("small", ""))}</span>{html.escape(lb["text"])}</div>')
            tl.append(f'tl.fromTo("#{lid}", {{x: -420, opacity: 0}}, {{x: 0, opacity: 1, duration: 0.28, ease: "back.out(1.6)"}}, {d0:.3f});')
            tl.append(f'tl.to("#{lid}", {{x: -420, opacity: 0, duration: 0.22, ease: "power2.in"}}, {d0 + lb["dur"] - 0.22:.3f});')
        gr = fx.get('grade')  # 색보정(ep11 광고 연출): 프레임에 CSS 필터 + 비네트·아래 그늘
        media_html.append(f'<div class="frame" id="{cid}" style="top:{-offy:.1f}px; transform-origin: 540px {offy + win / 2:.1f}px;{" filter: " + gr["filter"] + ";" if gr else ""}">{el}</div>')
        if gr:
            bg = f'radial-gradient(ellipse 75% 60% at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,{gr.get("vignette", 0.55)}) 100%)'
            if gr.get('shade'):
                bg = f'linear-gradient(to bottom, rgba(0,0,0,0) 60%, rgba(0,0,0,{gr["shade"]}) 100%), ' + bg
            media_html.append(f'<div class="winfx" id="{cid}-vig" data-start="{t:.3f}" data-duration="{L:.3f}" style="background: {bg};"></div>')
        for k, cp in enumerate(fx.get('copy', [])):  # 광고 카피(ep11): 얇고 자간 넓은 흰 글씨가 살짝 커진 상태에서 가라앉으며 서서히 나타남(자간 애니메이션은 렌더에서 끊겨 금지)
            cpid = f'{cid}-cp{k}'; d0 = t + cp['at']; sz = cp.get('size', 64); spc = cp.get('spacing', 0.12)
            media_html.append(f'<div class="winfx adcopy" id="{cpid}" data-start="{d0:.3f}" data-duration="{cp["dur"]:.3f}" '
                              f'style="top:{cp.get("y", 0.8) * win - sz * 0.7:.0f}px; font-size:{sz}px; font-weight:{cp.get("weight", 300)}; letter-spacing:{spc}em; color:{cp.get("color", "#FFFFFF")}; opacity:0;">{html.escape(cp["text"])}</div>')
            tl.append(f'tl.fromTo("#{cpid}", {{opacity: 0, y: 14, scale: {cp.get("open", 1.06)}}}, {{opacity: 1, y: 0, scale: 1, duration: {cp.get("fade", 0.7)}, ease: "power2.out"}}, {d0:.3f});')
            tl.append(f'tl.to("#{cpid}", {{opacity: 0, duration: 0.25, ease: "power1.in"}}, {d0 + cp["dur"] - 0.25:.3f});')
        # 창 위에 고정되는 효과(카메라와 무관): 창 좌표(1080 x win)
        sl = fx.get('spotlight')
        if sl:  # 핀 조명: 주변을 어둡게, 원 안만 밝게
            r0 = sl.get('r', 0.32) * W
            media_html.append(f'<div class="winfx" id="{cid}-spot" data-start="{t + sl["at"]:.3f}" data-duration="{sl["dur"]:.3f}" '
                              f'style="background: radial-gradient(circle {r0:.0f}px at {sl["cx"] * W:.0f}px {sl["cy"] * win:.0f}px, rgba(255,240,200,0.10) 0%, rgba(255,240,200,0.05) 70%, rgba(0,0,0,{sl.get("dark", 0.72)}) 100%); opacity:0;"></div>')
            tl.append(f'tl.fromTo("#{cid}-spot", {{opacity: 0}}, {{opacity: 1, duration: 0.15, ease: "power2.out"}}, {t + sl["at"]:.3f});')
        tn = fx.get('tint')
        if tn:  # 색 필터(푸른 우울 등): 곱하기 색 덮개
            media_html.append(f'<div class="winfx" id="{cid}-tint" data-start="{t + tn["at"]:.3f}" data-duration="{tn["dur"]:.3f}" style="background:{tn["color"]}; mix-blend-mode: multiply; opacity:0;"></div>')
            tl.append(f'tl.fromTo("#{cid}-tint", {{opacity: 0}}, {{opacity: 1, duration: {tn.get("fade", 0.5)}, ease: "power1.out"}}, {t + tn["at"]:.3f});')
        sp2 = fx.get('speedlines')
        if sp2:  # 집중선: 바깥쪽 방사선, 깜빡이며 살짝 회전
            media_html.append(f'<div class="winfx speed" id="{cid}-spd" data-start="{t + sp2["at"]:.3f}" data-duration="{sp2["dur"]:.3f}" '
                              f'style="background: repeating-conic-gradient(from 0deg at {sp2.get("cx", 0.5) * 100:.0f}% {sp2.get("cy", 0.5) * 100:.0f}%, rgba(255,255,255,0.85) 0deg 1.2deg, rgba(255,255,255,0) 1.2deg 7deg);"></div>')
            for k in range(int(sp2['dur'] / 0.06)):
                tl.append(f'tl.set("#{cid}-spd", {{rotation: {(k % 3) * 0.8:.1f}, opacity: {0.75 if k % 2 else 1}}}, {t + sp2["at"] + k * 0.06:.3f});')
        for k, stp in enumerate(fx.get('stamps', [])):  # 도장(✕ 등): 크게 쾅 찍히고 끝까지 남음
            if any('가' <= ch <= '힣' or ch.isalpha() for ch in stp.get('text', '✕')):   # 2026-10-22 사용자: 효과 글씨는 유리 알림창(toasts)으로
                print(f'⚠ 경고: 컷 {c["cut"]} 도장에 글자 "{stp["text"]}" — 효과 글씨는 toasts(유리 알림창)가 기본(02a 규칙). 도장은 ✕·◯ 같은 기호만')
            sid2 = f'{cid}-st{k}'; d0 = t + stp['at']; dd = stp.get('dur', L - stp['at'])
            media_html.append(f'<div class="winfx stamp" id="{sid2}" data-start="{d0:.3f}" data-duration="{dd:.3f}" '
                              f'style="left:{stp["x"] * W - stp.get("w", stp.get("size", 220)) / 2:.0f}px; top:{stp["y"] * win - stp.get("size", 220) / 2:.0f}px; width:{stp.get("w", stp.get("size", 220))}px; height:{stp.get("size", 220)}px; white-space: nowrap; '
                              f'font-size:{stp.get("size", 220)}px; line-height:{stp.get("size", 220)}px; color:{stp.get("color", "#E8322E")};">{html.escape(stp.get("text", "✕"))}</div>')
            tl.append(f'tl.fromTo("#{sid2}", {{scale: 2.4, opacity: 0, rotation: {stp.get("rot", -12)}}}, {{scale: 1, opacity: 1, rotation: {stp.get("rot", -12) / 3:.1f}, duration: 0.12, ease: "power4.in"}}, {d0:.3f});')
        for k, tp in enumerate(fx.get('taps', [])):  # 터치 효과: 손가락 누른 자리에 흰 원이 퍼짐(창 좌표)
            tid = f'{cid}-tap{k}'; r0 = tp.get('r', 70)
            media_html.append(f'<div class="winfx tap" id="{tid}" data-start="{t + tp["at"]:.3f}" data-duration="0.45" '
                              f'style="left:{tp["x"] * W - r0:.0f}px; top:{tp["y"] * win - r0:.0f}px; width:{2 * r0}px; height:{2 * r0}px;"></div>')
            tl.append(f'tl.fromTo("#{tid}", {{scale: 0.3, opacity: 0.85}}, {{scale: 1.5, opacity: 0, duration: 0.42, ease: "power2.out"}}, {t + tp["at"]:.3f});')
        pf = fx.get('puffs')
        if pf:  # 방귀 구름(ep10): 지정 위치에서 펑 커지며 떠올랐다 사라짐(창 좌표)
            shutil.copy(os.path.join(ROOT, 'assets/fx/gas_cloud.png'), os.path.join(out, 'media/gas_cloud.png'))
            for k, p_ in enumerate(pf):
                pid_ = f'{cid}-pf{k}'; sz = p_.get('size', 220); d0 = t + p_['at']; dur_ = p_.get('dur', 0.8)
                media_html.append(f'<img class="winfx puff" id="{pid_}" src="media/gas_cloud.png" data-start="{d0:.3f}" data-duration="{dur_:.3f}" '
                                  f'style="left:{p_["x"] * W - sz / 2:.0f}px; top:{p_["y"] * win - sz / 2:.0f}px; width:{sz}px; height:{sz}px; opacity:0;" />')
                tl.append(f'tl.fromTo("#{pid_}", {{scale: 0.15, opacity: {p_.get("alpha", 0.85)}, rotation: {p_.get("rot", 0)}}}, {{scale: 1, opacity: {p_.get("alpha", 0.85)}, y: {-p_.get("rise", 60)}, duration: {dur_ * 0.45:.3f}, ease: "back.out(2.5)"}}, {d0:.3f});')
                tl.append(f'tl.to("#{pid_}", {{scale: 1.25, opacity: 0, y: {-p_.get("rise", 60) * 2}, duration: {dur_ * 0.55:.3f}, ease: "power1.in"}}, {d0 + dur_ * 0.45:.3f});')
        gg = fx.get('gauge')
        if gg:  # 게이지: 라벨 + 막대가 차오르며 빨개지고 MAX
            media_html.append(f'<div class="winfx gauge{" glassg" if gg.get("glass") else ""}" id="{cid}-gg" data-start="{t + gg["at"]:.3f}" data-duration="{gg["dur"]:.3f}" style="top:{gg.get("y", 0.16) * win:.0f}px;">'
                              f'<span class="glabel">{html.escape(gg["label"])}</span><span class="gbar"><span class="gfill" id="{cid}-ggf"></span></span><span class="gmax" id="{cid}-ggm">MAX</span></div>')
            c0, c1 = ('#FFD3E4', '#FF7EB3') if gg.get('glass') else ('#FFD84A', '#E8322E')   # glass: 유리 느낌(분홍), 빨강 대신(02a 효과 글씨 규칙)
            tl.append(f'tl.fromTo("#{cid}-ggf", {{width: "0%", backgroundColor: "{c0}"}}, {{width: "100%", backgroundColor: "{c1}", duration: {gg.get("fill", 1.2)}, ease: "power2.in"}}, {t + gg["at"]:.3f});')
            tl.append(f'tl.fromTo("#{cid}-ggm", {{scale: 0, opacity: 0}}, {{scale: 1, opacity: 1, duration: 0.18, ease: "back.out(3)"}}, {t + gg["at"] + gg.get("fill", 1.2):.3f});')
            if gg.get('glass'):
                shutil.copy(os.path.join(ROOT, 'assets/fonts/Jua-Regular.ttf'), os.path.join(out, 'media/Jua.ttf'))
            else:
                tl.append(f'tl.to("#{cid}-gg", {{x: 6, duration: 0.04, yoyo: true, repeat: 7}}, {t + gg["at"] + gg.get("fill", 1.2):.3f});')
        fb = fx.get('flashback')
        if fb:  # 회상 화면: 앞 장면 한 프레임을 흑백 액자로 띄움
            png = f'media/{cid}_fb.png'
            fsrc = os.path.join(ROOT, f'outputs/{ep}/{fb["cut"]}/clip_{fb.get("tag", "v1")}.mp4') if fb.get('cut') else os.path.join(ROOT, fb['image'])
            if not os.path.exists(fsrc) and fb.get('image'):
                fsrc = os.path.join(ROOT, fb['image'])
            if fb.get('raw'):   # 미리 만든 사진을 그대로(ep05 v2 폴라로이드: 미순만 잘라 둔 사진)
                shutil.copy(os.path.join(ROOT, fb['image']), os.path.join(out, png))
            else:
                grab_frame(fsrc, fb.get('t', 0), os.path.join(out, png), crop_top=fb.get('top', 0.3), crop_h=win / H)
            fw = fb.get('w', 0.56) * W
            media_html.append(f'<div class="winfx fb" id="{cid}-fb" data-start="{t + fb["at"]:.3f}" data-duration="{fb["dur"]:.3f}" '
                              f'style="left:{fb.get("x", 0.5) * W - fw / 2:.0f}px; top:{fb.get("y", 0.12) * win:.0f}px; width:{fw:.0f}px;">'
                              f'<img src="{png}" style="width:100%; display:block;{"" if fb.get("color") else " filter: grayscale(1) contrast(1.1);"}" />'   # color: 폴라로이드(ep05 v2)
                              f'<div class="fblabel">{html.escape(fb.get("label", "(아까)"))}</div></div>')
            tl.append(f'tl.fromTo("#{cid}-fb", {{scale: 0.3, opacity: 0, rotation: -8}}, {{scale: 1, opacity: 1, rotation: -3, duration: 0.18, ease: "back.out(2)"}}, {t + fb["at"]:.3f});')
            tl.append(f'tl.to("#{cid}-fb", {{scale: 0.8, opacity: 0, duration: 0.15}}, {t + fb["at"] + fb["dur"] - 0.15:.3f});')
        # 카메라
        cam = fx.get('cam')
        if cam:
            fr = dict(scale=cam['from'], x=cam.get('pan_x', [0, 0])[0], y=cam.get('pan_y', [0, 0])[0])
            to = dict(scale=cam['to'], x=cam.get('pan_x', [0, 0])[1], y=cam.get('pan_y', [0, 0])[1], duration=L, ease='none')
            tl.append(f'tl.fromTo("#{cid}", {json.dumps(fr)}, {json.dumps(to)}, {t:.3f});')
        for mv in fx.get('moves', []):  # 카메라 이동 순서(ep11: 말하는 쪽으로 확대): 프레임을 scale·x·y로 옮김(창 중심 기준)
            tl.append(f'tl.to("#{cid}", {{scale: {mv["scale"]}, x: {mv.get("x", 0)}, y: {mv.get("y", 0)}, duration: {mv["dur"]:.3f}, ease: "{mv.get("ease", "power2.inOut")}"}}, {t + mv["at"]:.3f});')
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
                media_html.append(f'<div class="spark" id="{cid}-sp{k}" style="left:{sx}px; top:{sy}px;{" color:" + sp["color"] + "; text-shadow: 0 0 12px " + sp["color"] + ";" if sp.get("color") else ""}">{sp.get("glyph", "✦")}</div>')
                d = at + 0.08 * k
                tl.append(f'tl.fromTo("#{cid}-sp{k}", {{scale: 0, opacity: 0, rotation: -30}}, {{scale: 1, opacity: 1, rotation: 20, duration: 0.25, ease: "back.out(3)"}}, {d:.3f});')
                tl.append(f'tl.to("#{cid}-sp{k}", {{scale: 0.2, opacity: 0, duration: 0.3}}, {d + sp["dur"] - 0.5:.3f});')
        for k, fl in enumerate(fx.get('flash', [])):  # 셔터 플래시: 흰 화면이 번쩍 후 사라짐
            fid = f'{cid}-fl{k}'
            media_html.append(f'<div class="flash" id="{fid}" data-start="{t + fl["at"]:.3f}" data-duration="{fl["dur"]:.3f}"></div>')
            tl.append(f'tl.fromTo("#{fid}", {{opacity: {fl.get("peak", 0.9)}}}, {{opacity: 0, duration: {fl["dur"]:.3f}, ease: "power2.in"}}, {t + fl["at"]:.3f});')
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

    # 자막 겹침 검사(ep08 애니매틱 사고): 같은 자리(위/아래) 자막이 시간상 겹치면 렌더 중단
    for pos in ('top', 'bottom'):
        L = sorted([x for x in T['subtitles'] if (x.get('pos') == 'top') == (pos == 'top')], key=lambda x: x['start'])
        bad = [(a['text'], b['text'], round(a['end'] - b['start'], 2)) for a, b in zip(L, L[1:]) if b['start'] < a['end'] - 1e-6]
        if bad:
            raise SystemExit(f'자막 겹침({pos}): ' + '; '.join(f'"{x}"↔"{y}" {d}s' for x, y, d in bad))
    # 자막
    st = T['subtitle_style']; sub_html = []
    SP = FX['subtitle']
    for i, sb in enumerate(T['subtitles']):
        sid = f'sub{i:02d}'; dur = sb['end'] - sb['start']
        shout = '!!' in sb['text']
        cx = W * sb.get('x', 0.5)
        posstyle = f' top:{top + 40}px; bottom:auto;' if sb.get('pos') == 'top' else ''
        sub_html.append(f'<div class="sub" id="{sid}" data-start="{sb["start"]:.3f}" data-duration="{dur:.3f}" data-cx="{cx:.0f}" style="color:{sb.get("color", st["colors"][sb["speaker"]])};{posstyle}{" font-size:%dpx;" % sb["size"] if sb.get("size") else ""}">{html.escape(sb["text"].replace("…", "..."))}</div>')
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
    def title_line(ln):  # spans가 있으면 한 줄 안에서 단어별 색(ep09: "저녁메뉴"만 노랑, 색 위치는 사용자와 상의해 정함)
        if ln.get('spans'):
            return '<div>' + ''.join(f'<span style="color:{sp.get("color", "#FFFFFF")}">{html.escape(sp["text"])}</span>' for sp in ln['spans']) + '</div>'
        return f'<div style="color:{ln["color"]}">{html.escape(ln["text"])}</div>'
    title_html = ''.join(title_line(ln) for ln in ti['lines'])
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
  .frame .spottrack {{ position: absolute; pointer-events: none; }}
  .frame img:not(.layer), .frame video {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; display: block; }}
  #title {{ position: absolute; left: 0; width: 100%; top: {ti['center_y'] - ti['size'] - ti['line_gap'] / 2:.0f}px; text-align: center; font-size: {ti['size']}px; font-weight: {ti['weight']}; line-height: {ti['size'] + ti['line_gap']}px;{' -webkit-text-stroke: %dpx #111; paint-order: stroke fill; text-shadow: 0 4px 14px rgba(0,0,0,0.55);' % ti['stroke'] if ti.get('stroke') else ''} }}
  #channel {{ position: absolute; left: 0; width: 100%; top: {ch['center_y'] - ch['size'] * 0.7:.0f}px; text-align: center; font-size: {ch['size']}px; font-weight: {ch['weight']}; color: {ch['color']}; opacity: {ch.get('opacity', 1)}; line-height: 1.4;{' -webkit-text-stroke: %dpx #111; paint-order: stroke fill; text-shadow: 0 3px 10px rgba(0,0,0,0.55);' % ch['stroke'] if ch.get('stroke') else ''} }}
  .sub {{ position: absolute; bottom: {H - top - win + st['bottom_margin']}px; font-size: {st['size']}px; font-weight: {st['weight']}; white-space: nowrap; line-height: 1.25;
          -webkit-text-stroke: {st['stroke']}px {st['stroke_color']}; paint-order: stroke fill; transform-origin: 50% 100%; }}
  .card {{ position: absolute; left: 120px; top: {top + 36}px; font-size: 54px; font-weight: 700; color: #fff; text-shadow: 2px 2px 0 #000, 0 0 6px #000; line-height: 1.2; }}
  .spark {{ position: absolute; font-size: 64px; color: #FFE27A; text-shadow: 0 0 12px #FFD84A; transform-origin: 50% 50%; }}
  .blackfade {{ position: absolute; inset: 0; background: #000; }}
  .flash {{ position: absolute; inset: 0; background: #fff; }}
  .uibox {{ position: absolute; left: 0; top: {top + 200}px; width: {W}px; text-align: center; color: #fff; transform-origin: 50% 50%; }}
  .uilabel {{ font-size: 60px; font-weight: 700; opacity: 0.85; }}
  .uinum {{ font-size: 150px; font-weight: 800; color: #FFD84A; line-height: 1.1; display: inline-block; transform-origin: 50% 50%; }}
  .uiclock {{ font-size: 54px; font-weight: 700; margin-top: 10px; }}
  .ring {{ position: absolute; border: 10px dashed #FFD84A; border-radius: 50%; box-sizing: border-box; transform-origin: 50% 50%; }}
  .winfx {{ position: absolute; left: 0; top: 0; width: {W}px; height: {win}px; pointer-events: none; }}
  .speed {{ -webkit-mask-image: radial-gradient(ellipse at center, transparent 38%, #000 75%); mask-image: radial-gradient(ellipse at center, transparent 38%, #000 75%); }}
  .stamp {{ width: auto; height: auto; text-align: center; font-weight: 900; -webkit-text-stroke: 6px #fff; paint-order: stroke fill; text-shadow: 0 6px 16px rgba(0,0,0,0.5); transform-origin: 50% 50%; }}
  .gauge {{ height: auto; display: flex; align-items: center; justify-content: center; gap: 18px; font-size: 52px; font-weight: 800; color: #fff; -webkit-text-stroke: 6px #111; paint-order: stroke fill; }}
  .gbar {{ display: inline-block; width: 460px; height: 46px; border: 6px solid #111; border-radius: 28px; background: rgba(255,255,255,0.85); overflow: hidden; }}
  .gfill {{ display: block; height: 100%; width: 0%; background: #FFD84A; }}
  .gmax {{ color: #E8322E; font-size: 60px; display: inline-block; transform-origin: 50% 50%; }}
  .fb {{ height: auto; border: 10px solid #fff; box-shadow: 0 10px 30px rgba(0,0,0,0.55); transform-origin: 50% 50%; background: #fff; }}
  .fblabel {{ position: absolute; left: 0; right: 0; bottom: -64px; text-align: center; font-size: 46px; font-weight: 800; color: #fff; -webkit-text-stroke: 6px #111; paint-order: stroke fill; }}
  @font-face {{ font-family: "Jua"; src: url("media/Jua.ttf") format("truetype"); }}
  .chips {{ height: auto; text-align: center; z-index: 6; }}
  .chipsin {{ display: inline-flex; align-items: center; gap: 14px; padding: 14px 26px; border-radius: 999px; background: rgba(255,255,255,0.78); -webkit-backdrop-filter: blur(14px); backdrop-filter: blur(14px);
             box-shadow: 0 10px 30px rgba(0,0,0,0.22), inset 0 0 0 2px rgba(255,255,255,0.6); font-family: "Jua", "NotoKR", sans-serif; color: #5A4A52; }}
  .chiptitle {{ font-weight: normal; font-size: 34px; color: #9A8A92; margin-right: 6px; }}
  .chip {{ position: relative; display: inline-block; font-size: 48px; padding: 2px 16px; border-radius: 999px; background: rgba(255,126,179,0.16); transform-origin: 50% 50%; }}
  .strike {{ position: absolute; left: 8px; right: 8px; top: 52%; height: 5px; border-radius: 3px; background: #5A4A52; transform: scaleX(0); transform-origin: 0% 50%; }}
  .glassg {{ white-space: nowrap; font-family: "Jua", "NotoKR", sans-serif; font-weight: normal; color: #5A4A52; -webkit-text-stroke: 0; padding: 12px 28px; width: auto; left: 50%; transform: translateX(-50%); border-radius: 999px; background: rgba(255,255,255,0.78);
             -webkit-backdrop-filter: blur(14px); backdrop-filter: blur(14px); box-shadow: 0 10px 30px rgba(0,0,0,0.22); }}
  .glassg .gbar {{ border: 0; background: rgba(90,74,82,0.12); height: 34px; }}
  .glassg .gmax {{ color: #FF5C9A; font-size: 52px; }}
  .toast {{ height: auto; text-align: center; z-index: 6; transform-origin: 50% 50%; }}
  .toastin {{ display: inline-block; padding: 22px 54px 24px 46px; border-radius: 999px; background: rgba(255,255,255,0.78); -webkit-backdrop-filter: blur(14px); backdrop-filter: blur(14px);
             box-shadow: 0 10px 34px rgba(0,0,0,0.22), inset 0 0 0 2px rgba(255,255,255,0.6); font-family: "Jua", "NotoKR", sans-serif; font-size: 62px; color: #5A4A52; white-space: nowrap; }}
  .toasticon {{ display: inline-block; margin-right: 18px; color: #FF7EB3; font-family: "NotoKR", sans-serif; font-weight: 800; font-size: 66px; vertical-align: -2px; }}
  .focusbox {{ border: 5px solid rgba(255,255,255,0.95); border-radius: 10px; box-sizing: border-box; transform-origin: 50% 50%; }}
  .tagpill {{ z-index: 6; width: auto; height: auto; padding: 14px 40px 16px 34px; border-radius: 60px; color: #fff; font-size: 64px; font-weight: 900; white-space: nowrap; box-shadow: 0 8px 24px rgba(0,0,0,0.35); -webkit-text-stroke: 2px rgba(0,0,0,0.25); }}
  .tagsmall {{ font-size: 34px; font-weight: 800; margin-right: 18px; letter-spacing: 0.08em; opacity: 0.9; }}
  .adcopy {{ height: auto; transform-origin: 50% 50%; text-align: center; white-space: nowrap; line-height: 1.3; text-shadow: 0 2px 18px rgba(0,0,0,0.75), 0 0 4px rgba(0,0,0,0.5); }}
  .puff {{ width: auto; height: auto; transform-origin: 50% 70%; }}
  .tap {{ border-radius: 50%; background: radial-gradient(circle, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.5) 45%, rgba(255,255,255,0) 70%); transform-origin: 50% 50%; }}
  .arrow {{ position: absolute; font-size: 110px; color: #FFD84A; text-shadow: 0 0 10px #000; }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-duration="{total:.3f}" data-fps="{fps}">
  <div id="win">
    {chr(10).join('    ' + m for m in media_html if 'class="frame"' in m or 'class="winfx' in m or 'blackfade' in m or 'class="flash"' in m)}
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
