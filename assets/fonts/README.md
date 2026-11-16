# 폰트 카탈로그

이 PC에 설치된 폰트 중 **재배포가 허용된 무료 폰트(SIL OFL·Apache·MIT)만** 저장소에 넣었다. 각 폴더의 `LICENSE.txt` 참고.
견본: `specimen.png` · 다른 기기/클라우드에 설치: `python tools/install_fonts.py`

## 규칙
1. **기본 폰트는 무조건 Pretendard** (제목·본문·표·차트 모두).
2. **이 카탈로그에 없는 폰트는 쓰지 않는다.** 특히 맑은 고딕·굴림·돋움·바탕·궁서·HY 계열·한컴(HCR) 계열·Arial·Calibri·Times New Roman 등 시스템 기본 폰트 금지.
3. 디자인 폰트는 **한 작업에 1종까지**, 표지·섹션 제목·큰 숫자 같은 강조 자리에만. 본문은 항상 Pretendard.
4. **영문 전용 폰트에는 한글을 쓰지 않는다** (한글이 □로 깨짐).
5. 산돌구름다리 등 구독 폰트는 이 저장소에 넣지 않는다. PC에서 사용자가 지정할 때만 쓰고, 클라우드에서는 Pretendard로 대체.

## 추천 목록 (Claude가 여기서 골라 쓴다)

| 역할 | 폰트 | 한글 | 어울리는 작업 |
|---|---|---|---|
| **기본** | **Pretendard** (9굵기) | ✅ | 모든 작업의 기본. IR 덱 본문·제목 |
| 프레젠테이션 제목 | Freesentation (가변 굵기) | ✅ | 신뢰·차분한 톤의 IR 제목, 발표 슬라이드 |
| 세리프 | Noto Serif KR (가변 굵기) | ✅ | 브랜드 스토리, 인용문, 격식 있는 표지, 문화·출판·교육 |
| 손그림·제도 | Kkakdugi Drafting (4종) | ✅ | 교육·키즈·크리에이티브, 친근한 톤의 강조 문구 |
| 픽셀·레트로 | Mulmaru | ✅ | 게임·엔터·IT 서비스의 포인트 제목 |
| 레트로 도스 | DOSIyagiBoldface, DOSPilgi | ✅ | 레트로 콘셉트 행사·포스터 (IR에는 비추천) |
| 영문·숫자 강조 | Montserrat (18종), Plus Jakarta Sans (14종) | ❌ | 영문 슬로건, KPI 큰 숫자, 영문 로고타입 |
| 테크 영문 | Orbitron, Audiowide | ❌ | 테크·모빌리티·게임의 영문 포인트 |
| 포스터 영문 | Outward(초장체), Black Ops One, Rubik Glitch, Chewy, Special Elite(타자기) | ❌ | 행사 포스터·배너의 영문 제목 (IR 비추천) |
| 예비 | Noto Sans KR | ✅ | Pretendard에 없는 글자 대체용으로만 |

### 업종·톤별 빠른 선택
- 금융·B2B·헬스케어·공공 IR → Pretendard만 (필요하면 표지에 Freesentation)
- 소비재·라이프스타일·브랜드 → Pretendard + 표지·인용에 Noto Serif KR
- 교육·키즈·커뮤니티 → Pretendard + 강조에 Kkakdugi Drafting
- 게임·엔터·테크 → Pretendard + 영문/숫자에 Orbitron 또는 Montserrat, 포인트 제목에 Mulmaru
