# IR 덱 자동화

## 폴더
| 경로 | 내용 | 누가 |
|---|---|---|
| `inbox/` | 고객이 보낸 원본 사본 (조사서, 기존 IR, 엑셀, 템플릿) | 사용자 또는 Claude가 PC에서 찾아 복사 |
| `needs-survey.md` | 정리된 니즈 조사서 | Claude 자동 작성 |
| `templates/` | 회사 PPT 템플릿(.pptx) | 사용자 |
| `format-profile.md` | 템플릿·기존 자료에서 뽑은 서식 규칙 | Claude 자동 작성 |
| `data/*.csv` | 덱의 모든 숫자의 원본 | Claude 초안 → 사용자 확인 |
| `deck.json` | 슬라이드 구성 명세 | Claude 작성 |
| `../refs/ir/` | 레퍼런스 조사 결과 (링크·요약·구조 비교) | Claude 자동 작성 |
| `../output/ir-<작업명>/` | PPTX, PDF, 슬라이드 미리보기, 검수 결과 | 스크립트 |

## 한 번에 맡기기
> "ir 작업 시작해줘. 고객 자료는 다운로드 폴더에 있는 ○○ 파일들이야"

Claude는 `design-kit/prompts/06-ir.md`의 순서를 따릅니다.
1. 자료 수집: PC의 문서·다운로드·바탕화면에서 파일을 찾아 `inbox/`로 복사 → `python ir/scripts/extract_inbox.py`
2. 조사서 정리: 추출 텍스트를 `needs-survey.md`로 정리, 빈 칸은 확인 질문으로
3. 서식 분석: `python ir/scripts/format_profile.py ir/templates/<파일>.pptx` → `format-profile.md`
4. 레퍼런스 서칭: 웹 검색 → `refs/ir/<작업명>.md`
5. 구성: `investor-pitch-deck`, `deck-narrative-arc` 스킬로 스토리 → `deck.json`
6. 생성: `python ir/scripts/build_deck.py ir/deck.json`
7. 렌더: `python ir/scripts/render.py output/ir-<작업명>/deck.pptx` (PDF + 슬라이드 PNG)
8. 검수: `python ir/scripts/check_numbers.py ir/deck.json` + 슬라이드 이미지 눈으로 확인 + `deck-review-rubric`, `ib-check-deck`
9. `HANDOFF.md` 갱신, 커밋

## 스크립트 요약
- `extract_inbox.py`: docx·pdf·xlsx·csv·pptx·txt·md → `inbox/_extracted/*.md` (HWP는 PDF로 바꿔 넣기)
- `format_profile.py`: 템플릿의 슬라이드 크기, 테마 색, 폰트, 레이아웃 목록 추출
- `build_deck.py`: deck.json + data CSV + tokens.json → 차트 PNG + PPTX
- `render.py`: PPTX → PDF → 슬라이드 PNG (LibreOffice 필요)
- `check_numbers.py`: 덱에 들어간 숫자가 모두 `data/`에서 왔는지 대조
