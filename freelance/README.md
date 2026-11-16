# 외주 디자인 작업실

InDesign · Illustrator · Photoshop 작업을 PC, Claude, Codex, 휴대폰에서 이어가기 위한 공통 작업 폴더입니다.

**현재 저장소:** `pck9880-sys/claude-design` / **브랜치:** `codex/project-moment-ir` / **폴더:** `freelance/`

이 폴더는 기존 비공개 저장소 안에 있습니다. 독립 저장소나 폴더별 권한 분리가 아닙니다. 외부 작업자에게 기존 저장소를 공유하지 마세요. 외부 협업 시 고객별 비공개 저장소로 분리합니다.

## 바로 시작

- PC: [setup-windows.ps1](scripts/setup-windows.ps1)을 다운로드해 PowerShell에서 실행합니다. 기존 Git·Adobe 설치를 사용하며 앱·계정·원본을 변경하지 않습니다.
- 로컬 설치 기본 경로: `C:\Users\admin\Projects\freelance-design`. 기존 모먼트 폴더는 그대로 보존합니다. 기존 체크아웃을 재사용하려면 `-Destination 'C:\Users\admin\Desktop\프로젝트 모먼트\IR-개발'`로 실행할 수 있지만, 기존 Claude 설정의 Desktop 쓰기 차단이 적용될 수 있어 새 기본 경로를 권장합니다.
- 설치 후 `freelance/` 폴더에서 `claude` 또는 `codex`를 실행합니다. CLI가 이미 설치되어 있어야 합니다. 스크립트는 CLI를 자동 설치하거나 로그인하지 않습니다.
- 휴대폰 Claude Code에서 GitHub 저장소와 위 브랜치를 선택한 뒤 아래 시작 문구를 입력합니다. Claude의 GitHub 연결은 Claude 앱에서 별도로 해야 합니다. 이 대화의 Adobe 플러그인 연결도 Claude로 이전되지 않습니다.

> freelance/CLAUDE.md와 freelance/HANDOFF.md를 읽고 프로젝트 모먼트를 이어서 작업해줘. project-moment/STATUS.md에 기록된 기준본과 수정 요청을 확인하고, 먼저 레퍼런스의 실제 화면을 비교해줘.

## 역할 분담

| 환경 | 가능한 작업 | 필요한 조건 |
|---|---|---|
| PC + Claude Code/Codex | 원고·기획·스크립트 작성, Adobe 원본 편집, PDF/이미지 출력·검수 | 설치된 Adobe 앱, 로그인, 로컬 실행 권한 |
| 휴대폰 + Claude Code 클라우드 | 원고·페이지별 요청·작업 코드·리뷰 기록·GitHub 저장, 저장된 PDF 검토 | Claude의 Code 기능 및 GitHub 연결 |
| 이 대화의 Adobe 도구 | 지원되는 이미지 편집, INDD/AI 렌더링·변환 등 | 해당 도구 및 파일의 Adobe 업로드/접근 권한 |
| PC가 꺼진 상태 | GitHub에 있는 자료로 기획·수정 지시·검토 | 데스크톱 Adobe 앱은 실행되지 않음 |

GitHub는 저장·버전 관리 공간입니다. Adobe 앱 실행 서버나 휴대폰 원격 제어 서비스가 아닙니다. PC 자동 실행 에이전트·예약 작업·원격 제어는 이번에 설치하지 않았습니다.

## 폴더

- `projects/<고객명>/brief.md`: 목표·산출물·판형·편집 앱
- `projects/<고객명>/requests/`: 페이지별 수정 요청
- `projects/<고객명>/source/`: 버전이 붙은 AI/PSD/INDD/IDML 원본
- `projects/<고객명>/links/`: InDesign 링크 이미지 등
- `projects/<고객명>/output/`: PDF·미리보기·검수 결과
- `projects/<고객명>/private/`: PC 전용 민감 자료, Git 제외
- `projects/<고객명>/work/`: 임시 파일, Git 제외
- `templates/`: 신규 외주 작업용 조사서·요청서
- `docs/`: Adobe·휴대폰·레퍼런스 작업 절차
- `scripts/`: PC 세팅·환경 확인, Adobe 실행 점검용 JSX

## 저장 규칙

1. 작업 전 Git 상태 확인 → `git pull --ff-only`. PC와 클라우드가 같은 파일을 동시에 수정하지 않습니다.
2. 원본은 덮어쓰지 않고 `고객_작업_v001.ai`처럼 버전을 붙입니다. 기존 파일 변경 전 사본을 만듭니다.
3. AI/PSD/INDD 등 큰 원본은 이 폴더의 `.gitattributes`에 따라 Git LFS로 저장합니다. 각 작업 환경에 Git LFS가 필요합니다. LFS 저장공간·전송 한도는 GitHub 계정 정책에 따릅니다.
4. PDF·작은 미리보기·원고·작업 요청·핸드오프는 일반 Git으로 저장합니다. 100MB 이상 파일은 일반 Git으로 올리지 않습니다.
5. 결과와 `HANDOFF.md`를 커밋 후 작업 브랜치에 push합니다. main에는 직접 push하지 않습니다. 바이너리 충돌은 덮어쓰기나 자동 병합으로 해결하지 않습니다.
6. 고객 자료를 다른 외부 서비스에 보내는 작업은 요청한 범위와 연결 도구를 확인한 후 진행합니다. 계정 비밀번호·API 키는 저장하지 않습니다.

## 현재 확인 상태

- 사용자 확인: Windows PC에 세 Adobe 앱 설치 및 로그인 완료(2026-11-16).
- 이 세션: 클라우드이며 사용자 PC 파일·앱에 직접 연결되어 있지 않음.
- 준비됨: GitHub 공통 폴더, Claude/Codex 안내, Windows 설치·진단 스크립트, 페이지별 수정 양식, Adobe 작업 절차.
- 미확인: PC에서 세팅 스크립트 실행, 앱별 JSX 실행, Claude 모바일 GitHub 연결 및 실제 클라우드 세션 시작.

상세: [Adobe 작업](docs/ADOBE.md), [모바일·Claude](docs/MOBILE-CLAUDE.md), [레퍼런스 기준](docs/REFERENCES.md).
