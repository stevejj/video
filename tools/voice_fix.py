#!/usr/bin/env python3
"""발음 관문: 녹음한 대사를 받아쓰기(faster-whisper, 로컬 0원)로 확인하고, 원문과 다르면 다른 seed로 다시 녹음.
사용: python3 tools/voice_fix.py --ep ep08 --cuts 3b,4b,5b [--seeds 7,1234,99,2024] [--min 0.8]
원문과 받아쓰기의 한글 글자 유사도가 --min 이상인 첫 seed를 채택. 모두 미달이면 가장 높은 것을 쓰고 '사람 확인 필요'로 표시.
"""
import argparse, difflib, json, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROF = os.path.join(ROOT, 'outputs/voice_profile.json')
_M = None


def heard(path):
    global _M
    from faster_whisper import WhisperModel
    if _M is None:
        _M = WhisperModel('medium', device='cpu', compute_type='int8', download_root='/tmp/claude-0/-home-user-video/f018d661-8ddb-51f7-8e2d-f2480d28ac5d/scratchpad/models/whisper')
    segs, _ = _M.transcribe(path, language='ko')
    return ''.join(s.text for s in segs).strip()


def sim(a, b):
    k = lambda s: re.sub(r'[^가-힣]', '', s)
    return difflib.SequenceMatcher(None, k(a), k(b)).ratio()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ep', required=True); ap.add_argument('--cuts', required=True)
    ap.add_argument('--seeds', default='7,1234,99,2024'); ap.add_argument('--min', type=float, default=0.8)
    a = ap.parse_args()
    for cut in a.cuts.split(','):
        results = []
        for seed in [int(x) for x in a.seeds.split(',')]:
            P = json.load(open(PROF)); P['candidate_seeds'] = [seed]
            for l in P['episodes'][a.ep]['lines']:
                if l['cut'] == cut: l.pop('seed', None)
            json.dump(P, open(PROF, 'w'), ensure_ascii=False, indent=1)
            subprocess.run([sys.executable, os.path.join(ROOT, 'tools/voice_gen.py'), '--ep', a.ep, '--regen', cut, '--candidates', '1'], capture_output=True)
            P = json.load(open(PROF)); l = [x for x in P['episodes'][a.ep]['lines'] if x['cut'] == cut][0]
            h = heard(os.path.join(ROOT, l['file'])); s = sim(l['tts'], h)
            print(f'[{cut}] seed {seed}: "{h}" 유사도 {s:.2f}')
            results.append((s, seed))
            if s >= a.min: break
        best = max(results)
        if best[0] < a.min:  # 최고 seed로 다시 맞춤
            P = json.load(open(PROF)); P['candidate_seeds'] = [best[1]]
            json.dump(P, open(PROF, 'w'), ensure_ascii=False, indent=1)
            subprocess.run([sys.executable, os.path.join(ROOT, 'tools/voice_gen.py'), '--ep', a.ep, '--regen', cut, '--candidates', '1'], capture_output=True)
            print(f'[{cut}] ⚠ 기준 미달 → 최고 seed {best[1]}({best[0]:.2f}) 채택, 사람 확인 필요')
        else:
            print(f'[{cut}] ✓ seed {best[1]} 채택')
    P = json.load(open(PROF)); P['candidate_seeds'] = [42, 7, 1234]; json.dump(P, open(PROF, 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
