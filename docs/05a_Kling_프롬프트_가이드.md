# 05a. Kling 프롬프트 가이드 (v0.1, 2026-09-16 조사)

> 목적: Kling에 "어떻게 시키면 원하는 영상에 가깝게 나오는지"를 우리 프로젝트 기준으로 정리.
> 출처 표기: [공식] = kling.ai 퀵스타트·블로그, [MCP] = 이 세션의 who_am_i 조회, [커뮤니티] = 블로그·튜토리얼(검증 강도 낮음).
> 확인 못 한 것은 맨 끝 "미확인" 절에 따로 적었다. 미확인 항목은 동작 사전 테스트(G3b)에서 직접 검증한다.

## 1. 핵심 원칙 8가지

1. **이미지가 주 동인, 프롬프트는 동작만.** 이미지→영상에서 공식 공식은 "주체 + 동작"뿐이다. 이미지에 이미 있는 것(색, 옷, 배경)을 다시 설명하지 않는다. 20~40단어. [공식 image-to-video-guide] [커뮤니티 veed]
2. **한 클립에 동작 하나.** "5초 안에 끝나는 단순한 동작"이 공식 권장. 여러 지시가 섞이면 모델은 무시하거나 컷을 만든다. [공식 text-to-video-prompt-guide]
3. **이미지에서 일어날 법한, 물리적으로 가능한 동작만.** "이미지와 크게 벗어난 설명은 카메라 컷이나 전환을 유발할 수 있다." [공식 image-to-video-guide] → 우리 규칙집 R4와 동일.
4. **시작 프레임과 끝 프레임은 최대한 비슷하게.** 차이가 크면 "렌즈 전환(샷 스위치)"이 생긴다. 같은 구도, 같은 앵글, 같은 조명. 바뀌는 건 캐릭터의 자세·위치뿐. [공식 ai-video-start-end-frames]
5. **끝 상태를 문장으로 명시.** "~로 바뀐다", "~에 도달한다"처럼 도착점을 쓰면 멈춤·제자리 동작이 줄어든다. [커뮤니티 veed, insmind]
6. **카메라는 매번 고정 선언.** 카메라 지시가 비어 있으면 임의로 움직인다. 공식 어휘: "Static camera". 커뮤니티 강화 문구: "locked-off tripod shot, completely static camera". [공식 camera-control-guide] [커뮤니티 glbgpt]
7. **정확한 숫자와 복잡한 물리는 못 한다.** "공이 튀는" 류의 물리, 개수 지정은 신뢰 불가. [공식 text-to-video-prompt-guide]
8. **긴 클립일수록 오차가 누적된다.** 5초 기본, 3초도 가능(v3.0). 10초 이상은 시작·끝 차이가 큰 경우(낮→밤)에만. [공식 drift-consistency-guide] [커뮤니티 다수]

## 2. 시작+끝 프레임 (우리 파이프라인의 기본 모드)

- 사용 모델: **kling-video-v3_0** (first_image + tail_image, 3~15초, Element 최대 3개 바인딩 가능). [MCP][공식 element-library-3]
- 두 프레임 조건:
  - 같은 카메라 위치 번호, 같은 화면비(9:16), 같은 조명·시간대.
  - 배경 소품 위치 동일. 캐릭터 자세·위치만 다름.
  - 와이드↔클로즈업처럼 프레이밍이 다르면 안 됨.
- 프롬프트는 "전환"을 서술: `[캐릭터]가 [시작 상태]에서 [끝 상태]로 [속도감]하게 이동한다. 카메라 고정.` [커뮤니티 cliprise]
- Gemini에서 끝 프레임을 만들 때: 시작 프레임을 참조로 넣고 "동작이 끝난 상태만 바꿔라, 나머지는 픽셀 단위로 동일하게"를 요구한다. → `01a` 프롬프트 문서에 끝 프레임 템플릿 추가 예정.
- 끝 프레임만 넣는 건 지원 안 됨(O1 기준). 항상 시작 프레임과 함께. [공식 o1-user-guide]
- v2_6에서 끝 프레임을 쓰면 오디오 불가. v3_0은 오디오 기본 꺼짐. [MCP]

## 3. 우리 프로젝트용 프롬프트 템플릿

### 3.1 기본 템플릿 (v3_0, 시작+끝 프레임)
```
{캐릭터 영문명} {동작 한 문장, 이미지 안에서 가능한 것}. {끝 상태 한 문장}. {속도어: slowly / at a steady pace}. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur. {말 안 하는 컷: Beak stays closed the whole time. / 말·웃음 컷: The beak opens and closes only very slightly, keeping its exact shape and size.} No other characters appear. No new objects appear.
```
예시(걷기):
```
Pang Chang-su walks at a steady waddling pace from the left side of the living room to the sofa on the right. By the end he stands still beside the sofa, facing the camera. Static camera, locked-off tripod shot, no camera movement, same composition throughout. 3D animated plush character, short velvet fur. Beak stays closed the whole time. No other characters appear.
```
예시(문 밀고 나가기, 규칙집 R1·R3):
```
Pang Chang-su places one wing on the lever handle and pushes the front door open outward, away from the camera, into the corridor. By the end the door is fully open and he stands in the doorway. No keypad, no password. Slow, deliberate movement. Static camera, locked-off tripod shot, no camera movement. 3D animated plush character. Beak stays closed.
```

### 3.2 단어 규칙
- 쓰는 단어: `walks`, `turns`, `sits down`, `stands up`, `picks up`, `places`, `pushes`, `looks toward`, `slowly`, `steady`, `by the end`, `static camera`.
- 피하는 단어: `cinematic`, `detailed`, `realistic`(실사 쪽으로 끌려감 [커뮤니티 neolemon]), `dramatic`, `fast`, `suddenly`, 숫자 지정, 두 개 이상의 카메라 동작.
- 스타일 고정어: `3D animated plush character, short velvet fur` (프롬프트마다 동일하게 반복. "Pixar style" 같은 브랜드명보다 구체 서술이 낫다 [커뮤니티 neolemon]).
- 캐릭터 설명 블록은 **매번 글자 단위로 동일**하게 유지 [커뮤니티 atlascloud]. 단, 반복 서술만으로 캐릭터가 고정되진 않으며 Element 등록이 본질적 해법 [커뮤니티 magichour].

### 3.3 네거티브
- v3_0 MCP 인자 목록에 negative_prompt가 **없다**. [MCP] fal API에는 있고 기본값 "blur, distort, and low quality". [API]
- 따라서 우리는 금지 사항을 **긍정문으로 프롬프트 안에** 쓴다: `Beak stays closed`, `wings stay short and rounded with no fingers`, `the tuft stays on top of the head`, `no other characters appear`, `background stays exactly the same`.
- 공식이 제안한 네거티브 어휘(참고): blur, distort, extra limbs, shaky camera, morphing features, changing clothes. [공식 drift-guide, subject-binding]

### 3.4 멀티 참조 모델(v3_0_omni, o1)을 쓸 때
- 입력 image_1..7을 프롬프트에서 `图片1`..`图片7`로 지칭. UI에서는 `@이름`이지만 MCP는 중국어 표기. [MCP]
- 예: `图片1 is Pang Chang-su. 图片2 is the living room. Pang Chang-su from 图片1 stands in the living room of 图片2 and slowly sits down on the sofa. Static camera...`
- 영상 입력이 있으면 참조는 최대 4개. [공식 omni-guide]
- 시작+끝 프레임 파이프라인이 기본이고, omni는 "참조가 많이 필요한 샷"(투샷+소품)에만 쓴다.

## 4. Element (캐릭터 등록)

- 등록 이미지: 최소 2장(메인 1 + 보조 1), 최대 4장(메인 1 + 보조 3). **메인은 정면**이 일관성에 유리, 보조는 다른 각도. [공식 element-library-3] MCP는 cover + secondary 1~3, 태그 필수. [MCP]
- 우리 등록안(Q43 승인 후):
  - 팽창수: cover=`pang-changsu_hires_front.png`, secondary=`3q_left`, `body_side`, `body_back`
  - 팽미순: cover=`pang-misun_hires_front.png`, secondary=`3q_left`, `body_side`, `body_back`
  - 태그: Characters (Animals가 아니라 Characters로. 얼굴 인식 기준이 사람 얼굴 쪽이라 테스트로 비교)
- 프롬프트 참조: MCP는 `<<<id>>>` + elements 인자 `[{"id":"...","bindName":"Changsu"}]`. [MCP]
- v3_0 시작+끝 프레임에 바인딩 시 최대 3개. 우리는 2개(두 캐릭터)라 여유. [공식]
- 공식 조언: "고르게 조명된 고품질 마스터 이미지", 네거티브(또는 우리 식 긍정문)로 "morphing features"를 2차 가드로. [공식 subject-binding]
- 주의: 등록했다고 프롬프트에서 캐릭터 설명을 빼지 않는다. id + 설명 병행. [MCP 도구 설명]

## 5. 모션 컨트롤 (사람이 찍은 동작을 캐릭터에 입히기)

- 참조 영상 조건 [공식 motion-control-guide]:
  - 3~30초(캐릭터 방향을 이미지에 맞추는 모드는 3~10초). 짧은 변 340px 이상.
  - **한 사람만, 한 번에 찍은 단일 샷, 카메라 고정(삼각대), 컷 없음.**
  - 전신과 머리가 항상 보이고 가려지지 않음.
  - 동작은 "범위는 넓게, 속도는 중간, 이동 거리는 최소". 빠른 동작 금지.
  - 실제 사람 동작 권장. "스타일화된 인간형·동물형도 인식되지만 사람 동작이 더 정확."
- 캐릭터 이미지: 참조 영상과 같은 프레이밍(전신↔전신). 캐릭터가 움직일 여백을 남길 것. 짧은 변 300px 이상, 피사체가 화면의 5% 이상.
- 방향 모드: `motion_direction`(영상 방향·카메라워크 따름, 30초까지) / `image_direction`(이미지 방향 유지, 프롬프트로 카메라 지시 가능, 10초까지). 우리는 **image_direction** 기본(카메라 고정 유지). [MCP][공식]
- 프롬프트는 "연출 지시"만(조명, 분위기). 동작을 세세히 지시하면 참조 동작과 충돌. [공식 motion-transfer-tutorial]
- **위험 요소**: Element 바인딩은 "얼굴 정보만" 쓰고, 다른 종의 얼굴(고양이→사람)은 품질이 떨어진다고 명시. 펭귄 얼굴이 인식되는지는 **테스트 전에는 모른다.** [공식]
- 사용자가 찍을 참조 영상 목록(Q42): 걷기(좌→우 3걸음), 문 밀고 나가기, 앉기, 바닥 물건 집기, 돌아서기. 각 5초, 세로, 삼각대(또는 벽에 기대 고정), 전신 프레임, 단색 배경.

## 6. 멀티샷·오디오·길이 설정

| 항목 | 설정 | 근거 |
|---|---|---|
| prefer_multi_shots | **false 명시** | 공식은 "기본 꺼짐"이지만 MCP v3_0 기본값은 true로 표시됨. 우리는 샷을 직접 나누므로 끈다. [공식 3.0 guide][MCP] |
| enable_audio | **false** | 입 동작 유발 가능성, 비용. 효과음·BGM은 후반. v2_6은 끝 프레임과 병용 불가. [MCP][커뮤니티] |
| duration | **5** 기본, 미세 동작 3, 낮→밤 등 큰 변화만 8~10 | [공식][커뮤니티] |
| resolution | 테스트 720p, 본편 1080p | 비용 |
| imageCount | 테스트 1, 본편은 어려운 샷만 2 | 비용 |

멀티샷을 켤 일이 생기면 공식 형식은 `[Shot 1: Wide shot] ... [Shot 2: Medium shot] ...`이고 최대 6샷, 총 3~15초. [공식 multi-shot-guide]

## 7. 실패 유형별 대응 (00b B6 표와 연결)

| 증상 | Kling 쪽 원인 | 대응 |
|---|---|---|
| 캐릭터 붕괴 | 긴 클립, 참조 부재 | Element 등록, 5초 이하, 설명 블록 동일 유지 |
| 제자리 걸음·발 미끄러짐 | 끝 상태 없음, 동작 서술 모호 | 끝 프레임 + "by the end he stands at ~" + 걸음 역학 서술("each step lands then rolls forward") [커뮤니티 atlascloud] |
| 갑작스런 컷·앵글 변화 | 시작·끝 프레임 차이 큼, 프롬프트가 이미지와 불일치 | 프레임 재생성(구도 통일), 프롬프트에서 이미지 밖 요소 삭제 |
| 카메라 흔들림·줌 | 카메라 지시 없음 | "Static camera, locked-off tripod shot" 항상 포함 |
| 손가락·팔 생김 | 날개 조작 장면 | 날개 서술 고정, 물건 조작은 인서트 샷(S5)으로 분리 |
| 실사화 | cinematic/realistic 어휘 | 어휘 금지, 스타일 고정어 반복 |
| 부리 움직임 | 모델이 기본적으로 입 움직임 추가 경향 [커뮤니티] | "Beak stays closed the whole time" 명시 + 오디오 끔. **신뢰도 미확인 → 테스트 1순위** |

## 8. 동작 사전 테스트(G3b)에서 먼저 확인할 것

우선순위 순. 각 1클립, 720p, 5초.
1. 부리 닫힘 유지 여부 (같은 프레임으로 문구 유무 비교 2클립)
2. Element 등록 유무에 따른 얼굴 유지 차이 (같은 프레임·프롬프트 2클립)
3. 걷기(시작+끝 프레임): 제자리 걸음 여부
4. 문 밀고 나가기(R1·R3 검증)
5. 앉기 / 일어서기
6. 모션 컨트롤: 사용자 참조 영상 1개로 펭귄 인식 여부
7. 투샷에서 두 캐릭터가 서로 섞이지 않는지(Element 2개 바인딩)

## 9. 미확인 (테스트로 검증할 것)
- 부리 닫힘을 확실히 유지하는 방법. 공식 지침 없음, 커뮤니티 일화만.
- v3_0에서 네거티브 프롬프트 효과(인자 자체가 MCP에 없음).
- 시작·끝 프레임이 얼마나 달라도 되는지의 수치 기준.
- 오디오 켜짐이 동작 품질에 미치는 영향(비용·"초안엔 끄라" 조언만).
- 펭귄 캐릭터가 모션 컨트롤에서 인식되는지.
- 커스텀 멀티샷의 정확한 프롬프트 문법.
- 출력 fps.

## 10. 출처
- 공식: kling.ai/quickstart/text-to-video-prompt-guide, /image-to-video-guide, /ai-video-start-end-frames, /klingai-element-library-3-user-guide, /klingai-video-3-model-user-guide, /klingai-video-3-omni-model-user-guide, /klingai-video-o1-user-guide, /motion-control-user-guide, /klingai-video-26-audio-user-guide; kling.ai/blog/kling-ai-prompt-guide, /kling-ai-camera-control-video-guide, /fix-ai-video-drift-consistency-guide, /kling-3-subject-binding-character-consistency, /kling-video-3-multi-shot-guide, /ai-motion-transfer-video-tutorial
- API 미러: fal.ai kling-video v3/o1/v2.6 페이지, docs.kie.ai kling-3-0, github.com/aself101/kling-api
- 커뮤니티: blog.fal.ai kling-3-0-prompting-guide, veed.io kling 가이드, insmind, cliprise, atlascloud, magichour, glbgpt, videoai.me, neolemon, oakgen, phygital.plus, apidot
