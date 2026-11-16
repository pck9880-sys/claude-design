# 활동사진 15장 크기 변경

요청: Photoshop에서 활동사진 15장의 폭을 10cm, 해상도를 300픽셀/인치로 변경. 높이는 원본 비율 유지, 리샘플링 자동.

## 실행

Photoshop에서 **파일 → 스크립트 → 찾아보기**로 `ResizeActivity15_10cm_300ppi.jsx`를 실행하고 활동사진 폴더를 선택한다. 폴더에 지원 사진이 정확히 15장이면 바로 처리한다. 개수가 다르면 해당 폴더의 사진 15장을 직접 선택한다.

결과는 선택 폴더 안의 `폭10cm_300ppi_15장_<시각>`에 별도 저장한다. 원본 확장자를 유지하며 JPEG는 품질12, PNG는 PNG, TIFF는 LZW, PSD는 레이어를 보존한다. 기존 사용자 문서 및 디스크 원본은 덮어쓰지 않는다. 리사이즈 외에 색상·필터·크롭·AI 생성 편집을 적용하지 않는다.

입력의 사본만 열어 처리하고 저장 파일을 다시 열어 폭·해상도·비율을 검사한다. `결과검사.tsv`에 실제 픽셀 크기·ppi·cm·성공/실패를 기록한다. 픽셀 반올림 때문에 폭은 약 1181px이며 Photoshop의 cm 표시는 10.00에 가깝게 표시된다. 높이는 사진마다 다르다.

## 현재 검증 수준

- JavaScript/ExtendScript 구문 검사 완료.
- 실제 사진 15장의 처리 및 Photoshop 실행은 **아직 하지 못함**. 현재 클라우드 작업 공간에는 활동사진이 없고 사용자의 로컬 Photoshop에 연결되지 않음. 연결된 Adobe 저장소의 활동사진 폴더 검색도 일치 결과 없음.
- 이번 스크립트는 PC에서 Photoshop으로 실행해야 한다. 이미지가 이미 수정됐다고 보고하지 않는다.

Adobe 안내: https://helpx.adobe.com/photoshop/desktop/automate-tasks/automation-settings-and-presets/automate-photoshop-with-scripts.html
크기·해상도·리샘플링: https://helpx.adobe.com/photoshop/desktop/crop-resize-transform/resize-adjust-resolution/image-size-resolution-and-resampling.html
