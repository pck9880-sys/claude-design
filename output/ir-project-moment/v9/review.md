# v9 — 7p 원형 그래프와 파트별 이미지

- 기준본: v4/deck_v8.pptx. 사용자 요청: 7p의 70%·30%를 원형 그래프로, 각 파트별 이미지 배치.
- PPTX는 7p XML과 해당 관계, 새 원형 차트·Excel 데이터만 변경. 나머지 14장 XML·원본 미디어는 바이트 단위 보존.
- 70% 저가형 카피캣 / 30% owooii 확보 목표. 420억원 / 180억원은 `ir/data-project-moment/kpi.csv`의 원고 7p 출처 값 그대로 사용. 30%는 목표이며 달성 실적으로 표시하지 않음.
- 좌측: 카피캣 사례 이미지 7장. 중앙: 수정 가능한 PowerPoint 원형 차트. 우측: owooii 화보와 제품 이미지. 기존 상단 메뉴·제목 보존.
- 폰트: 기존 Pretendard 유지. 색: 프로젝트 토큰의 회색과 C73544. 숫자 크게, 단위 작게. 추가 이미지 생성 없음.

## 참고한 기존 자료

- 고객 요구: `output/ir-project-moment/needs-survey.md`, 기존 `style.json`의 에디토리얼·상단바·테두리 박스 기준.
- 사용자 포트폴리오: `홈투게더_IR_최종.pdf` 10~11p(구획·이미지/지표 분리), `키다_IR_최종.pdf` 2·12p(핵심 숫자 위계), `이프_IR_최종.pdf` 4·7p(비교 파트의 이미지 구획).
- 상장사 샘플: `아로마티카.pdf` 9·19p(그래프 구획·절제된 레이블), `에이유브랜즈.pdf` 13·19p(비중 차트·구조 분리).
- 이미지나 내용을 레퍼런스에서 가져오지 않고 기존 7p 이미지를 재사용.

## 검증

- 수치: `check_numbers.py` 통과 + 차트 캐시 70/30 대조.
- 파일: pptx 스킬의 `validate.py --original` 통과.
- 편집한 본문 요소: 1.5cm 여백 안에 위치. 7p 시각 검수로 문구·구분선 간격 보정.
- 기존 덱 전체 검사는 원본의 상단바 여백·선 굵기·작은 글자 등에 경고가 있음. 기준본 대비 신규 경고 없음. 원본의 다른 페이지는 이번 수정 범위 밖이므로 보존. 상세 `verification.json` 참조.
- 전체 PDF는 원본의 7p만 교체. 나머지 14페이지는 원본과 렌더 해시 일치.
- PC C드라이브 저장 여부는 클라우드에서 확인 불가. GitHub 브랜치에 저장 후 PC Git 폴더에서 pull 필요.

## 재생성

1. 저장소 루트에서 `python output/ir-project-moment/v9/edit_slide7.py`.
2. Pretendard를 인식하는 LibreOffice로 `deck_v9.pptx`를 같은 폴더에 PDF 변환.
3. `python output/ir-project-moment/v9/finalize_pdf.py`.
4. `python output/ir-project-moment/v9/verify_slide7.py` 및 스키마·차트 검증.

미리보기: `preview/slide-07.png`. 납품 검토: `7p-preview.pdf`, 전체 `deck_v9.pdf`, 편집본 `deck_v9.pptx`.
