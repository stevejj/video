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

**1컷 ✅ 통과 (2026-10-07)**: 18크레딧, 잔액 163 → **145**(보너스 88은 이 연결에서 차감되지 않음 = 에이전트 경로에서 사용 불가로 판단). 생성 50초. 실측: 카메라 이동 0.05px(고정), 배경 드리프트 1.55, 시작 프레임 대비 2.06, 끝 프레임 대비 3.11(기준 ≤ 8). 0~1.5s 왼쪽에서 두 걸음, 탁자 뒤(소파와 탁자 사이)로 지나감, 1.75~3s 소파 왼쪽 끝에서 정면으로 돌아 정지(2.5s 부근 눈 한 번 감김 = 자연스러운 깜빡임). 미순·이불·리모컨·탁자 고정. 편집 구간 0.5~2.0s 권장(걷기 2보 + 멈춤). 파일 `outputs/ep02/01/clip_v1.mp4`, 시트 `verify_v1/sheet.png`.

### 4 — 시작+끝, 3초 (편집 2.0s)
**입력**: `outputs/ep02/04/start_v1.png`(창수 왼쪽 가장자리, 물컵) + `outputs/ep02/04/end_v1.png`(소파 앞에서 컵을 미순에게 내밀고 미순이 받으려 날개 듦)
**인자**: 동일 (v3_0, 3s, 720p, multi_shots false, audio false)
**프롬프트**
```
Pang Chang-su is already walking from the very first frame, at a steady unhurried waddling pace to his right, entering from the left edge of the frame along the floor between the sofa and the table, holding a clear glass of water in the wing nearer the camera, keeping his body and head facing to his right the whole time. Each step lands on the wood floor and rolls forward; his feet do not slide; the glass stays level in his wing. After two steps he stops in front of the sofa beside Mi-sun and holds the glass out toward her at chest height, leaning slightly toward her, while Mi-sun lifts her wing a little to take it, exactly matching the end image. Pang Mi-sun otherwise stays lying still on the right half of the sofa under the beige duvet with her head on the cushion; the duvet, the black remote on the seat, the cushions and the empty table stay exactly where they are. Chang-su does not look at the viewer. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Both beaks stay closed the whole time. No other characters appear. No new objects appear. Exactly one glass exists. Wings stay short and rounded with no fingers.
```
**자막·음성**: 미순 리액션 "헤헤"(컵 받을 때). 효과음: 발소리, 컵 "톡".
**예상 시나리오**: 0~1.5s 걷기(컵 든 채), 1.5~3s 멈춰 컵 내밀기 + 미순 날개 듦.
**위험·감시 항목**: 중간 | 컵이 2개로 늘거나 사라짐, 컵이 기울어 물 쏟음, 날개가 팔처럼 늘어남(R9-5), 미순 머리가 크게 들림, 리모컨 이동.
**실패 시 편집 대안**: 앞 1.5s(걷기)만 쓰고 끝 프레임 정지 + 푸시인.
**크레딧**: 18. 145 → 127.

**4컷 ✅ 통과 (2026-10-07)**: 18크레딧, 잔액 145 → **127**. 생성 106초. 실측: 카메라 0.07px, 배경 드리프트 1.65, 시작 2.05 / 끝 3.08. 0~1.5s 컵 든 채 두 걸음(컵 수평 유지, 1개), 1.5~3s 소파 앞에서 컵을 내밀고 미순이 날개 들며 웃음. 리모컨·이불·탁자 고정. 편집 구간 0.5~2.5s. 파일 `outputs/ep02/04/clip_v1.mp4`.

### 6 — 시작+끝, 4초 (편집 2.5s)
**입력**: `outputs/ep02/06/start_v1.png`(창수 왼쪽 가장자리, 베개 양 날개, 컵 탁자 위) + `outputs/ep02/06/end_v1.png`(창수 오른쪽 끝 팔걸이 옆, 베개 미순 머리 밑, 날개 비움)
**인자**: v3_0, duration=4, 720p, multi_shots false, audio false
**프롬프트**
```
Pang Chang-su is already walking from the very first frame, at a steady unhurried waddling pace to his right, entering from the left edge of the frame and walking along the floor between the sofa and the table, past the whole sofa to its right end, carrying a white pillow in front of his belly with both wings, keeping his body and head facing to his right the whole time. Each step lands on the wood floor and rolls forward; his feet do not slide; the pillow stays in his wings. When he reaches the right end of the sofa beside Mi-sun's head, he bends forward and slides the pillow under her head while she lifts her head slightly and lets it settle on the pillow; then he straightens up with both wings empty, exactly matching the end image. Pang Mi-sun otherwise stays lying still under the beige duvet; the duvet, the black remote on the seat, the cushions, the glass on the table and the table stay exactly where they are. Chang-su does not look at the viewer. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Both beaks stay closed the whole time. No other characters appear. No new objects appear. Exactly one pillow and one glass exist. Wings stay short and rounded with no fingers.
```
**자막·음성**: 창수 "응."(걸어오며, 보이스오버). 효과음: 발소리 3보, 베개 "푹".
**예상 시나리오**: 0~2.5s 소파 앞을 가로질러 오른쪽 끝까지 3~4보, 2.5~4s 허리 숙여 베개 끼움 → 직립.
**위험·감시 항목**: **높음** (이동 거리 길고 물건 조작 + 미순 머리 들기 동시) | 창수가 탁자 앞으로 걷거나 미순 위를 지남, 베개가 2개/사라짐, 미순 머리가 크게 들리거나 몸이 일어남, 창수 크기 변화, 날개 늘어남.
**실패 시 편집 대안**: 걷기 구간만 쓰고(앞 2s) 끝 프레임 정지 + 푸시인으로 "끼움" 생략.
**크레딧**: 24. 127 → 103.
