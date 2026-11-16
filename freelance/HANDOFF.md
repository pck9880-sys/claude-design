# 외주 작업실 핸드오프

## 최신 — 사진·원고를 채운24쪽 예시 full-demo-v005
- 사용자 명시 허용: 사진·내용을 임의로 넣어 최대한 반영한 상태로 업로드.
- 이번 작업용 새 생성 이미지:20개 작품 장면+4개 활동 장면(활동사진9개 슬롯에 일부 반복). 6장2×2 시트 원본은 links/demo-v005/, 프레임은 각 사분면을 비파괴로 크롭.
- 가상 작가10명·소개·20작품 제목/설명·인용·인사말·프로그램 소개·8회기·명단·마무리 모두 예시 원고로 채움. 고객 book-data.json/원본은 변경하지 않음.
- 우측 작품제목10곳 누락 보완: 상단 제목25mm, 설명39mm, 사진65mm부터. 좌측v007 디자인·작가별10색·15mm여백·바깥쪽번호 유지.
- 실제 기관/지원명과 원고 지원문구 유지, 미수신 로고는 임시 문자표기. 표지/마무리에 디자인 예시 표시.
- 최신 output/full-demo-v005/24p PDF·PNG·펼침면, data/demo_content_v005.json·layout_demo_full_v005.json/.jsxinc, scripts/BuildDemoFullAlbumV005.jsx.
- 전체24쪽·대기문구0·우측제목/설명10개·텍스트폭/높이·15mm 검증 및 JSX 구문 확인. 실제 로컬InDesign 앱 실행은 미검증.


## 최신 — 원고 대조 검수
- output/full-v004/MANUSCRIPT-AUDIT.md에 HWP 구성안 대조 결과 기록.
-24쪽/10명×2쪽/표지10칸/활동3칸·마무리6칸 및 기관/지원문구는 일치.
- 오른쪽10쪽에 원고가 요구한 작품제목 칸 누락. 상단 설명만 존재, 검수 중 디자인 자동변경은 하지 않음.
- 실제 사진/로고·추가 원고 미반영, 대기표시72개. 실제 INDD 다운로드 차단으로 내부검증 미완료.


## 최신 — INDD·IDML 문서 패키지 변환
- 사용자는 스크립트가 아니라 InDesign 문서 파일 자체를 요청.
- 최신24p full-v004 검토PDF를 Adobe document_convert_pdf로 변환. INDD/IDML 모두 success:true와 ZIP 다운로드 링크 반환.
- INDD: https://to.adobe.com/oZa9S / IDML: https://to.adobe.com/tc2X0 (임시 다운로드 링크).
- 로컬 다운로드는 네트워크403으로 차단되어 패키지 추출·실제 열림·텍스트/프레임 편집성·문서 여백/펼침면 확인 및 바이너리 GitHub 업로드 미완료. 변환 성공 응답과 실물 검증을 구분.
- 링크 제공은 가능. JSX 직접 생성본과 PDF변환본은 다름. 실제 파일은 JSX로 새로 생성했다고 보고하지 않음.


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

## 추가 — 활동사진 15장 Photoshop 리사이즈
- 폭10cm·300ppi·비율유지·자동 리샘플 요청. 프로젝트 scripts/photoshop/ 아래 실행용 JSX와 안내 준비.
- 원본 별도 보존, 저장 결과 재열기 검사, 실제 처리 아직 미완료(로컬 PC/사진 접근 불가).

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
