# 프로젝트 모먼트 IR 저장 기준

- 기준본: `output/ir-project-moment/v4/deck_v8.pptx` (15장). 사용자 확인: 2026-11-16.
- PDF: `output/ir-project-moment/v4/프로젝트모먼트_IR_v8.pdf`
- GitHub: https://github.com/pck9880-sys/claude-design
- 개발 브랜치: `codex/project-moment-ir`
- 사용자 PC 저장 루트: `C:\Users\admin\Desktop\프로젝트 모먼트`
- PC Git 작업 폴더: `C:\Users\admin\Desktop\프로젝트 모먼트\IR-개발`
- 현재 클라우드 작업 폴더: `/workspace/claude-design`

v8은 보존하고 다음 수정본은 v9부터 만든다. 수정 범위는 사용자 요청 후 확정한다. 개발 브랜치에 결과와 변경 내역을 커밋하고 GitHub에 푸시한다. PC에서는 Git pull로 같은 결과를 받는다. 자동 동기화는 구성하지 않았다.

## PC 초기 설치

Git for Windows가 설치된 PC에서 `setup-local.ps1`을 다운로드해 PowerShell로 실행한다. GitHub 로그인 요청이 나오면 저장소에 접근 가능한 계정으로 로그인한다.

기존 `IR-개발` 폴더가 있으면 덮어쓰지 않고 중단한다. 설치 후 업데이트는 해당 폴더에서 `git pull --ff-only`로 진행한다. 클라우드와 PC에서 같은 파일을 동시에 수정하지 않는다.

PC 설치 완료 여부는 이 클라우드 세션에서 확인할 수 없다. 원본 자료 `ir/inbox/`는 GitHub 저장 대상에서 제외되어 있다.
