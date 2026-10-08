#!/usr/bin/env python3
"""무음 영상(HyperFrames 렌더) + 대사·효과음·배경음 믹스 → 완성 mp4.
사용: python3 tools/mix_audio.py --ep ep02 --video outputs/ep02/roughcut/ep02_roughcut_v0_silent.mp4 --out outputs/ep02/roughcut/ep02_v1.mp4
- 대사: voice_profile episodes[ep].placements (없으면 lines 의 at/file). 재사용 파일은 여러 번 배치 가능.
- 효과음: outputs/<ep>/sfx/sfx_list.json (assemble_ep01 과 같은 형식)
- 배경음: episodes[ep].bgm — target_lufs, duck_db(대사 사이드체인), fade, 선택 tempo_from/tempo(구간 템포 업), dip_at/dip_len/dip_db(한 박자 쉼)
"""
import argparse, json, os, re, subprocess
import imageio_ffmpeg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF = imageio_ffmpeg.get_ffmpeg_exe()


def lufs(path):
    out = subprocess.run([FF, '-i', path, '-af', 'loudnorm=print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(json.loads(re.search(r'\{.*\}', out, re.S).group(0))['input_i'])


def dur(path):
    out = subprocess.run([FF, '-i', path], capture_output=True, text=True).stderr
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', out)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ep', required=True); ap.add_argument('--video', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--no-bgm', action='store_true'); ap.add_argument('--no-sfx', action='store_true')
    a = ap.parse_args()
    P = json.load(open(os.path.join(ROOT, 'outputs/voice_profile.json')))['episodes'][a.ep]
    total = dur(a.video)
    inputs = ['-i', a.video]; fc = []; n = 0; voice = []; others = []
    places = P.get('placements') or [{'file': l['file'], 'at': l['at']} for l in P['lines'] if l.get('file') and 'at' in l]
    for v in places:
        n += 1; inputs += ['-i', os.path.join(ROOT, v['file'])]
        fc.append(f"[{n}:a]aresample=44100,aformat=channel_layouts=mono,adelay={int(v['at'] * 1000)}[a{n}]"); voice.append(f'a{n}')
    print(f'대사 {len(places)}개')
    if not a.no_sfx:
        X = json.load(open(os.path.join(ROOT, f'outputs/{a.ep}/sfx/sfx_list.json')))
        for it in X['items']:
            n += 1; inputs += ['-i', os.path.join(ROOT, it['file'])]
            ch = "aresample=44100,aformat=channel_layouts=mono"
            if it.get('loop'):
                ch += ",aloop=loop=-1:size=44100*60"
            ch += f",atrim=0:{it['len']},asetpts=PTS-STARTPTS"
            if it.get('fade_in'):
                ch += f",afade=t=in:st=0:d={it['fade_in']}"
            if it.get('fade_out'):
                ch += f",afade=t=out:st={it['len'] - it['fade_out']}:d={it['fade_out']}"
            ch += f",volume={it['gain']}dB,adelay={int(it['at'] * 1000)}"
            fc.append(f"[{n}:a]{ch}[a{n}]"); others.append(f'a{n}')
        print(f"효과음 {len(X['items'])}개")
    labels = voice + others
    B = P.get('bgm')
    if B and not a.no_bgm:
        bf = os.path.join(ROOT, B['file']); gain = B['target_lufs'] - lufs(bf); end = B['end_at']
        n += 1; inputs += ['-i', bf]
        base = f"[{n}:a]aresample=44100,aformat=channel_layouts=mono,aloop=loop=-1:size=44100*120,atrim=0:{end + 10},asetpts=PTS-STARTPTS"
        if B.get('tempo') and B.get('tempo_from') is not None:
            tf = B['tempo_from']
            fc.append(base + ",asplit[b0][b1]")
            fc.append(f"[b0]atrim=0:{tf},asetpts=PTS-STARTPTS[bA]")
            fc.append(f"[b1]atrim={tf},asetpts=PTS-STARTPTS,atempo={B['tempo']}[bB]")
            fc.append("[bA][bB]concat=n=2:v=0:a=1[bC]")
            src = "[bC]"
        else:
            fc.append(base + "[bC]"); src = "[bC]"
        vol = f"volume={gain:.2f}dB"
        if B.get('dip_at') is not None:
            d0 = B['dip_at']; d1 = d0 + B.get('dip_len', 1.0); dd = 10 ** (B.get('dip_db', -6) / 20)
            vol += f",volume='if(between(t,{d0},{d1}),{dd:.3f},1)':eval=frame"
        fc.append(f"{src}atrim=0:{end},asetpts=PTS-STARTPTS,{vol},afade=t=in:st=0:d={B['fade_in']},afade=t=out:st={end - B['fade_out']}:d={B['fade_out']}[bgm_raw]")
        if voice:
            fc.append(''.join(f'[{v}]' for v in voice) + f"amix=inputs={len(voice)}:normalize=0,apad=whole_dur={total},asplit[vsum][vsc]")
            ratio = 1 + B['duck_db'] / 3.0
            fc.append(f"[bgm_raw][vsc]sidechaincompress=threshold=0.02:ratio={ratio:.2f}:attack=30:release=400:makeup=1[bgm]")
            labels = ['vsum'] + others + ['bgm']
        else:
            labels.append('bgm_raw')
        print(f"배경음 {os.path.basename(bf)} gain {gain:+.1f}dB, {end}s까지, 템포 {B.get('tempo')}@{B.get('tempo_from')}, 딥 {B.get('dip_at')}")
    fc.append(''.join(f'[{x}]' for x in labels) + f"amix=inputs={len(labels)}:normalize=0,apad=whole_dur={total},alimiter=limit=0.85:level=false[mix]")
    subprocess.run([FF, '-y', '-loglevel', 'error', *inputs, '-filter_complex', ';'.join(fc), '-map', '0:v', '-map', '[mix]', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '160k', '-t', f'{total:.3f}', '-movflags', '+faststart', a.out], check=True)
    print('완료:', a.out, f'{total:.2f}s')


if __name__ == '__main__':
    main()
