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
