# 디자인 작업 규칙

이 폴더는 Claude Code에 디자인 작업을 맡기는 작업 공간입니다. 모든 세션은 이 규칙을 따릅니다.

## 언어
- 모든 안내, 진행 상황, 질문, 요약은 **반드시 한국어**로 쓴다 (작업 중간 안내와 다음 단계 박스 포함). 코드·명령어·경로·고유명사는 원문 유지.

## 작업 시작 전 반드시 읽을 것
1. `brief.md` — 이번 작업의 요구사항 (비어 있거나 `<채우기>`가 남아 있으면 작업하지 말고 무엇이 필요한지 보고)
2. `tokens.json` — 색·폰트·간격의 유일한 기준
3. `design-decisions.md` — 이전 수정 요청에서 생긴 규칙 (있으면)
4. `refs/` — 레퍼런스 이미지와 메모

## 폴더 규칙
- 입력: `assets/`(로고·폰트·이미지), `refs/`(레퍼런스) — 읽기만, 수정 금지
- 출력: `output/<작업명>/` 에만 생성
- 검증 스크린샷: `screenshots/<작업명>/`
- 루트의 기존 파일(`kv_*.jsx`, `poster_*.png` 등)은 지시 없이 수정·삭제 금지

## 스킬 사용
- 미적 방향 스킬은 작업당 하나만: `hallmark` / `taste-skill` / `frontend-design` 중 brief에 지정된 것 (지정 없으면 hallmark)
- 시스템·토큰: `ui-ux-pro-max`, `design-system`
- 모션: `animate`, `design-motion-principles`
- 검수: `impeccable`(디자인 품질), `web-design-guidelines`(접근성)
- 상세 프롬프트 모음: `design-kit/prompts/`

## GPT(Codex) 자동 위임
`python tools/gpt.py ...` 로 GPT에 일을 맡긴다. 사용자가 따로 말하지 않아도 아래 기준으로 판단해 바로 실행하고, 결과는 Claude가 검토한 뒤 반영한다.

| 상황 | 위임 | 명령 |
|---|---|---|
| **이미지가 필요할 때 (무조건)** — 히어로·배경·IR 표지·아이콘 일러스트 등 | GPT | `image "장면 설명" --keywords k1 k2 k3 --out assets/generated/<작업명>-<용도>.png` |
| 검색어가 3개 이상이거나 여러 출처 비교가 필요한 서칭 | GPT 병렬 + Claude 검토 | `research --batch 질문.txt --out-dir refs/research/<작업명>` |
| 레퍼런스 사례 수집 (IR·디자인) | GPT가 수집, Claude가 선별·요약 | `research "..." --out refs/ir/<작업명>-gpt.md` |
| 긴 문서 여러 개(합계 30쪽 이상)·엑셀 여러 시트 정리 | GPT 초안 + Claude 대조 | `organize --task "..." --in <파일들> --out <결과>.md` |
| 짧은 서칭(검색 1–2번), 짧은 문서, 코드·디자인 구현, 최종 판단 | Claude 혼자 | — |

### 이미지 제작 규칙 (항상 적용)
- 스타일: **클립아트 느낌의 플랫 일러스트**. 사실적·사진 같은 표현 금지. **사람 얼굴 금지** (필요하면 손·뒷모습·실루엣). 글자·로고 금지. 이 규칙은 `tools/gpt.py`가 모든 요청에 자동으로 붙인다.
- **키워드 먼저 뽑기**: 사용자 요청·brief·슬라이드 메시지에서 이미지에 꼭 들어갈 요소 3–6개를 `--keywords`로 정한다. 장면 설명도 이 키워드만으로 쓴다. 분위기를 살린다고 요소를 덧붙이지 않는다.
- **과하지 않게**: 주요 요소 1–3개, 색 3–4개, 단순한 배경, 여백 충분히.

### 이미지 검수·재생성 (Claude가 직접)
생성 후 반드시 이미지 파일을 열어 보고 아래를 모두 확인한다. 하나라도 어긋나면 문제점을 구체적으로 적어 다시 만든다.

| 확인 | 기준 |
|---|---|
| 키워드 | 키워드가 모두 알아볼 수 있게 들어 있음 |
| 벗어남 | 키워드와 무관한 사물·장면·장식이 없음 |
| 스타일 | 클립아트·플랫 느낌. 사진·3D·사실적 질감이 아님 |
| 얼굴 | 사람 얼굴이 보이지 않음 |
| 과함 | 요소·색이 많지 않고 배경이 단순함 |
| 글자 | 글자·숫자·로고·이상한 문자 없음 |
| 용도 | 들어갈 자리(비율, 여백, 배경색)와 어울림 |

- 재생성: `--attempt 2 --fix "<무엇이 틀렸고 어떻게 고칠지>"` (파일명에 `-v2`가 붙음). `--keywords`는 그대로 둔다.
- **최대 3회**. 3회째도 통과 못 하면 가장 나은 시안을 쓰고 남은 문제를 `HANDOFF.md`에 적는다.
- 통과한 시안만 실제 작업에 쓰고, 탈락한 시안은 삭제한다.
- 서칭·정리를 맡기는 동안 Claude는 기다리지 말고 다른 단계(구성, 레이아웃)를 진행한다 (`run_in_background`).
- GPT 결과는 초안이다. 링크 몇 개를 직접 열어 확인하고, 숫자는 원문과 대조한 뒤 쓴다.
- Codex·API 키가 없는 환경(일부 클라우드 세션)에서는 실패 메시지가 나온다. 그때는 Claude 혼자 하고, 이미지는 자리표시로 두고 `HANDOFF.md`에 "PC에서 이미지 생성 필요"를 적는다.
- 호출 기록: `tools/gpt-log.jsonl`

### 아이콘 (항상 라인 아이콘, 간단·명료)
- 먼저 Lucide 세트에서 찾는다: `python tools/icon.py find <키워드>` (`assets/icons/lucide/`, 2,055개, ISC 라이선스)
- 딱 맞는 게 없거나 고유한 뜻이면 **GPT가 SVG로 생성**: `python tools/gpt.py icon "<뜻>" --name <영문-이름> --keywords <요소 1–3개>` → `assets/icons/custom/`
- 규칙: 24px 격자, 선 굵기 1.75, 둥근 끝, 면 채움·글자 없음, 요소 2–6개, 한 아이콘 한 뜻. `tools/icon.py check`가 검사한다.
- 생성 후 `python tools/icon.py sheet <svg들> --out <모음.png>`로 Lucide 아이콘과 나란히 보고, 굵기·밀도가 다르거나 뜻이 불분명하면 `--attempt 2 --fix "<문제>"`로 다시 만든다 (최대 3회).
- 덱에서는 카드·단계·항목에 `"icon": "<이름>"`만 적으면 브랜드 색으로 자동 변환된다. 사진형 이미지 생성(`gpt.py image`)으로 아이콘을 만들지 않는다.

## NAS · Everything
- NAS 경로는 `tools/nas.json`의 `roots`. **NAS 파일은 절대 삭제·이동·덮어쓰기하지 않는다**: `tools/hooks/nas_guard.py`가 수정·삭제·이동·NAS로 복사하는 명령을 모두 차단한다. 우회하려 하지 않는다.
- NAS는 **읽을 때마다 사용자 허가**를 받는다. 필요한 파일은 프로젝트(`ir/inbox/` 등)로 복사해서 작업한다.
- 파일 찾기는 Everything으로 빠르게 찾는다 (연동 방식은 설정 후 이 항목에 기록).

## IR 덱 작업
- 절차는 `design-kit/prompts/06-ir.md`, 폴더 설명은 `ir/README.md`를 따른다.
- **숫자는 `ir/data/*.csv`에만 근거**. 원문에 없는 수치·고객사·인용을 만들지 않는다. 계산한 수치는 슬라이드의 `derived`에 근거를 적는다.
- 완료 전 `check_numbers.py` + `check_margins.py` + `check_style.py` 통과 + `render.py` 미리보기 이미지를 직접 확인.
- **스타일은 작업 전에 사용자가 고른다**: `/ir-start` 2-1단계. 카탈로그 `design-kit/ir-styles/styles.json`(표지 A–E, 상단 A–G, 연결 A–E, 카드 A–E, 이미지 A–C, 글머리·구분선·요약 바), 보기 이미지 `design-kit/ir-styles/previews/`. 선택은 `output/ir-<작업명>/style.json`.
- **글자·간격·선 고정값**: 최소 글자 크기·자간·행간은 선택한 typography 값, 간격은 `fixed.spacing_cm`(0.2/0.4/0.6/1.0/1.5cm), 선 굵기는 0.5/0.8/1.6pt만. `check_style.py`가 검사한다.
- **레퍼런스는 둘 다 같은 비중**: `refs/ir/portfolio/`(사용자 작업 26건, PDF + 서식 분석용 경량 PPTX `pptx-lite/`)와 `refs/ir/samples/`(수집 상장사 IR 21건 PDF). 둘 다 GitHub에 있어 PC가 꺼져도 쓸 수 있다. 내용·수치는 다른 덱에 옮기지 않고 스타일 참고만. 새 자료는 `python tools/lite_refs.py`로 가볍게 만들어 올린다.
- **PPT 여백 고정: 상하좌우 1.5cm** (`tokens.json` → `slide.margin_cm`). 제목·본문·차트·표·출처·페이지 번호·로고 모두 이 안에만. 꽉 찬 배경·장식만 예외이며 도형 이름을 `bleed:`로 시작한다. `build_deck.py`가 아닌 방법(pptx 스킬, Codex, 템플릿 직접 편집)으로 만든 PPT도 같은 기준으로 `check_margins.py`를 통과해야 한다.
- 자동 검수 훅: `deck*.json`을 고치면 숫자 대조, `build_deck.py`를 실행하면 여백 검사가 자동으로 돈다. 실패 메시지가 나오면 그 자리에서 고친다.
- 명령: `/ir-start <회사명> [자료 위치] [홈페이지]` 로 작업 시작, `/ir-deliver <작업명> [메모]` 로 납품 버전 확정(태그).
- **고객사 홈페이지 조사는 매번 한다** (`06-ir.md` 2-1단계): `tools/site_scan.py`로 색·로고·인용 문구·숫자 후보를 모으고 `check.md`로 정리. 홈페이지 숫자도 고객 확인 전에는 확정 값으로 쓰지 않는다.
- PC의 문서·다운로드·바탕화면·OneDrive는 **읽기만** 한다. 필요한 파일은 `ir/inbox/`로 복사해서 쓴다.
- `ir/inbox/`는 고객 원본이라 GitHub에 올라가지 않는다 (.gitignore).
- 레퍼런스는 링크·요약·구조 분석만 `refs/ir/`에 저장한다. 남의 덱 이미지·파일을 저장하지 않는다.
- 스킬: 구성 `investor-pitch-deck`·`deck-narrative-arc`·`deck-outline-first`, 차트 `chart-choice`·`data-viz-deck`, 제작 `pptx`·`pptx-author`·`pro-deck-builder`, 검수 `ib-check-deck`·`deck-review-rubric`, 갱신 `deck-refresh`

## 브랜드 색 (작업마다 다름)
- 루트 `tokens.json`은 **중립 기본값**이다. 고객 작업에서는 그대로 쓰지 않는다.
- 작업 시작 시 고객 색으로 **작업별 토큰**을 만든다: `python tools/make_tokens.py <출처> --out output/<작업폴더>/tokens.json`
  - 출처 우선순위: ① 고객이 준 색 코드(`--primary`) ② 회사 PPT 템플릿 테마 색(`--from-pptx`) ③ 로고 이미지에서 추출(`--from-image`) ④ 기존 IR·홈페이지 캡처 이미지(`--from-image`)
  - 색을 지어내지 않는다. 출처가 하나도 없으면 중립 기본값으로 진행하고 확인 질문에 "브랜드 색"을 넣는다.
  - 추출 결과(후보 색)는 결과 보고에 한 줄로 남겨 사용자가 확인할 수 있게 한다.
- IR 덱은 `deck.json`에 `"tokens": "output/<작업폴더>/tokens.json"`을 적는다. 웹·이미지 작업도 같은 파일의 색을 쓴다.
- 흰 글씨를 올리는 버튼·강조 배경은 `primaryHover`(대비 4.5 이상 자동 보정), 넓은 면·장식은 `primary`.

## 폰트 (반드시)
- **기본 폰트는 무조건 Pretendard.** 제목·본문·표·차트·이미지 속 글자 모두.
- **`assets/fonts/README.md` 카탈로그에 있는 폰트만** 쓴다. 맑은 고딕·굴림·돋움·바탕·HY·한컴(HCR)·Arial·Calibri 등 시스템 기본 폰트 금지. CSS·PPT의 대체 폰트(fallback) 목록에도 넣지 않는다 (대체는 `Noto Sans KR`, 그다음 `sans-serif`).
- 디자인 폰트는 카탈로그 "추천 목록"에서 작업 톤에 맞춰 **1종만** 골라 강조 자리에만 쓰고, 고른 이유를 결과 보고에 한 줄 남긴다.
- 영문 전용 폰트(Montserrat, Orbitron 등)에 한글을 넣지 않는다.
- 클라우드 세션에서 렌더 전에 `python tools/install_fonts.py`를 한 번 실행한다.

## 디자인 원칙
- 색·간격·radius·그림자는 `tokens.json` 값만 사용, 임의 HEX·매직 넘버 금지
- 실제 카피 사용 (lorem ipsum 금지). 카피가 없으면 brief 톤에 맞춰 쓰고 표시해 둘 것
- 모든 화면에 default / hover / focus / disabled / empty / error 상태 고려
- 375 / 768 / 1440px 반응형, `prefers-reduced-motion` 대응

## 작업 범위 (가드레일)
다음은 하지 말고 멈춘 뒤 `HANDOFF.md`에 보고:
- 이 폴더 밖 파일 수정, 패키지 전역 설치
- 외부 서비스에 게시·배포·업로드
- git: 푸시는 사용자가 요청할 때. 강제 푸시(`--force`), 원격 브랜치 삭제, 히스토리 재작성은 사용자가 그 작업을 직접 지목해 요청했을 때만 하고, 실행 전 무엇이 덮어써지는지 알릴 것
- `tokens.json` 임의 변경 (변경이 필요하면 제안만)
- brief에 없는 페이지·기능 추가
- API 키·비밀번호 입력이나 파일에 기록

## 완료 기준 (자가 평가)
완료 전 아래 표를 `output/<작업명>/rubric-result.md`에 채우고, 하나라도 실패면 고친 뒤 재평가.

| 항목 | 기준 |
|---|---|
| 대비 | 본문 4.5:1, 큰 글씨 3:1 이상 |
| 반응형 | 375/768/1440에서 깨짐·가로 스크롤 없음 (Playwright 스크린샷으로 확인) |
| 토큰 | 하드코딩 색·간격 0개 |
| 상태 | 필요한 상태 모두 구현 |
| 모션 | reduced-motion 대응, transform/opacity만 사용 |
| AI티 | 선택한 미적 스킬의 점검 통과 |

## 보고 방식
- 결정마다 근거 표시: brief / 토큰 / 레퍼런스 / 스킬 규칙 / 내 판단. "내 판단"만으로 정한 것은 `output/<작업명>/decisions.md`에 모아 둘 것
- 검증 수준 구분: 확인함(스크린샷으로 검증) / 추정함 / 못 함(이유)
- 작업이 끝나거나 막히면 `HANDOFF.md`를 갱신:
  1. 한 일 / 남은 일
  2. 내가 결정해야 할 것 (선택지와 추천)
  3. 결과 파일 경로와 스크린샷
  4. 다음 세션이 바로 이어갈 첫 지시문
- 내가 수정 요청을 하면 반영 후 `design-decisions.md`에 `[날짜] 요청 / 변경 / 이유 / 이후 적용할 규칙` 한 줄 추가
