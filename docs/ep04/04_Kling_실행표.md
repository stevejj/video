# ep04 Kling 실행표 — 최소안 (2026-10-18 사용자 "최소안 하자")

> 애니매틱 확인 후 컷별 결정(08 표준 순서). Kling = 4·6·7컷만, 나머지(1·2·3·5)는 정지 컷+줌(0원). **상한 66크레딧**, 잔액 675.
> 공통 규칙: 고정 카메라, 플러시, 날개 평소 길이·늘이기 금지(M16), 앉은 자세 머리 똑바로(M17), 미순 속눈썹 없음·부리 작게, 과자는 날개가 그릇에 닿은 뒤에만(ep03 교훈), 새 물체 없음. 실패 2회 연속 → 중단·재기획(F5). 핵심(훔치기·빈 그릇·기대기)이 안 보이면 채택 추천 금지(F6).

## 4컷 — M4s → M4e, 4초 (편집 2.5s) · 24크레딧
**입력**: first_image `outputs/ep04/04/start_v1.png`(M4s), tail_image `outputs/ep04/04/end_v1.png`(M4e)
**인자**: model=kling-video-v3_0, duration=4, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
```
Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the surroundings and objects stay photoreal and completely unchanged.
Pang Chang-su (left) and Pang Mi-sun (right) sit side by side on the sofa, both facing the camera, watching television. Chang-su holds a white bowl of chocolate chip cookies low on his lap and keeps looking at the camera the whole time; he does not notice anything. Mi-sun holds her salad bowl on her lap with a fork in her right wing. Her head stays perfectly upright and still, facing the camera, eyes wide open, innocent face. Only her left wing moves: it slides the short distance from the rim of her salad bowl to his cookie bowl right beside her, picks up ONE chocolate chip cookie from the top of his bowl, and brings it up in front of her beak, exactly matching the end image. Her wing keeps its normal short rounded length and never stretches. The cookie appears in her wing only after her wing has touched his bowl. Both beaks stay closed. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 0~1s 정지, 1~2.5s 미순 왼쪽 날개만 옆 그릇 → 쿠키 하나 → 부리 앞, 창수 정면 그대로.
**위험**: 쿠키가 미리 생김 / 날개 늘어남 / 미순 고개 돌아감 / 창수가 쳐다봄. 실패 시: M4s→M4e 정지 점프(애니매틱과 동일, 0원).

## 6컷 — I6 단독, 3초 (편집 1.5s) · 18크레딧
**입력**: first_image `outputs/ep04/06/start_v1.png`(I6)만
**인자**: 4컷과 동일, duration=3
```
Static camera, locked-off, no camera movement, same composition throughout. A close-up looking down into an empty white ceramic bowl with only a few chocolate chip cookie crumbs at the bottom. The soft rounded tip of a blue-grey plush penguin wing pats around the empty bottom of the bowl twice, slowly, searching, finding nothing; the crumbs shift slightly. The wing stays soft, rounded and fingerless, normal size. No cookies appear. No new objects appear. The bowl does not move.
```
**예상**: 날개 끝이 빈 그릇 바닥을 두 번 더듬음.
**위험**: 쿠키가 생김 / 날개가 손가락처럼 변함. 실패 시: I6 정지(0원).

## 7컷 — W5e → W7e, 4초 (편집 3.0s) · 24크레딧
**입력**: first_image `outputs/ep04/05/end_v1.png`(W5e), tail_image `outputs/ep04/07/end_v1.png`(W7e)
**인자**: 4컷과 동일, duration=4
```
Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the surroundings and objects stay photoreal and completely unchanged.
Pang Chang-su (left) and Pang Mi-sun (right) sit side by side on the sofa. At first Chang-su is looking at Mi-sun with a blank face, his cookie bowl almost empty on his lap; Mi-sun faces the camera holding a half-eaten cookie at her beak. She quickly finishes the last bite with a tiny beak movement, then leans her head sideways against Chang-su's shoulder and rubs her cheek on him affectionately, closing her eyes in happy curved lines; Chang-su's blank face melts into a smile, his eyes closing in happy curved lines too, exactly matching the end image. They stay sitting in the same places; only their heads tilt toward each other. Heads keep their normal size and shape and never stretch. Her salad bowl stays full on her lap; his bowl is empty with a few crumbs. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 0~1s 미순 마지막 한 입, 1~2.5s 창수 어깨에 기대 볼 비빔, 2.5~4s 둘 다 눈웃음.
**위험**: 머리가 겹쳐 하나로 섞임 / 미순 부리 크게 벌림 / 몸이 미끄러짐. 실패 시: W5e→W7e 정지 점프(0원).

## 현황
- 2026-10-18 사용자 "진행" → 3클립 동시 제출(24+18+24 = 66, 잔액 675 → 609).
- **4컷 ✅ (2026-10-18)**: 24크레딧. 카메라 0.02px, 배경 3.1. 0.5~1.5s 미순 왼쪽 날개(평소 길이)가 옆 그릇으로, 1.7~2.0s **그릇에서 쿠키를 집어 올림**(미리 생기지 않음), 2.2~2.5s 부리 앞, 2.7~3.8s 먹음. 미순 머리 똑바로, 창수 정면(모름). 시트 `outputs/ep04/04/verify_v1/sheet_6fps.jpg`. 편집 0.6~3.2s.
- **6컷 ✅**: 18크레딧. 날개 끝이 빈 그릇 바닥을 두 번 더듬음, 쿠키 안 생김. 1인칭 시점이라 카메라가 살짝 흔들림(4px, 허용). 편집 0.3~1.9s.
- **7컷 ✅**: 24크레딧, 잔액 **609**. 0.5~1.0s 미순 마지막 한 입, 2.0~4.0s 창수 어깨에 볼 기대고 둘 다 눈웃음, 머리 섞임 없음. 메모: 0.2~0.4s 창수 그릇 마지막 쿠키가 저절로 사라짐(짧아 허용). 편집 0~3.6s(1.35배 확대).
- **완성본 v1**: 16.2s, 정지 컷(1·2·3·5) + Kling(4·6·7), BGM F(-24 목표) + 기존 효과음 8개(와삭 4, 반짝 1, 그릇 톡 3), 최종 -18.8 LUFS. `outputs/ep04/roughcut/ep04_v1.mp4`, 시트 `v1_sheet.jpg`. **ep04 비용: Kling 66크레딧, 이미지 약 1,400원(보정 기준), 효과음 0원.**
