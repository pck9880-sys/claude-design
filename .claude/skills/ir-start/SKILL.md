---
name: ir-start
description: IR 덱 작업을 한 번에 시작한다. 사용자가 /ir-start 를 입력하거나 "IR 작업 시작"이라고 할 때 사용. 인자로 회사명, 고객 자료 위치(폴더·파일명·키워드), 홈페이지 주소를 받는다.
argument-hint: "<회사명> [자료 폴더/파일] [홈페이지 주소]"
---

# /ir-start

인자: `$ARGUMENTS` (예: `/ir-start 흙과손 다운로드/흙과손_자료 https://example.com`)
빠진 인자는 묻지 말고 아래 규칙대로 찾는다. 끝까지 못 찾은 것만 마지막 확인 질문에 넣는다.

모든 단계는 `design-kit/prompts/06-ir.md`를 따르고, 규칙은 `CLAUDE.md`를 따른다. 진행 안내는 짧게, 최종 보고는 사용자가 할 일만.

## 0. 작업 폴더
- 작업명: 회사명을 영문 소문자·하이픈으로 (예: `heuk-son`). 같은 이름이 있으면 `-2`.
- 만들기: `output/ir-<작업명>/`, `ir/inbox/<작업명>/`
- `ir/deck.json`이 이미 다른 작업용이면 `ir/deck-<작업명>.json`으로 새로 만든다 (기존 파일 덮어쓰기 금지).

## 1. 자료 수집 (병렬로 시작)
- 자료 위치가 주어지면 그곳, 아니면 회사명으로 문서·다운로드·바탕화면·OneDrive를 검색 (`find`, 최근 수정 순). 후보가 여럿이면 최신 것을 고르고 보고에 적는다.
- 찾은 파일은 `ir/inbox/<작업명>/`로 **복사** (원본 수정 금지) → `python ir/scripts/extract_inbox.py ir/inbox/<작업명>`
- 홈페이지: 인자 > 자료 속 주소·메일 도메인 > 회사명 웹 검색 순으로 찾는다.
  - `python tools/site_scan.py <주소> --out output/ir-<작업명>/site`
  - 동시에 백그라운드로 GPT 언론·투자 조사 (`tools/gpt.py research ... --out output/ir-<작업명>/site/press-gpt.md`)

## 2. 정리
- 니즈 조사서: `ir/needs-survey.md` 양식을 복사해 `output/ir-<작업명>/needs-survey.md`로 채운다.
- 숫자: `ir/data/`가 샘플이면 `ir/data-<작업명>/`를 새로 만들어 쓴다 (출처 `source` 열 필수).
- 브랜드 색: 고객 색 코드 > 템플릿 테마 > 로고 > 홈페이지 색 후보 순 → `python tools/make_tokens.py ... --out output/ir-<작업명>/tokens.json`
- 서식: 템플릿이 있으면 `python ir/scripts/format_profile.py <템플릿>` (결과를 `output/ir-<작업명>/format-profile.md`로 옮김)
- 홈페이지 체크: `output/ir-<작업명>/site/check.md`
- 레퍼런스: `refs/ir/portfolio/`에서 비슷한 덱 2–3개 선정 + 필요 시 웹 레퍼런스

## 3. 멈추는 지점
조사서의 **필수 항목**(마감, 투자 단계, 핵심 숫자, 분량) 중 비어 있는 게 있으면 덱 생성 전에 멈추고 확인 질문을 보낸다.
필수 항목이 모두 있으면 그대로 06-ir.md 5–7단계(구성 → 생성 → 렌더 → 검수)까지 진행한다.

## 4. 보고
- 사용자가 할 일만: 확인 질문(우선순위순), 고객에게 요청할 자료, 결과 파일 위치
- 한 줄씩: 사용한 자료 파일, 홈페이지 주소, 고른 브랜드 색과 출처, 고른 디자인 폰트와 이유
- `HANDOFF.md` 갱신 → 커밋 → 푸시
