#!/usr/bin/env python3
"""ep02 이미지 체인 실행기. 사용: python3 tools/ep02_imgs.py <id>  (B2, 1s, 1e, ...)
프롬프트는 docs/ep02/03_이미지_프롬프트_v2.md의 해당 섹션 코드블록에서 추출. 한 장만 만들고 비교 시트를 저장한다."""
import re, sys, os, json, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = 'assets/characters/pang-changsu/'; M = 'assets/characters/pang-misun/'; O = 'outputs/ep02/'
PRO = 'gemini-3-pro-image'; FLASH = 'gemini-3.1-flash-image'
MAN = {
 'B2': dict(out='assets/spaces/living_L1_night_misun_lying.png', model=PRO, refs=['assets/spaces/living_L1_night_empty.png','outputs/ep01/9-04/start_v1.png',M+'pang-misun_hires_front.png',M+'pang-misun_pose_lying.png',M+'expressions/pang-misun_expr_02_happy.png','assets/spaces/bedroom_B1_night.png']),
 '1s': dict(out=O+'01/start_v1.png', model=FLASH, refs=['assets/spaces/living_L1_night_misun_lying.png',C+'pang-changsu_hires_front.png',C+'pang-changsu_pose_walk_side.png',C+'expressions/pang-changsu_expr_01_neutral.png']),
 '1e': dict(out=O+'01/end_v1.png', model=FLASH, refs=[O+'01/start_v1.png',C+'pang-changsu_hires_front.png',C+'expressions/pang-changsu_expr_01_neutral.png']),
 '3s': dict(out=O+'03/start_v1.png', model=FLASH, refs=[O+'01/end_v1.png',C+'pang-changsu_hires_front.png',C+'expressions/pang-changsu_expr_01_neutral.png']),
 '2s': dict(out=O+'02/start_v1.png', model=FLASH, refs=['assets/spaces/living_L1_night_misun_lying.png',M+'pang-misun_hires_front.png',M+'pang-misun_pose_lying.png',M+'expressions/pang-misun_expr_02_happy.png']),
 '2e': dict(out=O+'02/end_v1.png', model=FLASH, refs=[O+'02/start_v1.png',M+'pang-misun_hires_front.png',M+'expressions/pang-misun_expr_02_happy.png']),
 '4s': dict(out=O+'04/start_v1.png', model=FLASH, refs=[O+'01/start_v1.png',C+'pang-changsu_hires_front.png',C+'pang-changsu_pose_hold_cup.png']),
 '4e': dict(out=O+'04/end_v1.png', model=FLASH, refs=[O+'01/end_v1.png',C+'pang-changsu_hires_front.png',M+'pang-misun_hires_front.png',M+'pang-misun_pose_hold_cup.png']),
 '5s': dict(out=O+'05/start_v1.png', model=FLASH, refs=[O+'01/end_v1.png',C+'pang-changsu_hires_front.png']),
 '6s': dict(out=O+'06/start_v1.png', model=FLASH, refs=[O+'04/start_v1.png',C+'pang-changsu_hires_front.png',C+'pang-changsu_pose_hold_cup.png']),
 '6e': dict(out=O+'06/end_v1.png', model=FLASH, refs=[O+'05/start_v1.png',C+'pang-changsu_hires_front.png',M+'pang-misun_hires_front.png',M+'pang-misun_pose_lying.png']),
 '7s': dict(out=O+'07/start_v1.png', model=FLASH, refs=[O+'06/end_v1.png',C+'pang-changsu_hires_front.png',C+'pang-changsu_pose_walk_side.png']),
 '7e': dict(out=O+'07/end_v1.png', model=FLASH, refs=[O+'07/start_v1.png',C+'pang-changsu_hires_front.png',C+'pang-changsu_pose_walk_side.png']),
 '9s': dict(out=O+'09/start_v1.png', model=FLASH, refs=[O+'06/end_v1.png',C+'pang-changsu_hires_front.png',C+'pang-changsu_pose_hold_cup.png']),
 '9e': dict(out=O+'09/end_v1.png', model=FLASH, refs=[O+'09/start_v1.png',C+'pang-changsu_hires_front.png',M+'pang-misun_hires_front.png',M+'pang-misun_pose_hold_cup.png']),
 '11s': dict(out=O+'11/start_v1.png', model=FLASH, refs=[O+'09/end_v1.png',C+'pang-changsu_hires_front.png',C+'pang-changsu_pose_hold_cup.png',M+'pang-misun_hires_front.png']),
 '11e': dict(out=O+'11/end_v1.png', model=PRO, refs=[O+'11/start_v1.png','outputs/ep01/9-04/start_v1.png',C+'pang-changsu_hires_front.png',C+'pang-changsu_pose_sit.png']),
 '14s': dict(out=O+'14/start_v1.png', model=FLASH, refs=[O+'11/end_v1.png',C+'pang-changsu_hires_front.png',C+'expressions/pang-changsu_expr_01_neutral.png']),
 '12s': dict(out=O+'12/start_v1.png', model=FLASH, refs=[O+'02/start_v1.png',O+'11/end_v1.png',M+'pang-misun_hires_front.png',M+'expressions/pang-misun_expr_01_neutral.png']),
 '12e': dict(out=O+'12/end_v1.png', model=FLASH, refs=[O+'12/start_v1.png',M+'pang-misun_hires_front.png',M+'expressions/pang-misun_expr_01_neutral.png']),
 '15e': dict(out=O+'15/end_v1.png', model=FLASH, refs=[O+'11/end_v1.png',C+'pang-changsu_hires_front.png',M+'pang-misun_hires_front.png',M+'expressions/pang-misun_expr_02_happy.png']),
 '16e': dict(out=O+'16/end_v1.png', model=PRO, refs=[O+'15/end_v1.png','outputs/ep01/9-04/start_v1.png',C+'pang-changsu_hires_front.png',M+'pang-misun_hires_front.png',M+'expressions/pang-misun_expr_02_happy.png']),
}
ORDER = ['B2','1s','1e','3s','2s','2e','4s','4e','5s','6s','6e','7s','7e','9s','9e','11s','11e','14s','12s','12e','15e','16e']


def prompt_for(pid):
    doc = open(os.path.join(ROOT, 'docs/ep02/03_이미지_프롬프트_v2.md'), encoding='utf-8').read()
    for sec in doc.split('\n### ')[1:]:
        head = sec.split('\n', 1)[0]
        if head.startswith(pid + ' '):
            m = re.search(r'```\n(.*?)\n```', sec, re.S)
            return m.group(1)
    raise SystemExit('no prompt for ' + pid)


def main():
    pid = sys.argv[1]; m = MAN[pid]
    os.makedirs(os.path.join(ROOT, 'outputs/ep02/prompts'), exist_ok=True)
    pf = os.path.join(ROOT, f'outputs/ep02/prompts/{pid}.txt'); open(pf, 'w', encoding='utf-8').write(prompt_for(pid))
    os.makedirs(os.path.dirname(os.path.join(ROOT, m['out'])), exist_ok=True)
    for r in m['refs']:
        assert os.path.exists(os.path.join(ROOT, r)), 'missing ref ' + r
    cmd = ['python3', os.path.join(ROOT, 'tools/nb_generate.py'), '--id', 'ep02-' + pid, '--out', m['out'], '--prompt-file', pf,
           '--ratio', '9:16', '--size', '1K', '--model', m['model']] + sum([['--ref', r] for r in m['refs']], [])
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    print(r.stdout[-600:], r.stderr[-300:] if r.returncode else '')
    # 비교 시트: 부모(첫 참조) | 결과
    from PIL import Image
    a = Image.open(os.path.join(ROOT, m['refs'][0])).convert('RGB'); b = Image.open(os.path.join(ROOT, m['out'])).convert('RGB')
    h = 760; a2 = a.resize((int(a.width * h / a.height), h)); b2 = b.resize((int(b.width * h / b.height), h))
    o = Image.new('RGB', (a2.width + b2.width + 10, h), 'white'); o.paste(a2, (0, 0)); o.paste(b2, (a2.width + 10, 0))
    sheet = os.path.join(ROOT, f'outputs/ep02/prompts/cmp_{pid}.jpg'); o.save(sheet, quality=85)
    print('size', b.size, 'sheet', sheet)


if __name__ == '__main__':
    main()
