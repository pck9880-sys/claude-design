# 레이어 2 · 이미지 · 그래픽 · 영상 (프롬프트)

> 11 nano-banana, 13 canvas-design, 14 algorithmic-art, 15 remotion(→ `remotion-best-practices`, `remotion-create`) 은 스킬로 설치됨.
> nano-banana는 Gemini API 키(`GEMINI_API_KEY`)를 직접 환경변수로 설정해야 동작합니다.

## 12. banana-claude — 5요소 이미지 프롬프트 공식
```
이미지 생성 프롬프트를 아래 5요소로 구성해 줘. 각 요소를 한 줄씩 채운 뒤 하나의 문장으로 합쳐.
1) 주제(Subject): 무엇이 / 누가
2) 행동·구도(Action/Composition): 무엇을 하고, 어떤 앵글·프레이밍인지
3) 환경(Setting): 장소, 시간대, 배경
4) 스타일(Style): 매체(사진/3D/일러스트), 참고 미학, 컬러 팔레트(브랜드 HEX)
5) 기술 사양(Technical): 조명, 렌즈/화각, 비율(예: 4:5), 해상도, 금지 요소(텍스트, 워터마크)
```

## 16. claude-remotion — 타이틀 순차 등장 · 타이밍
```
Remotion으로 타이틀 시퀀스를 만들어 줘 (30fps).
- 단어/줄 단위 스태거 등장: 간격 4–6프레임, spring({damping: 200}) 사용
- 각 요소 등장 0–12f, 유지, 퇴장 8f (진입보다 짧게)
- 핵심 키워드는 브랜드 색으로 강조, 마지막에 1초 홀드
- 타이밍 표(요소, 시작 프레임, 끝 프레임)를 코드 위 주석으로 남겨
```

## 17. blender-motion — Python 기반 3D 장면
```
Blender Python(bpy) 스크립트로 3D 장면을 만들어 줘. 실행: blender -b -P scene.py
- 오브젝트: <설명>, 재질은 브랜드 색 Principled BSDF
- 카메라 궤도 애니메이션 120프레임, 키프레임 보간은 Bezier ease
- 3점 조명, EEVEE 렌더, 1080x1080, PNG 시퀀스를 renders/ 에 출력
- 매직 넘버는 스크립트 상단 상수로 분리
```

## 18. ae-motion — JSX 기반 After Effects 스크립트
```
After Effects ExtendScript(.jsx)를 작성해 줘. (File > Scripts > Run Script File로 실행)
- 1920x1080, 30fps, 5초 컴포지션 생성
- 텍스트 레이어 <문구>, 위치/불투명도 키프레임 + Easy Ease(속도 영향 75%)
- 모든 작업을 app.beginUndoGroup / endUndoGroup 으로 감싸기
- 레이어 이름 규칙: TXT_, SHP_, BG_ 접두사
```
