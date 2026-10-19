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
**입력**: image_1 `outputs/ep08/06/start_v1.png`(K6), audio_1 `outputs/ep08/voice/scenes/s6.mp3`
**인자**: S3와 같음
```
One single continuous shot with a static, locked-off camera, no cuts, no camera movement: exactly the scene of 图片1 (same camera angle, same room, same furniture, same characters in the same places and the same clothes). 3D animated plush characters, short velvet fur; the room and the objects stay photoreal and unchanged.
An extreme close-up of Pang Mi-sun's face (light silver-grey, pink blush, beige tweed collar, small pearl hairpin, a small cartoon sweat drop). She calls out twice in disbelief, then explodes in anger, shouting the name syllable by syllable, her head shaking a little with rage. She speaks in Korean, exactly the voice, words and timing of 音频1, and nothing else:
1. "여보?"
2. "여보?"
3. "팽! 창! 수!!!"
Her beak opens and closes exactly in sync with 音频1. No other words, no English.
The sweat drop and the pearl hairpin stay in place. Chang-su does not appear. Chang-su's cheeks have NO pink blush at any time; only Mi-sun has pink blush. Mi-sun has NO eyelashes. Neither penguin has eyebrows (NO eyebrows); their eyes stay the same simple round glossy black eyes and the same size as in the first frame.
Wings keep their normal short rounded length and never stretch. Heads keep their normal shape. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 여보? 여보? (점점 굳는 얼굴) → 팽! 창! 수!!! 머리 흔들며 폭발.
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
