# ep08 Kling 실행표 — 남자 여자 준비시간 (애니매틱 확인 + 충전 후 실행)

> 상한 **420크레딧**(예상 378 + 재시도 1회분). 08 F10 관문:
> - G2: `lint_prompts.py` 통과 후 승인 요청.
> - G3: 클립마다 `qa_clip.py`(입모양 장면은 `--voice-ref`).
> - G4: 완성본 상태 이어짐 검사.
> - 입모양 장면은 **S6(5초, 가장 짧은 대사 클로즈업)으로 먼저 시험** → 합격하면 나머지 진행. 2회 연속 실패 시 중단(F5).
> - 옷 상태(states): 미순 원피스(S1~S3) → 트위드(S4·S6·S9), 창수 잠옷(S1·S2·S5) → 거품(S7) → 정장(S8). 각 장면 시작 이미지가 그 상태와 맞는지 이미지 단계에서 확인함.

## S1 침실 기상 — 입모양 · Kling 4.0 omni, 6초 · 60크레딧
**입력**: image_1 `outputs/ep08/01/start_v1.png`(K1), audio_1 `outputs/ep08/voice/scenes/s1.mp3`
**인자**: model=kling-video-v4_0(omni_ref_video), duration=6, aspect_ratio=9:16, 720p, prefer_multi_shots=true, enable_audio=true
```
One single continuous shot with a static, locked-off camera, no cuts, no camera movement: exactly the scene of 图片1 (same camera angle, same room, same furniture, same characters in the same places and the same clothes). 3D animated plush characters, short velvet fur; the room and the objects stay photoreal and unchanged.
Pang Mi-sun (left, light silver-grey, pink blush, light pink dress) sits on the bed. She glances at the alarm clock on the nightstand, startles, then turns toward the sleeping Chang-su and pats the yellow duvet right beside her with one short wing, urging him to wake up. She speaks in Korean, exactly the voice, words and timing of 音频1, and nothing else:
1. "어? 지금 몇 시야?"
2. "여보, 빨리 일어나!"
3. "준비 시간 한 시간밖에 안 남았어!"
Her beak opens and closes exactly in sync with 音频1. No other words, no English.
Pang Chang-su (right, darker blue-grey, blue checked pajama) stays lying on his back fast asleep the whole time: eyes closed, beak closed, he does not move his wings and does not get up. The duvet covers only Chang-su up to his chest.
The alarm clock stays on the nightstand and never moves. Mi-sun's wing only pats the duvet next to her; it never reaches across to him and never stretches.
Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes. Neither penguin has eyebrows (NO eyebrows); their eyes stay the same simple round glossy black eyes and the same size as in the first frame.
Wings keep their normal short rounded length and never stretch. Heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 0~1s 시계 보고 놀람 → 1~5.5s 창수 쪽으로 돌아 이불 탁탁 + 대사 3줄, 창수는 계속 잠.
**위험·대책**: 미순 날개가 창수까지 늘어남(ep03) → "이불만 두드림" 명시 / 창수가 일어남 / 이불이 둘을 덮음(M14).

## S2 화장대 드라이기 — 목소리만 · Kling 3.0, 5초 · 30크레딧
**입력**: first_image `outputs/ep08/02/start_v1.png`(K2)
**인자**: model=kling-video-v3_0, duration=5, 720p, prefer_multi_shots=false, enable_audio=false
```
Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the room, the furniture and the objects stay photoreal and completely unchanged.
Pang Mi-sun (light silver-grey plush penguin in a light pink dress) sits at the dressing table seen from BEHIND the whole time and never turns to the camera. She dries the top of her head with the white hair dryer held in one short wing, moving it slowly from side to side; the dryer stays in her wing the whole time.
In the background on the bed, Pang Chang-su (darker blue-grey, blue checked pajama) stays lying perfectly still with eyes closed, pretending to sleep, the black smartphone resting in his wing; he does not move.
Exactly one hair dryer and one phone; they never float or move on their own. Beaks stay closed. Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes. Neither penguin has eyebrows (NO eyebrows); their eyes stay the same simple round glossy black eyes and the same size as in the first frame.
Wings keep their normal short rounded length and never stretch. Heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 드라이기 좌우로, 창수는 가만히.
**위험·대책**: 미순이 돌아봄 / 창수가 움직여 머리가 굴러감(M17: 누워서 날개 금지 → 폰은 그대로 둠).

## S3 드레스룸 — 입모양 · Kling 4.0 omni, 5초 · 50크레딧
**입력**: image_1 `outputs/ep08/03/start_v2.png`(K3f, 눈썹 제거), audio_1 `outputs/ep08/voice/scenes/s3.mp3`
**인자**: model=kling-video-v4_0(omni_ref_video), duration=5, aspect_ratio=9:16, 720p, prefer_multi_shots=true, enable_audio=true
```
One single continuous shot with a static, locked-off camera, no cuts, no camera movement: exactly the scene of 图片1 (same camera angle, same room, same furniture, same characters in the same places and the same clothes). 3D animated plush characters, short velvet fur; the room and the objects stay photoreal and unchanged.
Pang Mi-sun (light silver-grey, pink blush, light pink dress) stands in front of the packed clothes rail holding the wooden hanger with the light blue dress in one short wing. She looks down at the dress, tilts her head, then sighs. She speaks in Korean, exactly the voice, words and timing of 音频1, and nothing else:
1. "여보, 나 오늘 뭐 입을까?"
2. "입을 옷이 진짜 너무 없네..."
Her beak opens and closes exactly in sync with 音频1. No other words, no English.
The hanger and the blue dress stay in her wing the whole time; the clothes on the rail never move. Exactly one hanger in her wing.
Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes. Neither penguin has eyebrows (NO eyebrows); their eyes stay the same simple round glossy black eyes and the same size as in the first frame.
Wings keep their normal short rounded length and never stretch. Heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 원피스 보며 갸웃 → 대사 2줄 → 한숨.
**위험·대책**: 옷걸이가 떠다님 / 행거 옷이 바뀜 / 입모양이 녹음과 다름(qa --voice-ref).

## S4 가방 진열장 — 목소리만 · Kling 3.0, 5초 · 30크레딧
**입력**: first_image `outputs/ep08/04/start_v2.png`(K4, 눈썹·속눈썹 사진 편집 제거)
**인자**: S2와 같음
```
Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the room, the furniture and the objects stay photoreal and completely unchanged.
Pang Mi-sun (light silver-grey, beige tweed two-piece suit, small pearl hairpin) stands in front of the lit bag shelf, seen from behind at a three-quarter angle the whole time; she does not turn to the camera. She points with one short wing at one bag after another, tilting her head left and right, unable to decide.
All the bags stay exactly in their places on the shelf; none of them moves or floats. Her beak stays closed. Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes. Neither penguin has eyebrows (NO eyebrows); their eyes stay the same simple round glossy black eyes and the same size as in the first frame.
Wings keep their normal short rounded length and never stretch. Heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 가방을 하나씩 가리키며 갸웃갸웃.
**위험·대책**: 가방이 움직임·떨어짐 / 미순이 돌아봄.

## S5 복도 — 목소리만 · Kling 3.0, 3초 · 18크레딧
**입력**: first_image `outputs/ep08/05/start_v1.png`(K5)
**인자**: model=kling-video-v3_0, duration=3, 720p, prefer_multi_shots=false, enable_audio=false
```
Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the room, the furniture and the objects stay photoreal and completely unchanged.
Pang Chang-su (darker blue-grey, small tuft, blue checked pajama) is seen from BEHIND the whole time. He waddles lazily down the hallway toward the open bathroom door with small penguin steps, waving one short wing over his shoulder without looking back. He never turns around.
The door stays open and unchanged. Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes. Neither penguin has eyebrows (NO eyebrows); their eyes stay the same simple round glossy black eyes and the same size as in the first frame.
Wings keep their normal short rounded length and never stretch. Heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 욕실 쪽으로 총총, 손 흔듦.
**위험·대책**: 돌아봄 / 얼굴이 생김.

## S6 미순 클로즈업 폭발 — 입모양 · Kling 4.0 omni, 5초 · 50크레딧
**입력**: image_1 `outputs/ep08/06/start_v2.png`(K6 배경 흐림), audio_1 `outputs/ep08/voice/scenes/s6.mp3`(2026-10-20 6c를 "창수야!!!"로 다시 녹음, 원래 녹음은 `s6_pangchangsu.mp3`)
**인자**: S3와 같음
```
One single continuous shot with a static, locked-off camera, no cuts, no camera movement: exactly the scene of 图片1 (same camera angle, same room, same furniture, same characters in the same places and the same clothes). 3D animated plush characters, short velvet fur; the room and the objects stay photoreal and unchanged.
An extreme close-up of Pang Mi-sun's face (light silver-grey, pink blush, beige tweed collar, small pearl hairpin, a small cartoon sweat drop). She calls out twice in disbelief, then explodes in anger, shouting his name, her head shaking a little with rage. She speaks in Korean, exactly the voice, words and timing of 音频1, and nothing else:
1. "여보?"
2. "여보?"
3. "창수야!!!"
Her beak opens and closes exactly in sync with 音频1. No other words, no English.
The sweat drop and the pearl hairpin stay in place. Chang-su does not appear. Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes. Neither penguin has eyebrows (NO eyebrows); their eyes stay the same simple round glossy black eyes and the same size as in the first frame.
Wings keep their normal short rounded length and never stretch. Heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 여보? 여보? (점점 굳는 얼굴) → 창수야!!! 머리 흔들며 폭발.
**위험·대책**: 얼굴 형태 무너짐(클로즈업) / 입모양 불일치.

## S7 샤워 — 목소리만 · Kling 3.0, 5초 · 30크레딧
**입력**: first_image `outputs/ep08/07/start_v1.png`(K7)
**인자**: S2와 같음
```
Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the room, the furniture and the objects stay photoreal and completely unchanged.
Pang Chang-su, a cute plush penguin toy (darker blue-grey with a small tuft), stands in the glass shower booth seen from BEHIND the whole time and never turns around. He happily scrubs the big pile of white soap bubbles on his head with both short wings, swaying a little, while water keeps falling from the rain showerhead. Some bubbles slide down his back. Wholesome, cute, family-friendly.
The glass door and the bathroom stay unchanged. Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes. Neither penguin has eyebrows (NO eyebrows); their eyes stay the same simple round glossy black eyes and the same size as in the first frame.
Wings keep their normal short rounded length and never stretch. Heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 양 날개로 머리 거품 박박, 몸 흔들흔들.
**위험·대책**: 돌아봄 / 거품이 이상하게 늘어남 / 몸 색이 미순처럼 밝아짐.

## S8 거실 정장 — 입모양 · Kling 4.0 omni, 5초 · 50크레딧
**입력**: image_1 `outputs/ep08/08/start_v1.png`(K8), audio_1 `outputs/ep08/voice/scenes/s8.mp3`
**인자**: S3와 같음
```
One single continuous shot with a static, locked-off camera, no cuts, no camera movement: exactly the scene of 图片1 (same camera angle, same room, same furniture, same characters in the same places and the same clothes). 3D animated plush characters, short velvet fur; the room and the objects stay photoreal and unchanged.
Pang Chang-su (darker blue-grey, small tuft, neat brown suit jacket, white shirt, dark tie) stands in the living room facing the camera, calm and smug, tapping one foot and tilting his head as if waiting. He speaks in Korean, exactly the voice, words and timing of 音频1, and nothing else:
1. "여보, 아직도 멀었어?"
2. "나 준비 다 했는데?"
His beak opens and closes exactly in sync with 音频1. No other words, no English.
His suit, shirt and tie stay exactly the same; he does not touch them. Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes. Neither penguin has eyebrows (NO eyebrows); their eyes stay the same simple round glossy black eyes and the same size as in the first frame.
Wings keep their normal short rounded length and never stretch. Heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 발 까딱·고개 갸웃하며 대사 2줄.
**위험·대책**: 옷이 바뀜 / 입모양 불일치.

## S9 현관 구두 — 입모양 · Kling 4.0 omni, 6초 · 60크레딧
**입력**: image_1 `outputs/ep08/09/start_v2.png`(K9f, 눈썹 제거·기준 눈), audio_1 `outputs/ep08/voice/scenes/s9.mp3`
**인자**: model=kling-video-v4_0(omni_ref_video), duration=6, aspect_ratio=9:16, 720p, prefer_multi_shots=true, enable_audio=true
```
One single continuous shot with a static, locked-off camera, no cuts, no camera movement: exactly the scene of 图片1 (same camera angle, same room, same furniture, same characters in the same places and the same clothes). 3D animated plush characters, short velvet fur; the room and the objects stay photoreal and unchanged.
Pang Mi-sun (light silver-grey, pink blush, beige tweed two-piece suit, small pearl hairpin) stands at the front entrance holding ONE high-heeled shoe in each short wing, among many shoes scattered on the floor. She looks up startled, then looks from one shoe to the other, flustered and worried. She speaks in Korean, exactly the voice, words and timing of 音频1, and nothing else:
1. "어?! 벌써 준비 다 했어?"
2. "나 아직 구두 못 골랐는데..."
3. "여보, 지금 몇 시야?"
Her beak opens and closes exactly in sync with 音频1. No other words, no English.
She keeps holding exactly one shoe in each wing the whole time; the shoes on the floor stay where they are and never move. Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes. Neither penguin has eyebrows (NO eyebrows); their eyes stay the same simple round glossy black eyes and the same size as in the first frame.
Wings keep their normal short rounded length and never stretch. Heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 놀라서 고개 듦 → 양손 구두 번갈아 보며 당황 → 시간 물음.
**위험·대책**: 구두가 날개에서 떨어지거나 늘어남 / 바닥 구두가 움직임 / 입모양 불일치.

## 합계
- 입모양(4.0): S1 60 + S3 50 + S6 50 + S8 50 + S9 60 = 270
- 목소리만(3.0): S2 30 + S4 30 + S5 18 + S7 30 = 108
- **합계 378크레딧**

- 2026-10-19 S6 제출이 거절됨: "copyright restrictions"(차감 0, 잔액 111). 어느 입력이 걸렸는지 Kling은 알려 주지 않음.
  - 유력 원인: K6 배경 선반의 명품풍 가방(켈리·버킷백 모양). ep07은 같은 방식(음성 참조+같은 캐릭터)으로 통과했으므로 캐릭터나 음성일 가능성은 낮음.
  - 무료 대안 `outputs/ep08/06/start_v2.png`: ISNet 마스크로 미순과 재킷은 선명하게 두고 배경만 흐림(얕은 심도). 얼굴·핀·식은땀·재킷은 v1과 같은 픽셀.
  - 같은 가방 선반이 보이는 다른 컷(K4 등)도 같은 이유로 거절될 수 있음 → 제출 전에 같은 처리 필요 여부 확인.
  - 재제출은 사용자 승인 대기.
- 2026-10-20 사용자 "그래" → K6 v2(배경 흐림)로 재제출 → **같은 사유로 거절**(차감 0, 잔액 111). 가방 선반은 원인 아님.
  - 통과한 ep07 S1 v2/S5 v2와 비교: 같은 모델·인자·캐릭터·음성 방식. 새로 들어간 것은 ① 프롬프트의 한글 "팽! 창! 수!!!" ② 녹음 속 "펭! 창! 수!"(ㅐ/ㅔ 같은 발음) ③ 미순 얼굴 클로즈업.
  - 새 유력 원인: "펭…수" + 펭귄 → EBS 캐릭터 **펭수(Pengsoo)** 저작권 필터에 걸림. 프롬프트 글자 또는 녹음 음성 인식 중 어느 쪽인지는 모름.
  - 사용자 결정 대기(아래 A/B/C).
- 2026-10-20 사용자 B안: 6c "팽창수!!!" → **"창수야!!!"**. 다시 녹음(seed 7, 받아쓰기 "창수야!" 1.00), s6 트랙 재조립(5.04s, 받아쓰기 "여보? 여보! 창수야!"). 프롬프트 3번 줄과 설명, 입력 이미지(v2) 수정 → lint 재검사 후 제출.
- **S6 v1 결과 (2026-10-20)**: 50크레딧, 잔액 **61**. `outputs/ep08/s6/clip_v1.mp4`, 시트 `verify_v1/motion_sheet.jpg`, `eyes_sheet.jpg`, `spec_clip_vs_ref.png`.
  - 소리: "여보? 여보?"는 우리 녹음과 똑같음(앞 2초 상관 1.0). "창수야!"는 Kling이 0.55s 늦게(3.09~4.06s) 다시 만듦(음높이 727Hz, 원본 696Hz로 비슷). 받아쓰기 "여보? 여보? 창수야!", 영어 없음.
  - `qa_clip` 전체 상관 0.42 → 기준 미달이지만 원인은 셋째 줄 재타이밍. 편집에서는 클립 자체 소리를 써서 입모양과 맞춤(자막 6c 타이밍도 클립 기준으로 옮김).
  - 화면: 고정 카메라, 한 컷, 부리가 세 마디에 맞춰 열림(0.5·1.5·3.2~3.8s). 볼터치·멈춤 검사 통과. 시작 화면이 K6보다 조금 넓게 잡힘(머리 작아짐, 끝까지 고정).
  - ⚠ 3.5s부터 오른쪽 눈 위 털이 접혀 **화난 미간 주름**처럼 보임. 그려진 눈썹 선은 아니고 눈 크기는 그대로임. 사용자 판단 대기.
- 2026-10-20 사용자: "그대로 써" → **S6 v1 ✅ 채택**(미간 주름 허용). 잔액 61, 나머지 8장면 328 필요 → 충전 대기.
- 2026-10-20 사용자: "자동으로 충전될 거야, 진행해" → 나머지 8장면 진행. 이미지 8장·음성 4개 업로드(URL은 스크래치패드 ep08_urls.txt).
- **S1 v1 ✅**: 60크레딧, 잔액 **1**. `outputs/ep08/s1/clip_v1.mp4`, 시트 `verify_v1/motion_sheet.jpg`, `wing_sheet.jpg`.
  - 소리 상관 0.97, 받아쓰기 3줄 그대로. 볼터치 0px.
  - 0~1.2s 시계 쪽 보고 놀람 → 2.0~3.2s 창수 쪽으로 돌아 날개로 이불 탁탁(날개 길이 정상) → 대사. 창수 계속 잠.
  - 5.58s 이후 멈춘 프레임(대사 끝 5.49s 뒤) → 편집에서 5.55s에서 자름.
- S3 제출 시 "Insufficient credits"(차감 0) → 자동 충전 대기.
- 2026-10-20 충전 확인(3001, Pro 등급 → 4.0 단가 초당 9). S3 45·S8 45·S9 54·S2 30·S4 30·S5 18·S7 30 = **252 제출**.
- **7장면 결과 (2026-10-20)** — 7개 모두 1회에 완료, 재시도 0. 시트 `outputs/ep08/sN/verify_v1/`.
  - **S3 ✅** 45: 상관 0.99, 받아쓰기 그대로. 옷걸이 날개에 계속 있음, 행거 옷 그대로. 4.96s 끝 프레임 멈춤 → 자름.
  - **S8 ✅** 45: 상관 0.99. 정장·넥타이 그대로, 볼터치 0px. 4.92s 이후 멈춤 → 자름.
  - **S9 ✅** 54: 상관 0.98. 양 날개 구두 한 짝씩(검정·베이지) 끝까지, 바닥 구두 그대로. 3.0s 눈 감고 한숨. 5.83s 이후 멈춤 → 자름.
  - **S2 ✅** 30: 뒷모습 드라이기 좌우, 창수 그대로 누워 잠.
  - **S4 ⚠✅** 30: 가방 가리키며 갸웃, 가방 그대로. 3.5s부터 옆모습으로 돌아섬(지시는 3/4 뒷모습 유지). 옆모습에 눈썹·속눈썹 없음, 부리 닫힘.
  - **S5 ✅** 18: 뒷모습으로 욕실까지 총총 + 손 흔듦, 돌아보지 않음.
  - **S7 ⚠✅** 30: 뒷모습 거품 박박. 2.0s부터 창수 볼 가장자리에 **분홍 볼터치**(F9) → `tools/fix_blush.py`로 지움(0원) → `clip_v1_fix.mp4`. `qa_clip` 볼터치 검사는 거품 때문에 펭귄 마스크가 빗나가 놓침(0px). 4.0s 이후 거품이 끈적하게 흘러내림 → 0~4.0s만 쓰는 것을 권장.
  - **ep08 Kling 합계: 362크레딧(S6 50 + S1 60 + 252), 실패 0, 거절 2회(차감 0).**
- **완성본 v1 (2026-10-20)**: `outputs/ep08/roughcut/ep08_v1.mp4` 41.2s, -17.4 LUFS, 시트 `v1_sheet.jpg`. 구성 `tools/ep08_edit.py`.
  - 30/40/30 띠, 장면별 띠 위치는 이미지 단계 값 그대로(`band_check_v1.jpg`로 9장면 확인).
  - 소리: 장면별 우리 녹음(S6만 클립 소리 -5.5dB), 효과음 5개(드라이기·샤워는 ElevenLabs 새로 생성), BGM E 우쿨렐레(대사 덕킹).
  - G4: 멈춘 프레임 없음(렌더 "sparse keyframes" 경고는 실제 멈춤 없음), 상태 이어짐 통과. 볼터치 의심 11.12~11.25s(S3)은 미순 혼자 나오는 장면 — 행거의 분홍 옷·분홍 자막을 잡은 오탐.
  - 캡션 `docs/ep08/05_릴스_캡션.md`.
