#!/usr/bin/env python3
"""ep 기획 단계 크레딧 계산기 (02c §2 전략 C′).
사용: python3 tools/budget.py <컷목록.json>   또는   python3 tools/budget.py --quick 18x3 4x2 6xUI
- 컷목록.json: [{"cut":"1-01","kind":"clip|ui|still","len":3}, ...]
- --quick: "개수x초" 묶음. kind 생략=clip, "UI"=그래픽 인서트(0크레딧), "S"=정지(0크레딧, 02c 효과 2개 필수)
단가: Kling v3_0 720p 초당 6크레딧(ep01 실측). ElevenLabs는 글자·초 단위라 별도.
"""
import json, sys

RATE = 6  # 크레딧/초


def main():
    items = []
    if len(sys.argv) > 2 and sys.argv[1] == '--quick':
        for tok in sys.argv[2:]:
            n, rest = tok.lower().split('x')
            kind = 'ui' if rest.endswith('ui') else ('still' if rest.endswith('s') else 'clip')
            sec = float(rest.rstrip('uis') or 3)
            items += [{'cut': f'{kind}{i}', 'kind': kind, 'len': sec} for i in range(int(n))]
    else:
        items = json.load(open(sys.argv[1]))
    clip = [x for x in items if x['kind'] == 'clip']
    cost = sum(x['len'] * RATE for x in clip)
    total_len = sum(x['len'] for x in items)
    print(f"컷 {len(items)}개, 총 {total_len:.1f}s, 평균 {total_len / max(1, len(items)):.2f}s/컷")
    print(f"  Kling 클립 {len(clip)}개 {sum(x['len'] for x in clip):.0f}s → {cost:.0f} 크레딧 (+재시도 여유 15% ≈ {cost * 1.15:.0f})")
    print(f"  UI 인서트 {sum(1 for x in items if x['kind'] == 'ui')}개, 정지 {sum(1 for x in items if x['kind'] == 'still')}개 (0 크레딧)")
    if total_len / max(1, len(items)) > 2.5:
        print('  ⚠ 평균 컷 길이 2.5s 초과 (02c M5: 1.5~2.5s)')
    if len(items) < 24 and total_len >= 55:
        print('  ⚠ 60초 편 컷 24개 미만 (02c M5)')


if __name__ == '__main__':
    main()
