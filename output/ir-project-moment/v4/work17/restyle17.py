"""v17 전체 리디자인: 딥 네이비, 라인 박스 제거, 태그→라벨, 새 상단바, 아이콘 보강.
python restyle17.py <사용자 v16.pptx> <출력.pptx>
"""
import subprocess
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Cm, Pt

HERE = Path(__file__).parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
import design17 as d  # noqa: E402

src, out = sys.argv[1], sys.argv[2]
tmp1 = HERE / "_stage1.pptx"
tmp2 = HERE / "_stage2.pptx"
ICON = HERE / "icons"

# 1) 7·13p·표지 전용 재구성
prs = Presentation(src)
total = len(prs.slides)
d.cover_slide(prs.slides[0])
d.header(prs.slides[6], 7, total, "Market"); d.slide7(prs.slides[6])
d.header(prs.slides[12], 13, total, "Financials"); d.slide13(prs.slides[12])
prs.save(tmp1)

# 2) 남은 빨강 계열 → 네이비 계열
subprocess.run([sys.executable, str(ROOT / "tools/recolor_pptx.py"), str(tmp1), str(tmp2),
                "C73544=1C5470", "8E2430=123A4F", "E7A2AA=BCD3DD", "E07A84=7FA3B3",
                "FCF5F6=EEF4F6", "FBEFF0=EEF4F6", "FBE5EE=EEF4F6"], check=True)

prs = Presentation(tmp2)
ACTIVE = {2: "Problem", 3: "Brand", 4: "Brand", 5: "Product", 6: "Market", 8: "Strategy", 9: "Strategy",
          10: "Traction", 11: "Traction", 12: "Strategy", 14: "Team", 15: "Team"}


def line_w(sh):
    try:
        return sh.line.width.pt if sh.line.width else 0
    except Exception:
        return 0


def has_fill(sh):
    try:
        return sh.fill.type == 1
    except Exception:
        return False


def rgb(sh):
    try:
        return str(sh.fill.fore_color.rgb)
    except Exception:
        return "FFFFFF"


def to_label(sh):
    sh.fill.background(); sh.line.fill.background()
    tf = sh.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.word_wrap = False
    for p in tf.paragraphs:
        p.alignment = PP_ALIGN.LEFT
        for r in p.runs:
            d.setfont(r, "Pretendard Bold", 10.5, d.NAVY, 40)


def icon(s, name, x, y, size=0.62):
    p = s.shapes.add_picture(str(ICON / f"{name}.png"), Cm(x), Cm(y), Cm(size), Cm(size))
    p.name = f"아이콘 {name}"
    return p


for idx, s in enumerate(prs.slides, 1):
    if idx in (1, 3, 7, 13):
        continue
    d.ungroup(s)
    d.header(s, idx, total, ACTIVE.get(idx, ""))
    for sh in list(s.shapes):
        if sh.shape_type != 1:
            continue
        txt = sh.text_frame.text.strip() if sh.has_text_frame else ""
        try:
            ast = sh.auto_shape_type
        except Exception:
            ast = None
        # 라인 박스 제거
        if not txt and ast == MSO_SHAPE.RECTANGLE and line_w(sh) >= 1.4:
            if sh.name == "카드" or (has_fill(sh) and rgb(sh) not in ("FFFFFF",)):
                sh.line.fill.background()
            else:
                d.remove(sh)
            continue
        if sh.name == "카드":
            sh.line.fill.background()
            if has_fill(sh) and rgb(sh) == "FFFFFF":
                sh.fill.solid(); sh.fill.fore_color.rgb = d.RGBColor(0xF6, 0xF7, 0xF9)
            elif has_fill(sh):
                sh.fill.solid(); sh.fill.fore_color.rgb = d.NAVY_L
            continue
        # 채운 알약 태그 → 네이비 라벨
        if txt and ast == MSO_SHAPE.ROUNDED_RECTANGLE and has_fill(sh) and sh.name != "말풍선":
            if sh.height < Cm(0.95):
                to_label(sh)
    # 페이지별 아이콘·정리
    if idx == 5:
        for sh in list(s.shapes):
            if sh.has_text_frame and sh.text_frame.text.startswith("Point."):
                x, y = d.cm(sh.left), d.cm(sh.top)
                icon(s, {"01": "fan", "02": "volume-x", "03": "sliders-horizontal"}[sh.text_frame.text[-2:]],
                     x, y - 0.02, 0.6)
                sh.left = Cm(x + 0.85)
    if idx == 9:
        rows = sorted([sh for sh in s.shapes if sh.name == "성장 모멘텀"], key=lambda x: x.top)
        for sh, ic in zip(rows, ["store", "megaphone", "globe", "package-plus"]):
            x, y = d.cm(sh.left), d.cm(sh.top)
            icon(s, ic, x, y + 0.08, 0.62)
            sh.left = Cm(x + 0.9); sh.width = sh.width - Cm(0.9)
        for sh in s.shapes:
            if sh.has_text_frame and sh.text_frame.text.strip() == "n/a":
                for p in sh.text_frame.paragraphs:
                    for r in p.runs:
                        r.text = "—"
    if idx == 12:
        for sh in list(s.shapes):
            if sh.has_text_frame and sh.text_frame.text.strip() in ("Cross Selling", "Global Expansion"):
                x, y = d.cm(sh.left), d.cm(sh.top)
                icon(s, "layers" if sh.text_frame.text.startswith("Cross") else "globe", x, y, 0.6)
                sh.left = Cm(x + 0.85)
    if idx == 11:
        for sh in list(s.shapes):
            if sh.name.startswith("아이콘 "):
                nm = sh.name.split(" ", 1)[1]
                if (ICON / f"{nm}.png").exists():
                    p = s.shapes.add_picture(str(ICON / f"{nm}.png"), sh.left, sh.top, sh.width, sh.height)
                    p.name = sh.name
                    d.remove(sh)

# 3p: 어두운 배경 위 네이비 글자 → 밝은 네이비 그레이
for sh in prs.slides[2].shapes:
    if sh.has_text_frame:
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                try:
                    if str(r.font.color.rgb) in ("1C5470", "123A4F"):
                        r.font.color.rgb = d.RGBColor(0xBC, 0xD3, 0xDD)
                except Exception:
                    pass
# 6p: 대지 밖 '2,200만 가구'를 상단 한 줄 요약으로
s6 = prs.slides[5]
for sh in list(s6.shapes):
    if sh.left > prs.slide_width - Cm(0.2):
        if "2,200" in (sh.text_frame.text if sh.has_text_frame else ""):
            sh.left, sh.top = Cm(d.L), Cm(5.0)
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    r.font.color.rgb = d.NAVY
        elif sh.has_text_frame and "생애" in sh.text_frame.text:
            d.remove(sh)
d.text(s6, d.L + 7.6, 5.2, 16, 1.0, [[("생애 단계별 가구 예시", "Pretendard SemiBold", 12, d.G1)]],
       anchor=MSO_ANCHOR.MIDDLE, name="가구 설명", wrap=False)
d.line(s6, d.L, 6.95, d.R, 6.95, d.RULE, 0.5, name="구분선")
# 15p: 대지 밖 기부 썸네일·문구를 Donation 영역으로
s15 = prs.slides[14]
dx = None
for sh in s15.shapes:
    if sh.name == "기부 영상 썸네일":
        dx = Cm(d.L) - sh.left
for sh in list(s15.shapes):
    if sh.left < 0 and dx is not None:
        sh.left = sh.left + dx
    if sh.name == "썸네일 계정":
        v = [x for x in s15.shapes if x.name == "기부 영상 썸네일"][0]
        sh.left = v.left + Cm(0.35); sh.top = v.top + v.height - Cm(0.95)
for sh in s15.shapes:
    if sh.name == "태그" and sh.has_text_frame and sh.text_frame.text.strip() == "Donation":
        sh.left = Cm(d.L)
    if sh.name in ("기부 영상 썸네일", "기부 후기 썸네일", "기부 사진 썸네일"):
        sh.top = Cm(6.0)
    if sh.name == "기부 문구":
        sh.top = Cm(15.0)
        for p in sh.text_frame.paragraphs:
            p.alignment = PP_ALIGN.LEFT
v = [x for x in s15.shapes if x.name == "기부 영상 썸네일"][0]
for sh in s15.shapes:
    if sh.name == "썸네일 계정":
        sh.left = v.left + Cm(0.35); sh.top = v.top + v.height - Cm(0.95)

prs.save(out)
tmp1.unlink(); tmp2.unlink()
print("저장", out)
