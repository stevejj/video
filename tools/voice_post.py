#!/usr/bin/env python3
"""대사 후처리 v7 — 재생성 없이 기존 mp3(공통 배속 1.2 적용본)를 화자별 배속·속마음 톤으로 재가공.
사용: python3 tools/voice_post.py --ep ep01 --out-dir outputs/ep01/voice/lines_v7
- 화자별 배속: 프로필 post.speedup_by_speaker (기존 1.2 대비 비율만큼 asetrate 재조정)
- 속마음 톤(inner=True 대사): 음량 -4dB, 150Hz 하이패스, 5.5kHz 로우패스(살짝 먹먹), 컴프레서
- 대화 파일(9-02+9-03)은 무음 지점에서 잘라 화자별로 처리 후 같은 간격으로 다시 이어 붙임
"""
import argparse, json, os, re, subprocess, tempfile
import imageio_ffmpeg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF = imageio_ffmpeg.get_ffmpeg_exe()
PROF = os.path.join(ROOT, 'outputs/voice_profile.json')


def run(args):
    subprocess.run([FF, '-y', '-loglevel', 'error', *args], check=True)


def duration(p):
    out = subprocess.run([FF, '-i', p], capture_output=True, text=True).stderr
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', out)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else 0.0


def chain(ratio, inner, ln):
    af = []
    if abs(ratio - 1.0) > 1e-3:
        af.append(f"asetrate=44100*{ratio:.5f},aresample=44100")
    if inner:
        af.append("highpass=f=150,lowpass=f=5500,acompressor=threshold=-20dB:ratio=2.5:attack=5:release=80,volume=-4dB")
    af.append(f"loudnorm=I={ln['I'] - (4 if inner else 0)}:TP={ln['TP']}:LRA={ln['LRA']}")
    return ','.join(af)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ep', default='ep01')
    ap.add_argument('--out-dir', default=None)
    a = ap.parse_args()
    P = json.load(open(PROF))
    base = P['post']['speedup']
    by = P['post'].get('speedup_by_speaker', {})
    ln = P['loudnorm']
    lines = P['episodes'][a.ep]['lines']
    out_dir = a.out_dir or os.path.join(ROOT, f'outputs/{a.ep}/voice/lines_v7')
    os.makedirs(out_dir, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='vpost_')
    done = {}
    for l in lines:
        src = os.path.join(ROOT, l['file'])
        name = os.path.basename(src)
        if name in done:
            l['file_v7'] = done[name]; continue
        dst = os.path.join(out_dir, name)
        group = [x for x in lines if os.path.basename(x['file']) == name]
        if len(group) == 1:
            ratio = by.get(l['speaker'], base) / base
            run(['-i', src, '-af', chain(ratio, l.get('inner', False), ln), dst])
        else:
            # 대화 파일: 무음 지점에서 분할
            out = subprocess.run([FF, '-i', src, '-af', 'silencedetect=noise=-35dB:d=0.12', '-f', 'null', '-'],
                                 capture_output=True, text=True).stderr
            ss = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', out)]
            se = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', out)]
            cut_a, cut_b = ss[0], se[0]
            parts = []
            for i, (g, seg) in enumerate(zip(group, [(0, cut_a), (cut_b, None)])):
                p = os.path.join(tmp, f'{name}_{i}.wav')
                trim = ['-ss', str(seg[0])] + (['-to', str(seg[1])] if seg[1] else [])
                ratio = by.get(g['speaker'], base) / base
                run([*trim, '-i', src, '-af', chain(ratio, g.get('inner', False), ln), p])
                parts.append(p)
            gap = os.path.join(tmp, 'gap.wav')
            run(['-f', 'lavfi', '-t', f'{cut_b - cut_a:.3f}', '-i', 'anullsrc=r=44100:cl=mono', gap])
            run(['-i', parts[0], '-i', gap, '-i', parts[1], '-filter_complex', '[0:a][1:a][2:a]concat=n=3:v=0:a=1[a]',
                 '-map', '[a]', '-c:a', 'libmp3lame', '-q:a', '2', dst])
            # 두 번째 화자의 시작 지점(파일 내) 갱신
            group[1]['split_at_v7'] = round(duration(parts[0]) + (cut_b - cut_a), 3)
        done[name] = os.path.relpath(dst, ROOT)
        for g in group:
            g['file_v7'] = done[name]; g['len_v7'] = round(duration(dst), 2)
        print(f"{name:16s} {l['speaker']:8s} ratio {by.get(l['speaker'], base) / base:.3f} inner={l.get('inner', False)} → {duration(dst):.2f}s")
    json.dump(P, open(PROF, 'w'), ensure_ascii=False, indent=1)
    print('완료:', out_dir)


if __name__ == '__main__':
    main()
