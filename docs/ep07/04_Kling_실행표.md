# ep07 Kling 실행표 — 포장마차 (애니매틱 확인 후)

> 상한 **230크레딧**, 잔액 459. 공통 규칙(08 F10 관문 G2 통과 필수):
> - 고정 카메라, 한 컷.
> - 미순 속눈썹 없음, 창수 볼터치 없음.
> - 날개 늘이기 금지, 새 물체 금지.
> - 맥주잔은 정확히 2개이고 날개에 들려 있음(떠다니면 실패).
> - 2회 연속 실패 시 중단(F5).
> - **입모양 방식**: Kling 4.0 `omni_ref_video`에 우리 녹음을 `audio_1`로 넣음. **초 단위 과금 10크레딧/초.**
> - **S5를 먼저 시험** → 부리가 대사에 맞으면 S1, 안 맞으면 멈추고 방법 재검토.

## [기록] S5 시험 — 미순 "이모! 맥주 한잔 더요!" + 둘 웃음 · Kling 4.0, 5초 · 50크레딧
**입력**: image_1 `outputs/ep07/w1/start_v1.png`(W1), audio_1 `outputs/ep07/voice/s5_track.mp3`(0.3s 이모!·1.9s 웃음, 5.0s)
**인자**: model=kling-video-v4_0, duration=5, aspect_ratio=9:16, resolution=720p, prefer_multi_shots=true(이 모델은 끌 수 없음), enable_audio=true, keepOriginalSound=false, imageCount=1
```
One single continuous shot with a static, locked-off camera, no cuts, no camera movement: exactly the scene of 图片1 (same camera angle, same pojangmacha tent, same food pan, same two plush penguins in the same places, same two glass beer mugs). 3D animated plush characters, short velvet fur; the tent, the food and the mugs stay photoreal and unchanged.
The light silver-grey penguin on the left with pink blush (Pang Mi-sun) raises one short wing high toward the right side as if calling the owner, and shouts the line in 音频1, "이모! 맥주 한잔 더요!", her beak opening and closing exactly in sync with the speech in 音频1. Then both penguins laugh together, beaks open in laughter, matching the laughter in 音频1, bodies shaking a little.
The darker blue-grey penguin on the right (Pang Chang-su) only laughs. Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes.
Both beer mugs stay on the counter in front of them, exactly two mugs, they never float or move on their own. Wings keep their normal short rounded length and never stretch. Both heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**합격 기준**: 부리 여닫기가 "이모!/맥주/한잔/더요" 음절과 맞음, 웃음 구간에 둘 다 웃음, 컷 분할 없음, W1 구도 유지.
**위험**: 4.0이 여러 컷으로 나눔 / 구도가 W1과 달라짐 / 오디오 참조를 무시함 → 그때는 S1(100) 진행 금지.

## [기록] S1 v1 대화(실패: 영어 대사) — L1~L6 · Kling 4.0, 10초 · 100크레딧 (S5 합격 후)
**입력**: image_1 W1, audio_1 `outputs/ep07/voice/s1_track.mp3`(9.6s 대화 + 무음, 10.0s)
```
One single continuous shot with a static, locked-off camera, no cuts, no camera movement: exactly the scene of 图片1 (same camera angle, same pojangmacha tent, same food pan, same two plush penguins in the same places, same two glass beer mugs). 3D animated plush characters, short velvet fur; the tent, the food and the mugs stay photoreal and unchanged.
The two penguins have a serious late-night talk about life, taking turns exactly as in 音频1: the light silver-grey penguin on the left with pink blush (Pang Mi-sun) speaks the higher voice lines, and the darker blue-grey penguin on the right (Pang Chang-su) speaks the other lines. Only the one who is speaking moves the beak, opening and closing exactly in sync with the speech in 音频1; the listener keeps the beak closed and nods or turns the head toward the speaker. They hold their beer mugs on the counter with both wings.
Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes.
Exactly two beer mugs; they stay in the penguins' wings or on the counter and never float or move on their own. Wings keep their normal short rounded length and never stretch. Both heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```

## S2 짠 + 원샷 — 와이드 · Kling 3.0, 5초 · 30크레딧 (C1 실패 → 와이드에서 짠, 사용자 선택에 따라)
**입력**: first_image W1
```
Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the tent, the food and the mugs stay photoreal and unchanged.
Pang Mi-sun (left, light silver-grey, pink blush, NO eyelashes) and Pang Chang-su (right, darker blue-grey, NO pink blush; only Mi-sun has pink blush) lift their glass beer mugs with both wings, clink the two mugs together once in the middle, then both tilt their heads back and drink the whole beer in one go, the beer level going down until the mugs are empty, then they put the empty mugs down on the counter.
The mugs move only together with the wings that hold them; they never float on their own. Exactly two mugs. Wings keep their normal short rounded length and never stretch. Both heads keep their normal shape. Beaks closed except touching the mug rims. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```

## S4 캬~ — C2 · Kling 3.0, 3초 · 18크레딧
**입력**: first_image `outputs/ep07/c2/start_v1.png`(C2)
```
Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the tent and the mugs stay photoreal and unchanged.
Right after finishing their beer, Pang Mi-sun (left, light silver-grey, pink blush, NO eyelashes) and Pang Chang-su (right, darker blue-grey, NO pink blush; only Mi-sun has pink blush), both with eyes closed, open their beaks wide together in a deeply satisfied "kya~" sigh, shake their heads a little with pleasure, then smile with eyes still closed in happy curves.
Exactly two empty mugs held in their wings; they never float. Wings keep their normal short rounded length and never stretch. Both heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```

## 합계: S5 50 + S1 100 + S2 30 + S4 18 = **198크레딧**

## 현황
- 2026-10-19 작성. 사용자: 애니매틱 이해됨, 짠은 A안(와이드에서 짠+원샷, C1 안 씀), S5 시험 "진행".
- S5 제출(50크레딧, 잔액 459 → 409). `outputs/ep07/s5/meta.json`.
- **S5 ✅ 입모양 시험 합격 (2026-10-19)**: 50크레딧.
  - Kling 결과 음성 = 우리 녹음(소리 크기 변화 상관 0.97, 어긋남 10ms).
  - 부리가 음절마다 여닫힘. 0.5~2.2s 미순 날개 번쩍 + "이모! 맥주 한잔 더요!", 2.3~5s 둘이 웃음.
  - 컷 분할 없음, 창수 볼터치 없음(qa_clip 통과), 맥주잔 2개.
  - 메모: 화면이 W1보다 조금 당겨짐(철판이 덜 보임).
- S1(100)·S2(30)·S4(18) 동시 제출. 잔액 409 → 261. ep07 합계 198 = 예상대로.

## S1 v2 대화 — 대사 원문·한국어 명시 · Kling 4.0, 10초 · 100크레딧 (승인 대기)
**입력**: image_1 W1, audio_1 `outputs/ep07/voice/s1_track.mp3`(같은 녹음)
**인자**: v1과 같음(kling-video-v4_0, 10s, 9:16, 720p, prefer_multi_shots=true, enable_audio=true)
```
One single continuous shot with a static, locked-off camera, no cuts, no camera movement: exactly the scene of 图片1 (same camera angle, same pojangmacha tent, same food pan, same two plush penguins in the same places, same two glass beer mugs). 3D animated plush characters, short velvet fur; the tent, the food and the mugs stay photoreal and unchanged.
The two penguins speak in Korean, using exactly the voices, words and timing of 音频1, and nothing else. They take turns in this exact order:
1. Mi-sun (left, light silver-grey, pink blush): "야, 인생 뭐 있냐."
2. Chang-su (right, darker blue-grey): "먹고 자고 싸는 거지 뭐."
3. Mi-sun: "중간중간 울어주고."
4. Chang-su: "그게 정답이지."
5. Mi-sun: "마지막 한 잔!"
6. Chang-su: "콜!"
Only the penguin who is speaking moves the beak, opening and closing exactly in sync with that line in 音频1; the listener keeps the beak closed and nods or turns the head toward the speaker. No other words, no English, no extra lines. They hold their beer mugs on the counter with both wings.
Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes.
Exactly two beer mugs; they stay in the penguins' wings or on the counter and never float or move on their own. Wings keep their normal short rounded length and never stretch. Both heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**합격 기준**: `qa_clip.py --voice-ref outputs/ep07/voice/s1_track.mp3` 상관 0.8 이상(클립 소리 = 우리 녹음) + 말하는 쪽 부리만 움직임 + 한 컷.
- **S1 v1 ❌ (2026-10-19)**: 100크레딧. Kling이 우리 녹음을 무시하고 **영어 대사를 지어냄**.
  - 지어낸 대사: "Life is just a series of late-night snacks…" / "Yeah, but the bill always comes eventually."
  - 부리는 그 영어에 맞춰 움직임. 녹음과의 상관 0.15.
  - 원인: S5는 프롬프트에 대사 원문을 적었고, S1은 "음성대로"만 적음.
  - 대책(F10에 추가): `lint_prompts.py`는 음성 참조가 있으면 따옴표 속 한국어 대사와 "in Korean"을 필수로 검사. `qa_clip.py --voice-ref`는 클립 소리와 녹음의 상관 0.8 미만이면 실패.
- **S2 ✅**: 30크레딧. 1.0~1.5s 날개로 잔 들고 짠 → 2.0~4.2s 쭉 원샷 → 4.8s 빈 잔 내려놓음. 잔 2개, 떠다님 없음, 볼터치 검사 통과.
- **S4 ✅**: 18크레딧. 1.0~2.0s 둘이 눈 감고 부리 크게 벌려 "캬~", 이후 미소. 창수 볼터치 0px.
- 잔액 **261**. S1 v2(100) 승인 대기. F5: S1 실패 1회째.

## S5 v2 — 빈 잔으로 "이모! 맥주 한잔 더요!" · Kling 4.0, 5초 · 50크레딧 (승인 대기)
**입력**: image_1 `outputs/ep07/w2/start_v1.png`(W2: W1 + 빈 잔), audio_1 `outputs/ep07/voice/s5_track.mp3`(같은 녹음)
**인자**: S5와 같음
```
One single continuous shot with a static, locked-off camera, no cuts, no camera movement: exactly the scene of 图片1 (same camera angle, same pojangmacha tent, same food pan, same two plush penguins in the same places, same two EMPTY glass beer mugs). 3D animated plush characters, short velvet fur; the tent, the food and the mugs stay photoreal and unchanged.
They have just finished their beer: both mugs are EMPTY the whole time, only a thin trace of foam inside, no beer is added.
The light silver-grey penguin on the left with pink blush (Pang Mi-sun) raises one short wing high toward the right side as if calling the owner, and shouts in Korean exactly the line in 音频1, "이모! 맥주 한잔 더요!", her beak opening and closing exactly in sync with the speech in 音频1. Then both penguins laugh together, beaks open in laughter, matching the laughter in 音频1, bodies shaking a little. No other words, no English.
The darker blue-grey penguin on the right (Pang Chang-su) only laughs. Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes.
Both empty mugs stay on the counter in front of them, exactly two mugs, they never float or move on their own. Wings keep their normal short rounded length and never stretch. Both heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**합격 기준**: 잔이 끝까지 빈 상태, `qa_clip.py --voice-ref outputs/ep07/voice/s5_track.mp3` 상관 0.8 이상, 한 컷, `check_props.py` 상태 이어짐 통과.

- **완성본 v1 ❌ 보내기 전 발견 (2026-10-19)**: 원샷으로 비운 잔이 S5(이모!)에서 다시 가득 참.
  - 원인: S5를 가득 찬 잔 W1에서 만듦. 소품 검사가 상태(가득/빈)를 보지 않았고, 전체 화면에선 주황 천막 때문에 색 검사도 무력했음.
  - 대책: `check_props.py`에 **상태 이어짐 검사(states)** 추가. v1을 실제로 실패로 잡는 것을 확인함.
  - 고치기: W2(빈 잔, Flash 125원) → S5 v2(50크레딧). 승인 대기.
