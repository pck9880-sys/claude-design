# Claude·Codex 이어하기

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

## 현재 먼저 할 일
새 레퍼런스 반영 시안 v003 한 장을 먼저 보고 방향성을 확인하는 단계다. 작가별 포인트색은 서로 다르되 비슷한 저채도 톤으로 계획하고, 현재는 샌드 브라운 한 장만 존재한다.
최신 사용자 허용에 따라 임의 원고·새 생성 사진으로 완성형 내지 예시를 제작했다. 예시 작가명/글/사진은 실제 고객 자료가 아니며 demo-sample과 interior_sample_v002 데이터에만 보관한다.
사용자가 내지 한 장을 보고 결정하겠다고 했다. output/interior-sample-v003/의 시안과 최신 피드백을 먼저 읽고 그 한 장만 수정한다. 나머지 23쪽의 새 디자인 적용은 피드백 이후에 진행. InDesign 한 쪽 생성 스크립트는 scripts/BuildInteriorSampleV003.jsx.

## 한 문장 시작

> freelance/projects/2026_11.16_인생사진첩/CLAUDE.md와 START-HERE.md를 읽고 인생사진첩을 이어서 작업해줘. 고객 HWP 원고와 최신 수신 현황을 확인하고, 다른 작업 이미지는 사용하지 마. InDesign 실행 가능 여부를 먼저 구분하고 24쪽 구조를 유지해줘.

## v002 — 내지 전체 작업의 최신 진입점

- 먼저 `output/v002/README.md`, `source/indesign/v002/README.md`를 읽는다.
- `data/layout_v002.json`에 표지·모든 내지 24쪽의 배치가 들어 있다.
- 현재 InDesign 생성 스크립트는 **scripts/BuildLayoutV002.jsx**이다. 기존 BuildAlbum.jsx는 이전 구조 초안.
- 데이터 갱신 후 `python scripts/sync_jsx_data.py` → `python scripts/build_layout.py` → InDesign에서 BuildLayoutV002.jsx 실행 순서.
- 자체 SVG/PNG 검토도와 Adobe 실제 출력은 구분한다. 실험한 직접 IDML은 빈 출력이 발견되어 배포하지 않았다. 자세한 내용은 automation/RENDER-CHECK-v002.md.

## 파일 위치

- `inputs/manuscript/`: 고객 HWP 원본 사본. 변경하지 않음.
- `inputs/references/`: 남산정 PDF 원본 사본. **표지 참고 전용**.
- `data/manuscript-extracted.md`: HWP 문단 원문. 문서 내부 스크립트는 실행하지 않고 추출.
- `data/client-request.md`: 사용자가 전달한 고객 요청과 그 해석.
- `data/book-data.json`: 편집 내용·24쪽 페이지 구성·자산 배치 데이터의 기준.
- `data/book-data.jsxinc`: InDesign이 읽는 데이터 사본. JSON 변경 후 `scripts/sync_jsx_data.py`로 갱신.
- `data/asset-mapping.csv`: 사진 수신 후 이름·작품·경로 대응 확인용. CSV를 고쳐도 JSON에 자동 반영되지 않으므로 대응을 확인해 JSON을 수정.
- `data/page-plan.csv`: 최초 구성 요약. 최신 구성 변경 시 JSON과 함께 갱신.
- `data/input-manifest.json`: 원본 체크섬과 사진 ZIP 미수신 기록.
- `scripts/BuildAlbum.jsx`: 새 24p InDesign 검토 구조 생성. 기존 원본 덮어쓰기 금지.

## 사진 수신 시

1. 활동사진·작품사진 ZIP을 32MiB 이하로 나눠 다시 받거나, 사용자가 이 비공개 저장소에 올린 실제 경로를 확인한다. 현재 첨부 포인터만으로는 큰 ZIP을 내려받을 수 없었다.
2. 원본 압축파일은 보존. 압축을 풀 때 상대 경로 이탈·심볼릭 링크를 차단하고 파일명·개수·크기·사진 방향·해상도를 목록화한다.
3. 작품 20장인지 실제 확인하고 각 작가의 2장과 표지용 1장을 정확히 연결한다. 불명확하면 임의로 인물과 작품을 묶지 않는다.
4. 허가된 실제 사진만 `links/` 아래에 넣고 JSON의 `assets[].path`를 프로젝트 기준 상대 경로로 지정한다. `artists[].mapping_confirmed`는 확인된 경우에만 true.
5. 실제 원본은 LFS 적용 대상·업로드 한도를 확인해 저장. JPG는 현재 일반 Git이며 파일당 100MB를 넘으면 별도로 LFS 적용.

## InDesign에서 검토 구조 생성

이 클라우드 세션에는 InDesign이 없다. JSX는 코드 구문을 확인한 제작 준비물이며 실제 앱 실행·렌더 검증은 아직 하지 않았다.

1. 해당 GitHub 브랜치를 사용 중인 비공개 작업 폴더에서 연다. 바탕화면 설치는 필요하지 않다.
2. `python scripts/sync_jsx_data.py` 실행(프로젝트 폴더 기준). JSON 검사 및 JSX 데이터 갱신.
3. InDesign에 Pretendard Regular/Bold 설치·활성화를 확인.
4. 창 → 유틸리티 → 스크립트 → 사용자 폴더에 BuildLayoutV002.jsx의 사본만 넣으면 상대 데이터 경로를 찾지 못하므로, 프로젝트 내부 **scripts/BuildLayoutV002.jsx 자체를 가리키는 스크립트 별칭/바로가기**로 실행하거나, 프로젝트 폴더 구조 전체를 유지한 채 스크립트를 실행한다.
5. `source/indesign/review_<시각>/`에 INDD·IDML·검토 PDF·BUILD-REPORT.txt가 생성된다. 고객 원본이나 기존 작업 파일을 덮어쓰지 않는다.
6. 자료가 없으면 원고·사진 자리가 표시된 **검토 구조**다. INDD를 열어 모든 펼침면과 오버셋·누락 링크·폰트·사진 비례를 확인한다. 부정확한 위치가 있으면 JSX/데이터에서 수정.
7. 완성된 INDD에서 IDML·검토 PDF를 다시 출력하고 핸드오프 및 실제 실행 결과를 기록한 뒤 commit/push.

## 제작 전 확인 필요

- 사진 ZIP 두 개의 실제 수신과 작가별 매핑.
- 인사말·작가소개글, 성함, 작품 제목·설명, 프로그램 소개·8회기 주제, 참여자·강사·봉사자 명단, 기관 정보.
- 기관·사랑의열매 로고 원본.
- 판형, 제본, 총 24p에 표지/뒤표지 포함 여부(현재 원고는 1~24p로 읽음), 인쇄소 도련·색상 사양.

## 완료 판정

파일이 GitHub에 있다는 것, JSX 구문이 통과한 것, 실제 Adobe 앱에서 실행한 것, 시각 검수한 것은 각각 구분한다. 최종 인쇄 전에는 빈 문구·미배치 이미지·미확정 매핑·누락 로고가 없어야 한다.
