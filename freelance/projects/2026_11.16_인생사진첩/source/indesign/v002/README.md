# v002 — 표지·내지 전체 24쪽

현재 편집 기준: `../../../data/layout_v002.json` 및 `../../../scripts/BuildLayoutV002.jsx`.

## 포함한 내지
- 2p 인사말, 3p 프로그램 소개와 8회기·활동사진 3장.
- 4~23p 작가 10명의 2쪽 펼침면 전체. 가로 중심/세로 중심의 두 가지 검토 배치, 작가소개·작품 제목·설명·쪽번호 포함.
- 24p 함께한 순간들, 활동사진 4~6장 자리·참여자·기관 정보.

사진·원고 미수신 상태의 배치안이다. 실제 작가·사진 방향과 원고 길이에 맞춰 조정해야 한다.

## InDesign 파일 생성

프로젝트 폴더에서 다음을 실행한다.

1. `python scripts/sync_jsx_data.py`
2. `python scripts/build_layout.py`
3. InDesign에서 프로젝트 내부 `scripts/BuildLayoutV002.jsx` 실행.

새 `source/indesign/v002_<시각>/`에 INDD·IDML·검토 PDF·실행 보고서가 생성되도록 구성했다. 기존 문서와 고객 원본은 덮어쓰지 않는다.

**현재 이 스크립트의 실제 PC 실행은 미완료다.** 직접 작성한 IDML을 Adobe 연결 도구로 시험했으나 출력이 빈 화면으로 나와 검수에 실패했다. 해당 IDML·빈 PDF·빈 JPEG는 사용 가능한 결과물로 배포하지 않았다. 현재 폴더에 검증된 완성 INDD/IDML이 있다고 해석하지 않는다.

검토 이미지: `../../../output/v002/`. 이는 같은 좌표 데이터에서 만든 SVG/PNG 배치 검토도이며 InDesign의 실제 출력 화면이 아니다.
