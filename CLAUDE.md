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
| **이미지가 필요할 때 (무조건)** — 히어로·배경·제품 연출·IR 표지·아이콘 일러스트 등 | GPT | `image "프롬프트" --out assets/generated/<작업명>-<용도>.png` |
| 검색어가 3개 이상이거나 여러 출처 비교가 필요한 서칭 | GPT 병렬 + Claude 검토 | `research --batch 질문.txt --out-dir refs/research/<작업명>` |
| 레퍼런스 사례 수집 (IR·디자인) | GPT가 수집, Claude가 선별·요약 | `research "..." --out refs/ir/<작업명>-gpt.md` |
| 긴 문서 여러 개(합계 30쪽 이상)·엑셀 여러 시트 정리 | GPT 초안 + Claude 대조 | `organize --task "..." --in <파일들> --out <결과>.md` |
| 짧은 서칭(검색 1–2번), 짧은 문서, 코드·디자인 구현, 최종 판단 | Claude 혼자 | — |

- 이미지 프롬프트는 5요소로 쓴다: 주제 / 구도 / 환경 / 스타일(tokens.json 색) / 기술 사양(비율, 글자 없음). 사람 얼굴·실존 브랜드·로고는 요청이 있을 때만.
- 서칭·정리를 맡기는 동안 Claude는 기다리지 말고 다른 단계(구성, 레이아웃)를 진행한다 (`run_in_background`).
- GPT 결과는 초안이다. 링크 몇 개를 직접 열어 확인하고, 숫자는 원문과 대조한 뒤 쓴다.
- Codex·API 키가 없는 환경(일부 클라우드 세션)에서는 실패 메시지가 나온다. 그때는 Claude 혼자 하고, 이미지는 자리표시로 두고 `HANDOFF.md`에 "PC에서 이미지 생성 필요"를 적는다.
- 호출 기록: `tools/gpt-log.jsonl`

## IR 덱 작업
- 절차는 `design-kit/prompts/06-ir.md`, 폴더 설명은 `ir/README.md`를 따른다.
- **숫자는 `ir/data/*.csv`에만 근거**. 원문에 없는 수치·고객사·인용을 만들지 않는다. 계산한 수치는 슬라이드의 `derived`에 근거를 적는다.
- 완료 전 `check_numbers.py` 통과 + `render.py` 미리보기 이미지를 직접 확인.
- PC의 문서·다운로드·바탕화면·OneDrive는 **읽기만** 한다. 필요한 파일은 `ir/inbox/`로 복사해서 쓴다.
- `ir/inbox/`는 고객 원본이라 GitHub에 올라가지 않는다 (.gitignore).
- 레퍼런스는 링크·요약·구조 분석만 `refs/ir/`에 저장한다. 남의 덱 이미지·파일을 저장하지 않는다.
- 스킬: 구성 `investor-pitch-deck`·`deck-narrative-arc`·`deck-outline-first`, 차트 `chart-choice`·`data-viz-deck`, 제작 `pptx`·`pptx-author`·`pro-deck-builder`, 검수 `ib-check-deck`·`deck-review-rubric`, 갱신 `deck-refresh`

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
