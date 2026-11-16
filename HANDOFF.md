# HANDOFF — test-run (세팅 검증용 시험 작업)

## 1. 한 일 / 남은 일
- 한 일: 샘플 brief(`output/test-run/brief.md`)로 도자기 원데이 클래스 랜딩 1페이지 제작, 375/768/1440 확인, 대비 계산, 2건 수정
- 남은 일: 실제 사진 2장, 공방 일정(예약 날짜), 주소·연락처, 예약 전송처

## 2. 결정해야 할 것
- **스킬 스크립트 실행 허용 여부**: hallmark의 `theme.mjs`(테마 뽑기)와 `sloplint.mjs`(AI티 검사)가 자동 모드에서 차단됨. 허용하지 않으면 hallmark는 규칙 문서만 쓰는 반쪽 상태로 동작
  - 추천: 내용을 확인한 뒤 `.claude/settings.json` allow에 `Bash(node .claude/skills/hallmark/scripts/*)` 추가
- **tokens.json의 primary 색**: `#E8572A` 위 흰 글씨는 대비 3.6:1로 기준 미달. 이번엔 `primaryHover(#C9461D)`를 버튼 배경으로 씀
  - 추천: 버튼용 색을 따로 정하거나 primary를 한 단계 진하게

## 3. 결과 파일
- `output/test-run/index.html`, `tokens.css`, `rubric-result.md`
- 스크린샷: 브라우저 패널에서만 확인, 파일로 저장되지 않음 (Playwright MCP는 새 세션부터 로드됨)

## 4. 다음 세션 첫 지시
"HANDOFF.md 읽고, Playwright로 output/test-run을 375/768/1440 스크린샷 찍어 screenshots/test-run/에 저장해 줘. 스크립트 실행이 허용됐으면 hallmark sloplint도 돌려 줘."
