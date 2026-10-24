#!/usr/bin/env python3
"""ep19 이미지 매니페스트 + 한 장 생성. 사용: python tools/ep19_imgs.py B0  (승인 뒤에만)
프롬프트는 docs/ep19/03_이미지_프롬프트.md 의 '### <id> ...' 코드블록을 읽어 outputs/ep19/prompts/<id>.txt 로 저장한 뒤 nb_generate 호출."""
import os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O = 'outputs/ep19/'
C = 'assets/characters/pang-changsu/'
M = 'assets/characters/pang-misun/'
S = 'assets/spaces/'
PRO = 'gemini-3-pro-image'
LITE = 'gemini-3.1-flash-lite-image'
FLASH = 'gemini-3.1-flash-image'
RATIO = '9:16'

MAN = {
    # 기준 투샷(부모). 침실 B1 밤 + 정면 새 구도 B1f.
    # 새 구도 B1f 빈 방(배경판). v1 실패 교훈: 참조 카메라를 따라가므로 빈 방을 먼저.
    'BF': dict(out=O + 'img/BF_v1.png', model=LITE, refs=[S + 'bedroom_B1_night.png']),
    'B0': dict(out=O + 'img/B0_v2.png', model=PRO,
               refs=[O + 'img/BF_v1.png', 'assets/characters/couple_twoshot_front.png',
                     C + 'pang-changsu_hires_front.png', M + 'pang-misun_hires_front.png',
                     'assets/characters/scale/A1_bed_sit.png']),
    # 변형 9장: 전부 B0 v2 편집. ID = 주 사용 컷 번호(preflight가 숫자를 컷으로 읽음).
    'C03': dict(out=O + 'img/C03_v1.png', model=FLASH, refs=[O + 'img/B0_v2.png', C + 'expressions/pang-changsu_expr_01_neutral.png', C + 'pang-changsu_hires_front.png']),
    'C06': dict(out=O + 'img/C06_v1.png', model=FLASH, refs=[O + 'img/B0_v2.png', C + 'expressions/pang-changsu_expr_12_thinking.png', C + 'pang-changsu_hires_front.png']),
    'C10': dict(out=O + 'img/C10_v1.png', model=FLASH, refs=[O + 'img/B0_v2.png', C + 'expressions/pang-changsu_expr_03_surprised.png', C + 'pang-changsu_hires_front.png']),
    'C11': dict(out=O + 'img/C11_v2.png', model=FLASH, refs=[O + 'img/B0_v2.png', C + 'expressions/pang-changsu_expr_06_sad.png', C + 'pang-changsu_hires_front.png']),
    'C13': dict(out=O + 'img/C13_v2.png', model=FLASH, refs=[O + 'img/B0_v2.png', C + 'expressions/pang-changsu_expr_07_flustered.png', C + 'pang-changsu_hires_front.png']),
    'C16': dict(out=O + 'img/C16_v1.png', model=FLASH, refs=[O + 'img/B0_v2.png', C + 'expressions/pang-changsu_expr_08_amazed.png', C + 'pang-changsu_hires_front.png']),
    'M09': dict(out=O + 'img/M09_v1.png', model=FLASH, refs=[O + 'img/B0_v2.png', M + 'expressions/pang-misun_expr_01_neutral.png', M + 'pang-misun_hires_front.png']),
    'M15': dict(out=O + 'img/M15_v1.png', model=FLASH, refs=[O + 'img/B0_v2.png', M + 'expressions/pang-misun_expr_02_happy.png', M + 'pang-misun_hires_front.png']),
    'C11P': dict(out=O + 'img/C11P_v1.png', model=FLASH, refs=[O + 'img/B0_v2.png', C + 'expressions/pang-changsu_expr_06_sad.png', C + 'pang-changsu_hires_front.png', M + 'pang-misun_hires_front.png']),
    'C14': dict(out=O + 'img/C14_v1.png', model=FLASH, refs=[O + 'img/B0_v2.png', C + 'expressions/pang-changsu_expr_02_happy.png', C + 'pang-changsu_hires_front.png', M + 'pang-misun_hires_front.png']),
}


def prompt_for(pid):
    doc = open(os.path.join(ROOT, 'docs/ep19/03_이미지_프롬프트.md'), encoding='utf-8').read()
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
    cmd = [sys.executable, os.path.join(ROOT, 'tools/nb_generate.py'), '--id', 'ep19-' + pid, '--out', m['out'], '--prompt-file', pf,
           '--ratio', RATIO, '--size', '1K', '--model', m['model']] + sum([['--ref', r] for r in m['refs']], [])
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    print(r.stdout[-600:], r.stderr[-300:] if r.returncode else '')


if __name__ == '__main__':
    main()
