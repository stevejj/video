#!/usr/bin/env python3
"""유료 생성 전 프롬프트 관문(F10). 실패가 하나라도 있으면 종료 코드 1 → 사용자에게 승인 요청 금지.
사용: python3 tools/lint_prompts.py docs/ep06/04_Kling_실행표.md [docs/ep06/03_이미지_프롬프트.md ...]
문서 안의 '## ' 또는 '### ' 제목 아래 첫 코드블록을 그 항목의 프롬프트로 본다.
파일 이름에 'Kling'이 있으면 영상 규칙, '이미지'가 있으면 이미지 규칙을 쓴다.
규칙마다 근거(실제로 났던 실수)를 적어 둔다. 새 실수가 나면 여기에 규칙을 추가한다(08 F10).
"""
import re, sys

LOW = str.lower


def has(p, *alts):
    return any(re.search(a, p, re.I) for a in alts)


def rules(kind):
    R = []
    def rule(name, why, cond, need):  # cond(p)가 참인 프롬프트는 need(p)가 참이어야 함
        R.append((name, why, cond, need))
    misun = lambda p: has(p, r'mi-?sun')
    changsu = lambda p: has(p, r'chang-?su')
    wings_act = lambda p: has(p, r'\bwings?\b')
    rule('미순 속눈썹 금지', 'ep04 W1·ep05: 이미지 모델이 미순에게 속눈썹을 붙임', misun, lambda p: has(p, r'no eyelashes'))
    rule('창수 볼터치 금지', 'ep06 C2: 창수가 돌아설 때 미순 볼터치가 옮겨 붙음(F9)',
         lambda p: changsu(p) and misun(p),  # 둘이 같이 나오면 항상(돌아서는 장면만 노리면 놓침)
         lambda p: has(p, r'chang-?su[^.]*no (pink )?blush', r'no (pink )?blush[^.]*chang-?su', r"chang-?su's cheeks have no", r'\b(his|he)\b[^.]*no (pink )?blush'))
    rule('날개 늘이기 금지', 'ep03: 팔이 길게 늘어나 괴물 같음(M16)', lambda p: kind == 'video' and wings_act(p), lambda p: has(p, r'never stretch', r'normal short length', r'keep (their|its) normal short'))
    rule('새 물체·새 캐릭터 금지', 'ep03: 이불 속에서 과자가 생김', lambda p: kind == 'video', lambda p: has(p, r'no new objects') and has(p, r'no other characters'))
    rule('고정 카메라', '참고 형식(한 샷 고정) — 카메라가 움직이면 배경이 흔들림', lambda p: kind == 'video', lambda p: has(p, r'static camera', r'locked-off'))
    rule('물건 잡기: 닿은 뒤에만 움직임', 'ep03 과자 순간이동·ep05 "덤벨이 들어야 하는 느낌"',
         lambda p: kind == 'video' and has(p, r'\b(picks? up|grabs?|lifts?|takes?|holds?)\b'),
         lambda p: has(p, r'only after', r'until (both of )?(her|his|their) wings?', r'never float', r'lie completely still', r'only (together|along) with'))
    rule('누운 캐릭터 + 날개 동작 금지', 'ep03: 누워서 날개 쓰면 머리가 굴러감(M17)',
         lambda p: kind == 'video' and has(p, r'\b(she|he|they|mi-?sun|chang-?su)\s+(is\s+|are\s+)?(lying|lies|lie down)') and wings_act(p), lambda p: False)
    rule('소품 고정', 'ep05·ep06: 소품은 사라지거나 움직이면 안 됨(F8)',
         lambda p: kind == 'video' and has(p, r'boombox|dumbbell|bowl|phone|remote|cup|mug'),
         lambda p: has(p, r'never moves?', r'does not move', r'stays? (on the floor|where|in place|completely unchanged)', r'only after', r'until', r'never floating', r'unchanged'))
    rule('음성 참조 시 대사 원문 필수', 'ep07 S1: 대사를 안 적었더니 Kling이 녹음을 무시하고 영어 대사를 지어냄(S5는 원문을 적어서 성공)',
         lambda p: kind == 'video' and has(p, r'音频|audio_1'),
         lambda p: bool(re.search(r'"[^"]*[가-힣][^"]*"', p)) and has(p, r'in korean'))
    if kind == 'image':
        rule('세로 9:16', '이미지 모델이 정사각형을 낼 때가 있음', lambda p: True, lambda p: has(p, r'9:16'))
        rule('글자·로고 금지', 'AI 글자 깨짐', lambda p: True, lambda p: has(p, r'no text'))
    return R


def blocks(doc):
    out = []; title = None
    lines = doc.split('\n'); i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith('## ') or ln.startswith('### '):
            title = ln.strip('# ').strip(); taken = False
        elif ln.startswith('```') and title and not locals().get('taken'):
            j = i + 1; body = []
            while j < len(lines) and not lines[j].startswith('```'):
                body.append(lines[j]); j += 1
            out.append((title, '\n'.join(body))); taken = True; i = j
        i += 1
    return out


def main():
    fails = 0
    for path in sys.argv[1:]:
        kind = 'video' if 'Kling' in path else 'image' if '이미지' in path else None
        if not kind:
            print(f'(건너뜀: 종류를 모름) {path}'); continue
        for title, p in blocks(open(path, encoding='utf-8').read()):
            if '[기록]' in title:  # 이미 제출한 프롬프트 기록(수정하면 기록이 거짓이 됨) → 검사 생략
                continue
            bad = [(n, w) for n, w, c, need in rules(kind) if c(p) and not need(p)]
            if bad:
                fails += len(bad)
                print(f'✗ {path} · {title}')
                for n, w in bad: print(f'    - {n}  ← {w}')
            else:
                print(f'✓ {path} · {title}')
    print('결과:', '통과' if not fails else f'실패 {fails}건 → 고치기 전에는 승인 요청·제출 금지')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
