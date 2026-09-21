# ep01 Kling 실행표 v1 (2026-09-21)

> 목적: 크레딧을 쓰기 전에 24컷 전부의 프롬프트·예상 시나리오·위험·대안을 한 번에 검토한다. **재생성 없음 원칙**(사용자 결정)이므로 "실패 시 편집 대안"이 실제 안전망이다.
> 근거: 02 스토리보드 v1.4, 05a 프롬프트 가이드, 05b 운영규칙, 02a §11 띠 레이아웃, 00b B6 실패 유형표.
> 재사용 컷(생성 없음): 6-04·6-05 = 6-03 클립, 10-03 = 1-01 클립. 끝 프레임 없이 프롬프트로만 처리: 1-03, 7-01.

## 0. 공통 고정 문장 (모든 프롬프트에 글자 단위로 동일)
- 카메라: `Static camera, locked-off tripod shot, no camera movement, same composition throughout.`
- 스타일: `3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged.`
- 부리, 대화가 아닌 모든 컷(속마음·혼잣말·감탄 포함, 22컷): `Beak stays closed the whole time.` (8-01만 그림대로 `His beak stays exactly as in the image, slightly open in a smile, and does not move.`)
- 부리, **대화 컷 2개**(9-02 미순→창수 "라면머글래?", 9-03 창수→미순 "끄래!!!"): `As he speaks a short line, his beak opens and closes only a tiny amount, barely parting, just enough to show he is talking; it keeps its exact small triangular shape and size and never opens wide, stretches, or turns into lips.` — **2026-09-21 사용자 결정**: 대화만 부리를 아주 작게 움직이고 음성을 붙인다. 속마음·혼잣말은 부리 닫힘 + 보이스오버 음성 + 자막.
- 금지의 긍정문: `No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.`

## 1. 생성 전 결정 사항 — 2026-09-21 내가 확정 (사용자: 컷마다 "진행"만)
| # | 항목 | 제안 | 이유 |
|---|---|---|---|
| D1 | 4-02 인서트 | **정지 컷**으로 확정(두드리지 않음) | 두드리면 손가락 생성 위험이 에피소드 최고. 타자 소리는 편집(W12) |
| D2 | 길이 단축 | 1-03: 5→**3**초, 7-01: 5→**4**초 | 편집 길이(2초·3초)에 충분하고, 정지·반복 동작은 길수록 드리프트. 크레딧도 절약 |
| D3 | 해상도 | **720p 확정**(사용자) | 띠 레이아웃의 1.5배 확대는 감수. 최종본 10개 후 재검토(05b 원칙) |
| D4 | Kling 웹 설정 | **불필요** | 띠 크롭이 원본 위 ≥22%·아래 ≥20%를 항상 잘라내므로 좌상단 "AI Generated"·우하단 로고 모두 화면 밖 |
| D5 | 실행 순서 | ① 4-01(정지: 단가·카메라 검증) → ② **9-03(대화 컷: 부리 미세 움직임·변형 검증, 3초 시작만)** → ③ 1-02(시작+끝) → ④ 6-01·9-01(고위험) → ⑤ 나머지 | 앞 결과가 뒤 프롬프트를 고칠 정보를 준다. 재생성은 없어도 **다음 컷 프롬프트 수정**은 0크레딧 |

## 1b. 10-03 엔딩 — 확정: 1-01 재사용
"아!!!"는 대화가 아니라 소리이므로 부리 닫힘 + 보이스오버. 스토리보드대로 1-01 클립 재사용, 추가 생성 없음.

## 2. 위험 등급 요약
| 등급 | 컷 | 핵심 위험 |
|---|---|---|
| **높음** | 6-01, 9-01 | 제자리 걸음·발 미끄러짐, 둘 컷 간격·좌우 |
| 중간 | 1-03, 2-01, 2-02, 5-02, 7-01, 9-02, **+ 대화 컷 9-02·9-03** | 물건 증식, 부위 변형(털뭉치·부리), 반복 동작 어긋남. **대화 컷은 부리 변형이 위험** → 9-03에서 먼저 검증 |
| 낮음 | 나머지 16컷 | 정지·미세 동작. 실패해도 정지 이미지로 대체 가능 |

**정지 컷 15개는 실패해도 손실이 0에 가깝다.** 시작 프레임을 정지 이미지로 넣으면 결과가 거의 같다(편집에서 1~2% 줌으로 정지감 완화 가능). 실제로 크레딧이 걸린 컷은 시작+끝 9개와 7-01·1-03이다.

## 3. 검증 절차 (클립마다, 06 B0~B4)
1. ffmpeg로 0.25초 간격 프레임 추출 + 첫·끝 프레임.
2. 첫 프레임 ↔ 시작 이미지, 끝 프레임 ↔ 끝 이미지: 배경 영역 평균 픽셀차(기준 ≤ 8), 캐릭터 위치·크기.
3. 전 프레임: 배경 고정 영역 드리프트, 카메라 이동(배경 특징점), 부리 영역 색·면적 변화(닫힘 지시 컷에서 열림 탐지).
4. 샘플 프레임을 눈으로 확인(손가락·증식·변형). **통과 클립도 사용자가 한 번 재생 확인.**
5. 결과·수치·판정을 `outputs/ep01/<컷>/meta.json`에 기록.

## 4. 컷별 실행표
### 1-01 — 시작만, 3초
**입력**: `outputs/ep01/1-01/start_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su and Pang Mi-sun lie asleep side by side under one blanket in the morning light. Nothing moves except the slow rise and fall of their breathing under the blanket. Both keep their eyes closed. The phone on the nightstand stays still. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 이불이 숨결에 아주 천천히 오르내리고 그 외 정지. 10-03에서 그대로 재사용.
**위험·감시 항목**: 낮음 | 눈을 뜨거나 몸을 뒤척임(1-02 역할 침범), 이불이 두 장으로 늘어남, 창밖 밝기 변동
**실패 시 편집 대안(재생성 없음)**: 정지 컷이라 실패해도 시작 프레임을 3초 정지 이미지로 대체(0크레딧, 화질 동일)

### 1-02 — 시작+끝, 3초
**입력**: `outputs/ep01/1-02/start_v1.png` + `end_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Lying on his side on the pillow, Pang Chang-su slowly opens his eyes halfway, waking to the alarm. Only his eyelids move; his head stays on the pillow and the blanket stays still. By the end his eyes are half open and unfocused, staring ahead. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**자막(속마음·혼잣말 → 보이스오버, 부리 닫힘)**: 또 아침..
**예상 시나리오**: 3초에 걸쳐 눈꺼풀만 반쯤 열림. 머리·이불 고정.
**위험·감시 항목**: 낮음 | 머리를 들거나 돌림, 눈이 완전히 뜨임, 눈동자 방향이 튐
**실패 시 편집 대안(재생성 없음)**: 앞 1.5초(감은 상태)만 쓰거나 끝 프레임 정지 이미지로 대체

### 1-03 — 시작만, 3초 (스토리보드 5→3 확정)
**입력**: `outputs/ep01/1-03/start_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su sits on the edge of the bed, sleepy, looking down at the floor. His dangling feet sway very slightly back and forth. His body, head and wings stay still. Mi-sun stays asleep behind him and does not move. The turned-back blanket stays as it is. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 발끝만 아주 작게 흔들림. 나머지 정지.
**위험·감시 항목**: 중간 | 일어서거나 발이 바닥에 닿음, 미순이 움직임, 이불이 다시 덮임. **5초는 드리프트가 늘어나므로 3초 권장**(편집 2초면 충분)
**실패 시 편집 대안(재생성 없음)**: 발 흔들림이 안 나와도 정지 컷으로 성립. 시작 프레임 정지 이미지 대체 가능

### 2-01 — 시작+끝, 4초
**입력**: `outputs/ep01/2-01/start_v1.png` + `end_v1.png`
**인자**: model=kling-video-v3_0, duration=4, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su slowly lowers the light grey towel from his face down to his chest with both wings, revealing his sleepy face. By the end the towel rests against his chest, held in both wings, and he looks straight at the camera. He stays standing in the same spot. The towel bar on the right stays empty. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 수건이 얼굴→가슴으로 내려오며 얼굴이 드러남. 4초.
**위험·감시 항목**: 중간 | 수건이 두 장이 되거나 걸이에 다시 생김(R25), 날개가 팔처럼 늘어남·손가락, 얼굴이 드러나며 표정이 바뀜(졸림 유지돼야 함)
**실패 시 편집 대안(재생성 없음)**: 끝 프레임 정지 이미지 2초로 대체(얼굴 드러난 상태). 체이닝 컷이라 끝 상태만 맞으면 2-02와 이어짐

### 2-02 — 시작+끝, 3초
**입력**: `outputs/ep01/2-02/start_v1.png` + `end_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su stands still, holding the towel at his chest, looking straight at the camera with a tired, resigned glare. The wet tuft on top of his head slowly dries and rises until it stands straight up. Nothing else moves at all: his head, eyes, wings and the towel stay completely still. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**자막(속마음·혼잣말 → 보이스오버, 부리 닫힘)**: 가기 싫다..
**예상 시나리오**: 털뭉치만 3초에 걸쳐 스르륵 일어섬. 얼굴·수건 고정.
**위험·감시 항목**: 중간 | 모델이 '털뭉치'를 못 알아듣고 머리를 움직임, 털뭉치가 형태 변형(R10), 눈이 감기거나 뜨임. 05b 점진 규칙의 첫 실전(부위 하나만 변화)
**실패 시 편집 대안(재생성 없음)**: 시작 1.5초 + 끝 1.5초 정지 이미지 컷(젖음→마름 점프컷)으로도 개그가 성립

### 3-01 — 시작만, 3초
**입력**: `outputs/ep01/3-01/start_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su stands still on the platform in profile, waiting sleepily with heavy eyelids. Only a slow blink and faint breathing. The adult next to him and the people in the distance stand still. The platform screen doors stay closed and no train arrives. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 정지. 눈 한 번 느리게 깜빡.
**위험·감시 항목**: 낮음 | **열차가 들어옴**(모델이 승강장에 열차를 붙이는 경향, R15), 사람들이 걷기 시작, 스크린도어 열림
**실패 시 편집 대안(재생성 없음)**: 시작 프레임 정지 이미지 대체

### 3-02 — 시작+끝, 3초
**입력**: `outputs/ep01/3-02/start_v1.png` + `end_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su slowly turns his head a little toward the camera, from full profile to a three-quarter view, staring blankly along the platform. His eyes stay tired and half-lidded and do not widen. His body and shoulders do not move. Screen doors stay closed, no train. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 고개만 살짝 카메라 쪽으로. 눈은 졸린 채.
**위험·감시 항목**: 낮음 | 눈이 커짐(끝 프레임 v1과 같은 실패), 몸까지 돌아섬, 부리 변형
**실패 시 편집 대안(재생성 없음)**: 끝 프레임 정지 이미지 대체

### 4-01 — 시작만, 3초
**입력**: `outputs/ep01/4-01/start_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su sits at his desk looking at the monitor. Only a slight slow nod of his head and one blink. His wings stay down, out of view behind the desk. The monitor screen stays a blank pale glow with no text. The mug and keyboard stay still. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 거의 정지. 첫 실행 컷 후보(가장 싸고 부리·카메라 검증).
**위험·감시 항목**: 낮음 | 화면에 글자·UI가 생김, 타이핑 동작으로 손가락 등장, 카메라가 줌인
**실패 시 편집 대안(재생성 없음)**: 시작 프레임 정지 이미지 대체

### 4-02 — 시작만, 3초
**입력**: `outputs/ep01/4-02/start_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Two short rounded flipper wing tips rest on the keyboard, completely still. The monitor screen stays a blank pale glow with no text. Nothing moves except a faint, barely visible settling of the wings. The wings stay short and rounded with no fingers, no hands, no thumbs. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 정지 인서트. 타자 소리는 편집에서(W12). **손가락 위험을 없애기 위해 두드리는 동작을 넣지 않음.**
**위험·감시 항목**: 낮음(정지로 고정 시) | 두드리게 하면 **손가락 생성 위험이 에피소드 최고**. 화면에 글자 생성
**실패 시 편집 대안(재생성 없음)**: 시작 프레임 정지 이미지 대체(사실상 동일 결과)

### 4-03 — 시작만, 3초
**입력**: `outputs/ep01/4-03/start_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su glares at the monitor with narrowed, annoyed eyes. His head pushes very slightly forward toward the screen and holds there. His expression stays the same flat glare. Nothing else moves. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**자막(속마음·혼잣말 → 보이스오버, 부리 닫힘)**: 모니터 뚫어!!!!
**예상 시나리오**: 고개가 아주 살짝 앞으로. 째려봄 유지.
**위험·감시 항목**: 낮음 | 표정이 화남·놀람으로 바뀜, 부리 열림(짜증 자막 컷이라 모델이 소리치게 만들 수 있음)
**실패 시 편집 대안(재생성 없음)**: 시작 프레임 정지 이미지 대체

### 5-01 — 시작만, 3초
**입력**: `outputs/ep01/5-01/start_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su sits at the table gazing at the stew with wide, sparkling eyes and a happy face. Thin steam rises gently from the stone pot. He, the dishes, the spoon and chopsticks on the napkin, and the customer behind him all stay still. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**자막(속마음·혼잣말 → 보이스오버, 부리 닫힘)**: 밥 마시따
**예상 시나리오**: 김만 오르고 정지.
**위험·감시 항목**: 낮음 | 먹기 시작함(숟가락이 날개로 이동 → 5-02 연속성 붕괴), 김이 연기처럼 과함, 반찬 개수 변동
**실패 시 편집 대안(재생성 없음)**: 시작 프레임 정지 이미지 대체

### 5-02 — 시작+끝, 4초
**입력**: `outputs/ep01/5-02/start_v1.png` + `end_v1.png`
**인자**: model=kling-video-v3_0, duration=4, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su chews slowly with small movements of his cheeks, holding the spoon still in his right wing above the pot. His happy curved eyes slowly grow heavier and sleepier over the clip as drowsiness sets in. The spoon, the dishes, the open rice bowl and its lid stay exactly where they are. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 볼 오물오물 + 눈이 천천히 무거워짐(05b 점진). 숟가락 고정.
**위험·감시 항목**: 중간 | **부리가 열려 씹는 입이 됨**(스토리보드 대비책: 실패 시 부리 닫힘 고정), 숟가락이 입으로 감·음식이 줄어듦, 볼이 과하게 부풂
**실패 시 편집 대안(재생성 없음)**: 부리가 열린 구간을 잘라내고 앞부분만 쓰거나 시작 프레임 정지 이미지 3초

### 5-03 — 시작만, 3초
**입력**: `outputs/ep01/5-03/start_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su sits before the empty dishes, heavy-eyed and drowsy. His head slowly dips forward once in a small doze and comes back up. Both wings stay on the table. The empty pot, the spoon inside it and the dishes stay still. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**자막(속마음·혼잣말 → 보이스오버, 부리 닫힘)**: 졸려...
**예상 시나리오**: 고개 한 번 꾸벅.
**위험·감시 항목**: 낮음 | 눈이 완전히 감김·잠듦, 머리가 테이블까지 떨어짐, 빈 그릇에 음식이 다시 생김(R25)
**실패 시 편집 대안(재생성 없음)**: 시작 프레임 정지 이미지 대체

### 6-01 — 시작+끝, 5초
**입력**: `outputs/ep01/6-01/start_v1.png` + `end_v1.png`
**인자**: model=kling-video-v3_0, duration=5, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su walks at a steady waddling pace to his right along the pavement, from beside the left tree to the front of the bench. Each step lands on the paving and rolls forward; his feet do not slide. By the end he stands still in front of the bench, body turned to his right. The trees, bench and leaf shadows stay still. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 3~4걸음 뒤뚱 이동 후 벤치 앞에서 정지. 에피소드 첫 걷기.
**위험·감시 항목**: **높음** | **제자리 걸음·발 미끄러짐**(B6 1순위), 크기 변화, 잎 그림자 깜빡임, 카메라가 따라 팬. 걷기는 05a §8 3순위 검증 항목
**실패 시 편집 대안(재생성 없음)**: 시작 프레임 1.5초 + 끝 프레임 1.5초 정지 점프컷. 또는 클립의 첫 2걸음만 쓰고 끝 프레임 정지로 마무리

### 6-02 — 시작만, 3초
**입력**: `outputs/ep01/6-02/start_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su stands with his eyes closed, face lifted slightly toward the sun, breathing slowly and calmly. Dappled leaf shadows drift very slowly across his face. His eyes stay closed the whole time and his head stays still. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**자막(속마음·혼잣말 → 보이스오버, 부리 닫힘)**: 후...
**예상 시나리오**: 정지. 잎 그림자만 살짝 흐름.
**위험·감시 항목**: 낮음 | 눈을 뜸, 그림자가 거칠게 깜빡임(조명 깜빡임 유형), 고개를 흔듦
**실패 시 편집 대안(재생성 없음)**: 시작 프레임 정지 이미지 대체

### 6-03 — 시작만, 3초
**입력**: `outputs/ep01/6-03/start_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su sits slumped at his desk with half-closed eyes, staring at the monitor. One tiny slow nod of his head and one slow blink. His posture stays slumped. The monitor screen stays a blank pale glow with no text. Nothing else moves. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**자막(속마음·혼잣말 → 보이스오버, 부리 닫힘)**: 아직도 3시.. (6-04·6-05: 4시·5시)
**예상 시나리오**: 4-01의 지친 버전. 6-04·6-05에서 재사용.
**위험·감시 항목**: 낮음 | 4-01과 동일 위험 + 자세가 펴짐(굽은 등 유지돼야 함)
**실패 시 편집 대안(재생성 없음)**: 시작 프레임 정지 이미지 대체

### 7-01 — 시작만, 4초 (스토리보드 5→4 확정)
**입력**: `outputs/ep01/7-01/start_v1.png`
**인자**: model=kling-video-v3_0, duration=4, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su stands beside his desk, beaming, and bounces gently on the spot with excitement, a small up-and-down bob with his feet staying on the carpet. His wings stay short at his sides. The dark monitor, the chair and the mug stay still. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**자막(속마음·혼잣말 → 보이스오버, 부리 닫힘)**: 퇴근!!
**예상 시나리오**: 제자리에서 작게 콩콩. 스토리보드 기본안(서 있는 정지 컷 + 들썩).
**위험·감시 항목**: 중간 | 걸어 나감, 너무 높이 뜀, 날개를 팔처럼 휘두름, 부리 열림(신남). **5초는 반복 동작이 어긋날 시간**이라 4초 권장
**실패 시 편집 대안(재생성 없음)**: 시작 프레임 정지 이미지 3초(들썩 없이도 표정으로 성립)

### 8-01 — 시작만, 3초
**입력**: `outputs/ep01/8-01/start_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su stands facing the camera at three-quarters, beaming with his beak slightly open, swaying very slightly from side to side with excitement. His feet stay planted. The adult behind him stays still. The screen doors stay closed and no train arrives. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. His beak stays exactly as in the image, slightly open in a smile, and does not move. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**자막(속마음·혼잣말 → 보이스오버, 부리 닫힘)**: 빨리집가!!!
**예상 시나리오**: 몸이 좌우로 아주 살짝. 부리는 살짝 열린 채 미세.
**위험·감시 항목**: 낮음 | 부리가 크게 벌어져 말함, 열차 진입, 걷기 시작
**실패 시 편집 대안(재생성 없음)**: 시작 프레임 정지 이미지 대체

### 9-01 — 시작+끝, 5초
**입력**: `outputs/ep01/9-01/start_v1.png` + `end_v1.png`
**인자**: model=kling-video-v3_0, duration=5, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su on the left and Pang Mi-sun on the right walk side by side at the same steady waddling pace to their right along the path, seen from behind at an angle. Each step lands and rolls forward with no sliding. By the end they stand still a short way further along the path, still side by side with the same gap, Chang-su still on the left. Both beaks stay closed. The lamps and buildings stay still. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 둘이 같은 속도로 3걸음. 에피소드 최고 난도.
**위험·감시 항목**: **높음** | 제자리 걸음, **둘의 속도가 달라 간격 변화**, 좌우 바뀜·얼굴 섞임, 카메라 쪽으로 돌아섬. 스토리보드 대비책: 싱글 컷 2개 분할(그러나 재생성 없음 원칙이면 아래 대안)
**실패 시 편집 대안(재생성 없음)**: 시작·끝 프레임 정지 점프컷(1.5+1.5). 또는 클립 앞 2초만 채택

### 9-02 — 시작+끝, 3초
**입력**: `outputs/ep01/9-02/start_v1.png` + `end_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Mi-sun slowly turns her upper body and head to her right, toward the left side of the frame, looking at her husband off-frame with a bright cheerful smile as she speaks. By the end she faces three-quarters to the left. Her lower body stays in place. Her husband does not appear in the frame. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. As she speaks a short line, her beak opens and closes only a tiny amount, barely parting, just enough to show he is talking; it keeps its exact small triangular shape and size and never opens wide, stretches, or turns into lips. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**자막(대화 → 음성 + 부리 아주 작게 움직임)**: 라면머글래? (미순)
**예상 시나리오**: 상체만 왼쪽으로 살짝 돌며 말함(핑크 자막).
**위험·감시 항목**: 중간 | **부리가 입술처럼 변형**(R12 클로즈업 위험), 과회전·정면 유지, 창수가 프레임에 들어옴, 볼터치 소실
**실패 시 편집 대안(재생성 없음)**: 끝 프레임 정지 이미지 2초 + 자막(말하는 움직임 없이도 성립)

### 9-03 — 시작만, 3초
**입력**: `outputs/ep01/9-03/start_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su looks to the right with wide sparkling eyes and a big delighted smile, his head tipping slightly forward with excitement as he answers. His eyes stay wide the whole time. Nothing else moves. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. As he speaks a short line, his beak opens and closes only a tiny amount, barely parting, just enough to show he is talking; it keeps its exact small triangular shape and size and never opens wide, stretches, or turns into lips. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**자막(대화 → 음성 + 부리 아주 작게 움직임)**: 끄래!!!
**예상 시나리오**: 고개 살짝 앞으로, 부리 미세. 편집 1.5초라 앞부분만 씀.
**위험·감시 항목**: 낮음 | 부리 변형, 표정이 가라앉음(R11: 반응은 처음부터 끝까지 유지)
**실패 시 편집 대안(재생성 없음)**: 시작 프레임 정지 이미지 대체

### 9-04 — 시작만, 4초
**입력**: `outputs/ep01/9-04/start_v1.png`
**인자**: model=kling-video-v3_0, duration=4, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su and Pang Mi-sun sit close together on the sofa watching the TV, which is where the camera is, completely still except slow blinks and breathing. Soft TV light flickers very gently on their faces. The empty pot and chopsticks on the table stay still. Both beaks stay closed. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 정지 + TV 불빛 미세 깜빡임.
**위험·감시 항목**: 낮음 | 서로 마주 보거나 말함, 불빛 깜빡임이 과함, 냄비에 라면이 다시 생김(R25)
**실패 시 편집 대안(재생성 없음)**: 시작 프레임 정지 이미지 대체(TV 불빛은 편집에서 밝기 흔들기 가능)

### 10-01 — 시작만, 3초
**입력**: `outputs/ep01/10-01/start_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su lies on his side in bed at night with half-open sleepy eyes, staring blankly ahead; Mi-sun sleeps beside him with her eyes closed. Only slow breathing. The bedside lamp stays lit and steady. Nothing else moves. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 정지. 눈 반쯤 뜬 채.
**위험·감시 항목**: 낮음 | 눈이 감김(10-02 역할 침범), 스탠드 깜빡임, 이불 증식
**실패 시 편집 대안(재생성 없음)**: 시작 프레임 정지 이미지 대체

### 10-02 — 시작+끝, 4초
**입력**: `outputs/ep01/10-02/start_v1.png` + `end_v1.png`
**인자**: model=kling-video-v3_0, duration=4, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Lying on his side on the pillow at night, Pang Chang-su slowly closes his half-open eyes and drifts off to sleep. Only his eyelids move; his head stays on the pillow. By the end his eyes are fully closed. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the room and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**자막(속마음·혼잣말 → 보이스오버, 부리 닫힘)**: 내일도 화이띵...!
**예상 시나리오**: 눈만 천천히 감김. 1-02의 역방향.
**위험·감시 항목**: 낮음 | 눈이 다시 뜨임, 머리 움직임
**실패 시 편집 대안(재생성 없음)**: 끝 프레임 정지 이미지 대체(암전으로 이어지므로 자연스러움)
