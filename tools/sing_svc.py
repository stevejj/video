#!/usr/bin/env python3
"""원곡 노래 → 미순·창수 목소리(노래 전용 음색 변환 Seed-VC, 무료·로컬). ep15 v3 (2026-10-23).
- v1 sing.py(말하기 녹음 + WORLD 음정 입히기): 사용자 "괴물이 말하는 것도 아니고" → 버림.
- v2 sing_sts.py(ElevenLabs 목소리 변환): 노래 음정을 못 따라감(원곡 대비 300~900센트) → 버림.
- v3 Seed-VC 44k 노래 모델(f0 조건): 음색만 캐릭터 목소리로 바꾸고 음정·박자·숨은 원곡 그대로. 시험(07줄): 음정 오차 중앙 12센트, 받아쓰기 일치.
준비: git clone https://github.com/Plachtaa/seed-vc /opt/seedvc (모델은 HuggingFace에서 자동으로 받음), inference.py 저장은 soundfile로 바꿈.
사용:
  python3 tools/sing_svc.py --ep ep15 refs      # 캐릭터 목소리 샘플(지난 편 대사 ~20s) → sing/ref_<sp>.wav
  python3 tools/sing_svc.py --ep ep15 convert   # 줄 구간(sing/sts/<id>_src.wav)마다 변환 → sing/svc/
  python3 tools/sing_svc.py --ep ep15 mix       # 제자리에 놓고 반주와 섞기 → sing/svc_<sp>.wav, sing/svc_preview*.mp3
원곡·가사·결과는 로컬에만(outputs/<ep>/ref, sing은 gitignore).
"""
import argparse, json, os, subprocess, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from sing_sts import pcm, write_wav, SR, PAD
import voice_gen as vg

SEEDVC = '/opt/seedvc'
STEPS = 30


def out_name(B, lid, sp):
    return os.path.join(B, f'sing/svc/vc_{lid}_src_ref_{sp}_1.0_{STEPS}_0.7.wav')


def cmd_refs(B):
    P = json.load(open(vg.PROF))
    for sp in ('misun', 'changsu'):
        xs, tot = [], 0.0
        for ep in ['ep09', 'ep08', 'ep11', 'ep02', 'ep10', 'ep07', 'ep06', 'ep05']:
            for l in P['episodes'].get(ep, {}).get('lines', []):
                f = os.path.join(ROOT, l.get('file') or '')
                if l['speaker'] == sp and not l.get('inner') and l.get('file') and os.path.exists(f) and 1.2 <= (l.get('len') or 0) <= 3.5:
                    y = pcm(f); xs += [y, np.zeros(int(0.25 * SR), np.float32)]; tot += len(y) / SR
                    if tot >= 20:
                        break
            if tot >= 20:
                break
        y = np.concatenate(xs); write_wav(os.path.join(B, f'sing/ref_{sp}.wav'), y / np.abs(y).max() * 0.8)
        print('샘플', sp, f'{len(y) / SR:.1f}s')


def lines(B):
    return json.load(open(os.path.join(B, 'ref/lyrics.json')))['lines']


def cmd_convert(B):
    for l in lines(B):
        for sp in (['misun', 'changsu'] if l['sp'] == 'both' else [l['sp']]):
            if os.path.exists(out_name(B, l['id'], sp)):
                continue
            subprocess.run(['python3', 'inference.py', '--source', os.path.join(B, f'sing/sts/{l["id"]}_src.wav'), '--target', os.path.join(B, f'sing/ref_{sp}.wav'),
                            '--output', os.path.join(B, 'sing/svc'), '--diffusion-steps', str(STEPS), '--f0-condition', 'True', '--auto-f0-adjust', 'False',
                            '--semi-tone-shift', '0', '--fp16', 'False'], cwd=SEEDVC, capture_output=True)
            print('변환', l['id'], sp)


def cmd_mix(B):
    L = lines(B)
    SC = {l['id']: l for l in json.load(open(os.path.join(B, 'ref/score_best.json')))['lines']}
    total = len(pcm(os.path.join(B, 'ref/sep/htdemucs/ref_audio/vocals.wav')))
    tracks = {sp: np.zeros(total, np.float32) for sp in ('misun', 'changsu')}
    for i, l in enumerate(L):   # 놓을 시각 = sing_sts.py와 같은 줄 구간 시작(t0)
        s0 = SC[l['id']]['syl'][0]['on'] if l['id'] in SC else l['t'][0]
        t0 = max(0.0, s0 - PAD)
        for sp in (['misun', 'changsu'] if l['sp'] == 'both' else [l['sp']]):
            p = out_name(B, l['id'], sp)
            if not os.path.exists(p):
                print('없음', l['id'], sp); continue
            y = pcm(p); i0 = int(t0 * SR); n = min(len(y), total - i0)
            f = int(0.03 * SR); env = np.ones(n); env[:f] = np.linspace(0, 1, f); env[-f:] = np.linspace(1, 0, f)
            tracks[sp][i0:i0 + n] += y[:n] * env
    for sp, y in tracks.items():
        write_wav(os.path.join(B, f'sing/svc_{sp}.wav'), y)
    m, c = os.path.join(B, 'sing/svc_misun.wav'), os.path.join(B, 'sing/svc_changsu.wav')
    acc = os.path.join(B, 'ref/sep/htdemucs/ref_audio/no_vocals.wav')
    ir = os.path.join(ROOT, 'assets/ir/cave_small.wav')
    fc = ("[0:a][1:a]amix=inputs=2:normalize=0,loudnorm=I=-18:TP=-2,asplit[d][w];[w][3:a]afir=dry=10:wet=10,volume=-18dB[r];[d][r]amix=inputs=2:normalize=0[v];"
          "[2:a]aresample=44100,pan=mono|c0=0.5*c0+0.5*c1,loudnorm=I=-22:TP=-3[acc];[v][acc]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[o]")
    subprocess.run([vg.FF, '-y', '-v', 'error', '-i', m, '-i', c, '-i', acc, '-i', ir, '-filter_complex', fc, '-map', '[o]', '-c:a', 'libmp3lame', '-q:a', '2',
                    os.path.join(B, 'sing/svc_preview.mp3')], check=True)
    subprocess.run([vg.FF, '-y', '-v', 'error', '-i', m, '-i', c, '-filter_complex', '[0:a][1:a]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5[o]', '-map', '[o]',
                    '-c:a', 'libmp3lame', '-q:a', '2', os.path.join(B, 'sing/svc_preview_vocals.mp3')], check=True)
    print('미리듣기', os.path.relpath(os.path.join(B, 'sing/svc_preview.mp3'), ROOT))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ep', required=True); ap.add_argument('cmd', choices=['refs', 'convert', 'mix'])
    a = ap.parse_args(); B = os.path.join(ROOT, f'outputs/{a.ep}')
    {'refs': cmd_refs, 'convert': cmd_convert, 'mix': cmd_mix}[a.cmd](B)


if __name__ == '__main__':
    main()
