#!/usr/bin/env python3
"""ep07 이미지 체인 실행기. 사용: python3 tools/ep07_imgs.py <W1|C1|C2>
프롬프트는 docs/ep07/03_이미지_프롬프트.md 의 '### <id> ' 섹션 코드블록. 한 장만 만들고 부모|결과 비교 시트 저장.
05c: 사용자 "진행" 후 한 장씩, 자동 재시도 0."""
import re, sys, os, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = 'assets/characters/pang-changsu/'; M = 'assets/characters/pang-misun/'; O = 'outputs/ep07/'
FLASH = 'gemini-3.1-flash-image'; PRO = 'gemini-3-pro-image'
MAN = {
 'W1': dict(out=O + 'w1/start_v1.png', model=PRO, refs=[M + 'pang-misun_hires_front.png', M + 'pang-misun_pose_hold_cup.png', C + 'pang-changsu_hires_front.png', C + 'pang-changsu_pose_hold_cup.png']),
 'C1': dict(out=O + 'c1/start_v1.png', model=FLASH, refs=[O + 'w1/start_v1.png']),
 'W2': dict(out=O + 'w2/start_v1.png', model=FLASH, refs=[O + 'w1/start_v1.png']),
 'C2': dict(out=O + 'c2/start_v1.png', model=FLASH, refs=[O + 'w1/start_v1.png', M + 'pang-misun_face_eyes_closed.png', C + 'pang-changsu_face_eyes_closed.png']),
}


def prompt_for(pid):
    doc = open(os.path.join(ROOT, 'docs/ep07/03_이미지_프롬프트.md'), encoding='utf-8').read()
    for sec in doc.split('\n### ')[1:]:
        if re.match(re.escape(pid) + r' ', sec):
            return re.search(r'```\n(.*?)\n```', sec, re.S).group(1)
    raise SystemExit('no prompt for ' + pid)


def main():
    pid = sys.argv[1]; m = MAN[pid]
    pd = os.path.join(ROOT, O, 'prompts'); os.makedirs(pd, exist_ok=True)
    pf = os.path.join(pd, f'{pid}.txt'); open(pf, 'w', encoding='utf-8').write(prompt_for(pid))
    os.makedirs(os.path.dirname(os.path.join(ROOT, m['out'])), exist_ok=True)
    for r in m['refs']:
        assert os.path.exists(os.path.join(ROOT, r)), 'missing ref ' + r
    cmd = [sys.executable, os.path.join(ROOT, 'tools/nb_generate.py'), '--id', 'ep07-' + pid, '--out', m['out'], '--prompt-file', pf,
           '--ratio', '9:16', '--size', '1K', '--model', m['model']] + sum([['--ref', r] for r in m['refs']], [])
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    print(r.stdout[-600:], r.stderr[-300:] if r.returncode else '')
    if r.returncode:
        sys.exit(r.returncode)
    from PIL import Image
    a = Image.open(os.path.join(ROOT, m['refs'][0])).convert('RGB'); b = Image.open(os.path.join(ROOT, m['out'])).convert('RGB')
    h = 760; a2 = a.resize((int(a.width * h / a.height), h)); b2 = b.resize((int(b.width * h / b.height), h))
    o = Image.new('RGB', (a2.width + b2.width + 10, h), 'white'); o.paste(a2, (0, 0)); o.paste(b2, (a2.width + 10, 0))
    sheet = os.path.join(pd, f'cmp_{pid}.jpg'); o.save(sheet, quality=85)
    print('size', b.size, 'sheet', sheet)


if __name__ == '__main__':
    main()
