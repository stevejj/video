#!/usr/bin/env python3
"""ep18 대사 녹음 — 후보 여러 개 → 처리 뒤(1.25배 캐릭터 톤) 받아쓰기로 고름(ep11 v15 방식).
사용: python3 tools/ep18_voice.py [--only C1a,C9] → outputs/ep18/voice/cands/*.mp3, best.json, lines/<cut>.mp3, preview.mp3
- 줄마다 감정 태그 2종 × seed 4개. 점수 = 받아쓰기 틀린 정도×4 + 목표 길이에서 벗어난 정도.
- 고른 결과는 voice_profile.json episodes.ep18.lines 에 기록.
"""
import argparse, difflib, json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_gen as vg, voice_emote as ve

ROOT = vg.ROOT
OUT = os.path.join(ROOT, 'outputs/ep18/voice')
SEEDS = (42, 7, 1234, 99)
# cut: (화자, 자막, 목표 길이(처리 뒤 s), [tts 후보 2종])
LINES = {
    'C1a': ('changsu', '미순아, 옷 많잖아~', 1.5, ['[teasing, gentle] 미순아, 옷 많잖아~', '[playful, amused] 미순아, 옷 많잖아~']),   # v11 사용자: 자기 → 미순아
    'C1b': ('misun', '아니야, 입을 옷이 없어!', 1.5, ['[whiny, pouting] 아니야, 입을 옷이 없어!', '[frustrated, cute] 아니야~ 입을 옷이 없어!']),
    'C2': ('changsu', '입을 옷이… 없다고?', 1.6, ['[doubtful, suspicious] 입을 옷이... 없다고?', '[slowly, skeptical] 입을 옷이... 없다고?']),
    'C4a': ('changsu', '그럼 이건 다 뭔데?', 1.3, ['[exasperated] 그럼 이건 다 뭔데?', '[muffled, annoyed] 그럼 이건 다 뭔데?']),
    'C4b': ('misun', '이건 작년 거고~ 저건 작아졌어!', 2.0, ['[defensive, quick] 이건 작년 거고~ 저건 작아졌어!', '[pouting, matter-of-fact] 이건 작년 거고~ 저건 작아졌어!']),
    'C5': ('changsu', '그럼 안 입는 거부터 정리해 봐.', 1.8, ['[calm, firm] 그럼 안 입는 거부터 정리해 봐.', '[patient, sighing] 그럼 안 입는 거부터 정리해 봐.']),
    'C6': ('misun', '이건 버리고~', 1.0, ['[cheerful, obedient] 이건 버리고~', '[sing-song, cute] 이건 버리고~']),
    'C7': ('misun', '이건… 아까운데…', 1.6, ['[hesitant, sad, clingy] 이건... 아까운데...', '[whispering, reluctant] 이건... 아까운데...']),
    'C8': ('changsu', '하… 그대로인데?', 1.6, ['[long sigh, deadpan] 하... 그대로인데?', '[sighs, tired] 하... 그대로인데?']),
    'C9': ('misun', '자기 미워!!', 1.0, ['[sulky, whining loudly] 자기 미워!!', '[upset, crying out] 자기 미워!!']),
    'C10a': ('changsu', '자기 옷 사주려고 정리하자고 한 거지~', 2.2, ['[soothing, sweet] 자기 옷 사주려고 정리하자고 한 거지~', '[gentle, apologetic] 자기 옷 사주려고 정리하자고 한 거지~']),
    'C10b': ('changsu', '우리 패딩 보러 갈까?', 1.3, ['[gentle, coaxing] 우리 패딩 보러 갈까?', '[warm, hopeful] 우리, 패딩 보러 갈까?']),
    'C11': ('misun', '정말?!', 0.7, ['[sniffling, suddenly hopeful] 정말?!', '[gasps, excited] 정말?!']),
    'C12': ('misun', '이미 담아놨지롱~', 1.3, ['[smug, sly, giggling] 이미 담아놨지롱~', '[playful, mischievous] 이미 담아놨지롱~']),
}
nt = lambda z: re.sub(r'[^가-힣]', '', z)


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
    ap = argparse.ArgumentParser(); ap.add_argument('--only', default='')
    a = ap.parse_args()
    only = [x for x in a.only.split(',') if x]
    P = json.load(open(vg.PROF)); vg.POST = P.get('post', {})
    os.makedirs(f'{OUT}/cands', exist_ok=True); os.makedirs(f'{OUT}/lines', exist_ok=True)
    todo = {c: v for c, v in LINES.items() if not only or c in only}
    jobs = [(sp, text, seed, f'{OUT}/cands/{c}_t{ti}_s{seed}.mp3')
            for c, (sp, sub, tgt, tags) in todo.items() for ti, text in enumerate(tags) for seed in SEEDS]
    with ThreadPoolExecutor(2) as ex:   # 계정 동시 처리 한도 3
        list(ex.map(lambda j: gen(P, *j), jobs))
    print('생성 완료', len(jobs), flush=True)

    from faster_whisper import WhisperModel
    m = WhisperModel('medium', compute_type='int8')
    bp = f'{OUT}/cands/best.json'
    best = json.load(open(bp)) if os.path.exists(bp) else {}
    tmp = f'{OUT}/cands/_fin.mp3'
    for c, (sp, sub, tgt, tags) in todo.items():
        rows = []
        for ti, text in enumerate(tags):
            for seed in SEEDS:
                src = f'{OUT}/cands/{c}_t{ti}_s{seed}.mp3.t.mp3'
                vg.finalize(src, tmp, P['loudnorm'], sp, False, 1.0, 1.25)
                d = vg.duration(tmp)
                h = ve.transcribe(m, tmp)[0].strip()
                sim = difflib.SequenceMatcher(None, nt(sub), nt(h)).ratio()
                score = (1 - sim) * 4 + abs(d - tgt) / tgt
                rows.append(dict(score=round(score, 3), t=ti, seed=seed, len=round(d, 2), heard=h, src=os.path.relpath(src, ROOT), tts=text))
        rows.sort(key=lambda r: r['score'])
        best[c] = dict(rows[0], top=[(r['score'], f"t{r['t']}s{r['seed']}", r['len'], r['heard']) for r in rows[:4]])
        b = rows[0]
        vg.finalize(os.path.join(ROOT, b['src']), f'{OUT}/lines/{c}.mp3', P['loudnorm'], sp, False, 1.0, 1.25)
        print(c, sub, '→', best[c]['top'][:3], flush=True)
    if os.path.exists(tmp):
        os.remove(tmp)
    json.dump(best, open(bp, 'w'), ensure_ascii=False, indent=1)

    # 프로필 기록
    lines = []
    for c, (sp, sub, tgt, tags) in LINES.items():
        if c not in best:
            continue
        b = best[c]
        lines.append(dict(cut=c, speaker=sp, subtitle=sub, tts=b['tts'], seed=b['seed'], speedup=1.25, inner=False,
                          len=vg.duration(f'{OUT}/lines/{c}.mp3'), file=f'outputs/ep18/voice/lines/{c}.mp3'))
    P = json.load(open(vg.PROF))
    P['episodes']['ep18'] = {'lines': lines}
    json.dump(P, open(vg.PROF, 'w'), ensure_ascii=False, indent=1)

    # 미리 듣기: 줄 사이 0.45s 쉼
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
