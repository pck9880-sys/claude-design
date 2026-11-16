# AGENTS.md — GPT(Codex)용 작업 규칙

이 저장소는 Claude와 GPT(Codex)가 함께 쓴다. **규칙의 원본은 `CLAUDE.md`** 이며 Codex도 그대로 따른다.
작업 시작 전에 `CLAUDE.md`, `HANDOFF.md`를 먼저 읽는다.

## Codex 전용 보충
- 모든 안내·보고는 한국어. 최종 보고는 사용자가 직접 해야 할 일만 짧게.
- 스킬: `.claude/skills/<이름>/SKILL.md`에 있다. 작업 종류에 맞는 스킬 파일을 직접 열어 읽고 따른다.
  - 디자인: `hallmark`, `impeccable`, `ui-ux-pro-max`, `frontend-design`
  - IR 덱: `investor-pitch-deck`, `deck-narrative-arc`, `pptx`, `pro-deck-builder`, `ib-check-deck`, `deck-review-rubric`
  - 절차 문서: `design-kit/prompts/` (IR은 `06-ir.md`)
- `tools/gpt.py`는 호출하지 않는다 (Codex 자신이 GPT이므로 재귀 호출 금지).
- Claude가 `tools/gpt.py`로 맡긴 작업이면: 요청받은 결과만 지정 경로에 만들고, 다른 파일은 수정하지 않는다.
- 클라우드에서 독립 작업할 때: 작업용 브랜치에 커밋하고, 끝나면 `HANDOFF.md`를 갱신한다. `main`에 직접 푸시하지 않는다.

## 숫자·출처
- IR 숫자는 `ir/data/*.csv`에만 근거. 확인 못 한 사실·링크·수치는 쓰지 않는다.
- 레퍼런스는 링크·요약·구조 분석만 저장. 남의 덱 이미지·파일 저장 금지.
- `refs/ir/portfolio/`는 사용자가 작업한 고객 자료. 스타일 참고만 하고 내용·수치를 다른 덱에 옮기지 않는다.
