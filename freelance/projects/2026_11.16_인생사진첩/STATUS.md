# 현재 상태

갱신: 2026-11-16

## 확정된 요구
- 폴더명 `2026_11.16_인생사진첩`.
- InDesign 메인, Illustrator 보조.
- 개인 PC가 꺼져도 서버가 실행을 이어가야 함. 로컬 COM 자동화만으로 충족되지 않음.
- Adobe 계정과 앱 구매 있음. 사용자에게 키·비밀번호를 채팅으로 요구하지 않음.

## 조사 결과
- Python은 작업 접수·파일 준비·API 호출·상태 확인을 맡을 수 있음. Python 자체가 InDesign 조판·렌더 엔진을 대체하지는 않음.
- Adobe Firefly Services의 InDesign API에는 Custom Scripts, Rendition, IDML 관련 기능이 있고 Illustrator API에도 Custom Scripts·렌더링 기능이 있음. 따라서 지원 범위·권한이 확보되면 클라우드 실행 설계 가능.
- 별도 대안은 InDesign Server를 호스팅하는 방식. 개인 데스크톱 앱 구독과 별도 제품이며 서버·라이선스·운영 준비 필요.
- 이 대화의 Adobe 연결 도구는 일부 클라우드 변환·렌더·병합을 제공하지만 사용자 정의 스크립트 실행 도구나 상시 작업 큐를 연결한 상태는 아님.
- 정확한 공식 근거·권한 조건은 `automation/FEASIBILITY.md`.

## 준비 완료 / 미완료
- 준비: GitHub 프로젝트 폴더, 원본·링크·결과·작업 기록 구조, 서버 방식 비교와 조사 기록.
- 미완료: 사용 계정의 InDesign API·Illustrator API 권한, 계약·비용 확인, 서버/저장소/큐 배포, 인증 연결, 실제 작업 실행·복구·품질 검증.
- PC용 설치 스크립트만 실행해서 이 요구사항이 완료되는 것은 아님.

## 다음 단계
1. Adobe Developer Console/관리자에서 두 API 이용 가능 여부와 계약·요금 확인. 데스크톱 구매만으로 권한이 있다고 가정하지 않음.
2. 기존 연결 도구로 충분한지, Python 서버 + Firefly Services Custom Scripts가 필요한지 실제 작업 범위로 결정.
3. 원본·사진·폰트·링크와 판형을 받은 뒤 작은 테스트 문서로 INDD/IDML/PDF와 Illustrator 연동을 검증.
4. 권한·비용·실행 환경 확인 후 상시 작업 서버를 구성. 현재 배포하거나 유료 자원을 생성하지 않음.
