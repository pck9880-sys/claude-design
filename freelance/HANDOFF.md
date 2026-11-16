# 외주 작업실 핸드오프

## 최신 — 인생사진첩 레퍼런스 반영 한 장 v003
- 사용자가 새 편집 레퍼런스와 작가별 유사 톤의 다른 색상을 요청. 우선 한 장만 검토.
- 프로젝트 output/interior-sample-v003/가 최신. 큰 사진+원형 타이포+모서리 선+하단 세로 프레임/단 편집, 샌드 브라운 한 장.
- 사용자 피드백 전 다른 작가/페이지에 적용하지 않음. 실제 앱 실행은 미검증.

## 최신 — 인생사진첩 완성형 한 장 예시 v002
- 사용자 요청으로 임의 텍스트·사진을 넣어 실제 책처럼 한 장 디자인. 상단 제목/작가소개·중앙 사진·하단 이야기 영역 구성.
- 사진은 이번 작업용 image_gen 신규 생성. 다른 작업 이미지 사용하지 않음. 예시 작가명·글·사진은 실제 고객 자료와 분리.
- 프로젝트 output/interior-sample-v002/, data/interior_sample_v002.json, scripts/BuildInteriorSampleV002.jsx가 최신. 실제 앱 출력은 미검증.
- 사용자 피드백 전 다른 페이지에 적용하지 않음.

## 최신 — 인생사진첩 내지 한 장 우선
- 사용자 요청으로 한 페이지 시안을 먼저 확인하고 전체 적용은 보류.
- 프로젝트 output/interior-sample-v001/에 4p 대표 시안 PNG/SVG, data에 편집 데이터, scripts/BuildInteriorSample.jsx에 한 쪽 InDesign 생성 코드.
- 실사진·원고는 미수신 자리 표시. 사용자 피드백 이후 이 시안을 바탕으로 이어간다.

갱신: 2026-11-16

## 내지 전체 v002 진행 (2026-11-16)
- 표지뿐 아니라 내지 전체24쪽의 배치·SVG 검토도 작성. `projects/2026_11.16_인생사진첩/output/v002/`와 data/layout_v002.json 참조.
- 현재 스크립트 BuildLayoutV002.jsx. 24p 네이티브 객체·문단 스타일·사진 프레임·출력 보고서 생성 경로를 준비했으나 실제 PC 실행은 미완료.
- 직접 IDML 생성/Adobe 출력 시험에서 빈 페이지가 발견되어 해당 파일은 배포하지 않음. 검토 이미지를 InDesign 출력이라고 보고하지 않음.
- 사진 ZIP 및 고객 추가 원고는 여전히 수신 대기. 다른 작업 이미지 사용 없음.

## 최신 고객자료·실제 상태 (2026-11-16)
- 프로젝트 `projects/2026_11.16_인생사진첩/`의 START-HERE.md·STATUS.md가 최신 기준.
- HWP와 표지 레퍼런스 PDF를 수신·보존·분석. 사진 ZIP 두 개는 각각 32MiB 전송 한도로 미수신. 업로드 완료라고 보고하지 않음.
- 24p: 표지1, 인사말2, 프로그램3, 10명 펼침면4~23, 마무리24. 인사말·작가소개글 등 원고 대기.
- InDesign 검토 구조 생성 JSX/데이터 준비, 실제 앱 실행·INDD/IDML/PDF 출력은 미완료. 사용자 PC 바탕화면에 설치하지 않음.
- InDesign/Illustrator API는 사용자 화면상 비활성화. 아래 이전 서버 조사 내용은 기술 조사이며 실사용 권한이 아님.
- 이전 Adobe 검색 결과의 관련 없는 08.png는 이번 책에 사용·업로드하지 않았으며 앞으로도 사용하지 않음.
- 다음 지시: "인생사진첩 START-HERE.md를 읽고 실제 수신 자료만으로 이어가줘. 사진 ZIP 수신과 작가별 매핑부터 확인해줘."

## 이전 서버 조사 — 인생사진첩
- 폴더 `projects/2026_11.16_인생사진첩/` 생성. 메인은 InDesign, 보조 Illustrator.
- 사용자 요구는 **PC가 꺼져도 서버 백그라운드 실행**. 로컬 원격 조작이나 PC COM 자동화만으로 해결하지 않는다.
- 사용자 확인: Adobe 계정·앱 구매 있음. 서버/API 이용 권한과 동일하다고 가정하지 않는다.
- 공식 문서상 Firefly Services의 InDesign/Illustrator Custom Scripts API가 존재하므로 Python 서버가 API를 호출하는 방식을 우선 검토. 별도 InDesign Server 호스팅은 대안.
- 조사 `projects/2026_11.16_인생사진첩/automation/FEASIBILITY.md`. 프로젝트 STATUS.md가 현재 사실의 기준이다.
- 권한·요금·인증·서버 배포·실제 실행은 미확인/미완료. 이번에는 유료 자원이나 상시 실행 서비스를 만들지 않음.

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

다음 지시문: "freelance/projects/2026_11.16_인생사진첩/START-HERE.md와 STATUS.md를 읽고 이어서 작업해줘."
