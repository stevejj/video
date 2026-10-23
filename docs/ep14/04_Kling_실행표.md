# ep14 Kling 실행표 — 인형뽑기 (2026-10-23)

> 잔여 **2,374크레딧**. 예상 **308크레딧**, 상한 **380**(재시도 1회분 일부). 720p 고정.
> - Kling 4.0 omni(입모양)는 **초당 과금**(초당 10). 3.0(움직임만)은 초당 6.
> - 입모양 장면 소리(audio_1)는 5초 이상이어야 해서 대사 앞뒤를 무음으로 채운 장면 소리 파일을 씀(`outputs/ep14/voice/scenes/`).
> - 관문: `lint_prompts.py` 통과 → 승인 → **C2(입모양, 가장 많이 쓰는 K4 화면)부터 먼저 1개 시험** → 합격하면 나머지 2개씩. 2회 연속 실패 시 중단.
> - 클립마다 `qa_clip.py`(입모양은 `--voice-ref`).
> - 옷: 미순 연분홍 후드, 창수 회색 후드(끝까지).

## 클립 목록
| C | 기획 # | 시작 이미지 | 모델 | 초 | 크레딧 | 다시 쓰는 곳 |
|---|---|---|---|---|---|---|
| C1 | 0·0b 거리 "우리 딱 5천 원어치만 할까?" | K1 | 4.0 omni 입모양 | 5 | 50 | — |
| C2 | 2 "저 오리.... 오늘 데려간다..." | K4 | 4.0 omni 입모양 | 5 | 50 | — |
| C3 | 3·5·9·12 집게: 내려가 잡고 → 들어 올림 → 놓침 | K5a → 끝 K5c | 3.0 시작+끝 | 5 | 30 | 몽타주 전부(빠르게·좌우 반전), 12번 성공은 앞 절반(잡고 올림)만 |
| C4 | 4·6·11 "나는.... 실패하지.... 않습니다." | K4 | 4.0 omni 입모양 | 5 | 50 | 같은 녹음이라 **1클립을 3번**(확대 정도만 바꿈) |
| C5 | 7 창수 "미순아... 그만해..." | K4 | 4.0 omni 입모양 | 5 | 50 | — |
| C6 | 8·10 쉿 | K7a → 끝 K7b | 3.0 시작+끝 | 3 | 18 | **2번**(10번은 더 빨리 끊음) |
| C7 | 13·15 오리 안고 정적 → "나는.... 실패하지.... 않습니다." | K8 | 4.0 omni 입모양 | 6 | 60 | 13번은 앞 무음 구간 |
| | 거리·기계 전체(#1)·휴대폰 알림(#14) | K3 정지 + 편집 | — | — | 0 | |
| | 합계 | | | | **308** | |

---

## C2 기계 안 시점: 미순 "저 오리.... 오늘 데려간다..." — 입모양 · Kling 4.0 omni, 5초 · 50크레딧 (먼저 시험)
**입력**: image_1 `outputs/ep14/img/K4_v1.png`, audio_1 `outputs/ep14/voice/scenes/c2.mp3`
**인자**: model=kling-video-v4_0(omni_ref_video), duration=5, aspect_ratio=9:16, 720p, prefer_multi_shots=true, enable_audio=true
```
One single continuous shot with a static, locked-off camera, no cuts, no camera movement: exactly the scene of 图片1 (same camera angle from inside the claw machine looking out through the glass, same arcade, same ducklings in the foreground, same characters in the same places and the same clothes). 3D animated plush characters, short velvet fur; the arcade, the glass and the plush ducklings stay photoreal and unchanged.
Pang Mi-sun (center, light silver-grey, pink blush, light pink hoodie) stares into the machine at the ducklings, slowly narrowing her eyes a little with quiet determination. She speaks in Korean, quietly and slowly, exactly the voice, words and timing of 音频1, and nothing else:
1. "저 오리.... 오늘 데려간다..."
Her beak opens and closes only very slightly, exactly in sync with 音频1. No other words, no English.
Pang Chang-su (left, darker blue-grey, small tuft, grey hoodie) stands still beside her looking at the machine, beak closed the whole time.
The ducklings in the foreground never move. Both penguins keep their wings still at their sides and never touch the glass.
Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes. Neither penguin has eyebrows (NO eyebrows); their eyes stay the same simple round glossy black eyes and the same size as in the first frame.
Wings keep their normal short rounded length and never stretch. Heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 0.3~2.6s 대사, 나머지는 응시.
**위험·대책**: 유리 반사가 얼굴을 가림 / 오리가 움직임 / 창수가 따라 말함 → "창수 부리 닫힘" 명시.

## C1 밤거리: 미순 "우리 딱 5천 원어치만 할까?" — 입모양 · Kling 4.0 omni, 5초 · 50크레딧
**입력**: image_1 `outputs/ep14/img/K1_v1.png`, audio_1 `outputs/ep14/voice/scenes/c1.mp3`
**인자**: C2와 같음
```
One single continuous shot with a static, locked-off camera, no cuts, no camera movement: exactly the scene of 图片1 (same camera angle, same night street, same glowing claw-machine shop, same characters in the same places and the same clothes). 3D animated plush characters, short velvet fur; the street, the shop and the fallen leaves stay photoreal and unchanged.
Pang Mi-sun (right, light silver-grey, pink blush, light pink hoodie) looks at the shop window, then turns her head toward Chang-su with a bright, excited face. She speaks in Korean, playfully, exactly the voice, words and timing of 音频1, and nothing else:
1. "우리 딱 5천 원어치만 할까?"
Her beak opens and closes only very slightly, exactly in sync with 音频1. No other words, no English.
Pang Chang-su (left, darker blue-grey, small tuft, grey hoodie) turns his head toward her and listens, beak closed the whole time.
Both penguins stay standing in place; they do not walk. Mi-sun's head fur stays light silver-grey, never pink.
Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes. Neither penguin has eyebrows (NO eyebrows); their eyes stay the same simple round glossy black eyes and the same size as in the first frame.
Wings keep their normal short rounded length and never stretch. Heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 0~1s 가게 봄 → 고개 돌림 → 1.2~2.9s 대사.
**위험·대책**: 걸어감(R: 걷기 금지 명시) / 미순 머리가 분홍으로(K2 실패) → 색 명시.

## C3 집게: 내려가 잡고 → 들어 올림 → 놓침 — 움직임 · Kling 3.0, 5초 · 30크레딧
**입력**: first_image `outputs/ep14/img/K5a_v1.png`, tail_image `outputs/ep14/img/K5c_v1.png`
**인자**: model=kling-video-v3_0, duration=5, 720p, prefer_multi_shots=false, enable_audio=false
```
Static camera, locked-off tripod shot, no camera movement, same composition throughout. Inside a claw crane machine.
The open silver three-pronged claw slowly lowers on its thin cable onto the pile of identical yellow plush ducklings, closes its prongs around exactly ONE duckling, and lifts it up about 20 cm. Then the duckling slips out between the prongs and drops back softly onto the pile, while the claw, now open again, hangs empty above it.
The duckling moves only after the closed prongs touch it, and only together with the claw; it never floats on its own. The cable stays straight and attached to the claw. The other ducklings stay still. Exactly one claw. No penguins, no people, no hands appear. No other characters appear. No new objects appear.
```
**예상**: 0~1.5s 내려감 → 1.5~2.5s 잡음 → 2.5~3.5s 올림 → 3.5~4.5s 툭 떨어짐.
**위험·대책**: 집게가 오리를 통과함 / 오리가 여러 마리 딸려 옴 → 실패해도 몽타주는 정지 이미지(K5a·K5b·K5c) 빠른 컷 + 효과음으로 대체(0원).

## C4 기계 안 시점: 미순 "나는.... 실패하지.... 않습니다." — 입모양 · Kling 4.0 omni, 5초 · 50크레딧
**입력**: image_1 `outputs/ep14/img/K4_v1.png`, audio_1 `outputs/ep14/voice/scenes/c4.mp3`
**인자**: C2와 같음
```
One single continuous shot with a static, locked-off camera, no cuts, no camera movement: exactly the scene of 图片1 (same camera angle from inside the claw machine looking out through the glass, same arcade, same ducklings in the foreground, same characters in the same places and the same clothes). 3D animated plush characters, short velvet fur; the arcade, the glass and the plush ducklings stay photoreal and unchanged.
Pang Mi-sun (center, light silver-grey, pink blush, light pink hoodie) keeps staring straight into the machine with a calm, serious face, completely still except her beak. She speaks in Korean, slowly and solemnly with long pauses, exactly the voice, words and timing of 音频1, and nothing else:
1. "나는.... 실패하지.... 않습니다."
Her beak opens and closes only very slightly, exactly in sync with 音频1, and stays closed during the pauses. No other words, no English.
Pang Chang-su (left, darker blue-grey, small tuft, grey hoodie) stands still beside her, glancing at her, beak closed the whole time.
The ducklings in the foreground never move. Both penguins keep their wings still at their sides and never touch the glass.
Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes. Neither penguin has eyebrows (NO eyebrows); their eyes stay the same simple round glossy black eyes and the same size as in the first frame.
Wings keep their normal short rounded length and never stretch. Heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 0.3~3.6s 대사(쉼 2번 부리 닫힘), 미순 거의 정지.
**위험·대책**: 쉼 동안 부리가 계속 움직임 → qa `--voice-ref`로 확인.

## C5 기계 안 시점: 창수 "미순아... 그만해..." — 입모양 · Kling 4.0 omni, 5초 · 50크레딧
**입력**: image_1 `outputs/ep14/img/K4_v1.png`, audio_1 `outputs/ep14/voice/scenes/c5.mp3`
**인자**: C2와 같음
```
One single continuous shot with a static, locked-off camera, no cuts, no camera movement: exactly the scene of 图片1 (same camera angle from inside the claw machine looking out through the glass, same arcade, same ducklings in the foreground, same characters in the same places and the same clothes). 3D animated plush characters, short velvet fur; the arcade, the glass and the plush ducklings stay photoreal and unchanged.
Pang Chang-su (left, darker blue-grey, small tuft, grey hoodie) slowly turns his head a little toward Mi-sun with a worried look and pleads with her. He speaks in Korean, softly and slowly, exactly the voice, words and timing of 音频1, and nothing else:
1. "미순아... 그만해..."
His beak opens and closes only very slightly, exactly in sync with 音频1. No other words, no English.
Pang Mi-sun (center, light silver-grey, pink blush, light pink hoodie) does not look at him; she keeps staring into the machine, beak closed the whole time.
The ducklings in the foreground never move. Both penguins keep their wings still at their sides and never touch the glass.
Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes. Neither penguin has eyebrows (NO eyebrows); their eyes stay the same simple round glossy black eyes and the same size as in the first frame.
Wings keep their normal short rounded length and never stretch. Heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 0~0.8s 고개 살짝 돌림 → 0.8~3.1s 대사.
**위험·대책**: 걱정 표정에 눈썹이 생김(K4b 실패) → 눈썹 금지 명시, 받은 클립 얼굴 검사.

## C6 창수 클로즈업: 쉿 — 움직임 · Kling 3.0, 3초 · 18크레딧
**입력**: first_image `outputs/ep14/img/K7a_v1.png`, tail_image `outputs/ep14/img/K7b_v2.png`
**인자**: model=kling-video-v3_0, duration=3, 720p, prefer_multi_shots=false, enable_audio=false
```
Static camera, locked-off tripod shot, no camera movement, same composition throughout. A close-up of Pang Chang-su's face in the arcade, 3D animated plush character with short velvet fur; the background stays photoreal and unchanged.
At the very start his beak opens just slightly as if about to speak. Then, in one quick motion, the narrow rounded tip of a light silver-grey plush flipper wing rises from the bottom edge of the frame and stops pressed lightly against only the CENTER of his beak, like a finger on the lips for "shh". His beak closes and he freezes, eyes a little wider. After the flipper stops, nothing moves.
Both sides of his beak stay visible. The flipper tip never covers his eyes or face, never grows longer, and has no fingers. No other character appears.
Chang-su's cheeks have NO pink blush at any time. He has NO eyebrows; his eyes stay the same simple round glossy black eyes and the same size as in the first frame.
The flipper keeps its normal short length and never stretches. Heads keep their normal shape. No other characters appear. No new objects appear.
```
**예상**: 0~0.4s 부리 살짝 열림 → 0.4~0.8s 날개 끝 탁 → 이후 정지.
**위험·대책**: 날개가 창수 자기 날개처럼 보임 → 미순 은회색 + 화면 밖 목소리로 구분. 실패 시 K7a→K7b 정지 컷 + "탁"(0원).

## C7 오리 안은 미순: 정적 → "나는.... 실패하지.... 않습니다." — 입모양 · Kling 4.0 omni, 6초 · 60크레딧
**입력**: image_1 `outputs/ep14/img/K8_v1.png`, audio_1 `outputs/ep14/voice/scenes/c7.mp3`
**인자**: model=kling-video-v4_0(omni_ref_video), duration=6, aspect_ratio=9:16, 720p, prefer_multi_shots=true, enable_audio=true
```
One single continuous shot with a static, locked-off camera, no cuts, no camera movement: exactly the scene of 图片1 (same camera angle, same arcade, same claw machine behind her, same character in the same place and the same clothes). 3D animated plush character, short velvet fur; the arcade and the plush duckling stay photoreal and unchanged.
Pang Mi-sun (light silver-grey, pink blush, light pink hoodie) stands facing the camera hugging exactly ONE yellow plush duckling to her chest between both short wings. For the first two seconds she stays still and proud, beak closed. Then she speaks in Korean, slowly and solemnly with long pauses, exactly the voice, words and timing of 音频1, and nothing else:
1. "나는.... 실패하지.... 않습니다."
Her beak opens and closes only very slightly, exactly in sync with 音频1, and stays closed during the pauses. No other words, no English.
The duckling stays in her wings the whole time and never moves on its own. Exactly one duckling.
Mi-sun has NO eyelashes and NO eyebrows; her eyes stay the same simple round glossy black eyes and the same size as in the first frame.
Wings keep their normal short rounded length and never stretch. Heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 0~2s 정적(13번) → 2.0~5.3s 대사(15번).
**위험·대책**: 오리 인형이 움직이거나 말함 → "never moves on its own" / 오리가 2마리로.

## 실행 기록
- **C2 v1** (2026-10-23, 실제 **45크레딧** = 초당 9, 잔여 2,329): `outputs/ep14/clips/C2_v1.mp4`.
  - qa_clip: 소리 = 우리 녹음(상관 0.99) ✓ / "창수 볼터치 의심"은 프레임 확인 결과 분홍 LED 조명(볼터치 없음, 오탐) / "멈춘 프레임"은 끝부분 정지 응시(의도).
  - 눈으로 본 것: 미순이 "눈을 가늘게"를 한쪽 눈을 더 감는 윙크처럼 함, 대사 중 부리가 한 번 크게 벌어짐(1~2s). 창수 털뭉치·무 볼터치·눈썹 없음 ✓, 오리 안 움직임 ✓.
  - 사용자 판단 대기(통과 → 나머지 진행 / 재시도 1회: "narrowing her eyes" 빼고 부리 더 작게).
- **C2 눈 고침(0원, 2026-10-23, 사용자: "눈은 Kling 안 쓰고 무료로 수정 가능하지 않아?")**: `tools/eye_patch.py` — 첫 프레임의 미순 눈 둘레(타원 38x34px)를 머리 따라가기(템플릿 매칭)로 매 프레임 붙임 → 윙크 사라지고 눈 크기 그대로. `outputs/ep14/clips/C2_v1_eyefix.mp4` (깜빡임도 사라짐). 부리 크게 벌어짐(1~2s)은 그대로.
- 이후 입모양 클립(C1·C4·C5·C7): 눈 모양을 바꾸는 표현("narrowing her eyes" 등) 쓰지 않음, 부리 "only very slightly" 유지. 눈이 바뀌면 eye_patch로 0원 수정.
- **C1 v1**(45) 통과: qa 볼터치·멈춤 ✓, 소리 상관 0.98. 미순이 가게 보다가 창수 쪽으로 돌아 웃으며 말함, 머리색 은회색 유지, 걷지 않음.
- **C3 v1**(30) 통과: 집게 내려가 잡고 → 들어 올림 → 오리가 더미 위로 떨어짐. qa "볼터치 의심"은 노란 오리(캐릭터 없음, 오탐).
