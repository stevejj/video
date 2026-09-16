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
| 팽창수 | `pang-changsu/pang-changsu_hires_front.png` | 고해상도 전신 정면 (768x1376) |
| 팽창수 | `pang-changsu/pang-changsu_3q_left.png` | 3/4 정면 좌향 |
| 팽창수 | `pang-changsu/pang-changsu_3q_right.png` | 3/4 정면 우향 (하단 텍스트 잘라냄) |
| 팽창수 | `pang-changsu/pang-changsu_pose_sit.png` | 앉은 자세 (2차, 정상 발) |
| 팽창수 | `pang-changsu/pang-changsu_expressions.png` | 표정 6종 그리드 |
| 팽창수 | `pang-changsu/expressions/pang-changsu_expr_0N_*.png` | 표정 개별 6장 (01 기본, 02 활짝, 03 놀람, 04 째려봄, 05 졸림, 06 슬픔) |
| 팽창수 | `pang-changsu/pang-changsu_pose_walk_side.png` | 걷는 자세 측면 (우향) |
| 팽창수 | `pang-changsu/pang-changsu_pose_lying.png` | 누운 자세 |
| 팽창수 | `pang-changsu/pang-changsu_face_eyes_closed.png` | 눈 감은 얼굴 |
| 팽창수 | `pang-changsu/pang-changsu_pose_hold_cup.png` | 날개로 컵 들기 |
| 투샷 | `couple_twoshot_front.png` | 두 캐릭터 정면 투샷 (창수 좌, 미순 우) |
| 팽미순 | `pang-misun/pang-misun_3q_left.png` | 3/4 정면 좌향 |
| 팽미순 | `pang-misun/pang-misun_3q_right.png` | 3/4 정면 우향 |
| 팽미순 | `pang-misun/pang-misun_pose_sit.png` | 앉은 자세 |
| 팽미순 | `pang-misun/pang-misun_pose_walk_side.png` | 걷는 자세 측면 (우향) |
| 팽미순 | `pang-misun/pang-misun_pose_lying.png` | 누운 자세 |
| 팽미순 | `pang-misun/pang-misun_hires_front.png` | 고해상도 전신 정면 |
| 팽미순 | `pang-misun/pang-misun_pose_hold_cup.png` | 날개로 컵 들기 |
| 팽미순 | `pang-misun/pang-misun_face_eyes_closed.png` | 눈 감은 얼굴 |
| 팽미순 | `pang-misun/pang-misun_expressions.png` | 표정 6종 그리드 (라벨 제거 재구성) |
| 팽미순 | `pang-misun/expressions/pang-misun_expr_0N_*.png` | 표정 개별 6장 |
| 원본 | `original/*_original.png` | 업로드 원본 (워터마크 포함, 수정 금지) |

원본 해상도 768x1376. 크롭 이미지는 시트에서 잘라낸 것이라 해상도가 낮다(정면 전신 약 280x335).
G1 단계에서 고해상도 턴어라운드를 새로 만들어 이 크롭들을 대체할 예정이다.

## 워터마크 제거 기록

- 시트 우하단에 Gemini 반투명 별 3개가 있었음 (큰 별 1개가 뒷모습 발 아래에 걸침).
- 배경 위 별 2개: OpenCV Telea 인페인팅.
- 발에 걸친 큰 별: 반투명 흰색 오버레이 역산(알파 팽미순 약 0.44, 팽창수 약 0.25) 후 경계 1px 인페인팅.
- 남은 흔적: 뒷모습 발 바닥 경계에 아주 옅은 밝은 선. 3배 확대에서만 보이며, 참조 이미지 용도에는 영향 없음.
- 재현: `python3 tools/remove_watermark.py`
