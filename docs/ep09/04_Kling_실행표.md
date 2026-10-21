# ep09 Kling 실행표 — 남자 여자 / "아무거나" (애니매틱 v2 확인 후, 2026-10-21 사용자 "진행해")

> **상한 400크레딧**(예상 약 357 + 재시도 여유). Pro 등급 단가 기준:
> - 4.0 omni: 초당 9.
> - 3.0: 초당 6.
>
> 관문:
> - G2: `lint_prompts.py` + `preflight_kling.py`(대사 원문 = 녹음 대사·순서, 음성 길이, 입력 파일) 통과 후 승인 요청.
> - G3: 클립마다 `qa_clip.py`(입모양 장면은 `--voice-ref`) + 시트(얼굴 눈·눈썹, 소품) + 거품·소품이 얼굴을 덮으면 가장자리 확대(ep08 S7).
> - G4: 완성본 상태 이어짐 검사.
>
> 운영 규칙:
> - 입모양 7장면은 ep08에서 검증된 방식(장면 트랙 + 대사 원문 + "in Korean")이라 시험 장면 없이 진행.
> - 단, 2개씩 제출하고, 받으면 바로 검사.
> - 2회 연속 실패 시 중단(F5).
> - 대사에 "팽/펭" 금지(ep08 S6 저작권).
> - 옷: 미순 연분홍 후드, 창수 회색 티(끝까지 같음).
> - 소품: 폰 1~3 창수 날개 → 5·6 소파 위 / 상자 7 닫힘 → 8 열림·치킨 → 9 빈 상자·뼈 / 닭다리 8장면 미순 날개에 2개.

## S1 거실 소파 — 입모양 · Kling 4.0 omni, 5초 · 45크레딧
**입력**: image_1 `outputs/ep09/01/start_v1.png`(K1), audio_1 `outputs/ep09/voice/scenes/s1.mp3`
**인자**: model=kling-video-v4_0(omni_ref_video), duration=5, aspect_ratio=9:16, 720p, prefer_multi_shots=true, enable_audio=true
```
One single continuous shot with a static, locked-off camera, no cuts, no camera movement: exactly the scene of 图片1 (same camera angle, same living room, same sofa, same two plush penguins in the same places and the same clothes). 3D animated plush characters, short velvet fur; the room and the objects stay photoreal and unchanged.
The two penguins speak in Korean, using exactly the voices, words and timing of 音频1, and nothing else. They take turns in this exact order:
1. Chang-su (left, darker blue-grey, grey T-shirt, holding the phone): "여보, 저녁 뭐 먹을래?"
2. Mi-sun (right, light silver-grey, pink hoodie, holding the TV remote): "음~ 아무거나~"
Only the penguin who is speaking moves the beak, opening and closing exactly in sync with that line in 音频1; the listener keeps the beak closed. No other words, no English.
Chang-su turns his head toward Mi-sun while asking. Mi-sun answers lazily without looking at him, leaning back on the cushion. The phone stays in Chang-su's wing and the remote stays in Mi-sun's wing the whole time; they never float or move on their own.
Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes. Neither penguin has eyebrows (NO eyebrows); their eyes stay the same simple round glossy black eyes and the same size as in the first frame.
Wings keep their normal short rounded length and never stretch. Heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 창수가 미순 쪽으로 고개 돌려 질문 → 미순이 기댄 채 시큰둥하게 대답.
**위험·대책**: 둘이 동시에 입을 움직임 → "말하는 쪽만 부리"(ep07에서 검증) / 리모컨·폰이 떠다님.

## S2 소파 — 입모양 · Kling 4.0 omni, 5초 · 45크레딧
**입력**: image_1 `outputs/ep09/02/start_v1.png`(K2), audio_1 `outputs/ep09/voice/scenes/s2.mp3`
**인자**: S1과 같음
```
One single continuous shot with a static, locked-off camera, no cuts, no camera movement: exactly the scene of 图片1 (same camera angle, same living room, same sofa, same two plush penguins in the same places and the same clothes). 3D animated plush characters, short velvet fur; the room and the objects stay photoreal and unchanged.
The two penguins speak in Korean, using exactly the voices, words and timing of 音频1, and nothing else. They take turns in this exact order:
1. Chang-su (left, darker blue-grey, grey T-shirt, holding the phone): "치킨?"
2. Mi-sun (right, light silver-grey, pink hoodie): "치킨은 너무 많이 먹었어."
Only the penguin who is speaking moves the beak, opening and closing exactly in sync with that line in 音频1; the listener keeps the beak closed. No other words, no English.
While answering, Mi-sun shakes her head firmly from side to side and waves one short wing in front of her chest as a clear "no". The phone stays in Chang-su's wing and the TV remote stays on the sofa cushion where it lies; they never float or move on their own.
Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes. Neither penguin has eyebrows (NO eyebrows); their eyes stay the same simple round glossy black eyes and the same size as in the first frame.
Wings keep their normal short rounded length and never stretch. Heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 창수 "치킨?" → 미순 고개를 젓고 날개를 휘저으며 거절. 편집에서 줌·핀 조명·펀치.
**위험·대책**: 날개 휘저을 때 늘어남 → "never stretch" / 리모컨이 날개로 옮겨감.

## S3 소파 메뉴 핑퐁 — 입모양 · Kling 4.0 omni, 6초 · 54크레딧
**입력**: image_1 `outputs/ep09/03/start_v2.png`(K3 v2, K2 눈 옮겨 붙임), audio_1 `outputs/ep09/voice/scenes/s3.mp3`
**인자**: S1과 같음, duration=6
```
One single continuous shot with a static, locked-off camera, no cuts, no camera movement: exactly the scene of 图片1 (same camera angle, same living room, same sofa, same two plush penguins in the same places and the same clothes). 3D animated plush characters, short velvet fur; the room and the objects stay photoreal and unchanged.
The two penguins speak in Korean, using exactly the voices, words and timing of 音频1, and nothing else. They take quick turns in this exact order:
1. Chang-su (left, darker blue-grey, grey T-shirt, holding out the phone): "피자?"
2. Mi-sun (right, light silver-grey, pink hoodie): "느끼해."
3. Chang-su: "떡볶이?"
4. Mi-sun: "매워."
5. Chang-su: "족발?"
6. Mi-sun: "밤에 무슨 족발이야~"
Only the penguin who is speaking moves the beak, opening and closing exactly in sync with that line in 音频1; the listener keeps the beak closed. No other words, no English.
Chang-su keeps holding out the phone toward Mi-sun, a little more eagerly with each question. Mi-sun turns her head away from the phone after each answer. The phone stays in Chang-su's wing the whole time; it never floats or moves on its own.
Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes. Neither penguin has eyebrows (NO eyebrows); their eyes stay the same simple round glossy black eyes and the same size as in the first frame.
Wings keep their normal short rounded length and never stretch. Heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 6줄 빠른 주고받기, 창수는 폰을 점점 들이밀고 미순은 매번 고개를 돌림. 편집에서 탈락 도장.
**위험·대책**: 짧은 대사가 빨라 부리 교대가 섞임 → qa 상관 + 시트로 확인. 섞여도 도장·자막이 가려 줌.

## S5 창수 녹아내림 — 입모양(창수) · Kling 4.0 omni, 5초 · 45크레딧
**입력**: image_1 `outputs/ep09/05/start_v1.png`(K5), audio_1 `outputs/ep09/voice/scenes/s5.mp3`
**인자**: S1과 같음
```
One single continuous shot with a static, locked-off camera, no cuts, no camera movement: exactly the scene of 图片1 (same camera angle, same sofa, same plush penguin in the same place and the same grey T-shirt). 3D animated plush character, short velvet fur; the sofa and the objects stay photoreal and unchanged.
The audio 音频1 has two lines in Korean, and nothing else:
1. Chang-su (the penguin in the picture): "그럼… 먹고 싶은 거 딱 하나만 말해봐…"
2. Mi-sun, who is NOT in the picture (an off-screen voice): "나 진짜 아무거나 괜찮다니까?"
During line 1, Chang-su's beak opens and closes exactly in sync with 音频1, tired and slow. During line 2, Chang-su keeps his beak closed, lets out a deep sigh and slowly sinks a little lower against the sofa backrest, his body softly slumping. No other words, no English.
The black smartphone stays lying on the cushion where it is; it never moves. Chang-su's cheeks have NO pink blush at any time. Mi-sun does not appear; Mi-sun has NO eyelashes. Neither penguin has eyebrows (NO eyebrows); his eyes stay the same simple round glossy black eyes and the same size as in the first frame.
Wings keep their normal short rounded length and never stretch. His head keeps its normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 창수가 지친 목소리로 말하고, 화면 밖 미순 대답에 한숨 쉬며 더 축 늘어짐. 편집에서 푸른 필터와 영혼 탈출.
**위험·대책**: 창수가 미순 대사까지 입을 움직임 → 줄마다 누가 말하는지 명시 / 미순이 화면에 생김.

## S6 창수 벌떡 — 입모양 · Kling 4.0 omni, 5초 · 45크레딧
**입력**: image_1 `outputs/ep09/06/start_v1.png`(K6), audio_1 `outputs/ep09/voice/scenes/s6.mp3`
**인자**: S1과 같음
```
One single continuous shot with a static, locked-off camera, no cuts, no camera movement: exactly the scene of 图片1 (same camera angle, same living room, same sofa, same two plush penguins in the same places and the same clothes). 3D animated plush characters, short velvet fur; the room and the objects stay photoreal and unchanged.
The two penguins speak in Korean, using exactly the voices, words and timing of 音频1, and nothing else. They take turns in this exact order:
1. Chang-su (left, darker blue-grey, grey T-shirt): "알았어! 그냥 치킨 시킨다!"
2. Mi-sun (right, light silver-grey, pink hoodie, seen in profile watching TV): "…난 안 먹을 거야."
Only the penguin who is speaking moves the beak, opening and closing exactly in sync with that line in 音频1; the listener keeps the beak closed. No other words, no English.
Right before line 1, Chang-su springs up and stands on the sofa seat with determination, raising one short wing high. Mi-sun keeps looking toward the right edge of the picture at the TV and answers without turning her head. The phone stays lying on the cushion and the TV remote stays in Mi-sun's wing; they never float or move on their own.
Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes. Neither penguin has eyebrows (NO eyebrows); their eyes stay the same simple round glossy black eyes and the same size as in the first frame.
Wings keep their normal short rounded length and never stretch. Heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 창수가 벌떡 소파 위에 서서 날개를 번쩍, 미순은 TV를 보며 딴청. 편집에서 집중선과 펀치.
**위험·대책**: 일어설 때 몸이 늘어남 → "Heads keep their normal shape" / 미순이 돌아봄.

## S7 현관 — 목소리만 · Kling 3.0, 4초 · 24크레딧
**입력**: first_image `outputs/ep09/07/start_v1.png`(K7)
**인자**: model=kling-video-v3_0, duration=4, 720p, prefer_multi_shots=false, enable_audio=false
```
Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the entrance, the door and the objects stay photoreal and completely unchanged.
Pang Chang-su (darker blue-grey, small tuft, grey T-shirt) stands facing the camera holding the closed brown takeout box up in front of his chest with both short wings, bouncing happily on the spot and swaying from side to side with a big happy smile. The box stays in his wings the whole time and moves only together with his wings; it never floats and never opens. Exactly ONE box.
Chang-su's cheeks have NO pink blush at any time. Mi-sun does not appear; Mi-sun has NO eyelashes. Neither penguin has eyebrows (NO eyebrows); his eyes stay the same simple round glossy black eyes and the same size as in the first frame.
Wings keep their normal short rounded length and never stretch. His head keeps its normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 상자를 들고 신나서 들썩들썩. 대사 "왔다 왔다~!"는 편집에서 넣고, 딩동·반짝도 편집.
**위험·대책**: 상자가 열림·떠다님.

## S8 식탁 — 입모양 · Kling 4.0 omni, 6초 · 54크레딧
**입력**: image_1 `outputs/ep09/08/start_v1.png`(K8), audio_1 `outputs/ep09/voice/scenes/s8.mp3`
**인자**: S1과 같음, duration=6
```
One single continuous shot with a static, locked-off camera, no cuts, no camera movement: exactly the scene of 图片1 (same camera angle, same dining table, same two plush penguins in the same places and the same clothes). 3D animated plush characters, short velvet fur; the kitchen, the table, the box and the food stay photoreal and unchanged.
The two penguins speak in Korean, using exactly the voices, words and timing of 音频1, and nothing else. They take turns in this exact order:
1. Mi-sun (left, light silver-grey, pink hoodie, a drumstick in each wing): "하나만 먹어볼까?"
2. Chang-su (right, darker blue-grey, grey T-shirt): "안 먹는다며…?"
3. Mi-sun: "오늘까지만 먹을 거야!"
Only the penguin who is speaking moves the beak, opening and closing exactly in sync with that line in 音频1; the listener keeps the beak closed. No other words, no English.
Mi-sun looks at the drumsticks happily and lifts one a little toward her beak; after line 3 she takes a happy bite. Chang-su stares at her drumsticks with drooping shoulders. Mi-sun keeps holding exactly one drumstick in each wing the whole time; the drumsticks move only together with her wings and never float. The open box with the fried chicken stays on the table where it is and never moves.
Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes. Neither penguin has eyebrows (NO eyebrows); their eyes stay the same simple round glossy black eyes and the same size as in the first frame.
Wings keep their normal short rounded length and never stretch. Heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 미순 "하나만 먹어볼까?" → 창수 "안 먹는다며…?" → 미순 "오늘까지만!" 하고 한 입. 편집에서 흑백 회상(6장면).
**위험·대책**: 닭다리가 3개 이상 되거나 떨어짐 / 한 입 물 때 부리가 닭다리를 삼킴 → 시트로 확인.

## S9 식탁 엔딩 — 입모양(미순) · Kling 4.0 omni, 5초 · 45크레딧
**입력**: image_1 `outputs/ep09/09/start_v1.png`(K9), audio_1 `outputs/ep09/voice/scenes/s9.mp3`
**인자**: S1과 같음
```
One single continuous shot with a static, locked-off camera, no cuts, no camera movement: exactly the scene of 图片1 (same camera angle, same dining table, same two plush penguins in the same places and the same clothes). 3D animated plush characters, short velvet fur; the kitchen, the table and the box stay photoreal and unchanged.
Mi-sun (left, light silver-grey, pink hoodie) speaks in Korean, exactly the voice, words and timing of 音频1, and nothing else:
1. "여보, 내일 저녁은 뭐 먹을래?"
Her beak opens and closes exactly in sync with 音频1. No other words, no English.
Mi-sun leans forward toward Chang-su with a bright, satisfied smile while asking. Chang-su (right, darker blue-grey, grey T-shirt) stays completely frozen and still the whole time, beak closed, the sweat drop beside his head. The empty box with the bones stays on the table where it is and never moves.
Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes. Neither penguin has eyebrows (NO eyebrows); their eyes stay the same simple round glossy black eyes and the same size as in the first frame.
Wings keep their normal short rounded length and never stretch. Heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 미순이 몸을 기울여 밝게 질문, 창수는 얼음. 편집에서 2.0s 정지 화면, 창수 쪽 줌인, 둥.
**위험·대책**: 창수도 입을 움직임 → "frozen, beak closed".

## 합계
- 입모양(4.0, 초당 9): S1 45 + S2 45 + S3 54 + S5 45 + S6 45 + S8 54 + S9 45 = 333
- 목소리만(3.0, 초당 6): S7 24
- **합계 약 357크레딧** (상한 400)
- 제출 순서(2개씩, 받으면 바로 검사): S1·S2 → S3·S5 → S6·S8 → S9·S7.

## 현황
- 2026-10-21 작성. `lint_prompts` 통과, `preflight_kling` 통과(일부러 옛 대사·없는 파일로 시험해 실패를 잡는 것 확인). Kling 잔액 2,749. 승인 대기.
