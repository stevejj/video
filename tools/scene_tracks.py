#!/usr/bin/env python3
"""장면별 음성 트랙 조립(0원): 대사 파일을 장면 안에 차례로 놓아 outputs/<ep>/voice/scenes/sN.mp3 를 만든다.
사용: python3 tools/scene_tracks.py --ep ep09 --lens 1=5,2=5,3=5.5,4=3.5,5=5,6=4.5,7=3.5,8=6,9=4.5 [--lead 0.3] [--gap 0.12] [--at 7=1.2]
- 장면 번호 = 대사 cut의 앞 숫자(1a→1, 7→7). 대사 사이 간격 gap, 첫 대사 시작 lead(장면별 --at 로 덮어씀).
- Kling 음성 참조는 5초 이상이어야 하므로 트랙 길이 = max(장면 길이, 5.0).
- 결과는 voice_profile episodes[ep].scenes 와 lines[*].scene_at 에 기록(편집·자막 시각 계산용).
"""
import argparse, json, os, re, subprocess
import imageio_ffmpeg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF = imageio_ffmpeg.get_ffmpeg_exe()
PROF = os.path.join(ROOT, 'outputs/voice_profile.json')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ep', required=True); ap.add_argument('--lens', required=True)
    ap.add_argument('--lead', type=float, default=0.3); ap.add_argument('--gap', type=float, default=0.12)
    ap.add_argument('--at', default='', help='장면별 첫 대사 시작 덮어쓰기, 예: 7=1.2')
    a = ap.parse_args()
    lens = {k: float(v) for k, v in (x.split('=') for x in a.lens.split(','))}
    at = {k: float(v) for k, v in (x.split('=') for x in a.at.split(',') if x)}
    P = json.load(open(PROF)); E = P['episodes'][a.ep]
    out = os.path.join(ROOT, f'outputs/{a.ep}/voice/scenes'); os.makedirs(out, exist_ok=True)
    scenes = {}
    for l in E['lines']:
        scenes.setdefault(re.match(r'\d+', l['cut'])[0], []).append(l)
    E['scenes'] = {}
    for s, ls in scenes.items():
        t = at.get(s, a.lead); ins = []; filt = []; offs = {}
        for i, l in enumerate(ls):
            l['scene_at'] = round(t, 2); offs[l['cut']] = round(t, 2)
            ins += ['-i', os.path.join(ROOT, l['file'])]
            filt.append(f'[{i}]aresample=44100,aformat=channel_layouts=mono,adelay={int(t * 1000)}:all=1[a{i}]')
            t += l['len_file'] + a.gap
        end = t - a.gap
        L = max(lens.get(s, end + 0.4), 5.0)
        if end > lens.get(s, end + 0.4):
            print(f'⚠ s{s}: 대사 끝 {end:.2f}s > 장면 길이 {lens[s]}s')
        dst = os.path.join(out, f's{s}.mp3')
        filt.append(''.join(f'[a{i}]' for i in range(len(ls))) + f'amix=inputs={len(ls)}:normalize=0,apad=whole_dur={L},atrim=0:{L}')
        subprocess.run([FF, '-y', '-v', 'error', *ins, '-filter_complex', ';'.join(filt), '-ac', '1', '-b:a', '128k', dst], check=True)
        E['scenes'][f's{s}'] = {'file': os.path.relpath(dst, ROOT), 'len': L, 'scene_len': lens.get(s), 'speech_end': round(end, 2), 'lines': offs}
        print(f's{s}: {len(ls)}줄, 대사 끝 {end:.2f}s, 트랙 {L}s')
    json.dump(P, open(PROF, 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
