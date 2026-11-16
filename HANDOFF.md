# HANDOFF

## 최신 — 우측 상단 설명글 full-v004
- 사용자 수정: 작가별 오른쪽에 간단한 설명글을 넣되 상단 배치.
- 오른쪽10쪽 모두 상단 x25/y25/폭161/높이20mm 설명글, 사진은8mm 아래 y53에서 시작(161×211mm). 오른쪽 아래 쪽번호 유지.
- 사진은 빈 프레임, 설명글은 각 right_asset의 description 연결. 원고 미수신 대기 표시.
- 최신 output/full-v004/, data/layout_full_v004.json/.jsxinc, scripts/BuildFullAlbumV004.jsx. 전체24쪽 검토 PDF 갱신. 이전 v003 보존.
- 15mm 안전여백·좌우 쪽번호·본문/사진8mm 간격·JSX 구문 확인. 실제 InDesign 실행은 미검증.


## 최신 — 전체24쪽 구성 full-v003 (2026-11-16)
- 사용자 요청으로 한 쪽 검토 제한 해제, v007 수정 디자인을 전체에 적용.
- 1표지(작가별1장 총10장 모자이크), 2인사말, 3프로그램/8회기/사진3장, 4~23작가10명×2쪽, 24마무리/활동6칸/명단·기관정보.
- 작가 왼쪽은 사진161×145mm+소개/본문, 오른쪽은 사진161×239mm+오른쪽 쪽번호만. 미수신 사진·원고는 빈 프레임/대기 문구. 예시 인명·본문은 전체판에 사용하지 않음.
- 작가별 유사 저채도10색, 사방15mm, 바깥쪽 쪽번호, 모서리8mm 및 하단 여백 유지. 작품·작가 순서와 대응은 임시ID이며 확인 전 확정하지 않음.
- 최신 output/full-v003/에24쪽 검토 PDF·개별PNG/SVG·펼침면11개·전체 보기·페이지맵. data/layout_full_v003.json/.jsxinc, scripts/BuildFullAlbumV003.jsx.
- 제작: scripts/build_album_full_v003.py → scripts/render_full_v003.py(검토 렌더), 실제 InDesign은 프로젝트 구조 유지 후 BuildFullAlbumV003.jsx 실행.
- 24쪽·전체 요소15mm·쪽번호 좌우·우측사진전용·텍스트 치수 검사 및 JSX 구문 확인. PNG/PDF는 자체 SVG 렌더링이며 네이티브 INDD/IDML 생성·실제 앱 실행은 미검증.


## 최신 — 사진 축소·하단 묶음 상향 v007
- 사용자 보충: 하단 제목 박스·작가소개·설명/인용 묶음 전체를 약간 위로 이동.
- 사진 높이153→145mm(폭161mm 유지), 캡션·우하단 모서리·하단 편집 묶음을8mm 위로 이동.
- 쪽번호/푸터 위치 유지. 본문 프레임 하단과 푸터선 간격3→11mm. 박스/본문 내부 상대 간격·15mm 안전여백·바깥쪽 쪽번호 유지.
- 최신 output/interior-sample-v007/, data/interior_sample_v007.json/.jsxinc, scripts/BuildInteriorSampleV007.jsx. 한 쪽만 수정.
- 좌표·여백·JSX 구문 및 PNG 시안 확인. 실제 InDesign 앱 실행은 미검증.


## 최신 — 하단 간격·모서리 정리 v006
- 하단 제목 박스와 작가소개 사이 3→8mm. 사진·하단 박스의 왼쪽선25mm 유지.
- 좌상단의 중복된 작은 ㄱ자 선 삭제. 바깥 모서리 선만 남김.
- 상단과 우하단 모두 사진에서 가로·세로8mm 간격. 15mm 안전영역을 유지하며 사진/본문 오른쪽 끝186mm로 맞춤.
- 바깥쪽 쪽번호·빈 사진·한 페이지 검토 유지. 최신 output/interior-sample-v006/, data/interior_sample_v006.json/.jsxinc, scripts/BuildInteriorSampleV006.jsx.
- 좌표·간격 검사 및 JSX 구문 확인. PNG/SVG는 자체 미리보기, 실제 InDesign 실행은 미검증.


## 최신 — 바깥쪽 쪽번호·세로선 정렬 v005
- 왼쪽(짝수) 페이지는 왼쪽, 오른쪽(홀수) 페이지는 오른쪽 쪽번호. 이후 페이지 수정 시에도 이 규칙 유지.
- 현재 04쪽 시안은 왼쪽 쪽번호. 사진 프레임·캡션·하단 제목 박스·하단 구분선의 시작 x=25mm로 정렬. 하단 제목 글자도 박스와 함께 이동.
- 15mm 여백·빈 사진 프레임 유지, 한 쪽만 수정. 최신 output/interior-sample-v005/, scripts/BuildInteriorSampleV005.jsx, data/interior_sample_v005.json/.jsxinc.
- 구조·여백·선 정렬·JSX 구문 확인. 자체 SVG/PNG 미리보기이며 실제 InDesign 실행은 미검증.


## 최신 — 15mm 여백·사진 빈 프레임 한 장 v004 (2026-11-16)
- 사용자 요청: 사진은 추후 삽입. 사진 위 원형·글자를 삭제하고 상하좌우 15mm 여백으로 한 장만 수정.
- 최신 시안: output/interior-sample-v004/ (사진 없는 PNG/SVG 및 15mm 가이드 확인본).
- 하단 예시 원고·세로 제목·단 편집 유지. 현재 한 장만 수정하며 나머지 23쪽 적용 보류.
- data/interior_sample_v004.json/.jsxinc, scripts/BuildInteriorSampleV004.jsx. 페이지·부모 페이지 여백 모두 15mm 설정.
- 1쪽·빈 사진 프레임 1개·원형 없음·모든 요소 15mm 안전영역 검증 및 JSX 구문 검사. 실제 InDesign 앱 실행/INDD 생성은 미완료. 미리보기는 SVG 렌더링.

## 인생사진첩 레퍼런스 반영 한 장 v003 (2026-11-16)
- 새 편집 레퍼런스의 사진/원형 타이포/얇은 선/단 구성을 반영한 한 장 시안.
- 프로젝트 output/interior-sample-v003/가 최신, 작가01 샌드 브라운 예시. 작가별 유사 저채도 포인트색은 방향 확인 후 적용.
- 다른 페이지 확대 적용은 보류. 시안용 생성 사진/예시 글이며 실제 고객 자료가 아님.

## 인생사진첩 한 장 완성형 예시 v002 (2026-11-16)
- 사용자가 임의 텍스트·사진을 넣은 실제 느낌의 디자인을 요청. 새 생성 골목 사진+예시 작가/원고로 한 페이지를 제작.
- 프로젝트 output/interior-sample-v002/가 최신. 고객 실제 자료와 예시는 분리, 다른 작업 이미지 사용 없음.
- 상단 제목·작가소개, 큰 사진, 하단 색면과 인용/설명으로 구성. 다른 내지 적용은 피드백 이후.

## 인생사진첩 전체 내지 v002 (2026-11-16)
- 표지/내지 전체24쪽 배치·SVG 검토도와 BuildLayoutV002.jsx 준비. 프로젝트 output/v002/ 및 START-HERE.md 참고.
- 실제 Adobe IDML 출력 시험은 빈 화면으로 검수 실패. 불완전한 IDML/PDF는 배포하지 않음. 실물 INDD/IDML 생성·실제 PC 실행은 아직 미완료.
- 사진 ZIP·추가 원고 수신 후 작가 매핑과 InDesign 네이티브 실행 검수가 필요.

## 인생사진첩 고객자료 수신·제작 준비 (2026-11-16)
- HWP 원고와 남산정 표지 레퍼런스 PDF를 프로젝트 inputs/에 저장·분석. 24p·10명 각2p.
- 활동사진/작품사진 ZIP은 각각 32MiB 전송 한도로 미수신·GitHub 업로드 미완료. 다른 작업의 08.png는 사용하지 않음.
- 프로젝트 전용 CLAUDE.md/START-HERE.md, 페이지·자산 데이터와 InDesign 검토 구조 JSX 준비. 실제 InDesign 실행·INDD/IDML/PDF 생성은 미완료.
- 인사말·작가소개·작품 문구·사진 매핑·기관/지원 로고·인쇄 사양 대기. 바탕화면 설치 요청 없음.
- 최신 사실은 freelance/projects/2026_11.16_인생사진첩/STATUS.md 기준.

## 인생사진첩 서버 백그라운드 요구 (2026-11-16)
- 신규 폴더 `freelance/projects/2026_11.16_인생사진첩/`. InDesign 메인, Illustrator 보조.
- 사용자 요구는 개인 PC가 꺼져도 서버에서 처리하는 방식. Adobe 계정·앱 구매 확인.
- 공식 자료로 InDesign/Illustrator Firefly Services API의 사용자 정의 스크립트 기능 확인. Python은 API 호출·작업 관리, Adobe 클라우드는 실제 문서 처리 담당 방식으로 검토.
- 기술 조사와 실행 준비 상태는 프로젝트 STATUS.md 및 automation/FEASIBILITY.md. 계정 API 권한·요금·인증·서버 배포·실제 실행은 아직 미완료. 로컬 스크립트 설치를 이 요구의 완료로 보고하지 않음.

## 외주 Adobe 공통 환경 (2026-11-16)
- 사용자 요청: GitHub 외주 폴더, Claude·휴대폰 이어하기, InDesign·Illustrator·Photoshop 활용.
- 구성: `freelance/README.md`, `CLAUDE.md`, `AGENTS.md`, `HANDOFF.md`, 프로젝트별 source/links/output/requests 구조, 템플릿·문서·Windows 설정/진단 스크립트·무수정 probe.jsx.
- GitHub 위치: 기존 비공개 `claude-design` 저장소, `codex/project-moment-ir` 브랜치의 `freelance/`. 별도 저장소나 폴더별 접근 제어는 아님. 외부 협업자 초대하지 않음.
- 사용자 확인: PC 세 Adobe 앱 설치·로그인 완료. 세션에서는 PC·Claude 모바일 연결을 직접 확인하지 못함.
- PC 권장 새 체크아웃: `C:\Users\admin\Projects\freelance-design` (기존 Desktop 원본·IR-개발 보존). 설치 스크립트 실행은 사용자 PC에서 필요.
- 모먼트 v9 7p는 사용자 품질 지적 시안임을 STATUS.md에 명시. v8을 기준으로 레퍼런스를 다시 검토해야 함. 이번 환경 구성에서는 추가 시안 제작하지 않음.
- 다음 작업: `freelance/HANDOFF.md`를 읽고 실제 PC·모바일 연결과 Adobe 실행 점검부터 이어가기.

## 프로젝트 모먼트 v9 — 7p 수정 완료 (2026-11-16)
- 사용자 요청: 페이지별 순차 수정, 우선 7p의 70/30을 원형 그래프로 전환하고 파트별 이미지 배치. Claude 작업 시 올린 레퍼런스 참고.
- 결과: `output/ir-project-moment/v9/deck_v9.pptx`, `deck_v9.pdf`, `7p-preview.pdf`. 30%는 확보 목표로 명시. 수치와 기존 이미지 유지.
- 중앙 native pie + 좌측 카피캣 이미지 + 우측 owooii 화보·제품 이미지. v8의 나머지 14장 XML 및 PDF 화면 보존.
- 검수/재생성: 같은 폴더 `review.md`, `verification.json`, `edit_slide7.py`, `finalize_pdf.py`, `verify_slide7.py`. 기존 전역 서식 경고는 남아 있으나 신규 경고 없음.
- 개발 브랜치 `codex/project-moment-ir`. PC 경로는 아래 저장 설정과 동일하며 클라우드에서 PC에 직접 저장하지 못함.
- 다음 작업: 사용자 7p 피드백 또는 다음 페이지 수정 요청에 따라 v9를 기준으로 이어서 수정.

## 프로젝트 모먼트 저장 설정 (2026-11-16, Codex)
- 사용자가 최종 작업 기준을 `DECK_v8`로 지정. 실제 파일은 `output/ir-project-moment/v4/deck_v8.pptx` (15장), PDF는 같은 폴더의 `프로젝트모먼트_IR_v8.pdf`.
- 원격 main의 `07f1bc3`에 v8이 이미 저장되어 있음을 확인. 후속 작업은 `codex/project-moment-ir` 브랜치 사용, 다음 수정본은 v9.
- PC 저장 루트는 사용자 지정 `C:\Users\admin\Desktop\프로젝트 모먼트`. Git 설치 대상은 하위 `IR-개발` 폴더.
- 저장 규칙과 PC 설치 스크립트: `output/ir-project-moment/SAVE-LOCATIONS.md`, `setup-local.ps1`.
- 현재는 클라우드 작업 환경으로 PC C드라이브 직접 접근 불가. PC 설치는 아직 확인하지 못함. 자동 동기화 없음.
- 남은 일: PC에서 설치 스크립트 실행, 사용자에게 구체적인 수정 범위를 받아 v8 사본에서 v9 개발. 이번에는 덱 내용을 수정하지 않음.

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
