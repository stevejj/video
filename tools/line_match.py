#!/usr/bin/env python3
"""입모양 클립의 대사별 소리 비교(0원): Kling이 대사를 늦추거나 다시 만들었는지 확인(ep08 S6·ep09 S1·S2).
사용: python3 tools/line_match.py --ep ep09 --cut s1 [--tag v1]
대사마다 우리 녹음 조각을 클립 소리에서 ±2s 안에서 찾아 시차·크기 변화 상관·음높이를 보고. 상관 0.8 이상이면 같은 녹음을 옮긴 것, 낮으면 다시 만든 소리.
"""
import argparse, json, os, re, subprocess
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SR = 16000


def pcm(f):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(r, np.float32)


def env(x, h=160):
    n = len(x) // h; return np.sqrt((x[:n * h].reshape(n, h) ** 2).mean(1))


def pitch(seg):
    out = []
    for i in range(0, len(seg) - 800, 320):
        fr = seg[i:i + 800] - seg[i:i + 800].mean()
        if np.sqrt(np.mean(fr ** 2)) < 0.02: continue
        ac = np.correlate(fr, fr, 'full')[799:]; lo, hi = SR // 900, SR // 120; k = lo + np.argmax(ac[lo:hi])
        if ac[k] / ac[0] > 0.4: out.append(SR / k)
    return round(float(np.median(out))) if out else 0


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ep', required=True); ap.add_argument('--cut', required=True); ap.add_argument('--tag', default='v1')
    a = ap.parse_args()
    V = json.load(open(os.path.join(ROOT, 'outputs/voice_profile.json')))['episodes'][a.ep]
    c = pcm(os.path.join(ROOT, f'outputs/{a.ep}/{a.cut}/clip_{a.tag}.mp4')); ec = env(c)
    n = a.cut[1:]; res = []
    for l in V['lines']:
        if re.match(r'\d+', l['cut'])[0] != n: continue
        r = pcm(os.path.join(ROOT, l['file'])); er = env(r); t0 = l['scene_at']; i0 = int(t0 * 100)
        best = (-1, 0)
        for sh in range(-100, 201):
            j = i0 + sh
            if j < 0 or j + len(er) > len(ec): continue
            cc = np.corrcoef(ec[j:j + len(er)], er)[0, 1]
            if cc > best[0]: best = (cc, sh)
        j = i0 + best[1]
        res.append(dict(cut=l['cut'], speaker=l['speaker'], ours=t0, clip=round(j / 100, 2), shift=round(best[1] / 100, 2), corr=round(best[0], 2),
                        pitch_ours=pitch(r), pitch_clip=pitch(c[j * 160:j * 160 + len(r)])))
        print(f"{l['cut']} {l['speaker']:8s} 우리 {t0:.2f}s → 클립 {j / 100:.2f}s (시차 {best[1] / 100:+.2f}s) 상관 {best[0]:.2f} 음높이 {res[-1]['pitch_ours']}→{res[-1]['pitch_clip']}Hz")
    json.dump(res, open(os.path.join(ROOT, f'outputs/{a.ep}/{a.cut}/verify_{a.tag}/line_match.json'), 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
