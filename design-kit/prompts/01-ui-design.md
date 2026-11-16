# 레이어 1 · 프런트엔드 & UI 디자인 (프롬프트)

> 01 frontend-design, 02 impeccable, 03 taste-skill, 04 animate, 06 theme-factory, 09 brandkit 은 스킬로 설치됨 (`.claude/skills/`).
> 아래는 설치형 소스가 없는 항목입니다. 작업 지시에 그대로 붙여 쓰세요.

## 05. design-motion — 세 가지 관점의 모션 검수
> 설치된 `design-motion-principles` 스킬과 함께 쓰면 좋습니다.

```
이 화면의 모든 애니메이션을 세 가지 관점으로 검수해 줘.
1) 목적: 이 모션이 상태 변화·위치·인과를 설명하는가? 장식뿐이면 제거.
2) 물리감: 이징(ease-out 진입 / ease-in 퇴장), 지속시간(마이크로 120–200ms, 화면 전환 250–400ms), 스태거 간격 일관성.
3) 접근성·성능: prefers-reduced-motion 대응, transform/opacity만 애니메이트, 레이아웃 시프트 없음.
각 항목을 [통과/수정 필요] 표로 정리하고 수정 코드까지 제시.
```

## 07. figma-implement — 디자인을 그대로 구현
```
Figma 링크: <URL>
Figma MCP의 get_design_context와 get_screenshot으로 해당 프레임을 읽고,
- 간격·폰트·색은 Figma 변수(get_variable_defs)를 우선 사용, 하드코딩 금지
- 기존 컴포넌트가 있으면 재사용(Code Connect 매핑 확인)
- 구현 후 브라우저 스크린샷을 Figma 스크린샷과 나란히 비교해 차이 목록을 보고
픽셀 차이가 4px 이상이면 수정 후 재비교.
```

## 08. playwright-mcp — 실제 브라우저 스크린샷 피드백
> MCP 설정은 `design-kit/.mcp.json` 에 포함됨.
```
구현이 끝나면 Playwright로 375 / 768 / 1440px 세 폭에서 스크린샷을 찍고,
레이아웃 깨짐, 텍스트 넘침, 가로 스크롤, 대비 부족을 스스로 점검해 고친 뒤 다시 찍어.
최종 스크린샷 3장을 screenshots/ 에 저장.
```

## 10. designer-skills — 전문적인 개발 전달 명세
```
완성된 화면에 대해 개발 핸드오프 명세(handoff.md)를 작성해 줘.
- 컴포넌트 목록과 상태(default/hover/focus/disabled/loading/empty/error)
- 디자인 토큰 표(색, 타이포, 간격, radius, 그림자)
- 반응형 브레이크포인트별 변경점
- 인터랙션·모션 스펙(트리거, 지속시간, 이징)
- 접근성 요구(포커스 순서, aria 라벨, 대비비)
```
