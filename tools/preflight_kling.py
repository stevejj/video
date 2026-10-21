#!/usr/bin/env python3
"""Kling 제출 전 사전 점검(G2+, 0원). lint_prompts(문구 규칙) 위에, 영상에서 돈이 나가는 실수를 잡는다.
사용: python3 tools/preflight_kling.py --ep ep09 [--ids S1,S2] [--cap 400]
문서 docs/<ep>/04_Kling_실행표.md 의 '## S<n> 제목' 섹션: **입력**(백틱 경로), **인자**(duration=N, "S1과 같음" 허용), 첫 코드블록.
검사(✗=실패 → 승인 요청 금지):
 A 문구 규칙: lint_prompts 영상 규칙 전체(대사 원문·in Korean·눈썹·볼터치·날개 등).
 B 입력 파일: 이미지·음성 파일이 있음.
 C 대사 원문: 프롬프트의 따옴표 한글 대사 = 그 장면 녹음 대사(voice_profile lines, 태그 제외), 개수·순서까지(ep07 S1 영어 대사 사고, ep08 S6 대사 변경).
 D 음성 길이: 음성 참조는 5초 이상, 영상 길이(duration) 이하.
 E 저작권: 대사·프롬프트에 팽/펭 + 수 조합, 브랜드 이름 없음(ep08 S6).
 F 화면 밖 화자: 그 장면 시작 이미지에 없는 캐릭터가 말하면 "off-screen" 명시.
 G 비용: 모델 단가 x 길이 합계 ≤ cap.
"""
import argparse, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import lint_prompts  # noqa: E402
from preflight_images import BRANDS  # noqa: E402

RATE = {'kling-video-v4_0': 9, 'kling-video-v3_0': 6}  # Pro 등급 초당 크레딧(ep08 실측)


def dur(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path], capture_output=True, text=True).stdout
    return float(out.strip() or 0)


def norm(s):
    return re.sub(r'[^가-힣]', '', re.sub(r'\[[^\]]*\]', '', s))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ep', required=True); ap.add_argument('--ids', default=''); ap.add_argument('--cap', type=int, default=400)
    a = ap.parse_args()
    doc = open(os.path.join(ROOT, f'docs/{a.ep}/04_Kling_실행표.md'), encoding='utf-8').read()
    V = json.load(open(os.path.join(ROOT, 'outputs/voice_profile.json')))['episodes'][a.ep]
    PR = json.load(open(os.path.join(ROOT, f'outputs/{a.ep}/props.json')))
    secs = {}; first_args = None
    for sec in doc.split('\n## ')[1:]:
        head = sec.split('\n', 1)[0]
        m = re.match(r'(S\d+)\s', head)
        if not m or '[기록]' in head:
            continue
        inp = re.search(r'\*\*입력\*\*:(.*)', sec); arg = re.search(r'\*\*인자\*\*:(.*)', sec); code = re.search(r'```\n(.*?)\n```', sec, re.S)
        args = arg.group(1) if arg else ''
        if 'model=' in args:
            first_args = first_args or args
        else:
            args = (first_args or '') + ' ' + args  # "S1과 같음, duration=6"
        d = re.findall(r'duration=(\d+)', args)
        secs[m.group(1)] = dict(title=head, inputs=re.findall(r'`([^`]+)`', inp.group(1) if inp else ''), model=re.search(r'model=(kling-video-v\d_\d)', args).group(1),
                                duration=int(d[-1]) if d else 0, prompt=code.group(1) if code else '')
    ids = [x for x in (a.ids.split(',') if a.ids else secs.keys()) if x]
    fails = 0; cost = 0
    for sid in ids:
        S = secs[sid]; p = S['prompt']; F = []; n = sid[1:]
        for nm, why, c, need in lint_prompts.rules('video'):
            if c(p) and not need(p):
                F.append(f'A {nm} ← {why}')
        for f in S['inputs']:
            if not os.path.exists(os.path.join(ROOT, f)):
                F.append(f'B 입력 파일 없음: {f}')
        quoted = [norm(x) for x in re.findall(r'"([^"]*[가-힣][^"]*)"', p)]
        lines = [l for l in V['lines'] if re.match(r'\d+', l['cut'])[0] == n]
        audio = [f for f in S['inputs'] if f.endswith('.mp3')]
        if audio:
            want = [norm(l['tts']) for l in lines]
            if quoted != want:
                F.append(f'C 대사 원문 불일치: 프롬프트 {quoted} ≠ 녹음 {want}')
            L = dur(os.path.join(ROOT, audio[0]))
            if L < 5.0:
                F.append(f'D 음성 {L:.2f}s < 5초(Kling 최소)')
            if L > S['duration'] + 0.05:
                F.append(f'D 음성 {L:.2f}s > 영상 {S["duration"]}s')
        if re.search(r'"[^"]*[팽펭][^"]*"', p) or any(re.search(w, p, re.I) for w in BRANDS):
            F.append('E 저작권 위험 단어(팽/펭 대사·브랜드)')
        cut = n.zfill(2)
        on_screen = set(PR.get('lipsync', {}).get(cut, [])) | {k.split('_')[0] for k in PR.get('states', {}).get(cut, {}) if k.endswith('_outfit')}
        for l in lines:
            if audio and l['speaker'] not in on_screen and not re.search(r'off-screen|not in the picture', p, re.I):
                F.append(f'F {l["speaker"]}가 화면에 없는데 말함 → "off-screen" 명시 필요')
        c = RATE.get(S['model'], 0) * S['duration']; cost += c
        print(f'{"✗" if F else "✓"} {sid} {S["title"][len(sid):].strip()}  [{S["model"]}, {S["duration"]}s, {c}크레딧]')
        for x in F: print('   ✗', x)
        fails += len(F)
    print(f'\n비용 합계 약 {cost}크레딧 (상한 {a.cap}){" ✗ 초과" if cost > a.cap else ""}')
    fails += cost > a.cap
    print('결과:', '통과' if not fails else f'실패 {fails}건 → 고치기 전에는 승인 요청·제출 금지')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
