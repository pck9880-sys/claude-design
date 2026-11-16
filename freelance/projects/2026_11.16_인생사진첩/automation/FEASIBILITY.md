# PC 종료 상태의 Adobe 백그라운드 제작 — 가능성 확인

확인 날짜: 2026-11-16. 공식 문서에 근거한 기술 조사이며 사용자 계정의 권한·요금·실행 성공을 확인한 결과는 아니다.

## 결론

기술적으로 가능하다. 요구 조건에 맞는 우선 검토안은 **서버의 Python 작업 관리자 + Adobe Firefly Services의 InDesign/Illustrator API**이다. Python은 요청·파일·API 호출·상태를 관리하고, Adobe 클라우드 엔진이 실제 Adobe 문서 처리를 맡는다. 개인 PC에 설치된 앱이나 원격 화면 연결에 의존하지 않는 구조다.

현재 상시 서버·자동 작업 큐는 배포하지 않았다. 이 조사로 향후 모든 편집이 지원되거나 기존 구독에 무료로 포함된다고 보장하지 않는다. 실제 작업별 지원 기능·폰트·링크·파일 제한을 테스트해야 한다.

## 방법 비교

| 방법 | PC가 꺼져도 실행 | 이번 요구와의 관계 |
|---|---|---|
| Python + PC의 Adobe COM/JSX | 불가 | PC가 켜져 있는 로컬 자동화에 적합 |
| 이 대화의 Adobe 클라우드 연결 도구 | 지원 작업은 가능 | 변환·렌더·병합 등 현재 노출된 기능에 한정. 상시 작업 큐는 별개 |
| Python 서버 + Firefly Services InDesign/Illustrator API | 권한·실행 서버가 있으면 가능 | 사용자 정의 스크립트 포함 지원 범위를 확인해 우선 검토 |
| 별도 InDesign Server 호스팅 | 서버가 가동 중이면 가능 | 자체 운영 대안. Illustrator 실행은 별도 해결 필요 |

## 확인한 공식 기능

- [InDesign API 개요](https://developer.adobe.com/firefly-services/docs/indesign-apis/): 데이터 병합, 렌더링, 사용자 정의 스크립트, 문서 정보, INDD→IDML 등.
- [InDesign API 인증](https://developer.adobe.com/firefly-services/docs/indesign-apis/getting-started/): Developer Console 프로젝트, InDesign API 구성, OAuth Server-to-Server 자격 증명 필요.
- [Illustrator API 개요](https://developer.adobe.com/firefly-services/docs/illustrator/): 사용자 정의 스크립트, 렌더링, 데이터 병합, 문서 처리 등.
- [Illustrator API 인증](https://developer.adobe.com/firefly-services/docs/illustrator/getting-started/): Adobe 담당자와 준비한 API 프로젝트·서버 간 인증을 전제로 함. 사용자 계정에서의 제공 여부는 별도 확인.
- [InDesign Server 소개](https://developer.adobe.com/indesign/uxp/introduction/applications/ids): UI 없는 자동 조판 엔진.
- [InDesign Server FAQ](https://www.adobe.com/products/indesignserver/faq.html): 별도 서버 제품, 지원 플랫폼·버전 호환·클라우드 서버 라이선스 설명. 데스크톱 제품의 일반 스크립팅과 서버 엔진 운영을 구분함.
- [pywin32 공식 저장소](https://github.com/mhammond/pywin32): Python의 Windows COM 지원. 이는 로컬 PC 자동화 경로이며 PC 종료 요구를 해결하지 않음.

## 제안하는 작업 흐름 — 설계안, 미배포

1. 휴대폰/Claude/Codex에서 수정 요청과 자료를 준비해 작업 기록을 저장.
2. 상시 가동 Python 작업 서버가 지정된 요청을 접수. 작업 ID·입력 버전·상태를 기록.
3. InDesign API에서 템플릿/문서와 스크립트를 처리. 보조 벡터 작업은 Illustrator API의 지원 범위에서 실행하고 링크 자산으로 사용.
4. 완료된 원본·IDML·검토 PDF를 접근 가능한 파일 저장소에 보관하고 GitHub에 버전 기록과 결과 위치 저장. 대용량 원본은 용량에 따라 LFS/별도 저장소를 선택.
5. 폰트 누락·링크 누락·오버셋·페이지 수·실제 출력 화면을 검수. 실패는 기록하고, 불명확한 요청을 무한 재시도하지 않음.

GitHub 폴더는 작업을 실행하는 서버가 아니다. GitHub Actions를 사용하더라도 별도 인증·자료 저장·작업 시간 제한과 비용 설계가 필요하다. 이번에는 워크플로를 설치하지 않았다.

## 실행 전에 필요한 확인

- 계정에서 InDesign API와 Illustrator API를 사용할 수 있는지, 계약·사용량·요금.
- 자체 InDesign Server를 택한다면 설치 가능한 서버와 해당 라이선스.
- 서버의 비밀 저장소에 인증 연결. 자격 증명을 GitHub 파일이나 채팅에 기록하지 않음.
- 원본 템플릿·사진·폰트와 사용 허용 범위, 인쇄 사양.
- 소규모 실제 호출로 편집 가능한 원본 및 출력 결과 확인. 기존 도구가 지원하는 작업은 해당 Adobe 도구 사용.
