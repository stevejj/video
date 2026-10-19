# ep05 Kling 실행표 (2026-10-19 사용자: 애니매틱 "이해됨", "2개 다 가자")

> 애니매틱 v1 확인 후 컷별 결정(08 표준 순서). Kling은 2컷과 5컷만 씁니다. 1·3·4컷은 정지 컷에 줌을 줍니다(0원). **상한 70크레딧**, 잔액 609.
> 공통 규칙:
> - 고정 카메라, 플러시 질감.
> - 날개는 평소 길이로, 늘이기 금지(M16).
> - 미순은 속눈썹 없음, 부리 닫힘.
> - 창수는 뒷모습 그대로, 돌아보지 않음.
> - 덤벨은 미순 날개가 덤벨에 닿은 뒤에만 움직임(ep03 교훈: 멀리서 잡으면 순간이동).
> - 새 물체 없음.
> - 실패 2회 연속이면 중단하고 재기획(F5).
> - 핵심(포즈 → 확인하러 옴 / 돌아가 같은 포즈)이 안 보이면 채택 추천 금지(F6).

## 2컷: K1 → K3, 5초 (편집 약 4.0s) · 30크레딧
**입력**: first_image `outputs/ep05/01/start_v1.png`(K1), tail_image `outputs/ep05/03/start_v1.png`(K3)
**인자**: model=kling-video-v3_0, duration=5, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
```
Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the gym, the floor, the dumbbell rack and the bench stay photoreal and completely unchanged.
Pang Chang-su stands in the foreground on the left, seen from behind, holding a black smartphone up with his wing, taking a photo of Pang Mi-sun. He stays seen from behind the whole time and never turns around. Mi-sun stands in the middle of the gym holding two small pink dumbbells at shoulder height with a proud smile. Right after the photo is taken, she bends down a little and places the two pink dumbbells on the rubber floor right where she stands, then waddles quickly with small penguin steps toward Chang-su and stops right beside him on his right side. Chang-su lowers the phone in front of his chest and she leans in to look down at the phone screen with a curious, serious face, exactly matching the end image. The pink dumbbells stay on the floor where she put them. Her wings keep their normal short rounded length and never stretch. Her head keeps its normal shape and stays upright. Her beak stays closed. No eyelashes. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 0~1s 포즈 유지, 1~2s 덤벨을 바닥에 내려놓음, 2~4s 총총 걸어와 창수 옆, 4~5s 폰 들여다봄.
**위험**:
- 덤벨이 날개에 붙어 따라옴, 또는 바닥에서 저절로 생김.
- 창수가 돌아봄.
- 허리 굽힐 때 몸이 늘어남.
- 폰이 2개가 됨.

실패 시: 애니매틱 v2의 퍼펫 구간(덤벨 낙하 → 총총)으로 대체합니다(0원).

## 5컷: K3 → K1, 5초 (편집 약 4.5s) · 30크레딧
**입력**: first_image `outputs/ep05/03/start_v1.png`(K3), tail_image `outputs/ep05/01/start_v1.png`(K1)
**인자**: 2컷과 동일
```
Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the gym, the floor, the dumbbell rack and the bench stay photoreal and completely unchanged.
Pang Chang-su stands in the foreground on the left, seen from behind, holding a black smartphone in front of his chest. He stays seen from behind the whole time and never turns around. Pang Mi-sun stands right beside him on his right side looking down at the phone screen. She turns and waddles back with small penguin steps to the two pink dumbbells lying on the rubber floor just in front of her, and stops right next to them. She bends her whole body down and wraps one wing around each dumbbell handle. The dumbbells lie completely still on the floor until both of her wings are holding them. Then she lifts them with real effort, as if they are heavy: she strains for a moment, her body tenses and leans back slightly, and the dumbbells rise slowly together with her wings, never floating or moving on their own. She stands up straight and raises them to shoulder height with the same proud smile as before, facing the camera. Chang-su raises the phone up again to take her photo, exactly matching the end image. Her wings keep their normal short rounded length and never stretch. Her head keeps its normal shape and stays upright. Her beak stays closed. No eyelashes. No other characters appear. No new objects appear. Wings stay soft, rounded and fingerless.
```
**예상**: 0~1.5s 돌아서 총총 덤벨 옆으로, 1.5~2.5s 몸 숙여 양 날개로 손잡이를 감쌈(덤벨 그대로), 2.5~3.5s 힘주며 천천히 들어 올림, 3.5~5s 다시 같은 포즈. (갸웃은 4컷 정지 K3가 맡음) 끝 = K1이라 1컷과 이어져 루프가 됩니다.
**위험**:
- 덤벨이 날개에 미리 생기거나 날개보다 먼저 떠오름(사용자 필수 조건: "덤벨이 움직이는 게 아니라 들어야 하는 느낌").
- 돌아설 때 뒷모습이 이상해짐.
- 창수가 돌아봄.

실패 시: 애니매틱 v2의 퍼펫 구간(숙이기 → 덤벨 들기 → 팝)으로 대체합니다(0원).

## 현황
- 2026-10-19 실행표 작성. 승인("진행") 대기.
- 2026-10-19 사용자: "정지화면이 나은지 일단 내가 판단해볼게. 너무 정지화면이면 재미없더라, 애니매틱으로 할 수 있는 최선을 해야 영상처럼 보일 것 같다" → **Kling 보류**, 무료 애니매틱 v2(퍼펫) 먼저 만듦.
- **애니매틱 v2 (0원)**: 10.0s, 6컷. `outputs/ep05/roughcut/ep05_animatic_v2.mp4` (-19.9 LUFS)
  - 퍼펫 재료: `tools/ep05_puppet.py`.
    - ISNet 누끼(`tools/cutout.py`)로 미순 K1·K3와 바닥 덤벨을 오려냄.
    - 미순 없는 배경판 plateA(폰 듦)·plateB(폰 내림)를 만듦.
    - 두 장 모두 가려진 구멍은 랙 무늬를 80px 반복해 채우고, 바닥은 아래 바닥 결을 복사함.
  - 01 포즈 들썩 2번 → 셔터 플래시+찰칵(합성음)
  - 02 덤벨 떨어져 튕김+화면 흔들림+툭 → 총총 2번 뛰고 폰 쪽으로 기울기
  - 03 폰 화면 인서트 1.0→1.1 줌+손떨림
  - 04 갸웃(8°)
  - 05 총총 → 허리 숙여 덤벨 집음 → 포즈로 팝
  - 06 포즈 들썩 → 셔터 → 루프
  - 전 컷 손떨림(drift 4px).
  - 소리: 셔터 `tools/sfx_shutter.py` 합성, 덤벨 ep02 charger_drop, 발소리 ep01 footsteps, 팝 ep01 sparkle, BGM F(-20).
  - 설정: `edit_list_animatic_v2.json`, `hf_fx_v2.json`, `sfx/sfx_list.json`.
  - 메모: 셔터처럼 0.4s보다 짧은 소리는 LUFS 측정이 안 됨(-inf) → gain을 고정값으로 둠.
  - 사용자 판단 대기: v2로 완성할지, Kling 2컷(60크레딧)을 넣을지.
- 2026-10-19 사용자: "Kling으로 만들 건데, Kling이 실패했을 때 애니매틱으로 구현한다는 거였어. 덤벨을 다시 잡아서 운동하는 순간에 덤벨이 움직이는 게 아니라 덤벨을 들어야 하는 느낌이어야 해."
  - **Kling이 본편이고, 퍼펫 애니매틱(v2)은 실패한 컷의 대체용**입니다.
  - 5컷 프롬프트를 고쳤습니다. 덤벨 바로 옆까지 걸어가서 양 날개로 손잡이를 감싸기 전까지 덤벨은 바닥에 그대로 있고, 힘주며 천천히 들어 올립니다(무게감). 갸웃은 4컷 정지 화면으로 넘겼습니다.
  - 2개 제출(60크레딧).
- 2026-10-19 제출: 2컷 `Ac3HEyv9…`, 5컷 `AcPpYpik…` (각 30, 잔액 609 → 549). ID 전체는 `outputs/ep05/02|05/meta.json`.
