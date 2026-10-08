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

**6컷 ✅ 통과 (2026-10-07)**: 24크레딧, 잔액 127 → **103**. 생성 84초. 실측: 카메라 0.11px, 배경 드리프트 2.03, 시작 2.09 / 끝 3.29. 0~2.0s 베개 들고 소파 앞을 가로질러 오른쪽 끝까지(탁자 뒤), 2.0~3.0s 허리 숙여 베개를 미순 머리 밑에 넣음(미순은 눈 감고 웃으며 머리 살짝), 3.0~4.0s 직립해 정면. 베개 1개, 컵·리모컨·이불 고정. 고위험 컷이 1회 통과. 편집 구간 0.5~3.0s. 파일 `outputs/ep02/06/clip_v1.mp4`.

### 2 — 시작+끝, 3초 (편집 2.0s) — 대화 컷
**입력**: `outputs/ep02/02/start_v1.png`(미순 얼굴, 카메라 응시, 02 활짝) + `outputs/ep02/02/end_v1.png`(고개 왼쪽, 부리 살짝)
**인자**: v3_0, duration=3, 720p, multi_shots false, audio false
**프롬프트**
```
Pang Mi-sun lies on the sofa cushion under the beige duvet, looking at the camera with a happy smile. Slowly she turns her head a little to her left side of the frame, toward the left end of the sofa, and settles there looking that way, exactly matching the end image. As she speaks a short line, her beak opens and closes only a tiny amount, barely parting, just enough to show she is talking; it keeps its exact small triangular shape and size and never opens wide, stretches, or turns into lips. Her head stays on the cushion the whole time and does not lift; her wings rest still on top of the duvet; the duvet, the cushion and the sofa stay exactly where they are. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**자막·음성**: 미순 요청 1(대사는 사용자 확정 후 교체, 자막 핑크 팝). 벨 #1.
**예상 시나리오**: 0~1.2s 고개 천천히 왼쪽, 1.2~3s 부리 미세하게 몇 번.
**위험·감시 항목**: 중간 | 부리를 크게 벌림(ep01 9-03·9-02 전례: 끝 프레임에 열린 부리가 있으면 동작 끝에서 엶), 머리를 들어 올림, 눈이 감김, 날개가 올라옴.
**실패 시 편집 대안**: 앞 1.5s(고개 돌림)만 쓰고 끝 프레임 정지.
**크레딧**: 18. 103 → 85.

**2컷 ✅ 통과 (2026-10-07)**: 18크레딧, 잔액 103 → **85**. 생성 47초. 실측: 카메라 0.05px, 배경 드리프트 2.86, 시작 2.27 / 끝 3.10. 0~1.0s 고개가 왼쪽으로 돌며 눈 한 번 깜빡, 1.0~3.0s 부리가 작게 몇 번 열렸다 닫힘(삼각형 유지, 입술화 없음). 열림 폭은 "미세"보다 조금 큰 "보통"(ep01 9-02와 같은 수준) — 대화 컷이라 허용. 머리 쿠션 고정, 날개·이불 고정. 편집 구간 0.3~2.3s. 파일 `outputs/ep02/02/clip_v1.mp4`.

### 3 — 시작만, 3초 (편집 1.5s) — 대화 컷 "응."
**입력**: `outputs/ep02/03/start_v1.png`(창수 상반신, 선 자세, 뒤 커튼·소파 끝)
**인자**: v3_0, duration=3, 720p, multi_shots false, audio false
**프롬프트**
```
Pang Chang-su stands still facing slightly to the right of the frame with a calm neutral face. He blinks once, slowly, and gives one very small nod of his head, about one centimeter, then holds still. As he speaks one short word, his beak opens and closes only a tiny amount, barely parting, just enough to show he is talking; it keeps its exact small triangular shape and size and never opens wide, stretches, or turns into lips. His head stays at the same height and angle otherwise and does not turn toward the camera; his wings hang still at his sides; the curtain and sofa behind him stay exactly where they are. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**자막·음성**: 창수 "응."(파일 A, 5회 재사용의 첫 번째). **10컷(속마음 "흐음..")에도 이 클립 재사용** + 푸시인.
**예상 시나리오**: 깜빡 1회 + 끄덕 1회 + 부리 미세.
**위험·감시 항목**: 낮음~중간 | 고개를 카메라로 돌림(ep01 4-01 전례), 부리 크게 벌림, 몸을 흔듦.
**실패 시 편집 대안**: 정지 프레임 + 푸시인(0크레딧), "응."은 보이스오버.
**크레딧**: 18. 85 → 67.

**3컷 ✅ 통과 (2026-10-07)**: 18크레딧, 잔액 85 → **67**. 생성 140초(대기열). 실측: 시작 2.24, 첫↔끝 3.33, **카메라 3.3px·배경 드리프트 3.4** = 아주 느린 푸시인이 섞임(머리가 끝에서 조금 커짐). 기준(≤8) 안이고 10컷 재사용 시 HyperFrames 푸시인과 방향이 같아 허용. 1.5s 깜빡 1회, 2.0s 부리 한 번 작게 열림("응."), 고개 카메라로 안 돌림, 날개 고정. 편집 구간 0.8~2.3s(깜빡+"응."). 파일 `outputs/ep02/03/clip_v1.mp4`. **10컷은 이 클립 0.3~2.3s 재사용.**

### 5 — 시작만, 3초 (편집 2.0s)
**입력**: `outputs/ep02/05/start_v1.png`(창수 소파 왼쪽 끝 앞에 정면으로 섬, 컵 탁자 위)
**인자**: v3_0, duration=3, 720p, multi_shots false, audio false
**프롬프트**
```
Pang Chang-su stands facing the camera beside the left end of the sofa. He begins to sit down: his knees bend and his body lowers about halfway toward the empty left seat cushion, his bottom stopping well above the cushion without touching it; he pauses there for a moment as if hearing something, then straightens his knees and stands fully upright again in exactly the same spot where he started, with both feet flat on the floor and his wings hanging at his sides. He never sits on the sofa. His head keeps facing the camera at the same angle with a calm neutral face. Pang Mi-sun lies completely still on the right half of the sofa under the beige duvet; the duvet, the black remote on the seat, the cushions, the glass on the table and the table stay exactly where they are. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Both beaks stay closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**자막·음성**: 미순 요청 2(보이스오버, 자막 팝 1.1배), 벨 #2.
**예상 시나리오**: 0~1.2s 무릎 굽혀 반쯤 내려감, 1.2~1.8s 멈춤, 1.8~3s 다시 섬.
**위험·감시 항목**: 중간 | 완전히 앉아 버림(11컷과 겹침), 몸이 옆으로 이동, 미순이 움직임.
**실패 시 편집 대안**: 앞 1.5s(굽히기)만 쓰고 컷 → 6컷 걷기(시작 프레임이 다르므로 점프 컷 허용).
**크레딧**: 18. 67 → 49.

**5컷 ❌ 불합격 (2026-10-07)**: 18크레딧, 잔액 67 → **49**. 생성 118초. 카메라 0.93px, 배경 1.62(기술 통과). 그러나 동작이 틀림: "앉기 시작 → 반쯤 → 다시 섬"을 **소파 위로 뛰어올라 좌면에 올라섰다가 뛰어내리는** 동작으로 해석(0.5~2.5s 좌면 위, 날개 벌림, 3.0s 착지). "begins to sit down"이 "소파에 오르기"로 읽힘(ep01 0b-1: 동작 동사는 크게 해석됨). 사용 가능 구간 0~0.8s(정지)뿐. 파일 `outputs/ep02/05/clip_v1.mp4` 보관.
**재시도 안(승인 대기, 18)**: 동사를 바꾼다 — `He stays standing on the floor the whole time. Only his knees bend a little, lowering his body about ten centimeters as if he is about to sit, then straighten again; he never climbs onto the sofa, never jumps, and never sits.` "sit down"이라는 표현 자체를 지움.
**대안(0크레딧)**: 5s 정지 프레임 + HyperFrames 푸시인 2.0s. "앉으려다" 개그는 자막·음성 타이밍으로만 표현.
→ **사용자 결정 "대안" (2026-10-07)**: 5컷은 정지 프레임(`05/start_v1.png`) + HyperFrames 푸시인 2.0s. 클립 재생성 없음. 02c M11 예외(정지 컷)로 기록, 정지 초 검증에서 1컷 허용.

### 7 — 시작+끝, 3초 (편집 2.0s)
**입력**: `outputs/ep02/07/start_v1.png`(창수 소파 앞 중앙, 좌향 측면 걷기) + `outputs/ep02/07/end_v1.png`(같은 자리에서 돌아서 소파 쪽을 향함, 등이 카메라 쪽)
**인자**: v3_0, duration=3, 720p, multi_shots false, audio false
**프롬프트**
```
Pang Chang-su is already walking from the very first frame, at a steady unhurried waddling pace to his left along the floor in front of the sofa, seen from the side, keeping his body and head facing left. Each step lands on the wood floor and rolls forward; his feet do not slide. After two steps he stops and turns around on the spot, pivoting his whole body in place without moving sideways, until he faces the sofa with his back toward the camera, and stands still there with his wings hanging at his sides, exactly matching the end image. He holds nothing. Pang Mi-sun lies completely still on the right half of the sofa under the beige duvet with her head on the white pillow; the duvet, the pillow, the black remote on the seat, the cushions, the glass on the table and the table stay exactly where they are. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Both beaks stay closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**자막·음성**: 미순 요청 3(보이스오버, 자막 팝 1.2배), 벨 #3, 창수 "응."(턴 끝).
**예상 시나리오**: 0~1.2s 왼쪽으로 두 걸음, 1.2~2.5s 제자리 턴, 2.5~3s 정지.
**위험·감시 항목**: 중간 | 턴하면서 옆으로 밀림(R3 제자리), 카메라를 보고 멈춤, 걸음이 미끄러짐.
**실패 시 편집 대안**: 앞 1.2s(걷기)만 쓰고 7e 정지 프레임으로 컷.
**크레딧**: 18. 49 → 31.

**7컷 ✅ 통과 (2026-10-08)**: 18크레딧, 잔액 49 → **31**. 생성 92초. 실측: 카메라 0.06px, 배경 2.65, 시작 2.19 / 끝 3.07. 0~1.0s 왼쪽으로 두 걸음, 1.0~2.5s 제자리 턴(등 보임), 2.5~3.0s 오른쪽을 향한 옆모습까지 돌아섬 — 끝 프레임(뒷모습)을 지나 스토리보드 원안(우향 턴)까지 간 셈이라 오히려 좋음. 옆으로 밀림 없음, 미순·소품 고정. 편집 구간 0.3~2.3s. 파일 `outputs/ep02/07/clip_v1.mp4`.

### 9 — 시작+끝, 4초 (편집 2.5s)
**입력**: `outputs/ep02/09/start_v1.png`(창수 왼쪽 가장자리, 김 나는 머그) + `outputs/ep02/09/end_v1.png`(소파 앞, 머그가 미순 날개에 들려 올라감, 창수 기울임)
**인자**: v3_0, duration=4, 720p, multi_shots false, audio false
**프롬프트**
```
Pang Chang-su is already walking from the very first frame, at a steady unhurried waddling pace to his right, entering from the left edge of the frame along the floor between the sofa and the table, holding a white mug with a little steam in the wing nearer the camera, keeping his body and head facing to his right the whole time. Each step lands on the wood floor and rolls forward; his feet do not slide; the mug stays level in his wing. After three steps he stops in front of the sofa beside Mi-sun and holds the mug out to her, leaning slightly toward her; Mi-sun takes the mug in her wing and lifts it up with a happy smile, while Chang-su's wing becomes empty, exactly matching the end image. Pang Mi-sun otherwise stays lying under the beige duvet with her head on the white pillow; the duvet, the pillow, the black remote on the seat, the cushions, the glass on the table and the table stay exactly where they are. Chang-su does not look at the viewer. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Both beaks stay closed the whole time. No other characters appear. No new objects appear. Exactly one mug and one glass exist. Wings stay short and rounded with no fingers.
```
**자막·음성**: 창수 "응."(걸어오며), 미순 요청 4(받자마자, 자막 최대), 벨 #4. 효과음: 발소리, 머그 "톡".
**예상 시나리오**: 0~2.0s 머그 들고 세 걸음, 2.0~4.0s 건네기 → 미순이 받아 듦.
**위험·감시 항목**: 중간 | 머그 2개/사라짐, 김이 과장됨, 날개 늘어남, 미순 머리 들림.
**실패 시 편집 대안**: 앞 2.0s(걷기)만 쓰고 끝 프레임 정지 + 푸시인.
**크레딧**: 24. 31 → 7. **이 컷 이후 충전 필요**(11·12·14·15·16 = 102).

**9컷 ✅ 통과 (2026-10-08)**: 24크레딧, 잔액 31 → **7**. 생성 52초. 실측: 카메라 0.07px, 배경 3.05, 시작 2.16 / 끝 3.24. 0~2.0s 머그 들고 세 걸음(김 유지, 1개), 2.0~3.0s 내밀기 → 미순이 받아 들어 올림(김 계속), 창수 날개 비움. 3.5~4.0s 창수가 고개를 카메라 쪽으로 살짝 돌림(ep01 4-01과 같은 "카메라 흘끗") → 편집 구간을 0.5~3.0s로 잡으면 안 보임. 파일 `outputs/ep02/09/clip_v1.mp4`.

## 2. 현황 (2026-10-08)
| 컷 | 상태 | 크레딧 |
|---|---|---|
| 1 | ✅ | 18 |
| 2 | ✅ | 18 |
| 3 | ✅ (10컷 재사용) | 18 |
| 4 | ✅ | 18 |
| 5 | ❌ → 정지+푸시인(사용자 결정) | 18 |
| 6 | ✅ | 24 |
| 7 | ✅ | 18 |
| 9 | ✅ | 24 |
| 8·13 | 그래픽 | 0 |
| 11·12·14·15·16 | **대기 (충전 필요: 24+18+18+18+24 = 102)** | — |
합계 사용 156, 잔액 7. 7/8 통과(87%). 다음: 충전 후 11컷부터.

### 11 — 시작+끝, 4초 (편집 2.5s)
**입력**: `outputs/ep02/11/start_v1.png`(창수 소파 왼쪽 끝 앞에 직립, 충전기 든 채, 탁자에 컵·머그) + `outputs/ep02/11/end_v1.png`(창수 왼쪽 좌석에 앉아 등 기댐, 충전기 바닥)
**인자**: v3_0, duration=4, 720p, multi_shots false, audio false
**프롬프트**
```
Pang Chang-su stands facing the camera beside the left end of the sofa, holding a small white charger with its coiled cable in one wing. He bends forward a little and sets the charger down on the wood floor beside the left armrest, then straightens up with both wings empty. Then he turns and sits down slowly onto the empty left seat cushion of the sofa, his back settling against the backrest, his short legs stretched out on the cushion in front of him with his small grey feet resting on the seat, facing the camera, and stays sitting there still, exactly matching the end image. He sits only on the left seat cushion and does not touch Mi-sun. Pang Mi-sun lies completely still on the right half of the sofa under the beige duvet with her head on the white pillow; the duvet, the pillow, the black remote on the seat, the cushions, the glass and the mug on the table and the table stay exactly where they are. Chang-su does not look at the viewer while moving. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Both beaks stay closed the whole time. No other characters appear. No new objects appear. Exactly one charger, one glass and one mug exist. Wings stay short and rounded with no fingers.
```
**자막·음성**: 창수 작은 숨 1회(앉을 때). 효과음: 충전기 "툭", 소파 "푹". 시계 카드 없음(16컷에 21:30).
**예상 시나리오**: 0~1.5s 허리 숙여 충전기 내려놓기, 1.5~3.5s 돌아서 앉기, 3.5~4s 정지.
**위험·감시 항목**: **높음** (내려놓기 + 앉기 두 동작, 5컷 전례: "sit"이 소파 위로 오르기로 번짐) | 소파 위로 뛰어오름, 충전기가 2개/사라짐, 미순 쪽으로 앉음, 미순 몸 들림. 5컷과 달리 **끝 프레임(앉은 자세)이 있어** 보간이 앉기를 붙잡아 줄 것으로 예상.
**실패 시 편집 대안**: 앞 1.5s(내려놓기)만 쓰고 11e 정지 프레임 + 푸시인으로 "앉음" 처리.
**크레딧**: 24. 충전 후 잔액에서 차감. (현재 7 → 생성 불가, 충전 필요)

**11컷 ✅ 통과 (2026-10-08, 충전 후 잔액 337)**: 24크레딧, 잔액 337 → **313**. 생성 168초. 실측: 카메라 0.06px, 배경 2.11, 시작 2.22 / 끝 3.28. 0~1.5s 허리 숙여 충전기를 바닥(왼쪽 팔걸이 옆)에 놓음, 1.5~2.5s 일어나 돌아섬, 2.5~4.0s 왼쪽 좌석에 앉아 등 기댐(정면, 발 좌면 위). 충전기 1개 바닥, 컵·머그 탁자, 미순 고정. 5컷과 달리 끝 프레임이 앉기를 잡아 줌(0b 규칙 보강: **앉기는 끝 프레임 필수**). 편집 구간 0.5~3.5s. 파일 `outputs/ep02/11/clip_v1.mp4`. **15컷 시작 = 이 클립 끝 프레임(11e) 재사용.**

### 12 — 시작+끝, 3초 (편집 2.0s) — 대화 컷, 느리게
**입력**: `outputs/ep02/12/start_v1.png`(미순 얼굴, 베개, 리모컨 날개 옆, 01 기본) + `outputs/ep02/12/end_v1.png`(고개 왼쪽, 부리 살짝)
**인자**: v3_0, duration=3, 720p, multi_shots false, audio false
**프롬프트**
```
Pang Mi-sun lies on the white pillow under the beige duvet with a calm, gentle face, looking at the camera. Very slowly she turns her head a little to her left side of the frame, toward the left end of the sofa where Chang-su sits, and settles there looking that way, exactly matching the end image. As she speaks a short, soft line, her beak opens and closes only a tiny amount, barely parting, just enough to show she is talking; it keeps its exact small triangular shape and size and never opens wide, stretches, or turns into lips. Her head stays on the pillow the whole time and does not lift; her wings rest still on top of the duvet; the black remote on the seat cushion beside her wing, the duvet, the pillow and the sofa stay exactly where they are. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**자막·음성**: 미순 요청 5(느리게 0.9, 다정하게), **벨 없음**. 13컷 인서트는 이 컷 시작 프레임 크롭.
**예상 시나리오**: 0~1.5s 고개 천천히 왼쪽, 1.5~3s 부리 미세.
**위험·감시 항목**: 낮음~중간 (2컷과 같은 유형, 통과 전례) | 리모컨이 움직이거나 날개가 리모컨을 집음(R25: 15컷에서 창수가 집어야 함), 부리 크게 벌림.
**실패 시 편집 대안**: 앞 1.5s만 쓰고 끝 프레임 정지.
**크레딧**: 18. 313 → 295.
