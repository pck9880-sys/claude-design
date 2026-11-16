---
name: ir-deliver
description: 완성된 IR 덱을 고객 납품 버전으로 확정한다. 사용자가 /ir-deliver 를 입력하거나 "납품", "고객에게 보낼 버전 확정"이라고 할 때 사용. 최종 검수 → 납품 폴더 복사 → git 태그 → 푸시.
argument-hint: "<작업명> [메모]"
---

# /ir-deliver

인자: `$ARGUMENTS` (예: `/ir-deliver heuk-son 1차 시안`)

1. **최종 검수** (하나라도 실패하면 멈추고 사용자에게 보고, 태그하지 않는다)
   - `python ir/scripts/check_numbers.py <deck.json>`
   - `python ir/scripts/build_deck.py <deck.json>` 후 `python ir/scripts/check_margins.py output/ir-<작업명>/deck.pptx --tokens output/ir-<작업명>/tokens.json`
   - `python ir/scripts/render.py output/ir-<작업명>/deck.pptx` → 미리보기 이미지를 직접 보고 넘침·겹침·잘림 확인
2. **버전 번호**: `git tag -l "ir-<작업명>-v*"`로 마지막 번호 확인 → 다음 번호 `vN`
3. **납품 폴더**: `output/ir-<작업명>/deliver/vN/` 에 복사
   - `<회사명>_IR_vN.pptx`, `<회사명>_IR_vN.pdf`
   - `NOTE.md`: 날짜, 메모, 사용한 데이터 파일과 기준일, 고객 확인이 끝나지 않은 항목
4. **커밋·태그·푸시**
   - `git add output/ir-<작업명> ir/` → 커밋 메시지 `IR 납품: <회사명> vN — <메모>`
   - `git tag -a ir-<작업명>-vN -m "<회사명> vN 납품: <메모>"`
   - `git push origin main --follow-tags`
5. **보고**: 납품 파일 경로 2개, 태그 이름, 고객 확인이 남은 항목만.

되돌리기가 필요하면: `git show ir-<작업명>-vN:output/ir-<작업명>/deliver/vN/` 로 그 시점 파일을 꺼낸다 (기존 태그는 지우거나 옮기지 않는다).
