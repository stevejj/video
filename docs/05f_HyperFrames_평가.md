# 05f. HyperFrames 평가 (2026-10-07, 사용자 요청으로 다운로드)

소스: `external/hyperframes/`(gitignore, `github.com/heygen-com/hyperframes` 얕은 클론 302MB). CLI는 `npx hyperframes@latest`(v0.8.139)로 실행, 로컬 렌더는 무료·계정 불필요(HeyGen 크레딧 안 씀).

## 무엇인가
HTML+CSS+GSAP로 영상을 "코딩"하고 헤드리스 Chrome으로 프레임을 찍어 MP4로 만드는 오픈소스 프레임워크. 에이전트용 스킬 21개(기획→HTML→린트→프리뷰→렌더), Studio(GUI 타임라인 편집기), 오디오 믹서(페이드·덕킹·EQ·컴프·리버브를 `data-fx-chain`으로), 자막 스킬(자동 전사·스타일 35종), 등록소 블록(차트·전환 등).

## 이 환경에서 검증한 것
- `render` 성공: 1080×1920 4초, 120프레임, **15.6초**(소프트웨어 GPU). 결과 `outputs/hyperframes_test/layout_test_4s.mp4`, 소스 `index.html`.
- 우리 레이아웃(02a §11 30/40/30, 제목 2줄 흰·노랑, 채널명, 세로 40% 창에 Kling 클립 오프셋 크롭, 시간 카드, 자막 팝인(GSAP back.out), 음성 mp3)을 전부 HTML/CSS로 재현. 한글 폰트는 `@font-face`로 NotoSansKR 지정.
- 필요 설정(이 컨테이너): ffmpeg/ffprobe가 PATH에 없어 npm `ffmpeg-static`·`ffprobe-static`을 받고 `HYPERFRAMES_FFMPEG_PATH`/`HYPERFRAMES_FFPROBE_PATH`로 지정. Chrome은 `npx hyperframes browser ensure`로 자동 설치됨.

## 우리 파이프라인과 비교
| 항목 | 지금(tools/assemble_ep01.py, ffmpeg) | HyperFrames |
|---|---|---|
| 텍스트(제목·자막·카드) | PIL로 PNG 렌더 후 overlay, 팝인은 scale 수식 | CSS 텍스트 + GSAP 애니메이션(팝·흔들림·크기 점증·색) — 훨씬 자유롭고 수정 즉시 |
| 효과(줌 펀치·푸시인·흔들림) | zoompan/crop 수식, 디버깅 어려움 | CSS transform 트윈 한 줄 |
| UI 인서트(카운터·화살표·시계) | 별도 PNG 제작 필요 | HTML로 바로(숫자 올라가는 애니메이션 등) |
| 오디오 믹스 | amix/sidechaincompress/loudnorm 필터 체인 | `data-volume`·자동화 레인·덕킹·이펙트 체인, 프리뷰=렌더 동일 |
| 편집 GUI | 없음(JSON 수정 → 재조립) | Studio에서 타임라인·캔버스 드래그, 변경 이력 |
| 렌더 속도 | 62초 편 약 1~2분 | 4초=16초 → 60초 편 약 4~5분 예상 |
| 결정성 | ffmpeg 그대로 | 동일 입력=동일 출력 보장 설계 |

## ep01을 이걸로 편집할 수 있는가
**가능.** 우리가 이미 가진 JSON(`edit_list.json` 컷 순서·길이·오프셋, `band_offsets.json`, `text_overlay.json`, `sfx/sfx_list.json`, `voice_profile.json`의 lines)이 그대로 HyperFrames 구성 요소(클립 `<video data-start/duration/data-media-start>`, 텍스트 `<div>` + GSAP, `<audio data-start data-volume>`)로 1:1 대응된다. 변환기 `tools/ep_to_hyperframes.py`를 만들면 ep01·ep02 모두 같은 JSON에서 HTML을 생성하고, 이후 세부 조정은 Studio나 HTML 직접 수정으로 한다.
- 남는 검증: 27컷 전체 렌더 시간·메모리, 자막 외곽선(현재 text-shadow 4중 — `-webkit-text-stroke`로 교체 가능), BGM 덕킹을 자동화 레인으로 옮겼을 때 음량이 v10과 같은지(loudnorm 상당 기능 확인 필요).
- 단점: 한 편당 HTML 1개가 늘어나고, 렌더에 Chrome이 필요해 로컬 PC에서 돌리려면 Node 22+ 설치가 필요.

## ep01 v11 — HyperFrames로 0크레딧 역동성 (2026-10-07, 사용자: "Kling 안 쓰고 HyperFrames로 할 수 있는 부분만")
파이프라인: `outputs/ep01/hf_fx.json`(컷별 카메라·펀치·흔들림·퍼펫 계획) → `tools/ep_to_hyperframes.py`(edit_list·band_offsets·text_overlay·hf_fx → `outputs/ep01/hf/index.html`) → `tools/hf_render.sh ep01 v11`(린트·렌더 24fps·**v10 오디오 mux**). 오디오 믹스는 검증된 ffmpeg v10 트랙을 그대로 쓴다(HyperFrames 믹서로 옮기는 건 후순위).

적용한 것(02c §3)
- 정지 컷: 2% 줌 → **푸시인 8~12% + 손떨림 드리프트(±5px)**, 컷마다 방향을 바꿈(1-03·9-04 풀아웃, 3-01 팬, 5-03 틸트다운).
- 리액션 컷 줌 펀치 + 흔들림: 4-03(모니터 뚫어), 5-01(밥), 7-01(퇴근, 반짝 ✦ 6개), 8-01(빨리집가), 9-03(끄래), 10-03(아!!!, 흔들림 커짐).
- 자막: 팝인(back.out) / 외침("!!")은 0.3→1.18→1 오버슈트 + 회전 + 흔들림. 시간 카드 슬라이드 인. 4-02 타이핑 지터.
- **컷아웃 퍼펫(4-02)**: 정지 프레임에서 날개 2개를 오려 알파 레이어로 만들고(색 마스크+손 모양, 배경은 inpaint) GSAP로 번갈아 들썩임(회전 ±5°, 14px, 초당 ~9회). 자산 `outputs/ep01/4-02/puppet/`. **"팔이 움직이는" 0크레딧 방법은 이것뿐**이며, 날개 끝처럼 윤곽이 단순하고 배경이 평평한 컷에서만 통한다. 숟가락 들기·세수·일어나기처럼 부위가 겹치거나 형태가 바뀌는 동작은 퍼펫으로 안 되고 Kling이 필요하다.

HyperFrames의 "생성 영상" 기능 확인: `media-use` 스킬의 image-to-video는 **HeyGen 사진 아바타(사람 얼굴 립싱크, HeyGen 크레딧)**이고, 애니메이션 런타임은 GSAP·CSS·Lottie·Three.js·anime.js 등 **이미 그려진 요소를 움직이는 것**이다. 캐릭터 그림 자체를 새로 그려 팔을 움직이는 기능은 없다.

결과: `outputs/ep01/roughcut/ep01_roughcut_v11_hf.mp4`(최종 v11c: 카메라·펀치·자막 + 퍼펫·드리프트, 4-02 창 44%·자막 상단). 정지 초 지표(verify_motion)는 픽셀 변화량 기준이라 느린 푸시인을 "정지"로 세는 한계가 있음 → 지표보다 눈으로 판단.

### 퍼펫 2호: 5-02 숟가락 (2026-10-07, 사용자 "밥먹는 느낌도 낼 수 있는 거 아니야?")
- 결론: **어렵지만 가능**. 날개+숟가락을 한 레이어로 오려(타원 마스크 + 금속 픽셀) 어깨를 피벗으로 -46° 회전 + 34px 상승 → 숟가락 머리가 부리에 닿는다. 배경은 inpaint 후 **원래 숟가락 자리를 위쪽 배 털로 세로 패치**(inpaint만으로는 숟가락 잔상이 남음).
- 되는 조건: 움직일 부위가 한 덩어리로 오려지고(날개+숟가락), 움직인 뒤 드러나는 배경이 단순 질감(배 털·의자)이며, 목적지(부리)가 레이어 "앞"에 있어도 겹쳐 보이는 게 자연스러운 경우.
- 안 되는 것: 부리가 열리거나 볼이 부푸는 변형, 몸을 일으키는 자세 변화(윤곽 자체가 바뀜), 세수처럼 두 날개가 얼굴을 가리며 문지르는 동작(가려지는 부분을 새로 그려야 함). 이런 건 Kling.
- 자산 `outputs/ep01/5-02/puppet/`, 계획은 `hf_fx.json` 5-02 `puppet.layers[].keys`(키프레임 방식; 변환기가 `pivot`→transform-origin 자동 계산).

### v11e (2026-10-07, 사용자 지시)
- 5-02 숟가락 퍼펫 **제거**(원래 정지+푸시인). 2-02 "가기 싫다..": Kling 클립(털뭉치가 마르며 일어남) 대신 **정지 프레임 + 눈 깜빡임 퍼펫 3회**(눈꺼풀 = 눈 위 45px 털을 타원으로 복사 + 얇은 감은 눈 선, scaleY 0→1, 0.07s 감고 0.1s 유지 0.09s 뜸), 털뭉치 고정. 9-04 TV: 두 머리를 오려(창수는 털뭉치 포함) 목 아래 피벗으로 **끄덕임**(y 5px·회전 2°, 서로 엇박자 3회).
- 변환기: 레이어 `init`(초기 상태)와 임의 속성 키프레임(`scaleY` 등) 지원. 단일 컷 테스트는 `--edit <컷 1개짜리 edit_list>`로 15초 안에 확인.
