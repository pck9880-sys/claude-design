# Claude·Codex 이어하기

## 현재 먼저 할 일
최신 사용자 허용에 따라 임의 원고·새 생성 사진으로 완성형 내지 예시를 제작했다. 예시 작가명/글/사진은 실제 고객 자료가 아니며 demo-sample과 interior_sample_v002 데이터에만 보관한다.
사용자가 내지 한 장을 보고 결정하겠다고 했다. output/interior-sample-v002/의 시안과 최신 피드백을 먼저 읽고 그 한 장만 수정한다. 나머지 23쪽의 새 디자인 적용은 피드백 이후에 진행. InDesign 한 쪽 생성 스크립트는 scripts/BuildInteriorSampleV002.jsx.

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
