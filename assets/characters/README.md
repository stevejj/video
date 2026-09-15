# 캐릭터 참조 이미지

## 파일 목록

| 캐릭터 | 파일 | 내용 |
|---|---|---|
| 팽미순 | `pang-misun/pang-misun_sheet_clean.png` | 캐릭터 시트 전체 (워터마크 제거) |
| 팽미순 | `pang-misun/pang-misun_face_front.png` | 얼굴 정면 대형 |
| 팽미순 | `pang-misun/pang-misun_body_front.png` | 전신 정면 |
| 팽미순 | `pang-misun/pang-misun_body_side.png` | 전신 측면 (좌향) |
| 팽미순 | `pang-misun/pang-misun_body_back.png` | 전신 뒷모습 |
| 팽창수 | `pang-changsu/pang-changsu_sheet_clean.png` | 캐릭터 시트 전체 (워터마크 제거) |
| 팽창수 | `pang-changsu/pang-changsu_face_front.png` | 얼굴 정면 대형 |
| 팽창수 | `pang-changsu/pang-changsu_body_front.png` | 전신 정면 |
| 팽창수 | `pang-changsu/pang-changsu_body_side.png` | 전신 측면 (좌향) |
| 팽창수 | `pang-changsu/pang-changsu_body_back.png` | 전신 뒷모습 |
| 원본 | `original/*_sheet_original.png` | 업로드 원본 (워터마크 포함, 수정 금지) |

원본 해상도 768x1376. 크롭 이미지는 시트에서 잘라낸 것이라 해상도가 낮다(정면 전신 약 280x335).
G1 단계에서 고해상도 턴어라운드를 새로 만들어 이 크롭들을 대체할 예정이다.

## 워터마크 제거 기록

- 시트 우하단에 Gemini 반투명 별 3개가 있었음 (큰 별 1개가 뒷모습 발 아래에 걸침).
- 배경 위 별 2개: OpenCV Telea 인페인팅.
- 발에 걸친 큰 별: 반투명 흰색 오버레이 역산(알파 팽미순 약 0.44, 팽창수 약 0.25) 후 경계 1px 인페인팅.
- 남은 흔적: 뒷모습 발 바닥 경계에 아주 옅은 밝은 선. 3배 확대에서만 보이며, 참조 이미지 용도에는 영향 없음.
- 재현: `python3 tools/remove_watermark.py`
