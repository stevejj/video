# ep03 Kling 실행표 (2026-10-16)

> 규칙: ep02 실행표 §0 공통 문장 그대로(고정 카메라, 플러시, 부리 닫힘, 새 물체 없음). 클립마다 실행표 → 사용자 "진행" → 생성 1회 → 검증(`tools/verify_clip.py --ep ep03`) → 보고. 자동 재시도 없음. 720p, 6크레딧/초. 잔액 **895**(2026-10-17 조회, 충전 반영).
> 02c M14: 이불은 절대 들리지 않음. 날개는 이불 위에서만 움직임. 동사는 작게(slides, reaches, settles). 2단만 "pulls".

## 클립 1 — S → E1, 4초 (편집 0.0~4.0)
**입력**: `outputs/ep03/01/start_v1.png`(S) + `outputs/ep03/01/end_v1.png`(E1)
**인자**: model=kling-video-v3_0, duration=4, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
```
Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the surroundings and objects stay photoreal and completely unchanged.
Pang Chang-su sits on the left seat cushion facing the camera, holding a small silver snack bag low in both wings in front of his belly. In the first two seconds he lifts one wing a little, takes one potato chip from the top of the bag, brings it to his beak with a small movement and eats it; the bag stays low at chest height the whole time. Pang Mi-sun lies completely still on the right under the beige duvet with her head on the pillow, looking at the camera. From about two seconds, her upper wing slides slowly across the top of the duvet toward him, reaches the top of his bag and takes ONE chip, then holds it halfway back toward her beak, exactly matching the end image; her head, eyes and other wing do not move at all, and the duvet stays flat and in place, never lifted. As her wing reaches the bag, Chang-su pauses and turns only his head a little toward her, about 30 degrees, his body still facing the camera, and holds that pose, exactly matching the end image. When Chang-su eats the chip his beak opens only a tiny amount, keeping its small triangular shape, then closes and stays closed; Mi-sun's beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상**: 0~2s 창수 과자 1개 먹음(작게), 2~3.5s 미순 날개 미끄러져 과자 집음, 3.5~4s 창수 멈칫·고개 30도.
**위험**: 창수가 봉지를 높이 들어 올림 / 미순 고개가 따라 돎 / 이불이 들림 / 과자가 여러 개로 늘어남 / 창수 부리 크게 벌어짐. 실패 시 대안: 앞 2초만 쓰고 E1 정지 프레임 0.5s(푸시인 없음) 뒤 클립 2.
**크레딧**: 24 → 예상 잔액 871.

## 클립 1 v2 — S → K1 → E1, Kling 4.0 키프레임, 5초 (C안, 2026-10-17)
**입력**: first_image `outputs/ep03/01/start_v1.png`(S), keyframe_1 `outputs/ep03/01/key_v1.png`(K1, 날개가 봉지에 닿음), tail_image `outputs/ep03/01/end_v1.png`(E1)
**인자**: model=kling-video-v4_0, duration=5, resolution=720p, imageCount=1 (aspect_ratio 생략 = 첫 프레임 따름). 4.0은 오디오·멀티샷 인자 없음.
**길이 5초로 늘린 이유**: 키프레임은 시간 순서만 지정되고 위치는 모델이 정함(가운데 근처 예상). 4초면 "먹기 → 뻗기 → 닿기"가 2초 안에 몰려 급해짐.
```
Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the surroundings and objects stay photoreal and completely unchanged.
Pang Chang-su sits on the left seat cushion facing the camera, holding a small silver snack bag low in both wings in front of his belly. First he takes one potato chip from the bag with a small movement and eats it, his beak opening only a tiny amount; the bag stays low the whole time. Pang Mi-sun lies under the beige duvet with her head on the pillow, eyes wide open, looking at the camera the whole time; her head never turns. Then her upper wing, still empty, stretches out slowly and comically long along the top of the duvet, all the way to his bag, exactly matching the middle keyframe, and its tip dips into the top of the bag and comes out holding ONE chip. The wing then slides back halfway toward her, holding that single chip, exactly matching the end image. The duvet stays flat, never lifted. As the chip leaves his bag, Chang-su pauses and turns only his head a little toward her, about 30 degrees, his body still facing the camera, and holds that pose. Mi-sun's beak stays closed. No other characters appear. No new objects appear. The chip appears only after the wing tip has touched the bag. Wings stay soft, rounded and fingerless.
```
**예상**: 0~2s 창수 과자 먹기, 2~2.5s 미순 빈 날개가 늘어나 봉지에 닿음(K1), 2.5~4s 과자 한 개 들고 돌아옴, 4~5s 창수 고개 30도.
**위험**: 키프레임이 너무 이르거나 늦게 배치돼 먹기·뻗기가 겹침 / 날개 늘어남이 끊기거나 날개가 두 개로 보임 / 과자가 여전히 미리 생김. 실패 시 대안: 클립 1 v1의 0~2s(먹기) + v2 중 쓸 만한 구간 이어 붙이기.
**크레딧**: 제출 응답 **50**(4.0 = 10/초, 720p). 잔액 871 → 821. 2026-10-17 사용자 "진행".

**클립 1 v2 ✅ 통과 (2026-10-17)**: 50크레딧(4.0 = 10/초), 잔액 871 → **821**. 생성 153초. 실측: 카메라 0.01px, 배경 1.45, 첫↔끝 1.92. 동작: 0.5~1.5s 창수 과자 먹기, **2.0~2.5s 미순 빈 날개가 쭉 늘어남, 2.8~3.5s 날개 끝이 봉지 안, 3.7s 과자 한 개 들고 나옴**, 4.0~4.3s 날개가 과자 들고 돌아옴, 4.0s 창수 한쪽 눈 깜빡 후 4.2s부터 고개 미순 쪽. 과자가 미리 생기지 않음, 날개 끊김 없음, 미순 고개 고정(2.7s 깜빡 1회). 파일 `outputs/ep03/01/clip_v2.mp4`, 시트 `verify_v2/sofa_sheet.jpg`, `verify_v2/reach_2.0-4.5.jpg`. 편집 0~5.0s 전체.
- 교훈 확정(05a 반영): **먼 거리 집기 동작은 Kling 4.0 중간 키프레임으로 "닿는 순간"을 고정**하면 순간이동 없이 된다. 비용 = 이미지 95원 + 4.0 10/초.

## 클립 2 — E1 → E2, 4초 (편집 4.0~8.0)
**입력**: `outputs/ep03/01/end_v1.png`(E1) + `outputs/ep03/02/end_v1.png`(E2)
**인자**: 동일, duration=4
```
Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the surroundings and objects stay photoreal and completely unchanged.
Pang Chang-su sits on the left seat cushion holding a small silver snack bag low in both wings; his head is turned a little toward Pang Mi-sun. In the first second he turns his head back to face the camera and settles the bag in his wings. Mi-sun lies completely still under the beige duvet with her head on the pillow, looking at the camera; the chip in her upper wing is gone. Then her upper wing slides across the top of the duvet to his bag, closes on the top of the bag and PULLS the whole bag out of his wings in one smooth motion, dragging it across the duvet to rest on top of the duvet beside her belly, and her wing settles on the bag, exactly matching the end image; her head, eyes and other wing do not move at all, and the duvet stays flat and in place, never lifted. Chang-su's wings, suddenly empty, stay raised in the air for a moment, then lower slowly to rest at his sides on the cushion; he keeps facing the camera with a calm face and blinks slowly twice, exactly matching the end image. Both beaks stay closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상**: 0~1s 창수 정면 복귀, 1~2.5s 봉지 끌려감, 2.5~4s 빈 날개 내리고 깜빡 2회.
**위험**: 봉지가 복제됨(창수 손에도 남음) / 미순이 일어남 / 창수가 봉지를 쫓아 몸을 기울임 / 이불 들림. 실패 시 대안: 1단 클립 끝 + E2 정지 프레임 2s.
**크레딧**: 24 → 예상 잔액 847.

## 클립 2 v2 — E1 → K1(재사용) → E2, Kling 4.0 키프레임, 5초 (2026-10-17 제안)
**입력**: first_image `outputs/ep03/01/end_v1.png`(E1), keyframe_1 `outputs/ep03/01/key_v1.png`(K1 재사용: 늘어난 날개가 봉지에 닿은 순간, 창수 정면), tail_image `outputs/ep03/02/end_v1.png`(E2)
**인자**: model=kling-video-v4_0, duration=5, resolution=720p, imageCount=1
**K1 재사용 이유**: "날개가 봉지에 닿은 순간 + 창수 정면 + 봉지 창수 손"이 클립 2 중간에 필요한 그림과 같음 → 새 이미지 0원.
```
Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the surroundings and objects stay photoreal and completely unchanged.
Pang Mi-sun lies under the beige duvet with her head on the pillow, eyes wide open, looking at the camera the whole time; her head never turns. First her upper wing brings the single chip to her beak and she eats it with a tiny beak movement, then her beak stays closed. At the same time Pang Chang-su, sitting on the left cushion with a small silver snack bag held low in both wings, turns his head back to face the camera. Then her upper wing, now empty, stretches out comically long again along the top of the duvet all the way to his bag, exactly matching the middle keyframe; this time the wing tip grips the top edge of the whole bag and pulls the entire bag out of his wings in one smooth motion, dragging it back across the top of the duvet until it rests beside her belly, and the wing, back to its normal short length, settles on the bag, exactly matching the end image. Chang-su's wings stay raised in the air for a moment, suddenly empty, then lower slowly to rest at his sides; he keeps facing the camera with a calm face and blinks slowly twice. The duvet stays flat, never lifted. Exactly one snack bag the whole time; the bag is never in two places. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 0~1s 미순 과자 먹기·창수 고개 정면, 1~2.5s 빈 날개 다시 늘어나 봉지에 닿음(K1), 2.5~4s 봉지째 끌어옴, 4~5s 창수 빈 날개 내리고 깜빡 2회.
**위험**: 봉지 복제(창수 손에도 남음) / 날개가 짧아지는 과정에서 끊김 / 창수가 봉지를 따라 몸을 기울임 / 미순 고개 돌아감. 실패 시 대안: 2.5s까지 쓰고 E2 정지 프레임 2.0s.
**크레딧**: 50(4.0 = 10/초). 잔액 821 → 771.

**클립 2 v2 ✅ 통과(조건 1개) (2026-10-17)**: 50크레딧, 잔액 821 → **771**. 생성 154초. 실측: 카메라 0.01px, 배경 1.55, 첫↔끝 2.29. 동작: 0~0.8s 미순이 훔친 과자를 먹음, 0.8~1.0s 창수 깜빡·정면, 2.0~2.75s 빈 날개 다시 늘어나 봉지에 닿음, **3.0~3.5s 봉지째 끌려감(봉지 1개, 복제 없음), 창수 빈 날개 번쩍 들림**, 3.75~4.75s 봉지 미순 배 옆, 창수 날개 내리고 4.25s 깜빡. **조건**: 0.42~0.68s 미순이 과자 먹을 때 **부리를 크게 벌림**(입 안 보임, 0.3초) — 캐릭터 규칙 "부리 작게"와 다름. 파일 `outputs/ep03/02/clip_v2.mp4`, 시트 `verify_v2/sofa_4fps.jpg`, `verify_v2/yank_2.9-3.7.jpg`, `verify_v2/misun_eat_0.3-0.9.jpg`.
- 무음 가편집 v0: 클립 1 v2 + 클립 2 v2 = **10.0s**, 제목 "TV vs / 과자", 채널명. `outputs/ep03/roughcut/ep03_roughcut_v0_silent.mp4`, 시트 `v0_sheet.jpg`.

- **사용자 피드백 (2026-10-17)**: "팔이 길게 늘어나면 어떡해, 괴물 같잖아" → 클립 1·2 v2 불채택(늘어난 날개). 02c M16 추가. 재배치안 검토.

## 재배치 클립 3 — S2 → E1b, Kling 3.0 시작+끝, 4초 (2026-10-17)
**입력**: first_image `outputs/ep03/03/start_v1.png`(S2), tail_image `outputs/ep03/03/end_v1.png`(E1b)
**인자**: model=kling-video-v3_0, duration=4, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
```
Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the surroundings and objects stay photoreal and completely unchanged.
Pang Chang-su sits on the left seat cushion facing the camera, holding a small silver snack bag low in both wings in front of his belly. In the first two seconds he takes one potato chip from the bag and eats it, his beak opening only a tiny amount; the bag stays low the whole time. Pang Mi-sun lies right beside him with her head on the seat cushion and her body under the beige duvet, eyes wide open, looking at the camera the whole time; her head does not move. From about two seconds, her lower wing, the one lying on the seat right next to his bag, slides a short distance to the top of his bag, takes ONE chip and lifts it up to the front of her beak, where her other wing comes down to hold it too, exactly matching the end image. Her wings keep their normal short rounded length and never stretch. The chip appears only after her wing has touched the bag. As her wing lifts the chip out of his bag, Chang-su pauses and turns his head down toward her, about 30 degrees, his body still facing the camera, and holds that pose, exactly matching the end image. Mi-sun's beak stays closed. The duvet stays in place. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 0~2s 창수 과자 먹기, 2~3s 미순 아래쪽 날개가 짧게 봉지로 가서 과자 집어 부리 앞으로, 3~4s 창수 고개 미순 쪽.
**위험**: 과자 미리 생김 / 날개가 늘어남 / 미순 고개 돌아감. 실패 시 대안: 0~2s(먹기)만 쓰고 E1b 정지 0.5s.
**크레딧**: 24. 잔액 771 → 747.

## 재배치 클립 4 — E1b → E2b, Kling 3.0 시작+끝, 4초 (2026-10-17)
**입력**: first_image `outputs/ep03/03/end_v1.png`(E1b), tail_image `outputs/ep03/04/end_v1.png`(E2b)
**인자**: 클립 3과 동일
```
Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the surroundings and objects stay photoreal and completely unchanged.
Pang Mi-sun lies beside Pang Chang-su with her head on the seat cushion and her body under the beige duvet, eyes wide open, looking at the camera the whole time; her head does not move. First she eats the chip in front of her beak, her beak opening only a tiny amount and keeping its small triangular shape, then her beak stays closed. At the same time Chang-su, sitting on the left cushion holding a small silver snack bag low in both wings, turns his head back to face the camera. Then her lower wing slides a short distance to his bag, grips the top of the whole bag and pulls it out of his wings in one smooth motion onto her chest, on top of the duvet, and her other wing settles on the bag, exactly matching the end image. Her wings keep their normal short rounded length and never stretch. Chang-su's wings, suddenly empty, stay raised in the air for a moment, then lower slowly to rest at his sides; he keeps facing the camera with a calm face and blinks slowly twice, exactly matching the end image. Exactly one snack bag the whole time; it is never in two places. The duvet stays in place. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 0~1s 미순 과자 먹기·창수 정면, 1~2.5s 봉지째 미순 가슴 위로, 2.5~4s 창수 빈 날개 내리고 깜빡 2회.
**위험**: 봉지 복제 / 미순 부리 크게 벌림(클립 2 v2와 같은 문제) / 창수가 봉지 따라 기울임. 실패 시 대안: 1s부터 사용.
**크레딧**: 24. 잔액 747 → 723.
- 2026-10-17 사용자 "진행" → 클립 3·4 동시 제출(각 24, 잔액 771 → 723).

**재배치 클립 3 ❌ (2026-10-17)**: 24크레딧. 카메라 0.06px·배경 2.19(기술 통과). **실패**: 1.8~3.0s 미순 **머리가 통째로 굴러 뒤집힘**(얼굴이 거꾸로, 위쪽 날개가 얼굴 위를 덮으며 지나감) 후 3.2s 원위치. 창수 과자 먹기도 거의 안 보임(부리만 살짝), 고개 돌림 없음. 시트 `outputs/ep03/03/verify_v1/close_6fps.jpg`.
**재배치 클립 4 ❌ (2026-10-17)**: 24크레딧, 잔액 **723**. 기술 통과(카메라 0.06px, 배경 1.54). **실패**: 0.7~1.2s 미순 부리 크게 벌림, 1.3~2.2s 머리가 다시 굴러 뒤집힘, 2.3~2.5s 봉지 끌려감, 2.7s~ 봉지 미순 가슴·창수 빈손(이 구간만 정상). 시트 `outputs/ep03/04/verify_v1/close_6fps.jpg`.
- 원인: S2에서 미순 **머리가 옆으로 크게 기울어진 채 누운 자세** + 움직이는 날개가 머리 반대편(위쪽) → 날개가 얼굴을 넘어가야 해서 Kling이 머리를 굴려 버림. S2 메모 ①을 허용한 것이 실수.
- 교훈(05a·02c 반영): **팔을 뻗는 캐릭터는 머리가 똑바로 선 자세(앉기)로**. 누운 캐릭터가 손을 쓰면 머리가 구른다. 움직일 날개는 시작 프레임에서 목표물 쪽에 있어야 한다.

## 현황
- 2026-10-17 이미지 S·E1·E2 통과. 클립 1 사용자 "진행".
- **클립 1 ⚠ 조건부 (2026-10-17)**: 24크레딧, 잔액 895 → **871**. 생성 84초. 실측: 카메라 0.01px(고정), 배경 드리프트 2.7, 첫↔끝 3.0. 동작: 0.5~1.75s 창수가 과자 1개 꺼내 먹음(눈 감고 음미, 봉지 낮게 유지) ✅, 3.25~4.0s 창수 고개 미순 쪽 ✅. **실패**: 미순 날개가 봉지까지 가지 않음 — 2.25s에 과자가 **미순 가슴 앞 날개 위에서 갑자기 생김**(순간이동), 그 뒤 날개가 과자를 든 채 E1 위치로 뻗음. "창수 봉지에서 훔친다"가 안 읽힘. 부가: 1.75s부터 미순 눈이 웃는 눈(^^)으로 감김. 원인 추정: 미순 날개 끝↔봉지 거리가 소파 절반(플러시 날개로 닿을 수 없는 거리) → 모델이 늘리지 않고 과자를 만들어 냄. 파일 `outputs/ep03/01/clip_v1.mp4`, 시트 `verify_v1/sofa_sheet.jpg`, `verify_v1/reach_1.75-2.75.jpg`.
- 교훈(05a 반영 후보): **"A가 B의 물건을 집는다"는 시작 프레임에서 손이 닿는 거리여야 한다.** 멀면 Kling은 팔을 늘리지 않고 물건을 손에 생성한다. 먼 거리를 원하면 "닿는 순간" 중간 키프레임을 이미지로 고정한다.
