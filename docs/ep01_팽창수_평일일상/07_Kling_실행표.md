# ep01 Kling 실행표 v1 (2026-09-21)

> 목적: 크레딧을 쓰기 전에 24컷 전부의 프롬프트·예상 시나리오·위험·대안을 한 번에 검토한다. **재생성 없음 원칙**(사용자 결정)이므로 "실패 시 편집 대안"이 실제 안전망이다.
> 근거: 02 스토리보드 v1.4, 05a 프롬프트 가이드, 05b 운영규칙, 02a §11 띠 레이아웃, 00b B6 실패 유형표.
> 재사용 컷(생성 없음): 6-04·6-05 = 6-03 클립, 10-03 = 1-01 클립. 끝 프레임 없이 프롬프트로만 처리: 1-03, 7-01.

## 0. 공통 고정 문장 (모든 프롬프트에 글자 단위로 동일)
- 카메라: `Static camera, locked-off tripod shot, no camera movement, same composition throughout.`
- 스타일: `3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged.`
- 부리, 대화가 아닌 모든 컷(속마음·혼잣말·감탄 포함, 22컷): `Beak stays closed the whole time.` (8-01만 그림대로 `His beak stays exactly as in the image, slightly open in a smile, and does not move.`)
- 부리, **대화 컷 2개**(9-02 미순→창수 "라면머글래?", 9-03 창수→미순 "끄래!!!"): `As he speaks a short line, his beak opens and closes only a tiny amount, barely parting, just enough to show he is talking; it keeps its exact small triangular shape and size and never opens wide, stretches, or turns into lips.` — **2026-09-21 사용자 결정**: 대화만 부리를 아주 작게 움직이고 음성을 붙인다. 속마음·혼잣말은 부리 닫힘 + 보이스오버 음성 + 자막.
- 금지의 긍정문: `No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.`

## 0b. 프롬프트 사전 점검표 (2026-09-21, 4-01·9-03 실측에서 도출 — 호출 전 매번 확인)
| # | 점검 | 근거 |
|---|---|---|
| 1 | **동작 동사가 "크게" 해석돼도 괜찮은가?** speaks/answers/chews/bounces/sways/excitement/delighted 같은 단어는 지우거나 정적 서술로 바꾼다. 부정문(never, only a tiny amount)은 **안 통한다** | 9-03: tiny+never를 다 넣고도 입을 활짝 엶 |
| 2 | 변화가 필요한 부위는 **말이 아니라 끝 프레임**으로 준다 | 프레임 보간은 지켜지고 문장은 무시됨 |
| 3 | 시선·머리 방향을 **긍정문으로, 클립 내내** 고정했는가 (`keeps facing X the whole time` + `does not turn toward the camera`) | 4-01·9-03 둘 다 카메라를 돌아봄 |
| 4 | 정지 컷이면 **정지 이미지로 충분하지 않은가**(0크레딧). 클립은 "시키지 않은 동작"이 들어올 위험만 있다 | 4-01: 정지 컷인데 고개 회전 |
| 5 | 길이는 편집 길이 +1초 이내인가 (3초 최소) | 길수록 드리프트 |
| 6 | 프레임 안에 없는 것을 언급하지 않았는가 (열차·사람·소리) | R4 |

## 1. 생성 전 결정 사항 — 2026-09-21 내가 확정 (사용자: 컷마다 "진행"만)
| # | 항목 | 제안 | 이유 |
|---|---|---|---|
| D1 | 4-02 인서트 | **정지 컷**으로 확정(두드리지 않음) | 두드리면 손가락 생성 위험이 에피소드 최고. 타자 소리는 편집(W12) |
| D2 | 길이 단축 | 1-03: 5→**3**초, 7-01: 5→**4**초 | 편집 길이(2초·3초)에 충분하고, 정지·반복 동작은 길수록 드리프트. 크레딧도 절약 |
| D3 | 해상도 | **720p 확정**(사용자) | 띠 레이아웃의 1.5배 확대는 감수. 최종본 10개 후 재검토(05b 원칙) |
| D4 | Kling 웹 설정 | **불필요** | 띠 크롭이 원본 위 ≥22%·아래 ≥20%를 항상 잘라내므로 좌상단 "AI Generated"·우하단 로고 모두 화면 밖 |
| D5 | 실행 순서 | 4-01·9-03 완료 → **전략 B: 클립은 9컷만.** ① 1-02(눈 뜨기) → ② 6-01(걷기, 고위험) → ③ 9-01(둘 걷기) → ④ 2-01 → 2-02 → 3-02 → 5-02 → 9-02 → 10-02 | 앞 결과가 뒤 프롬프트를 고칠 정보를 준다. 재생성은 없어도 **다음 컷 프롬프트 수정**은 0크레딧 |

## 1b. 10-03 엔딩 — 확정: 1-01 재사용
"아!!!"는 대화가 아니라 소리이므로 부리 닫힘 + 보이스오버. 스토리보드대로 1-01 클립 재사용, 추가 생성 없음.

## 1c. 4-01 실측에서 얻은 것 (2026-09-21) — **사용자 채택**(카메라 흘끗 비트 수용)
- **단가 18크레딧/3초.** 초당 6이면 24컷 81초 = 486 > 잔여 373 → **약 113 부족**. 대응 후보(사용자 결정): ① 4초 컷 5개→3초, 5초 컷 2개→4초로 단축(−42) ② 정지 컷 일부를 정지 이미지로 대체(컷당 −18; 1-01·3-01·9-04·10-01 후보) ③ v3_0_turbo(시작 프레임 전용) 단가 확인 후 정지 컷 15개에 적용 ④ 크레딧 충전.
- **"looking at the monitor"만으로는 부족**: 모델이 1.1초 끄덕임 뒤 고개를 카메라로 돌려 정면 응시. → 시선을 유지해야 하는 컷에 `He does not turn his head toward the camera and never looks at the viewer.` 삽입(1-03·3-01·4-03·5-01·5-02·5-03·6-03).
- 기술 항목은 전부 통과: 첫 프레임=시작 이미지(차 1.95), 카메라 0.08px, 배경 드리프트 3.0, 부리 닫힘·형태 유지, 손가락·글자·새 물건 없음. 24fps, 716x1284.

## 1d. 9-03 실측에서 얻은 것 (2026-09-21) — 불합격, 정지 이미지 대체 권장
- **"speaks"가 들어가면 부리가 크게 열린다.** tiny/barely/never opens wide 전부 무시(0.75·1.0·2.25·2.5s 입안 노출). → 대화 컷 9-02는 말하라는 문장 삭제, `Her beak stays closed for almost the whole clip and only parts by a hair at the very end, matching the end image` — 시작(닫힘)→끝(살짝) 프레임 보간으로만 움직임.
- **카메라 돌아보기 2회째**(4-01, 9-03). 이 모델의 기본 경향으로 보고 `does not turn his head toward the camera` 문장을 카메라를 봐야 하는 컷(2-01·2-02·1-02·10-01·10-02·9-04·3-02·8-01) 외 **전부에** 삽입.
- 기술 항목(카메라 0.2px, 첫 프레임 일치 2.81, 눈·정체성 유지)은 통과. 48초 생성, 18크레딧(373→355).

## 1e. 크레딧 보호 전략 (2026-09-21, 사용자 지시 "크레딧 계속 소모된다")
현황: 2컷 생성(36크레딧), 1컷 채택·1컷 정지 이미지 대체 예정. 잔여 **355**.

| 안 | 내용 | 필요 크레딧 | 잔여 |
|---|---|---|---|
| A. 전부 클립 | 남은 22컷 전부 v3_0 생성 (75초) | ~450 | **부족 ~95** |
| **B. 동작 컷만 클립 (✅ 확정 2026-09-22)** | 시작+끝 프레임이 있는 **9컷만** 생성(1-02·2-01·2-02·3-02·5-02·6-01·9-01·9-02·10-02, 34초 ≈ 204). **정지 컷 13개는 시작 프레임 정지 이미지**(1~2% 느린 줌으로 정지감 완화, 0크레딧) | ~204 | **~150 남음** — 걷기 2컷 재시도 여유 |
| C. B + 선택 클립 | B에 더해 정지 컷 중 움직임이 가치 있는 2~3개만 클립(1-01 숨, 6-02 숨·잎그림자, 1-03 발) | ~260 | ~95 |

B의 근거: 4-01과 9-03이 보여줬듯 정지 컷의 클립은 **얻는 것(숨·깜빡임)보다 잃을 위험(시키지 않은 동작)이 크다**. 애니매틱에서 정지 프레임 리듬이 이미 확인됐고, 편집 길이가 2초라 정지+미세 줌으로 충분하다. 실제 크레딧은 **움직임이 이야기인 컷**(눈 뜨기·수건·털뭉치·고개·졸음·걷기·돌아보기·눈 감기)에 쓴다.
B를 택하면 turbo 단가 시험(3-01)은 불필요해진다.

## 1f. 1-02 실측 (2026-09-22) — ✅ 통과, 시작+끝 유형 검증
- 끝 프레임 보간이 정확: 첫 1.94 / 끝 1.80. 눈만 1.75→3.0s에 변화, 머리·이불 고정, 카메라 0.01px. 하품·돌아보기 없음.
- **끝 프레임이 있으면 "시키지 않은 동작"이 억제된다.** 정지 컷 2개(4-01·9-03)에서 나온 카메라 돌아보기가 여기선 없었다. 전략 B(시작+끝 9컷만 클립)의 근거가 실측으로 확인됨.
- 변화 시작이 예상(0.8s)보다 늦은 1.75s → 편집 창을 클립 뒤쪽(1.0~3.0s)으로. 이후 시작+끝 컷도 **변화는 후반에 몰린다**고 예상한다.
- tail_image 포함 18크레딧(추가 요금 없음). 생성 166초(시작만 컷의 2~3배).

## 1g. 3컷 회고 — 문구별 적용 여부 (2026-09-22, 4-01·9-03·1-02)

### 잘 적용된 문구 (증거 있음 → 유지)
| 문구 | 증거 | 판정 |
|---|---|---|
| `Static camera, locked-off tripod shot, no camera movement, same composition throughout` | 카메라 이동 0.08 / 0.20 / 0.01px (3/3) | **확실** |
| `the surroundings and objects stay photoreal and completely unchanged` + `No new objects appear` | 배경 드리프트 3.0 / — / 2.3, 새 물건 0건 (3/3) | **확실** |
| `Beak stays closed the whole time` | 4-01·1-02 닫힘 유지 (2/2) | **확실** (말하라는 문장이 없을 때) |
| `Wings stay short and rounded with no fingers` | 손가락 0건 (3/3) | **확실** |
| `3D animated plush character, short velvet fur` | 털 결·정체성 유지 (3/3) | **확실** |
| `The monitor screen stays a blank pale glow with no text` | 글자 0건 (4-01) | 확실 |
| `His eyes stay wide the whole time` | 9-03 눈 크기 유지 | 확실 |
| **끝 프레임 + `exactly matching the end image`** | 1-02 끝 프레임 차 1.80, 시키지 않은 동작 0건 | **가장 강력** |

### 무시된 문구 (→ 쓰지 않거나 프레임으로 대체)
| 문구 | 결과 |
|---|---|
| `looking at the monitor` / `looks to the right` (시선만 지정) | 4-01·9-03 모두 카메라로 돌아섬 |
| `opens and closes only a tiny amount, barely parting, never opens wide` | 9-03 입안이 보이게 활짝 |
| `Only a slight slow nod` | 4-01 끄덕임 + 시키지 않은 회전 |

### 일반화
**장면·카메라·소품·정체성 제약은 지켜지고, 캐릭터의 머리·입 "정도" 제약은 무시된다.** 캐릭터 동작은 끝 프레임으로만 확실히 통제된다. `does not turn his head toward the camera` 부정문은 1-02에서 지켜졌지만 끝 프레임이 함께 있었으므로 **단독 효과는 미검증**.

### 순서 변경의 효과 (실측)
| 순서 | 결과 |
|---|---|
| 스토리보드 순서였다면 | 1-01·1-02·1-03… 정지 컷에 크레딧을 쓰며 진행. 대화 컷 문제는 20번째(9-02)에서, 정지 컷의 임의 동작 문제는 여러 컷을 쓴 뒤에 발견 |
| 실제(유형 표본 먼저) | 4-01 → 시선 문장 16컷 반영 / 9-03 → 9-02 수정 + **전략 B(정지 13컷 정지 이미지, ~234크레딧 절약)** / 1-02 → 끝 프레임 방식 확증 + 편집 창 후반 |
| 성적 | 3컷 54크레딧, 채택 2·대체 1. 클립마다 새 교훈 → 다음 클립 통과(1→실패, 2→실패, 3→통과) |

### 내 예측의 오차 (다음 예상에 반영)
- 변화 시작 시점을 0.8s로 예상했으나 실제 1.75s. **3초 클립의 변화는 후반 절반에 몰린다** → 편집 창은 뒤쪽, 걷기 컷은 "첫 프레임부터" 명시.
- 정지 컷의 "임의 동작" 위험을 첫 컷 전엔 낮게 봤음 → 전략 B로 정정.
- 검수 지표의 부리/눈 박스는 고정 좌표라 머리 이동과 섞임 → 수치는 참고, 판정은 확대 띠로.

## 1h. 6-01 실측 (2026-09-22) — ✅ 통과, 걷기 검증
- 발이 번갈아 딛고 그림자가 따라감(미끄러짐 없음). 0초부터 이동 시작 → `is already walking from the very first frame` 효과 있음(1-02의 "후반 몰림"을 상쇄). 끝 프레임 뒷모습이 카메라 돌아보기를 막음.
- 4초=24크레딧(초당 6 선형). 생성 93초.
- 9-01(둘 걷기)에 그대로 이식: 첫 프레임부터 걷기, `exactly matching the end image`, 4초, 좌우 순서·간격을 긍정문으로.

## 1i. 9-01 실측 (2026-09-22) — ✅ 통과, 둘 걷기 검증
- 좌우 순서·간격 유지, 둘 다 발 딛음, 특징 섞임 없음. `Chang-su always on the left and Mi-sun always on the right` + `same gap` 긍정문 + 끝 프레임 조합이 효과.
- 중간에 뒷모습→3/4 복귀(끝 프레임 수렴). 이상 없음.
- 고위험 2컷(6-01·9-01) 모두 1회 통과 → 남은 5컷은 전부 미세 동작(수건·털뭉치·고개·눈)이라 위험이 더 낮다. 4초=24, 49초 생성.

## 1j. 2-01 실측 (2026-09-22) — ✅ 통과, 물건 조작 검증
- 수건 1장 유지·걸이 비움(`There is exactly one towel; the towel bar stays empty` + 끝 프레임). 날개 손가락 없음. 동작이 1.25s에 시작해 3.0s 정착 — "from the very first frame"이 시작을 앞당김(1-02의 1.75s보다 빠름).
- 5컷 연속 통과(1-02·6-01·9-01·2-01) → 끝 프레임 방식이 안정적으로 확인됨. 4초=24, 67초 생성.

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
Pang Chang-su and Pang Mi-sun lie asleep side by side under one blanket in the morning light. Nothing moves except the slow rise and fall of their breathing under the blanket. Both keep their eyes closed. The phone on the nightstand stays still. He does not turn his head toward the camera and never looks at the viewer. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 이불이 숨결에 아주 천천히 오르내리고 그 외 정지. 10-03에서 그대로 재사용.
**위험·감시 항목**: 낮음 | 눈을 뜨거나 몸을 뒤척임(1-02 역할 침범), 이불이 두 장으로 늘어남, 창밖 밝기 변동
**실패 시 편집 대안(재생성 없음)**: 정지 컷이라 실패해도 시작 프레임을 3초 정지 이미지로 대체(0크레딧, 화질 동일)

### 1-02 — 시작+끝, 3초
**입력**: `outputs/ep01/1-02/start_v1.png` + `end_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Lying on his side on the pillow, Pang Chang-su slowly opens his eyes halfway. Only his eyelids move; his head stays on the pillow facing the same direction the whole time and does not lift or turn toward the camera; the blanket and pillow stay still. By the end his eyes are half open and unfocused, staring ahead, exactly matching the end image. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
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
Pang Chang-su sits on the edge of the bed, sleepy, looking down at the floor. He does not turn his head toward the camera and never looks at the viewer. His dangling feet sway back and forth by a tiny amount. His body, head and wings stay still. Mi-sun stays asleep behind him and does not move. The turned-back blanket stays as it is. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 발끝만 아주 작게 흔들림. 나머지 정지.
**위험·감시 항목**: 중간 | 일어서거나 발이 바닥에 닿음, 미순이 움직임, 이불이 다시 덮임. **5초는 드리프트가 늘어나므로 3초 권장**(편집 2초면 충분)
**실패 시 편집 대안(재생성 없음)**: 발 흔들림이 안 나와도 정지 컷으로 성립. 시작 프레임 정지 이미지 대체 가능

### 2-01 — 시작+끝, 4초
**입력**: `outputs/ep01/2-01/start_v1.png` + `end_v1.png`
**인자**: model=kling-video-v3_0, duration=4, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su begins lowering the light grey towel from the very first frame, slowly and smoothly over the whole clip, bringing it down from his face to his chest with both short rounded flipper wings, revealing his sleepy half-lidded face. By the end the towel rests against his chest, held in both wings, and he looks straight at the camera, exactly matching the end image. He stays standing in the same spot and his head stays at the same height. There is exactly one towel; the chrome towel bar on the right wall stays empty. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 수건이 얼굴→가슴으로 내려오며 얼굴이 드러남. 4초.
**위험·감시 항목**: 중간 | 수건이 두 장이 되거나 걸이에 다시 생김(R25), 날개가 팔처럼 늘어남·손가락, 얼굴이 드러나며 표정이 바뀜(졸림 유지돼야 함)
**실패 시 편집 대안(재생성 없음)**: 끝 프레임 정지 이미지 2초로 대체(얼굴 드러난 상태). 체이닝 컷이라 끝 상태만 맞으면 2-02와 이어짐

### 2-02 — 시작+끝, 3초
**입력**: `outputs/ep01/2-02/start_v1.png` + `end_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su stands still, holding the towel at his chest, looking straight at the camera with a tired, resigned glare. From the very first frame the wet, drooping tuft on top of his head slowly dries and rises, smoothly over the whole clip, until it stands straight up, exactly matching the end image. Nothing else moves at all: his head stays at the same height and angle, his eyes keep the same tired half-lidded look, his wings and the towel stay completely still, and there is exactly one towel. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
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
Pang Chang-su stands still on the platform in profile, waiting sleepily with heavy eyelids. He does not turn his head toward the camera and never looks at the viewer. Only a slow blink and faint breathing. The adult next to him and the people in the distance stand still. The platform screen doors stay closed and no train arrives. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 정지. 눈 한 번 느리게 깜빡.
**위험·감시 항목**: 낮음 | **열차가 들어옴**(모델이 승강장에 열차를 붙이는 경향, R15), 사람들이 걷기 시작, 스크린도어 열림
**실패 시 편집 대안(재생성 없음)**: 시작 프레임 정지 이미지 대체

### 3-02 — 시작+끝, 3초
**입력**: `outputs/ep01/3-02/start_v1.png` + `end_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su slowly turns his head a little toward the camera, from full profile to a three-quarter view, staring blankly along the platform. His eyes stay tired and half-lidded and do not widen. His body and shoulders do not move. Screen doors stay closed, no train. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 고개만 살짝 카메라 쪽으로. 눈은 졸린 채.
**위험·감시 항목**: 낮음 | 눈이 커짐(끝 프레임 v1과 같은 실패), 몸까지 돌아섬, 부리 변형
**실패 시 편집 대안(재생성 없음)**: 끝 프레임 정지 이미지 대체

### 4-01 — 시작만, 3초
**입력**: `outputs/ep01/4-01/start_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su sits at his desk looking at the monitor. Only a slight slow nod of his head and one blink. His wings stay down, out of view behind the desk. The monitor screen stays a blank pale glow with no text. The mug and keyboard stay still. He does not turn his head toward the camera and never looks at the viewer. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 거의 정지. 첫 실행 컷 후보(가장 싸고 부리·카메라 검증).
**위험·감시 항목**: 낮음 | 화면에 글자·UI가 생김, 타이핑 동작으로 손가락 등장, 카메라가 줌인
**실패 시 편집 대안(재생성 없음)**: 시작 프레임 정지 이미지 대체

### 4-02 — 시작만, 3초
**입력**: `outputs/ep01/4-02/start_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Two short rounded flipper wing tips rest on the keyboard, completely still. The monitor screen stays a blank pale glow with no text. Nothing moves except a faint, barely visible settling of the wings. The wings stay short and rounded with no fingers, no hands, no thumbs. He does not turn his head toward the camera and never looks at the viewer. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 정지 인서트. 타자 소리는 편집에서(W12). **손가락 위험을 없애기 위해 두드리는 동작을 넣지 않음.**
**위험·감시 항목**: 낮음(정지로 고정 시) | 두드리게 하면 **손가락 생성 위험이 에피소드 최고**. 화면에 글자 생성
**실패 시 편집 대안(재생성 없음)**: 시작 프레임 정지 이미지 대체(사실상 동일 결과)

### 4-03 — 시작만, 3초
**입력**: `outputs/ep01/4-03/start_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su glares at the monitor with narrowed, annoyed eyes. His head pushes very slightly forward toward the screen and holds there. He does not turn his head toward the camera and never looks at the viewer. His expression stays the same flat glare. Nothing else moves. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
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
Pang Chang-su sits at the table gazing at the stew with wide, sparkling eyes and a happy face. He does not turn his head toward the camera and never looks at the viewer. A faint wisp of steam rises from the stone pot. He, the dishes, the spoon and chopsticks on the napkin, and the customer behind him all stay still. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
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
Pang Chang-su sits still, holding the spoon motionless in his right wing above the pot, his cheeks slightly full. He does not turn his head toward the camera and never looks at the viewer. His happy curved eyes slowly grow heavier and sleepier over the clip as drowsiness sets in; that is the only thing that changes. The spoon, the dishes, the open rice bowl and its lid stay exactly where they are. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 눈만 천천히 무거워짐(시작+끝 보간). 씹기 동작은 9-03 교훈으로 삭제(입이 열림), 식기 소리로 대신. 숟가락 고정.
**위험·감시 항목**: 중간 | **부리가 열려 씹는 입이 됨**(스토리보드 대비책: 실패 시 부리 닫힘 고정), 숟가락이 입으로 감·음식이 줄어듦, 볼이 과하게 부풂
**실패 시 편집 대안(재생성 없음)**: 부리가 열린 구간을 잘라내고 앞부분만 쓰거나 시작 프레임 정지 이미지 3초

### 5-03 — 시작만, 3초
**입력**: `outputs/ep01/5-03/start_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su sits before the empty dishes, heavy-eyed and drowsy. He does not turn his head toward the camera and never looks at the viewer. His head dips forward once, very slightly, in a small doze and comes back up; the movement is tiny. Both wings stay on the table. The empty pot, the spoon inside it and the dishes stay still. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**자막(속마음·혼잣말 → 보이스오버, 부리 닫힘)**: 졸려...
**예상 시나리오**: 고개 한 번 꾸벅.
**위험·감시 항목**: 낮음 | 눈이 완전히 감김·잠듦, 머리가 테이블까지 떨어짐, 빈 그릇에 음식이 다시 생김(R25)
**실패 시 편집 대안(재생성 없음)**: 시작 프레임 정지 이미지 대체

### 6-01 — 시작+끝, 4초 (5→4 확정 2026-09-22: 이동 0.8m·편집 3초에 충분, 드리프트·크레딧 절감)
**입력**: `outputs/ep01/6-01/start_v1.png` + `end_v1.png`
**인자**: model=kling-video-v3_0, duration=4, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su is already walking from the very first frame, at a steady waddling pace to his right along the pavement, from beside the left tree to the front of the bench, keeping his body and head facing to his right the whole time. Each step lands on the paving and rolls forward; his feet do not slide. By the end he stands still in front of the bench, exactly matching the end image. The trees, bench and leaf shadows stay still. He does not turn his head toward the camera and never looks at the viewer. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 3~4걸음 뒤뚱 이동 후 벤치 앞에서 정지. 에피소드 첫 걷기.
**위험·감시 항목**: **높음** | **제자리 걸음·발 미끄러짐**(B6 1순위), 크기 변화, 잎 그림자 깜빡임, 카메라가 따라 팬. 걷기는 05a §8 3순위 검증 항목
**실패 시 편집 대안(재생성 없음)**: 시작 프레임 1.5초 + 끝 프레임 1.5초 정지 점프컷. 또는 클립의 첫 2걸음만 쓰고 끝 프레임 정지로 마무리

### 6-02 — 시작만, 3초
**입력**: `outputs/ep01/6-02/start_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su stands with his eyes closed, face lifted slightly toward the sun, breathing slowly and calmly. Dappled leaf shadows drift very slowly across his face. His eyes stay closed the whole time and his head stays still. He does not turn his head toward the camera and never looks at the viewer. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
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
Pang Chang-su sits slumped at his desk with half-closed eyes, staring at the monitor. He does not turn his head toward the camera and never looks at the viewer. One tiny slow nod of his head and one slow blink. His posture stays slumped. The monitor screen stays a blank pale glow with no text. Nothing else moves. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
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
Pang Chang-su stands beside his desk, beaming, completely still except for a slow, contented rise and fall of his body as he breathes. His feet stay planted on the carpet and his wings stay short at his sides. The dark monitor, the chair and the mug stay still. He does not turn his head toward the camera and never looks at the viewer. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
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
Pang Chang-su stands facing the camera at three-quarters, beaming, still except for a slow happy breath. His feet stay planted. The adult behind him stays still. The screen doors stay closed and no train arrives. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. His beak stays exactly as in the image, slightly open in a smile, and does not move. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**자막(속마음·혼잣말 → 보이스오버, 부리 닫힘)**: 빨리집가!!!
**예상 시나리오**: 몸이 좌우로 아주 살짝. 부리는 살짝 열린 채 미세.
**위험·감시 항목**: 낮음 | 부리가 크게 벌어져 말함, 열차 진입, 걷기 시작
**실패 시 편집 대안(재생성 없음)**: 시작 프레임 정지 이미지 대체

### 9-01 — 시작+끝, 4초 (5→4 확정 2026-09-22: 6-01과 같은 0.8m 이동)
**입력**: `outputs/ep01/9-01/start_v1.png` + `end_v1.png`
**인자**: model=kling-video-v3_0, duration=4, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su on the left and Pang Mi-sun on the right are already walking from the very first frame, side by side at the same steady waddling pace to their right along the path, seen from behind at an angle, both keeping their bodies and heads facing to their right the whole time. Each step lands on the path and rolls forward; their feet do not slide. They stay side by side with the same gap between them, Chang-su always on the left and Mi-sun always on the right. By the end they stand still a short way further along the path, exactly matching the end image. The lamps, shrubs and buildings stay still. Neither of them turns toward the camera or looks at the viewer. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush characters, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Both beaks stay closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 둘이 같은 속도로 3걸음. 에피소드 최고 난도.
**위험·감시 항목**: **높음** | 제자리 걸음, **둘의 속도가 달라 간격 변화**, 좌우 바뀜·얼굴 섞임, 카메라 쪽으로 돌아섬. 스토리보드 대비책: 싱글 컷 2개 분할(그러나 재생성 없음 원칙이면 아래 대안)
**실패 시 편집 대안(재생성 없음)**: 시작·끝 프레임 정지 점프컷(1.5+1.5). 또는 클립 앞 2초만 채택

### 9-02 — 시작+끝, 3초
**입력**: `outputs/ep01/9-02/start_v1.png` + `end_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Mi-sun slowly turns her upper body and head to her right, toward the left side of the frame, looking at her husband off-frame with a bright cheerful smile as she speaks. By the end she faces three-quarters to the left. Her lower body stays in place. Her husband does not appear in the frame. She keeps looking to the left toward him and does not turn to face the camera. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. As she speaks a short line, her beak opens and closes only a tiny amount, barely parting, just enough to show he is talking; it keeps its exact small triangular shape and size and never opens wide, stretches, or turns into lips. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
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
Pang Chang-su looks to the right with wide sparkling eyes and a big delighted smile, his head tipping slightly forward with excitement as he answers. His eyes stay wide the whole time. Nothing else moves. He does not turn his head toward the camera and never looks at the viewer. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. As he speaks a short line, his beak opens and closes only a tiny amount, barely parting, just enough to show he is talking; it keeps its exact small triangular shape and size and never opens wide, stretches, or turns into lips. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
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
Pang Chang-su and Pang Mi-sun sit close together on the sofa watching the TV, which is where the camera is, completely still except slow blinks and breathing. The empty pot and chopsticks on the table stay still. Both beaks stay closed. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 정지 + TV 불빛 미세 깜빡임.
**위험·감시 항목**: 낮음 | 서로 마주 보거나 말함, 불빛 깜빡임이 과함, 냄비에 라면이 다시 생김(R25)
**실패 시 편집 대안(재생성 없음)**: 시작 프레임 정지 이미지 대체(TV 불빛은 편집에서 밝기 흔들기 가능)

### 10-01 — 시작만, 3초
**입력**: `outputs/ep01/10-01/start_v1.png`
**인자**: model=kling-video-v3_0, duration=3, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Pang Chang-su lies on his side in bed at night with half-open sleepy eyes, staring blankly ahead; Mi-sun sleeps beside him with her eyes closed. Only slow breathing. The bedside lamp stays lit and steady. Nothing else moves. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**예상 시나리오**: 정지. 눈 반쯤 뜬 채.
**위험·감시 항목**: 낮음 | 눈이 감김(10-02 역할 침범), 스탠드 깜빡임, 이불 증식
**실패 시 편집 대안(재생성 없음)**: 시작 프레임 정지 이미지 대체

### 10-02 — 시작+끝, 4초
**입력**: `outputs/ep01/10-02/start_v1.png` + `end_v1.png`
**인자**: model=kling-video-v3_0, duration=4, resolution=720p, prefer_multi_shots=false, enable_audio=false, imageCount=1
**프롬프트**
```
Lying on his side on the pillow at night, Pang Chang-su slowly closes his half-open eyes and drifts off to sleep. Only his eyelids move; his head stays on the pillow. By the end his eyes are fully closed. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur; the surroundings and objects stay photoreal and completely unchanged. Beak stays closed the whole time. No other characters appear. No new objects appear. Wings stay short and rounded with no fingers.
```
**자막(속마음·혼잣말 → 보이스오버, 부리 닫힘)**: 내일도 화이띵...!
**예상 시나리오**: 눈만 천천히 감김. 1-02의 역방향.
**위험·감시 항목**: 낮음 | 눈이 다시 뜨임, 머리 움직임
**실패 시 편집 대안(재생성 없음)**: 끝 프레임 정지 이미지 대체(암전으로 이어지므로 자연스러움)
