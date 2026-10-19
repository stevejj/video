# ep06 Kling 실행표 — 댄스배틀 (애니매틱 확인 후 실행)

> 상한 **120크레딧**, 잔액 549. 공통 규칙:
> - 고정 카메라. 노란 붐박스는 움직이지 않음(F8, 자동 검사).
> - 날개는 평소 길이로, 늘이기 금지(M16). 미순은 속눈썹 없음, 부리 닫힘.
> - 새 물체·새 캐릭터 없음.
> - 2회 연속 실패 시 중단(F5). 핵심(번갈아 춤 / 창수 돌아서 박수)이 안 보이면 채택 추천 금지(F6).
> - 실패 컷은 퍼펫 애니매틱 구간으로 대체(0원 안전망).
> - **체이닝**: C2 시작 = C1 마지막 프레임, C3 시작 = C2 마지막 프레임 → 한 샷처럼 이어짐. 그래서 C1 → C2 → C3 순서대로 하나씩 제출.
> - 인자(공통): model=kling-video-v3_0, duration=5, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1

## C1 미순 차례 — K1 → (끝 프레임 없음), 5초 · 30크레딧
**입력**: first_image `outputs/ep06/01/start_v1.png`
```
Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the alley, the brick wall, the pavement and the yellow boombox stay photoreal and completely unchanged, and the boombox never moves.
Pang Chang-su stands in the foreground on the left, seen from behind, watching calmly with his short wings held behind his back, only nodding his head to the beat. He stays seen from behind the whole time and never turns around.
Pang Mi-sun, facing the camera, dances energetically on the spot to a bouncy hip hop beat: she sways her body from side to side with small penguin steps, bounces up and down on every beat, flaps her short wings up and down, and bobs her head, with a playful, confident smile. She stays in the same spot.
Her wings keep their normal short rounded length and never stretch. Both heads keep their normal shape. Her beak stays closed. No eyelashes. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 5초 내내 미순 좌우 뒤뚱 + 통통 + 날개 퍼덕, 창수는 뒷모습으로 고개만 까딱.
**위험**: 창수가 돌아봄 / 미순이 자리 이동 / 날개 늘어남 / 붐박스가 움직임.

## C2 창수 차례 — C1 마지막 프레임 →, 5초 · 30크레딧
**입력**: first_image = C1 마지막 프레임(추출 후 업로드)
```
Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the alley, the brick wall, the pavement and the yellow boombox stay photoreal and completely unchanged, and the boombox never moves.
Now it is Pang Chang-su's turn. Chang-su, in the foreground on the left, dances on the spot to a bouncy hip hop beat: he spins around once in place on his feet, wiggles his round body and bottom from side to side, flaps his short wings, and at the end points one short wing toward Mi-sun as if saying "your turn". He finishes seen from behind again, in the same spot.
Pang Mi-sun, facing the camera, watches him with her wings at her sides, nodding along to the beat, a little impressed.
Wings keep their normal short rounded length and never stretch. Both heads keep their normal shape. Her beak stays closed. No eyelashes. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 0.5~2s 제자리 한 바퀴, 2~4s 엉덩이 흔들기·날개 퍼덕, 4~5s 날개로 미순 가리킴.
**위험**: 회전할 때 얼굴·몸이 뭉개짐 / 창수가 자리를 벗어남 / 미순이 같이 춤춤.

## C3 미순 반격 + 창수 박수 — C2 마지막 프레임 → KE, 5초 · 30크레딧
**입력**: first_image = C2 마지막 프레임(`outputs/ep06/c2/chain_v1.png`), tail_image `outputs/ep06/03/end_v1.png`(KE)
```
Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the alley, the brick wall, the pavement and the yellow boombox stay photoreal and completely unchanged, and the boombox never moves.
Pang Mi-sun answers with a big finishing dance move on the spot: she spins around once quickly, does a little hop, and lands in a proud final pose with one short wing raised high and the other wing on her hip, eyes closed in happy upward curves, beak closed.
Pang Chang-su, in the foreground on the left, freezes, then slowly turns around on the same spot to face the camera, his eyes wide open in shock, and claps his short wings together in front of his chest, exactly matching the end image. Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush.
Wings keep their normal short rounded length and never stretch. Both heads keep their normal shape. Beaks stay closed. No eyelashes on either penguin. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 0~2s 미순 회전·점프·포즈, 2~3.5s 창수 멈칫 → 돌아섬, 3.5~5s 정면 놀란 눈 + 박수.
**위험**: 창수 정면에 볼터치가 생김(C2에서 실제로 생김 → 프롬프트에 금지 문장 추가) / 창수 돌아설 때 얼굴이 미리 생김 / 날개 박수가 손가락처럼 변함 / 미순 포즈가 KE와 어긋남.

## 현황
- 2026-10-19 작성. 애니매틱 v1 확인 + "진행" 대기.
- **C1 ✅ (2026-10-19)**: 30크레딧. 카메라 0.03px(최대 0.26), 배경 1.4.
  - 미순: 5초 내내 제자리에서 좌우 뒤뚱·통통·날개 퍼덕·눈 감고 흥 타기. 날개는 평소 길이.
  - 창수: 뒷모습 유지, 고개 까딱. 붐박스 그대로.
  - 체이닝 프레임: 104(4.33s, 정면·양 날개 위·눈 뜸·미소)를 골라 C2 시작으로 씀. 마지막 프레임은 고개가 기울고 흐려서 안 씀. 편집에서 C1은 0~4.33s까지 사용.
  - 시트 `outputs/ep06/c1/verify_v1/motion_sheet.jpg`.
- C2 제출(`outputs/ep06/c2/meta.json`), 잔액 549 → 489.
