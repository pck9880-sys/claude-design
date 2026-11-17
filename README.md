# AI 매니저 — 디자이너용 선행 작업 자동화 (macOS · Windows)

Illustrator / InDesign 작업 화면을 보고, **시키지 않아도** 레퍼런스·폰트·초안·가이드라인을 미리 준비합니다.
할 일이 바닥나면 매니저 자신을 개선합니다.

```
[supervisor.py] ── 상주, 크래시/롤백 관리
   └ [manager.main]
       ├ 10분마다: 맨 앞 앱/창 → (민감 창이면 중단) → 스크린샷 + Adobe 문서 정보(폰트·링크)
       │           → 화면이 바뀌었으면 플래너(Claude)가 작업 0~3개 생성 → 큐(중복 제거)
       ├ 작업자: 큐를 쉬지 않고 소화 (시간당 상한, 자리 비움 땐 무거운 작업도)
       └ 60분마다(할 일이 없으면 20분): 자기 업그레이드 → 테스트 통과 시 반영 → 재시작
                                       10분 안에 죽으면 자동 롤백
```

## 결과물 위치: `~/AI_Inbox`
| 폴더 | 내용 |
|---|---|
| `references/` | 레퍼런스 표 + 무드 요약 (출처 URL 포함) |
| `fonts/` | 눈누·Adobe Fonts 추천표 + 라이선스 요약, 누락 폰트 경고 |
| `drafts/` | 카피 초안, 레이아웃 SVG, InDesign 자동화 JSX 초안 |
| `guidelines/` | 그리드·컬러·타이포 규칙, 링크/폰트 점검 체크리스트 |
| `reports/YYYY-MM-DD.md` | 오늘 한 일 |
| `FEEDBACK.md` | **직접 작성** — "폰트 추천은 고딕 위주로", "레퍼런스 그만" 등. 플래너와 자기 업데이트가 읽음 |
| `STOP` / `PAUSE` | 파일을 만들면 긴급 정지 / 일시정지 |

원본 .ai / .indd 파일은 **절대 수정하지 않습니다** (Adobe 스크립트는 읽기 전용).

## 설치
1. Claude Code 설치 → 터미널에서 `claude` 실행 → **Max 계정으로 로그인**
2. macOS: `bash install/install_mac.sh` / Windows(PowerShell): `install\install_windows.ps1`
3. 아래 권한 허용

## 필요한 권한
### macOS (설치 스크립트가 알려주는 python 실행 파일에 부여)
- **화면 기록** — 스크린샷
- **손쉬운 사용** — 맨 앞 앱/창 제목
- **자동화** → Illustrator, InDesign, System Events — 첫 실행 시 팝업
- 코드 서명 불필요: 업데이트는 .py만 바뀌고 python 실행 파일은 그대로라서 권한이 유지됨
### Windows
- 관리자 권한 불필요 (사용자 로그온 작업으로 등록)
- PowerShell 실행 정책: 설치 스크립트 1회 실행용 `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
- Adobe COM 접근: 별도 허가 없음 (pywin32)
- 백신이 화면 캡처를 경고하면 `.venv\Scripts\pythonw.exe` 허용
### 쓰지 않는 권한 (의도적으로 제외)
- 키 입력 감시(입력 모니터링), 전체 디스크 접근, 관리자/sudo

## 안전장치
- 민감한 앱/창(비밀번호 관리자, 메신저, 메일, 은행, 시크릿 창)은 캡처하지 않음 → `config.yaml`에서 조정
- 폰트는 추천과 링크만 제공. 다운로드/설치는 금지 (`fonts.auto_install: false`)
- 로그인·결제·전송·설치 금지 규칙이 모든 작업 프롬프트에 포함됨
- 자기 업데이트 제한: 보호 파일(config, supervisor, safety, selfupdate, install) 수정 시 폐기,
  400줄 초과 변경 거부, 테스트 실패 시 거부, 사람이 수정 중(git 변경 있음)이면 건너뜀, 롤백 태그 `good-*`
- Max 사용량 한도에 걸리면 60분 쉬고 재개, 시간당 작업 수 상한 4 (자리 비움일 땐 8)

## 개발
```bash
python -m pytest -q
```
개선 아이디어는 `docs/BACKLOG.md`에 적으면 자기 업데이트가 하나씩 구현합니다.
