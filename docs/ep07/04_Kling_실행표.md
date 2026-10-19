# ep07 Kling 실행표 — 포장마차 (애니매틱 확인 후)

> 상한 **230크레딧**, 잔액 459. 공통 규칙(08 F10 관문 G2 통과 필수):
> - 고정 카메라, 한 컷.
> - 미순 속눈썹 없음, 창수 볼터치 없음.
> - 날개 늘이기 금지, 새 물체 금지.
> - 맥주잔은 정확히 2개이고 날개에 들려 있음(떠다니면 실패).
> - 2회 연속 실패 시 중단(F5).
> - **입모양 방식**: Kling 4.0 `omni_ref_video`에 우리 녹음을 `audio_1`로 넣음. **초 단위 과금 10크레딧/초.**
> - **S5를 먼저 시험** → 부리가 대사에 맞으면 S1, 안 맞으면 멈추고 방법 재검토.

## S5 시험 — 미순 "이모! 맥주 한잔 더요!" + 둘 웃음 · Kling 4.0, 5초 · 50크레딧
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

## S1 대화 — L1~L6 · Kling 4.0, 10초 · 100크레딧 (S5 합격 후)
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
- 2026-10-19 작성. 애니매틱 v1 확인 + S5 시험 "진행" 대기.
