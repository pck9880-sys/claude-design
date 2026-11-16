# HANDOFF

마지막 갱신: 2026-11-16 (세팅 세션 종료 시점)

## 1. 현재 상태 — 세팅 완료
- 디자인 스킬 19개: `.claude/skills/` (출처·용도는 `design-kit/README.md`)
- 상황별 프롬프트 모음: `design-kit/prompts/` (레이어 1–6, 42개 항목)
- 규칙: `CLAUDE.md` (한국어 안내, 작업 범위, 완료 기준, 핸드오프 방식)
- 권한: `.claude/settings.json`
  - 허용: 파일 편집, npm/npx/node, git 일반 명령과 푸시(강제 푸시 포함)
  - 차단: `npm publish`, `rm -rf`, `.env` 읽기
  - hallmark 스크립트: `theme.mjs`, `sloplint.mjs`만 검토 후 허용 (install·install-hook·imagegen은 미허용)
- Playwright MCP: `.mcp.json` (새 세션부터 로드)
- 미리보기 서버: `.claude/launch.json` → `output/` 폴더를 localhost:4173으로 제공
- GitHub: 비공개 저장소 `pck9880-sys/claude-design`, 브랜치 `main`
  - 폰·아이패드: Claude 앱 Code 탭에서 클라우드 세션으로 이어서 작업 (PC 꺼져도 동작)
  - 다른 PC: `git clone` 후 작업

## 2. 시험 작업 결과 (output/test-run)
- 도자기 원데이 클래스 랜딩 1페이지, 375/768/1440 확인, 대비 계산, 2건 자체 수정
- 결과: `output/test-run/index.html`, `tokens.css`, `rubric-result.md`
- 미확인: hallmark sloplint 자동 검사(당시 차단), Playwright 스크린샷 파일 저장

## 3. 결정해야 할 것
- **tokens.json**: 아직 예시 값. primary `#E8572A` 위 흰 글씨는 대비 3.6:1로 기준 미달 → 버튼용 진한 색을 따로 정할 것
- `assets/`, `refs/`에 실제 브랜드 자료 넣기

## 4. IR 자동화 (완료, 2026-11-16)
- 스킬 15개 추가: pptx, pptx-author, ib-check-deck, deck-refresh, pitch-deck, sector-overview, comps-analysis (Anthropic) / investor-pitch-deck, deck-narrative-arc, deck-outline-first, deck-review-rubric, chart-choice (pm-claude-skills) / data-viz-deck, pro-deck-builder / ppt-creator
- 도구: python-pptx·pymupdf·pdfplumber·python-docx·openpyxl, LibreOffice, Pretendard 폰트(`assets/fonts/Pretendard`)
- 스크립트: `ir/scripts/` (자료 추출, 서식 분석, 덱 생성, 렌더, 숫자 대조) — 사용법 `ir/README.md`
- 절차: `design-kit/prompts/06-ir.md`, 조사서 양식: `ir/needs-survey.md`
- 권한: 웹 검색 자동, 문서·다운로드·바탕화면·OneDrive 읽기 자동(쓰기 금지)
- 시험: `ir/deck.sample.json` + 가상 데이터 → `output/ir-sample/` (PPTX, PDF, 미리보기 9장) 통과
- 남은 것: Pretendard를 PC에 설치하면 PowerPoint에서도 같은 폰트로 보임 (`assets/fonts/Pretendard/*.otf` 더블클릭 → 설치)
- `ir/data/*.csv`의 현재 값은 **가상 샘플**. 실제 작업 시작 시 교체

## 5. GPT(Codex) 연동 (완료, 2026-11-16)
- 같은 저장소 사용: Codex는 `AGENTS.md` → `CLAUDE.md` 규칙을 따름
- Claude 자동 위임: `tools/gpt.py` (image / research / organize). 기준은 `CLAUDE.md` "GPT(Codex) 자동 위임"
- PC: Codex CLI 0.169.0 설치, ChatGPT 로그인 사용 (API 키 불필요)
- 클라우드 Claude 세션: GPT 호출 불가. **사용자 결정(2026-11-16): OpenAI API 키는 쓰지 않음** → 클라우드에서는 이미지 자리만 잡고 `HANDOFF.md`에 "PC에서 이미지 생성 필요"를 남긴 뒤, PC 세션에서 생성
- 시험 통과: 이미지 생성, 병렬 서칭 2건, 자료 정리 1건
- 참고 자료: `refs/ir/seed-ir-mistakes.md` (시드 IR에서 투자자가 지적하는 실수, GPT 조사)

## 6. 진행 중 작업 — 프로젝트모먼트 IR 리디자인 (v1 완료, 2026-11-16)
- 원본: 바탕화면 `프로젝트 모먼트/` (원고·니즈조사서·레퍼런스·1차시안·사진) → 사본 `ir/inbox/project-moment/` (GitHub 제외)
- 결과: `output/ir-project-moment/deck.pptx`, `deck.pdf` (16장), 검수 `review.md`, 조사서 `needs-survey.md`
- 명세 `ir/deck-project-moment.json`, 데이터 `ir/data-project-moment/`, 스타일 `output/ir-project-moment/style.json`
- 확인 필요: 2025 매출 12억 vs 11.6억, 마감·투자 단계, CI/BI 로고 원본
- 이번에 추가된 기능: 사진 채우기 크롭·자동 축소, hero·gallery 레이아웃, 카드 F(에디토리얼), 팀 6인, 데이터 폴더별 숫자 검사

## 7. 다음 세션 첫 지시 예시
"HANDOFF.md 읽고 이어서 해줘"
