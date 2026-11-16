# 다른 PC(회사 데스크톱)에서 이어서 작업하기

아이맥을 꺼도 GitHub에 있는 자료만으로 이어갈 수 있게 정리한 절차다.

## 자료가 있는 곳 (두 군데)
| 자료 | 위치 | 이유 |
|---|---|---|
| 구성안·스크립트·작업 기록 | 이 저장소 `claude-design`, 브랜치 `codex/project-moment-ir` | 공개 저장소. 실명·사진 없음 |
| 실제 사진(원본·CMYK)·실명 데이터·사용자 시안 캡처 | 비공개 `pck9880-sys/imac-outputs` Release **insaeng-album-assets** | 어르신 실명·얼굴 사진이라 공개 저장소에 올리지 않음 |
| 최신 InDesign 패키지(v008) | 비공개 `imac-outputs` Release **v008-insaeng-album** | INDD + Links + 폰트. 손으로 고친 INDD를 이어서 편집할 때 쓴다 |

## 처음 한 번 준비
1. GitHub CLI 로그인: `gh auth login`. 계정은 pck9880-sys. 비공개 Release를 받으려면 이 계정이어야 한다.
2. 저장소 받기
   ```
   gh repo clone pck9880-sys/claude-design
   cd claude-design && git checkout codex/project-moment-ir
   ```
3. 비공개 자료를 프로젝트 폴더에 풀기
   ```
   cd freelance/projects/2026_11.16_인생사진첩
   gh release download insaeng-album-assets -R pck9880-sys/imac-outputs -p "insaeng-album-assets.zip"
   ```
   그다음 zip을 **이 폴더에 그대로** 푼다. 그러면 `links/`, `data/`, `refs/` 아래에 자료가 채워진다.
   - Windows: `Expand-Archive insaeng-album-assets.zip -DestinationPath . -Force`
   - Mac: `ditto -x -k insaeng-album-assets.zip .`
4. 폰트: InDesign에서 아래 폰트가 보여야 한다.
   - **Pretendard**: 저장소 `assets/fonts/Pretendard`
   - **Noto Serif CJK KR**(Bold 사용): 저장소에 없으므로 PC에 설치한다. v008 패키지의 `Document fonts`에도 들어 있다.
5. InDesign 2025, Python 3 + Pillow(`pip install pillow`). Python은 CMYK 다시 변환이나 데이터 재생성이 필요할 때만 쓴다.

## 작업 방식 두 가지
- **스크립트로 다시 만들기** (권장): `scripts/BuildAlbumV008.jsx`를 InDesign에서 실행하면 `source/indesign/v008_<시각>/`에 INDD가 새로 생긴다. 사진은 `links/photos-cmyk/`를 프로젝트 기준 상대 경로로 찾는다. **패키지가 없어도 된다.**
- **손으로 고친 INDD 이어서 편집**: v008 패키지 zip을 받아서 패키지 폴더의 INDD를 연다. INDD는 사진을 절대 경로로 기억하므로 **패키지(Links 포함)로 옮겨야 링크가 깨지지 않는다.** 손으로 수정한 파일은 다시 패키지로 묶어 Release에 올린다.

## 갱신 규칙
- 사진·실명 데이터가 바뀌면 `insaeng-album-assets.zip`을 다시 만들어 Release 첨부를 교체한다: `gh release upload insaeng-album-assets <zip> --clobber -R pck9880-sys/imac-outputs`
- 이 공개 저장소에는 `.gitignore`로 막아 둔 실명·사진 폴더를 올리지 않는다.
- Claude 메모리·개인 스킬(`~/.claude`)은 아이맥에만 있다. 다른 PC의 Claude는 이 문서, `CLAUDE.md`, `STATUS.md`, `DESIGN-v009-PLAN.md`를 먼저 읽게 한다.
