#!/usr/bin/env python3
"""Kling 클립 검수 묶음(G3, 0원): 다운로드 → qa_clip(볼터치·멈춤·음성 상관) → 받아쓰기 → 동작 시트 → 첫/끝 프레임 눈 크기.
사용: python3 tools/clip_review.py --ep ep09 --cut s1 --url URL [--tag v1] [--voice]
결과: outputs/<ep>/<cut>/clip_<tag>.mp4, verify_<tag>/motion_sheet.jpg, review.txt
"""
import argparse, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    return (r.stdout + r.stderr).strip()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ep', required=True); ap.add_argument('--cut', required=True); ap.add_argument('--url')
    ap.add_argument('--tag', default='v1'); ap.add_argument('--voice', action='store_true', help='입모양 장면: 장면 음성과 상관·받아쓰기')
    a = ap.parse_args()
    d = os.path.join(ROOT, f'outputs/{a.ep}/{a.cut}'); os.makedirs(d, exist_ok=True)
    clip = os.path.join(d, f'clip_{a.tag}.mp4'); vd = os.path.join(d, f'verify_{a.tag}'); os.makedirs(vd, exist_ok=True)
    if a.url:
        subprocess.run(['curl', '-sS', '-o', clip, a.url], check=True)
    rep = []
    qa = [sys.executable, 'tools/qa_clip.py', clip]
    if a.voice:
        qa += ['--voice-ref', f'outputs/{a.ep}/voice/scenes/{a.cut}.mp3']
    rep.append('[qa_clip]\n' + run(qa))
    dur = float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', clip]))
    if a.voice:
        from faster_whisper import WhisperModel
        m = WhisperModel('medium', device='cpu', compute_type='int8', download_root='/tmp/claude-0/-home-user-video/f018d661-8ddb-51f7-8e2d-f2480d28ac5d/scratchpad/models/whisper')
        segs, _ = m.transcribe(clip, language='ko', word_timestamps=True)
        rep.append('[받아쓰기] ' + ' '.join(f'{w.start:.2f}:{w.word.strip()}' for s in segs for w in s.words))
    ts = [round(i * (dur - 0.08) / 7, 2) for i in range(8)]
    for k, t in enumerate(ts):
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(t), '-i', clip, '-frames:v', '1', '-vf',
                        f"scale=270:-1,drawtext=text='{t}':x=6:y=6:fontsize=22:fontcolor=yellow:box=1:boxcolor=black", os.path.join(vd, f'f_{k}.png')])
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', os.path.join(vd, 'f_%d.png'), '-filter_complex', 'tile=8x1', '-frames:v', '1', os.path.join(vd, 'motion_sheet.jpg')])
    for k in range(8):
        os.remove(os.path.join(vd, f'f_{k}.png'))
    rep.append(f'[길이] {dur:.2f}s  시트 {os.path.relpath(vd, ROOT)}/motion_sheet.jpg')
    txt = '\n'.join(rep); open(os.path.join(vd, 'review.txt'), 'w').write(txt); print(txt)


if __name__ == '__main__':
    main()
