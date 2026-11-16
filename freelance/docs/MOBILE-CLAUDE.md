# Claude·휴대폰에서 이어하기

## 한 번만 필요한 계정 연결

1. Claude 앱/웹에서 GitHub 연결을 허용한다. 이 대화에서 해당 계정 연결을 대신 실행하지 않았다.
2. Claude Code 클라우드 기능을 사용할 수 있는 계정에서 `pck9880-sys/claude-design`을 선택한다. 목록에 없다면 GitHub의 Claude 연동 앱에 해당 비공개 저장소 접근이 허용되어 있는지 확인한다.
3. 작업 브랜치 `codex/project-moment-ir`를 선택한다. 폴더는 `freelance/`.
4. 다음 프롬프트로 시작한다.

> freelance/CLAUDE.md와 freelance/HANDOFF.md를 먼저 읽어줘. 프로젝트 모먼트 STATUS.md와 requests/007.md를 확인해줘. 지금 환경에서 Adobe 앱을 실제로 실행할 수 있는지 구분하고, 실행할 수 없으면 원고·수정 지시·작업 코드와 PC 실행 순서까지 준비해줘. 끝나면 현재 작업 브랜치에 저장해줘.

브랜치 선택 UI가 없는 환경에서는 새 세션이 만든 브랜치와 기준 커밋을 먼저 확인한다. 다른 환경의 미커밋 작업을 강제 전환하거나 덮어쓰지 않는다. main에는 직접 푸시하지 않는다.

## 휴대폰에서 맡길 수 있는 일

- 페이지별 수정 요구와 이미지 후보·원고·수치·레퍼런스 비교 기록.
- GitHub에 올라온 PDF 다운로드/열기 및 피드백.
- 스크립트·레이아웃 명세·핸드오프 준비와 저장.
- 해당 모바일/클라우드 환경에 실제 연결된 Adobe 기능이 있으면 그 기능의 지원 범위에서 실행.

PC의 미커밋 파일이나 `private/` 자료는 휴대폰에서 보이지 않는다. INDD/AI/PSD는 휴대폰 검토를 위해 작은 PDF/이미지를 함께 저장한다. PC가 꺼져 있어도 GitHub에 올라온 자료는 사용할 수 있지만 PC Adobe 앱은 실행되지 않는다.

## PC로 이어받기

```powershell
cd 'C:\Users\admin\Projects\freelance-design'
git status
git pull --ff-only
git lfs pull
cd freelance
claude
```

로컬 변경이나 브랜치 차이가 있으면 먼저 작업을 보존하고 맞는 브랜치를 확인한다. Adobe 실행 후 원본·검토 PDF·기록을 함께 commit/push해야 휴대폰에서도 최신 결과가 보인다. 자동 동기화·자동 실행 서비스는 설치하지 않았다.
