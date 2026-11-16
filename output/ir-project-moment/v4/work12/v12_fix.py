"""v12: 사용자 v11 기준.
10p 매출·영업이익 그래프를 연도별 2개 막대(한 기준선)로, 10·13p 타임라인 점을 알약 가운데로.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Cm, Pt

SRC, OUT = sys.argv[1], sys.argv[2]
RED = RGBColor(0xC7, 0x35, 0x44)
DEEP = RGBColor(0x8E, 0x24, 0x30)
PALE = RGBColor(0xE7, 0xA2, 0xAA)
DARK = RGBColor(0x17, 0x1A, 0x1F)
BAR2 = RGBColor(0x45, 0x4C, 0x56)
TXT2 = RGBColor(0x45, 0x4C, 0x56)
GRAY = RGBColor(0x84, 0x8C, 0x97)
LINE = RGBColor(0xC3, 0xC9, 0xD1)
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
cm = lambda e: e / 360000

prs = Presentation(SRC)


def setfont(r, font, size, color):
    r.font.name = font; r.font.size = Pt(size); r.font.color.rgb = color
    rpr = r._r.get_or_add_rPr()
    for tag in ("ea", "cs"):
        el = rpr.find(f"{{{A}}}{tag}")
        if el is None:
            el = etree.SubElement(rpr, f"{{{A}}}{tag}")
        el.set("typeface", font)


def text(s, x, y, w, h, t, size, font, color, align=PP_ALIGN.CENTER, name="텍스트"):
    tb = s.shapes.add_textbox(Cm(x), Cm(y), Cm(w), Cm(h)); tb.name = name
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.TOP
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = t; setfont(r, font, size, color)
    return tb


def rect(s, x, y, w, h, color, name):
    sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Cm(x), Cm(y), Cm(w), Cm(max(h, 0.03)))
    sh.fill.solid(); sh.fill.fore_color.rgb = color; sh.line.fill.background(); sh.name = name
    return sh


# ---------- 타임라인: 점을 알약 가운데 아래로 ----------
for sn in (10, 13):
    s = prs.slides[sn - 1]
    shs = list(s.shapes)
    pills = [x for x in shs if x.name == "태그" and abs(cm(x.top) - 4.72) < 0.05]
    dots = [x for x in shs if x.name == "타임라인 점"]
    centers = []
    for pl in pills:
        pcx = pl.left + pl.width // 2
        d = min(dots, key=lambda d: abs(d.left - pl.left))
        d.left = pcx - d.width // 2
        centers.append(pcx)
    first = min(centers)
    for ln_name in ("타임라인 선", "타임라인 실적 구간"):
        for ln in [x for x in shs if x.name == ln_name]:
            end = ln.left + ln.width
            ln.left = first
            ln.width = end - first
    # 실적 구간 끝을 마지막 실적 점(또는 사용자가 정한 끝)에 맞춤
    act = [x for x in shs if x.name == "타임라인 실적 구간"]
    if act:
        a = act[0]
        end = a.left + a.width
        nearest = min(centers, key=lambda c: abs(c - end))
        if abs(nearest - end) < Cm(1.5):
            a.width = nearest - a.left

# ---------- 10p 그래프: 연도별 막대 2개 ----------
s = prs.slides[9]
box = [x for x in s.shapes if x.name == "그래프 상자"][0]
gx, gy, gw, gh = cm(box.left), cm(box.top), cm(box.width), cm(box.height)
kill = ("매출 막대", "매출 값", "영업이익 막대", "영업이익 값", "행 이름", "매출 기준선", "그래프 구분선",
        "영업이익 기준선", "연도 ")
for x in list(s.shapes):
    if x.name.startswith(kill):
        x._element.getparent().remove(x._element)

years = ["2023", "2024", "2025", "2026E"]
rev = [82, 604, 1200, 2020]
op = [-16, 100, 130, 0]
# 범례
lx, ly = gx + 0.45, gy + 1.3
for lab, col in (("매출액", PALE), ("영업이익", BAR2)):
    rect(s, lx, ly + 0.12, 0.28, 0.28, col, "범례 칸")
    tb = text(s, lx + 0.4, ly, 2.4, 0.5, lab, 10.5, "Pretendard SemiBold", TXT2, PP_ALIGN.LEFT, "범례")
    lx += 0.4 + (1.35 if lab == "매출액" else 1.6) + 0.5
base = gy + gh - 1.15
top = gy + 2.75
px0, px1 = gx + 0.6, gx + gw - 0.6
colw = (px1 - px0) / 4
bw, bg = 0.95, 0.14
RH = base - top
OH = RH * 0.42           # 영업이익은 별도 눈금(최대값이 막대 높이의 42%)
for i in range(4):
    cx = px0 + colw * (i + 0.5)
    last = i == 3
    # 매출
    x1 = cx - bw - bg / 2
    h = RH * rev[i] / max(rev)
    rect(s, x1, base - h, bw, h, RED if last else PALE, f"매출 막대 {years[i]}")
    text(s, x1 - 0.6, base - h - 0.55, bw + 1.2, 0.5, f"{rev[i]:,}", 12 if last else 11,
         "Pretendard ExtraBold" if last else "Pretendard Bold", RED if last else DARK, name=f"매출 값 {years[i]}")
    # 영업이익
    x2 = cx + bg / 2
    v = op[i]
    h2 = OH * abs(v) / max(abs(o) for o in op)
    rect(s, x2, base - h2 if v >= 0 else base, bw, h2, DEEP if last else BAR2, f"영업이익 막대 {years[i]}")
    ty = base - h2 - 0.55 if v > 0 else base - 0.55
    text(s, x2 - 0.6, ty, bw + 1.2, 0.5, f"{v:,}", 12 if last else 11,
         "Pretendard ExtraBold" if last else "Pretendard Bold", DEEP if last else TXT2, name=f"영업이익 값 {years[i]}")
    text(s, cx - 1.2, base + 0.35, 2.4, 0.5, years[i], 11.5, "Pretendard Bold", RED if last else TXT2,
         name=f"연도 {years[i]}")
ln = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Cm(px0 - 0.1), Cm(base), Cm(px1 + 0.1), Cm(base))
ln.line.color.rgb = LINE; ln.line.width = Pt(0.8); ln.name = "기준선"

prs.save(OUT)
print("저장", OUT)
