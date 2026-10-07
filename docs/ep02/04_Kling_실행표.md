# ep02 Kling 실행표 (2026-10-07)

> 규칙: ep01 `07_Kling_실행표.md` §0 공통 문장·§0b 사전 점검표·§3 검증 절차 그대로. 컷마다 실행표 → 사용자 "진행" → 생성 1회 → 검증 → 결과 보고. 자동 재시도 없음. 생성 길이 = 편집 길이 +1s를 3/4/5로 올림. 단가 6크레딧/초(720p, kling-video-v3_0).
> 잔액 163 (2026-10-07 조회). 보너스 88은 이 연결에서 안 보임 → 1컷 생성 후 잔액 변화로 확인.
> 사전 결정: 미순의 "발 까딱"(스토리보드 1컷)은 시키지 않은 큰 동작을 부를 수 있어(0b-1) **미순은 완전 정지**로 지시. 움직임은 창수 걷기만.

## 0. 공통 고정 문장
- `Static camera, locked-off tripod shot, no camera movement, same composition throughout.`
- `3D animated plush characters, short velvet fur; the surroundings and objects stay photoreal and completely unchanged.`
- 부리: 대화 컷(2·12 미순, 3·14 창수 "응.")만 `As she/he speaks a short line, the beak opens and closes only a tiny amount, barely parting; it keeps its exact small triangular shape and never opens wide.` 나머지는 `Both beaks stay closed the whole time.`
- `No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.`
- 걷기 공통(ep01 6-01·9-01 검증 문장): `already walking from the very first frame, at a steady unhurried waddling pace ... Each step lands on the floor and rolls forward; the feet do not slide.`

## 1. 컷별 실행표

### 1 — 시작+끝, 3초 (편집 1.5s)
**입력**: `outputs/ep02/01/start_v1.png` + `outputs/ep02/01/end_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su is already walking from the very first frame, at a steady unhurried waddling pace to his right, entering from the left edge of the frame along the floor in front of the sofa, keeping his body and head facing to his right the whole time. Each step lands on the wood floor and rolls forward; his feet do not slide. After two steps he stops beside the left end of the sofa and turns his body to face the camera, standing still with both feet flat on the floor and his wings hanging at his sides, exactly matching the end image. He holds nothing. Pang Mi-sun lies completely still on the right half of the sofa under the beige duvet with her head on the cushion, looking toward the camera; she does not move at all, and the duvet, the black remote on the seat, the cushions and the empty table stay exactly where they are. Chang-su does not look at the viewer while walking. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Both beaks stay closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**자막·음성**: 없음(시계 카드 "21:00"은 HyperFrames). 효과음: 발소리 2보, TV 환경음.
**예상 시나리오**: 0~2s 왼쪽에서 두 걸음 걸어 들어옴, 2~3s 소파 왼쪽 끝에서 정면으로 돌아 정지. 미순·소품 고정.
**위험·감시 항목**: 중간 | 창수가 탁자 앞이 아니라 뒤로 걷거나 탁자를 통과, 걸음이 미끄러짐(발 슬라이드), 미순이 고개를 돌리거나 이불이 움직임, 리모컨 이동, 창수 크기 변화(시작·끝 프레임 보간이라 낮음), 날개가 팔처럼 늘어남.
**실패 시 편집 대안(재생성 없음)**: 앞 1.5s만 사용(걷기 부분만, 끝 자세는 다음 컷 2가 확대라 안 보임) 또는 1e 정지 프레임 + HyperFrames 푸시인.
**검증(§3)**: 첫·끝 프레임 ↔ 시작·끝 이미지 배경 픽셀차 ≤ 8, 미순 영역 변화 없음, 리모컨 위치 동일, 프레임 0.25s 간격 시트 눈 확인.
**크레딧**: 18. 생성 전 163 → 예상 145 (보너스가 먼저 빠지면 163 유지).
