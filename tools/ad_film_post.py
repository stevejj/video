#!/usr/bin/env python3
"""광고 화면 질감 + 위아래 검은 띠(렌더 뒤 후처리, 0원). ep11 v12(2026-10-23 사용자 ③⑤).
- 광고 구간(0 ~ --until초)에만:
  - 고운 필름 입자(프레임마다 바뀜).
  - 밝은 곳 은은한 빛 번짐(흐린 복사본을 '스크린'으로 살짝 섞음).
  - 위아래 검은 띠(--bars px).
- --until 순간(현실 복귀)에 띠가 --open초 동안 위아래로 빠지며 열리고, 입자·빛 번짐도 같이 사라짐.
- 소리는 손대지 않음(무음 렌더에 쓰고, 소리는 mix_audio에서).
사용: python3 tools/ad_film_post.py --in SILENT.mp4 --out OUT.mp4 --until 23.5 [--bars 160 --open 0.35 --grain 9 --bloom 0.22]
"""
import argparse, subprocess
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='src', required=True); ap.add_argument('--out', required=True); ap.add_argument('--until', type=float, required=True)
    ap.add_argument('--bars', type=int, default=160); ap.add_argument('--open', type=float, default=0.35)
    ap.add_argument('--grain', type=int, default=7); ap.add_argument('--bloom', type=float, default=0.14)
    a = ap.parse_args()
    U, O, B = a.until, a.open, a.bars
    k = f'min(1,max(0,({U}+{O}-t)/{O}))'          # 띠 두께 비율: 광고 구간 1 → 열리며 0
    on = f'lt(t,{U})'
    fc = (f'[0:v]split[base][glow];'
          f'[glow]gblur=sigma=28,eq=brightness=0.02[g];'
          f"[base][g]blend=all_mode=screen:all_opacity={a.bloom}:enable='{on}'[b];"
          f"[b]noise=alls={a.grain}:allf=t:enable='{on}'[n];"
          # drawbox의 h에 시각(t) 식을 쓰면 이 ffmpeg(7.0)에선 화면 전체가 검게 칠해짐 → 검은 띠 그림을 위·아래에서 밀어 넣는 overlay로
          f'color=c=black:s=1080x{B}:r=24[bar];[bar]split[bt][bb];'
          f"[n][bt]overlay=x=0:y='-{B}*(1-{k})':eval=frame:shortest=1[t1];"
          f"[t1][bb]overlay=x=0:y='H-{B}*{k}':eval=frame:shortest=1[v]")
    subprocess.run([FF, '-y', '-v', 'error', '-i', a.src, '-filter_complex', fc, '-map', '[v]', '-c:v', 'libx264', '-crf', '21', '-preset', 'medium',
                    '-pix_fmt', 'yuv420p', a.out], check=True)
    print('완료', a.out)


if __name__ == '__main__':
    main()
