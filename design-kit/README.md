# Design Kit — 클로드 코드 디자인 위임용 소스 모음

스킬은 상위 폴더 `클로드/.claude/skills/`에, Playwright MCP 설정은 `클로드/.mcp.json`에 있습니다.
전역(모든 프로젝트)에서 쓰려면 원하는 스킬 폴더를 `~/.claude/skills/`로 복사하세요.

## 1. 설치된 스킬 (`클로드/.claude/skills/`, 19개)

| 캡처 항목 | 설치된 스킬 | 출처 (GitHub) |
|---|---|---|
| 01 frontend-design | `frontend-design` | anthropics/skills |
| 02 impeccable | `impeccable` | pbakaus/impeccable |
| 03 taste-skill | `taste-skill` | Leonxlnx/taste-skill |
| 04 animate | `animate` | emilkowalski/skills |
| 05 design-motion | `design-motion-principles` | kylezantos/design-motion-principles |
| 06 theme-factory | `theme-factory` | anthropics/skills |
| 08 playwright (스크린샷 검증) | `webapp-testing` + `클로드/.mcp.json`의 Playwright MCP | anthropics/skills, microsoft/playwright-mcp |
| 09 brandkit / 20 brandkit-sync | `brand`, `design-system` | nextlevelbuilder/ui-ux-pro-max-skill |
| 11 nano-banana | `nano-banana` (⚠ `GEMINI_API_KEY` 직접 설정 필요) | dennisonbertram/claude-media-skills |
| 13 canvas-design | `canvas-design` | anthropics/skills |
| 14 algorithmic-art | `algorithmic-art` | anthropics/skills |
| 15 remotion-superpowers | `remotion-best-practices`, `remotion-create` | remotion-dev/skills |
| 21 slide-decks | `slides` | nextlevelbuilder/ui-ux-pro-max-skill |
| (영상) ui-ux-pro-max | `ui-ux-pro-max` | nextlevelbuilder/ui-ux-pro-max-skill |
| (영상) hallmark | `hallmark` | Nutlope/hallmark |
| (영상) emil-design-eng | `emil-design-eng` | emilkowalski/skills |
| (영상) web-design-guidelines | `web-design-guidelines` | vercel-labs/agent-skills |

## 2. 연결형 (설치 대신 연결)
- **07 figma-implement / 22 figma-mcp**: Claude 앱에 Figma 커넥터가 이미 연결되어 있음. 사용법은 `prompts/01-ui-design.md` #07
- **08 playwright-mcp**: `클로드/.mcp.json`에 설정됨 (처음 실행 시 `npx`로 자동 설치, Node 필요)

## 3. 프롬프트로 저장 (`prompts/`)
설치형 공식 소스를 찾지 못했거나 "작성 기법"인 항목 → 복사해서 쓰는 지시문

| 파일 | 항목 |
|---|---|
| `01-ui-design.md` | 05 design-motion, 07 figma-implement, 08 playwright, 10 designer-skills |
| `02-creative.md` | 12 banana-claude, 16 claude-remotion, 17 blender-motion, 18 ae-motion |
| `03-product-interaction.md` | 19 hi-fi-mockups, 20 brandkit-sync, 23–28 |
| `04-prompt-skills.md` | 29–36 (프롬프트 작성 기법 8개) |
| `05-trust-eval.md` | 37–42 (가드레일·평가·핸드오프) — CLAUDE.md에 넣기 추천 |

## 추천 조합 (전부 쓰지 말 것)
- **랜딩/웹 화면**: hallmark 또는 taste-skill 중 하나 + impeccable(검수) + web-design-guidelines(접근성)
- **앱 UI·디자인 시스템**: ui-ux-pro-max + design-system + emil-design-eng
- **모션**: animate + design-motion-principles
- **영상**: remotion-best-practices
- **백그라운드 위임 시 필수**: `prompts/05-trust-eval.md`의 37·40·42를 CLAUDE.md에

> 스킬끼리 방향이 겹치므로(hallmark ↔ taste-skill ↔ frontend-design) 한 작업에 미적 방향 스킬은 하나만 쓰는 게 결과가 안정적입니다.
