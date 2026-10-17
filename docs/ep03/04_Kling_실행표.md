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

## 현황
- 2026-10-17 이미지 S·E1·E2 통과. 클립 1 실행표 제출, 사용자 "진행" 대기.
