# 외주 작업실 핸드오프

갱신: 2026-11-16

## 완료한 구성
- GitHub `pck9880-sys/claude-design`, 브랜치 `codex/project-moment-ir`의 `freelance/` 폴더.
- Claude/Codex 공통 규칙, 프로젝트별 원본·링크·결과·요청 구조, 새 프로젝트 조사서.
- Windows 로컬 체크아웃 설치와 Git LFS 초기화 스크립트. 기존 Adobe 앱 감지용 스크립트, 앱 내 실행용 무수정 JSX 점검 파일.
- 세 Adobe 앱의 원본·출력·검수·휴대폰 이어하기 절차.
- 기존 모먼트 v8/v9와 IR 레퍼런스는 복제하지 않고 저장소 내부 경로로 연결.

## 사용자 확인 / 미확인
- PC에 InDesign·Illustrator·Photoshop 설치 및 Adobe 로그인 완료라고 사용자 확인.
- 이 세션에서는 PC에 접근하지 못하므로 설치 스크립트·앱 내 JSX 점검은 실행하지 못함.
- Claude 모바일 GitHub 연결·Code 세션은 사용자 계정에서 시작해야 함. 서비스 연결·원격 PC 실행은 자동 설정되지 않음.

## 다음 실행
PC에서 `scripts/setup-windows.ps1`을 실행한 후 출력된 작업 폴더의 `freelance/`에서 Claude Code/Codex 시작. 진단 결과는 로컬 `workstation-health.json`에 생성됨(Git 제외).

다음 지시문: "freelance/CLAUDE.md와 프로젝트 모먼트 STATUS.md를 읽고 Adobe 실행 가능 여부부터 확인해줘. v9 7p는 품질 피드백이 남은 시안이며 v8 기준의 스타일을 다시 검토해야 해."
