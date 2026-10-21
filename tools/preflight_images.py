#!/usr/bin/env python3
"""이미지 생성 전 사전 점검(G2+, 0원). lint_prompts(문구 규칙)보다 넓게, '보내면 돈이 나가는' 실수를 미리 잡는다.
사용: python3 tools/preflight_images.py --ep ep09 [--ids K1,K2] [--cap 2000]
입력:
- docs/<ep>/03_이미지_프롬프트.md 의 '### <id> 제목' 섹션('[기록]'은 건너뜀). '첨부:' 줄 + 첫 코드블록.
- tools/<ep>_imgs.py 의 MAN(id → out·model·refs). 생성 순서 = MAN 순서.
- outputs/<ep>/props.json 의 states(옷·소품 상태, prompt_kw), lipsync(장면별 말하는 캐릭터).
검사(✗=실패 → 승인 요청 금지, △=경고 → 보고에 적고 사람이 판단):
 A 문구 규칙: lint_prompts 이미지 규칙 전체.
 B 매니페스트: MAN에 있음, 참조 파일이 있거나 앞 순서에서 만들어짐, 결과 파일 덮어쓰기 경고, 결과 경로 중복.
 C 첨부 수: 문서 '첨부' 개수 = refs 개수, 프롬프트의 FIRST/SECOND… 서수 ≤ refs 개수.
 D 캐릭터 참조: 이름이 나온 캐릭터의 시트(또는 그 캐릭터가 나온 앞 K 이미지)가 refs에 있음.
 E 상태: props.json states의 prompt_kw(옷·소품)가 프롬프트에 있음(F8).
 F 위험 단어: 안전 필터 단어(ep08 K7 빈 응답) ✗, 브랜드·캐릭터 이름(ep08 S6 저작권) ✗, 감정 단어(ep08 K3·K9 눈썹) △.
 G 소품 개수: 손에 드는 소품이 나오면 'exactly/ONE' 개수 명시.
 H 띠: 30/40/30 띠 에피소드면 'MIDDLE 40%'.
 I 입모양 준비: 입모양 장면의 말하는 캐릭터는 얼굴이 보이고(뒷모습 금지) 부리 닫힘으로 시작.
 J 비용: 모델 단가 합계 ≤ cap, 동시 요청 2개 이하 안내.
"""
import argparse, importlib.util, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import lint_prompts  # noqa: E402

PRICE = {'gemini-3.1-flash-image': 125, 'gemini-3-pro-image': 255}  # 05c 보정 단가(원)
ORD = ['FIRST', 'SECOND', 'THIRD', 'FOURTH', 'FIFTH', 'SIXTH']
SAFETY = [r'\bnaked\b', r'\bnude\b', r'no clothes', r'\bwet\b', r'\bbath(ing)?\b(?! ?mat)', r'\bblood', r'\bknife', r'\bkill', r'\bunderwear']
BRANDS = [r'\bkfc\b', r'\bbbq\b', r'교촌', r'bhc', r'\bchanel\b', r'herm[eè]s', r'\bgucci\b', r'\blouis vuitton\b', r'\bnike\b', r'pengsoo', r'펭수',
          r'coca[- ]?cola', r'\bpepsi\b', r'\bstarbucks\b', r'\bbaemin\b', r'배달의민족', r'\bnetflix\b', r'\bsamsung\b', r'\biphone\b', r'\bapple\b']
EMOTION = [r'troubled', r'flustered', r'worried', r'angry', r'furious', r'\bsad\b', r'determined', r'exhausted', r'\bsmug\b', r'frown', r'shocked',
           r'serious', r'stern', r'annoyed', r'disgust', r'uninterested', r'bored', r'chin raised', r'half-closed', r'sleepy']  # ep09 K3: 'uninterested, chin raised' → 눈이 작고 반쯤 감김
HELD = r'\b(drumsticks?|box|phone|smartphone|remote|hanger|shoes?|mug|cup|bowl|spoon|chopsticks|fork)\b'


def load_man(ep):
    p = os.path.join(ROOT, f'tools/{ep}_imgs.py')
    spec = importlib.util.spec_from_file_location(f'{ep}_imgs', p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.MAN


def sections(doc):
    out = {}
    for sec in doc.split('\n### ')[1:]:
        head = sec.split('\n', 1)[0]
        if '[기록]' in head:
            continue
        pid = head.split()[0]
        att = re.search(r'^첨부:(.*)$', sec, re.M)
        code = re.search(r'```\n(.*?)\n```', sec, re.S)
        out[pid] = dict(title=head, attach=att.group(1) if att else '', prompt=code.group(1) if code else '')
    return out


def has(p, pat):
    return re.search(pat, p, re.I) is not None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ep', required=True); ap.add_argument('--ids', default=''); ap.add_argument('--cap', type=int, default=2000)
    a = ap.parse_args()
    doc = open(os.path.join(ROOT, f'docs/{a.ep}/03_이미지_프롬프트.md'), encoding='utf-8').read()
    S = sections(doc); MAN = load_man(a.ep)
    PR = json.load(open(os.path.join(ROOT, f'outputs/{a.ep}/props.json')))
    B = json.load(open(os.path.join(ROOT, f'outputs/{a.ep}/band_offsets.json'))) if os.path.exists(os.path.join(ROOT, f'outputs/{a.ep}/band_offsets.json')) else {}
    ids = [x for x in (a.ids.split(',') if a.ids else S.keys()) if x]
    order = list(MAN.keys()); made = set(); outs = {}
    fails = warns = 0; cost = 0
    for pid in ids:
        F, W = [], []
        if pid not in S:
            F.append('B 문서에 프롬프트 섹션 없음'); print(f'✗ {pid}'); [print('   ✗', x) for x in F]; fails += 1; continue
        p = S[pid]['prompt']; m = MAN.get(pid)
        # A 문구 규칙
        for n, why, c, need in lint_prompts.rules('image'):
            if c(p) and not need(p):
                F.append(f'A {n} ← {why}')
        # B 매니페스트
        if not m:
            F.append('B MAN(tools/{ep}_imgs.py)에 없음')
        else:
            cost += PRICE.get(m['model'], 0)
            if m['out'] in outs.values():
                F.append(f'B 결과 경로 중복: {m["out"]}')
            outs[pid] = m['out']
            if os.path.exists(os.path.join(ROOT, m['out'])):
                W.append(f'B 결과 파일이 이미 있음 → 덮어씀: {m["out"]}')
            for r in m['refs']:
                produced_by = [k for k in order if MAN[k]['out'] == r]
                if os.path.exists(os.path.join(ROOT, r)):
                    continue
                if produced_by and order.index(produced_by[0]) < order.index(pid):
                    W.append(f'B 참조 {r}는 {produced_by[0]} 결과(먼저 만들고 확인한 뒤 진행)')
                else:
                    F.append(f'B 참조 파일 없음: {r}')
            # C 첨부 수
            n_att = len(re.findall(r'\(\d+[,)]', S[pid]['attach']))
            if n_att != len(m['refs']):
                F.append(f'C 문서 첨부 {n_att}개 ≠ MAN refs {len(m["refs"])}개')
            used = [i for i, o in enumerate(ORD) if re.search(rf'\b{o}\b', p)]
            if used and max(used) + 1 > len(m['refs']):
                F.append(f'C 프롬프트가 {ORD[max(used)]} 첨부를 말하지만 refs는 {len(m["refs"])}개')
            # D 캐릭터 참조
            for name, key in (('mi-?sun', 'pang-misun'), ('chang-?su', 'pang-changsu')):
                if has(p, rf'\b{name}\b') and not has(p, rf'{name}[^.]*(is not in|does not appear|not in the picture)'):
                    if not any(key in r for r in m['refs']):
                        if any(r in [MAN[k]['out'] for k in order] for r in m['refs']):
                            W.append(f'D {key} 시트 없이 앞 K 이미지로만 참조(얼굴이 크게 나오면 시트 추가 권장)')
                        else:
                            F.append(f'D {key} 참조 없음')
        # E 상태(옷·소품)
        cut = re.sub(r'\D', '', pid).zfill(2)
        for prop, st in PR.get('states', {}).get(cut, {}).items():
            for kw in st.get('prompt_kw', []):
                if not has(p, re.escape(kw)):
                    F.append(f'E {prop} 상태 "{st["start"]}" 문구 없음: "{kw}"')
        # F 위험 단어
        for w in SAFETY:
            if has(p, w):
                F.append(f'F 안전 필터 단어 "{w}" (ep08 K7 빈 응답) → "cute plush toy" 식으로 바꿈')
        for w in BRANDS:
            if has(p, w):
                F.append(f'F 브랜드·캐릭터 이름 "{w}" (ep08 S6 저작권 거절)')
        emo = [w.strip('\\b') for w in EMOTION if has(p, w)]
        if emo:
            W.append(f'F 감정 단어 {emo} → 눈썹이 생길 수 있음(ep08 K3·K9). 몸짓·부리로 표현했는지 결과에서 눈썹 확인')
        # G 소품 개수
        # 소품이 나오는 문장마다 개수(exactly/대문자 ONE·TWO)가 같은 문장에 있어야 함("one short wing"은 개수가 아님)
        for sent in re.split(r'(?<=[.;])\s', p):
            if sent.strip().startswith('Keep'):
                continue
            first = [mm for mm in re.finditer(HELD, sent, re.I)  # 처음 등장(the X·Mi-sun's X·shoe cabinet 같은 재지칭·가구는 제외)
                     if not re.search(r"(\bthe|\bher|\bhis|'s)\s+(\w+\s+){0,4}$", sent[:mm.start()], re.I) and not re.match(r'\s*(cabinet|rack)', sent[mm.end():])]
            if first and not re.search(r'\bexactly\b|\bONE\b|\bTWO\b', sent):
                F.append(f'G 소품 개수 명시 없음: "{sent.strip()[:70]}…"')
        # H 띠
        if B.get('band_ratio') == 0.4 and not has(p, r'MIDDLE 40%'):
            F.append('H 30/40/30 띠인데 "MIDDLE 40%" 없음')
        # I 입모양 준비
        for who in PR.get('lipsync', {}).get(cut, []):
            nm = 'mi-?sun' if who == 'misun' else 'chang-?su'
            seg = ' '.join(s for s in re.split(r'(?<=[.!])\s', p) if has(s, nm))
            if has(seg, r'from BEHIND|seen from behind|back to the camera'):
                F.append(f'I 입모양 장면인데 {who}가 뒷모습')
            if not has(seg, r'facing the camera|three-quarter|toward the camera|face (is )?visible|close-up'):
                W.append(f'I {who} 얼굴 방향 명시 없음(입모양 장면은 얼굴이 보여야 함)')
            if not has(p, r'beak[s]? (stays? |are |is )?closed|beaks? closed'):
                F.append(f'I 입모양 장면은 부리 닫힘으로 시작해야 함("beak closed")')
        mark = '✗' if F else ('△' if W else '✓')
        print(f'{mark} {pid} {S[pid]["title"][len(pid):].strip()}  [{("Pro" if "pro" in m["model"] else "Flash") if m else "?"} {PRICE.get(m["model"], 0) if m else 0}원]')
        for x in F: print('   ✗', x)
        for x in W: print('   △', x)
        fails += len(F); warns += len(W)
    print(f'\n비용 합계 약 {cost:,}원 (상한 {a.cap:,}원){" ✗ 초과" if cost > a.cap else ""} · 동시 요청은 2개 이하(ep08 빈 응답)')
    if cost > a.cap:
        fails += 1
    print('결과:', '통과' if not fails else f'실패 {fails}건 → 고치기 전에는 승인 요청 금지', f'· 경고 {warns}건(보고에 적기)')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
