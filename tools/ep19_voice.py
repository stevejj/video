#!/usr/bin/env python3
"""ep19 대사 녹음 — ep18 방식 그대로: 줄마다 감정 태그 2종 × seed 4 → 무음 제거 → 1.25배 → 받아쓰기로 고름.
사용: python tools/ep19_voice.py [--only L09,L11] → outputs/ep19/voice/cands/*.mp3, best.json, lines/<id>.mp3, preview.mp3
- 점수 = 받아쓰기 틀린 정도×4 + 목표 길이에서 벗어난 정도. 속마음(inner)은 조립 때 약한 울림을 따로 얹음(ep16 방식).
- 고른 결과는 voice_profile.json episodes.ep19.lines 에 기록.
"""
import argparse, difflib, json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_gen as vg, voice_emote as ve

ROOT = vg.ROOT
OUT = os.path.join(ROOT, 'outputs/ep19/voice')
SEEDS = (42, 7, 1234, 99)
# id: (화자, 자막, 목표 길이(처리 뒤 s), 속마음 여부, [tts 후보 2종])  — 기획안 "대사 줄 규격" 표
LINES = {
    'L01':  ('misun',   '아 이거 진짜 웃기다 ㅋㅋ', 1.8, False, ['[giggling, amused] 아 이거 진짜 웃기다', '[laughs] 아, 이거 진짜 웃기다']),
    'L04':  ('changsu', '(치맥…)', 0.8, True,  ['[quietly, low voice, tempted] 치맥...', '[whispering, longing] 치맥...']),
    'L06a': ('changsu', '(토요일에… 자기한테 뭐라고 하지)', 2.4, True, ['[quietly, low voice, thinking] 토요일에... 자기한테 뭐라고 하지', '[muttering, hesitant] 토요일에... 자기한테 뭐라고 하지']),
    'L06b': ('changsu', '말할까말까말까말까할까말까', 2.4, True, ['[muttering quickly, anxious] 말할까 말까 말까 말까 할까 말까', '[whispering fast, torn] 말할까 말까 말까 말까 할까 말까']),  # 2026-10-24 사용자 변경
    'L07':  ('misun',   '자기야.', 0.7, False, ['[flat, casual] 자기야.', '[calm, matter-of-fact] 자기야.']),
    'L08':  ('changsu', '응, 왜?', 0.7, False, ['[casual, calm] 응, 왜?', '[nonchalant, relaxed] 응, 왜?']),
    'L09':  ('misun',   '나 토요일에 친구들이랑 저녁 먹어도 돼? 좀 늦을 것 같은데.', 3.8, False,
             ['[casual, asking] 나 토요일에 친구들이랑 저녁 먹어도 돼? 좀 늦을 것 같은데.', '[gentle, a little careful] 나 토요일에 친구들이랑 저녁 먹어도 돼? 좀 늦을 것 같은데.']),
    'L10a': ('changsu', '(토요일…?)', 0.9, True, ['[quietly, surprised, low voice] 토요일...?', '[whispering, stunned] 토요일...?']),
    'L10b': ('changsu', '(이게 되네?)', 0.9, True, ['[quietly, delighted, holding back a laugh] 이게 되네?', '[whispering, excited] 이게 되네?']),
    'L11':  ('changsu', '아… 토요일에? 미순이 없이 나 혼자 뭐 하냐…', 3.2, False,
             ['[slow, low voice, trailing off, pretending to be sad] 아... 토요일에? 미순이 없이 나 혼자 뭐 하냐...', '[sighing, drawn out, sulky] 아... 토요일에? 미순이 없이 나 혼자 뭐 하냐...']),
    'L12':  ('misun',   '그런가? 그럼 가지 말까?', 1.8, False, ['[thoughtful, soft] 그런가? 그럼 가지 말까?', '[hesitant, considering] 그런가? 그럼 가지 말까?']),
    'L13':  ('changsu', '어어어, 아니아니아니.', 1.4, False, ['[flustered, quick, panicked] 어어어, 아니 아니 아니.', '[hurried, nervous] 어어어, 아니아니아니.']),
    'L14':  ('changsu', '아니야, 재밌게 놀다 와~ 나도 그냥… 친구나 만나지 뭐.', 3.6, False,
             ['[reassuring, cheerful, slightly forced] 아니야, 재밌게 놀다 와. 나도 그냥... 친구나 만나지 뭐.', '[casual, hiding excitement] 아니야, 재밌게 놀다 와. 나도 그냥... 친구나 만나지 뭐.']),
    'L15':  ('misun',   '그래? 그럼 나 잡는다~', 1.6, False, ['[cheerful, light] 그래? 그럼 나 잡는다~', '[happy, bouncy] 그래? 그럼 나 잡는다~']),
    'L16':  ('changsu', '야야야 토요일 콜!!!', 1.3, False, ['[whispering excitedly, urgent] 야야야 토요일 콜!', '[hushed, thrilled] 야야야, 토요일 콜!']),
}
nt = lambda z: re.sub(r'[^가-힣]', '', z)


def transcribe(m, path):
    """ve.transcribe와 같되 PyAV 대신 ffmpeg로 16k mono float32를 읽어 넘김(이 PC의 av 19와 faster-whisper 비호환 회피)."""
    import numpy as np
    raw = subprocess.run([vg.FF, '-v', 'error', '-i', path, '-af', 'adelay=500,apad=pad_dur=0.4', '-ar', '16000', '-ac', '1', '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, dtype=np.float32)
    seg, _ = m.transcribe(audio, language='ko', beam_size=5)
    return ''.join(s.text for s in seg)


def gen(P, sp, text, seed, raw):
    if os.path.exists(raw + '.t.mp3'):
        return
    for k in range(5):
        try:
            vg.post(f'/v1/text-to-speech/{P["voices"][sp]}?output_format=mp3_44100_128',
                    {'text': text, 'model_id': P['model_id'], 'language_code': 'ko', 'seed': seed,
                     'voice_settings': dict(P['voice_settings'], stability=0.5)}, raw)
            break
        except SystemExit as e:
            print('  재시도', e, flush=True); time.sleep(4 * (k + 1))
    vg.trim(raw, raw + '.t.mp3')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--only', default=''); ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    only = [x for x in a.only.split(',') if x]
    todo = {c: v for c, v in LINES.items() if not only or c in only}
    jobs = [(sp, text, seed, f'{OUT}/cands/{c}_t{ti}_s{seed}.mp3')
            for c, (sp, sub, tgt, inner, tags) in todo.items() for ti, text in enumerate(tags) for seed in SEEDS]
    chars = sum(len(j[1]) for j in jobs)
    print(f'줄 {len(todo)} · 호출 {len(jobs)} · 글자 약 {chars}')
    if a.dry:
        return
    P = json.load(open(vg.PROF)); vg.POST = P.get('post', {})
    os.makedirs(f'{OUT}/cands', exist_ok=True); os.makedirs(f'{OUT}/lines', exist_ok=True)
    with ThreadPoolExecutor(2) as ex:   # 계정 동시 처리 한도 3
        list(ex.map(lambda j: gen(P, *j), jobs))
    print('생성 완료', len(jobs), flush=True)

    from faster_whisper import WhisperModel
    m = WhisperModel('medium', device='cpu', compute_type='int8')
    bp = f'{OUT}/cands/best.json'
    best = json.load(open(bp)) if os.path.exists(bp) else {}
    tmp = f'{OUT}/cands/_fin.mp3'
    for c, (sp, sub, tgt, inner, tags) in todo.items():
        rows = []
        for ti, text in enumerate(tags):
            for seed in SEEDS:
                src = f'{OUT}/cands/{c}_t{ti}_s{seed}.mp3.t.mp3'
                if not os.path.exists(src):
                    continue
                vg.finalize(src, tmp, P['loudnorm'], sp, False, 1.0, 1.25)
                d = vg.duration(tmp)
                h = transcribe(m, tmp).strip()
                sim = difflib.SequenceMatcher(None, nt(sub), nt(h)).ratio()
                score = (1 - sim) * 4 + abs(d - tgt) / tgt
                rows.append(dict(score=round(score, 3), t=ti, seed=seed, len=round(d, 2), heard=h, src=os.path.relpath(src, ROOT), tts=text))
        if not rows:
            print(c, '후보 없음(생성 실패)'); continue
        rows.sort(key=lambda r: r['score'])
        best[c] = dict(rows[0], top=[(r['score'], f"t{r['t']}s{r['seed']}", r['len'], r['heard']) for r in rows[:4]])
        b = rows[0]
        vg.finalize(os.path.join(ROOT, b['src']), f'{OUT}/lines/{c}.mp3', P['loudnorm'], sp, False, 1.0, 1.25)
        print(c, sub, '→', best[c]['top'][:3], flush=True)
    if os.path.exists(tmp):
        os.remove(tmp)
    json.dump(best, open(bp, 'w'), ensure_ascii=False, indent=1)

    lines = []
    for c, (sp, sub, tgt, inner, tags) in LINES.items():
        if c not in best:
            continue
        b = best[c]
        lines.append(dict(cut=c, speaker=sp, subtitle=sub, tts=b['tts'], seed=b['seed'], speedup=1.25, inner=inner,
                          len=vg.duration(f'{OUT}/lines/{c}.mp3'), file=f'outputs/ep19/voice/lines/{c}.mp3'))
    P = json.load(open(vg.PROF))
    P.setdefault('episodes', {})['ep19'] = {'lines': lines}
    json.dump(P, open(vg.PROF, 'w'), ensure_ascii=False, indent=1)

    gap = f'{OUT}/cands/_gap.wav'
    subprocess.run([vg.FF, '-y', '-v', 'error', '-f', 'lavfi', '-t', '0.45', '-i', 'anullsrc=r=44100:cl=mono', gap], check=True)
    ins = []
    for l in lines:
        ins += ['-i', os.path.join(ROOT, l['file']), '-i', gap]
    n = len(ins) // 2
    fc = ''.join(f'[{i}:a]aresample=44100,aformat=channel_layouts=mono[a{i}];' for i in range(n)) + ''.join(f'[a{i}]' for i in range(n)) + f'concat=n={n}:v=0:a=1[o]'
    subprocess.run([vg.FF, '-y', '-v', 'error', *ins, '-filter_complex', fc, '-map', '[o]', '-c:a', 'libmp3lame', '-q:a', '2', f'{OUT}/preview.mp3'], check=True)
    os.remove(gap)
    print('미리 듣기', f'{OUT}/preview.mp3')


if __name__ == '__main__':
    main()
