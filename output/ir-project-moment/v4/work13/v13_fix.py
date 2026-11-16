"""v13: 사용자 v12 기준. 10·13p 그래프를 레퍼런스 스타일로 (추세선+점+점선 낙하선+옅은 영역,
연도 축 링 마커, 강조 연도 말풍선 알약, 세로 범례, 'Step-by-step Growth')."""
import copy
import sys
sys.stdout.reconfigure(encoding="utf-8")
from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Cm, Pt, Emu
sys.path.insert(0, __file__.rsplit("\\", 1)[0] if "\\" in __file__ else ".")
from leaves import leaves

SRC, OUT = sys.argv[1], sys.argv[2]
RED = RGBColor(0xC7, 0x35, 0x44)
DEEP = RGBColor(0x8E, 0x24, 0x30)
PALE = RGBColor(0xE7, 0xA2, 0xAA)
DEV = RGBColor(0xC3, 0xC9, 0xD1)
DARK = RGBColor(0x17, 0x1A, 0x1F)
TXT2 = RGBColor(0x45, 0x4C, 0x56)
GRAY = RGBColor(0x84, 0x8C, 0x97)
LINE = RGBColor(0xC3, 0xC9, 0xD1)
WHITE = RGBColor(255, 255, 255)
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
prs = Presentation(SRC)


def setfont(r, font, size, color):
    r.font.name = font; r.font.size = Pt(size); r.font.color.rgb = color
    rpr = r._r.get_or_add_rPr()
    for tag in ("ea", "cs"):
        el = rpr.find(f"{{{A}}}{tag}")
        if el is None:
            el = etree.SubElement(rpr, f"{{{A}}}{tag}")
        el.set("typeface", font)


def text(s, x, y, w, h, runs, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.BOTTOM, name="텍스트"):
    tb = s.shapes.add_textbox(Cm(x), Cm(y), Cm(w), Cm(h)); tb.name = name
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.word_wrap = False; tf.vertical_anchor = anchor
    p = tf.paragraphs[0]; p.alignment = align
    for t, f, sz, c in runs:
        r = p.add_run(); r.text = t; setfont(r, f, sz, c)
    return tb


def rect(s, x, y, w, h, color, name, shape=MSO_SHAPE.RECTANGLE):
    sh = s.shapes.add_shape(shape, Cm(x), Cm(y), Cm(w), Cm(max(h, 0.03)))
    sh.fill.solid(); sh.fill.fore_color.rgb = color; sh.line.fill.background(); sh.name = name
    return sh


def line(s, x0, y0, x1, y1, color, wpt, dash=None, name="선"):
    ln = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Cm(x0), Cm(y0), Cm(x1), Cm(y1))
    ln.line.color.rgb = color; ln.line.width = Pt(wpt); ln.name = name
    if dash:
        ln.line.dash_style = dash
    return ln


def ring(s, cx, cy, d, color, wpt, name):
    o = s.shapes.add_shape(MSO_SHAPE.OVAL, Cm(cx - d / 2), Cm(cy - d / 2), Cm(d), Cm(d))
    o.fill.solid(); o.fill.fore_color.rgb = WHITE
    o.line.color.rgb = color; o.line.width = Pt(wpt); o.name = name
    return o


def pill(s, cx, y, label, color, name="말풍선"):
    w = 0.6 + 0.34 * len(label)
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Cm(cx - w / 2), Cm(y), Cm(w), Cm(0.6))
    sh.adjustments[0] = 0.5; sh.fill.solid(); sh.fill.fore_color.rgb = color; sh.line.fill.background()
    sh.name = name
    tf = sh.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE; tf.word_wrap = False
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = label; setfont(r, "Pretendard Bold", 10, WHITE)
    # 아래로 향한 작은 꼬리
    t = s.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, Cm(cx - 0.13), Cm(y + 0.58), Cm(0.26), Cm(0.16))
    t.rotation = 180; t.fill.solid(); t.fill.fore_color.rgb = color; t.line.fill.background(); t.name = name + " 꼬리"


def area(s, pts, base, name="추세 영역"):
    ff = s.shapes.build_freeform(Cm(pts[0][0]), Cm(base), scale=1.0)
    ff.add_line_segments([(Cm(x), Cm(y)) for x, y in pts] + [(Cm(pts[-1][0]), Cm(base))], close=True)
    sh = ff.convert_to_shape(); sh.name = name
    sh.line.fill.background()
    spPr = sh._element.spPr
    for el in spPr.findall(f"{{{A}}}solidFill") + spPr.findall(f"{{{A}}}noFill"):
        spPr.remove(el)
    grad = etree.Element(f"{{{A}}}gradFill"); grad.set("rotWithShape", "1")
    gl = etree.SubElement(grad, f"{{{A}}}gsLst")
    for pos, alpha in (("0", "26000"), ("100000", "0")):
        gs = etree.SubElement(gl, f"{{{A}}}gs"); gs.set("pos", pos)
        c = etree.SubElement(gs, f"{{{A}}}srgbClr"); c.set("val", "C73544")
        etree.SubElement(c, f"{{{A}}}alpha").set("val", alpha)
    lin = etree.SubElement(grad, f"{{{A}}}lin"); lin.set("ang", "5400000"); lin.set("scaled", "0")
    geom = spPr.find(f"{{{A}}}custGeom")
    geom.addnext(grad)
    return sh


def chart(s, x0, x1, yT, yA, years, groups, legend, hl, callout, unit="", line_vals=None, step_text=True):
    """groups: [ [ [(v,color),..stack] per year ], ... ] 막대 묶음(최대 2), groups[0] 이 추세선 기준.
    groups[1] 은 별도 눈금(최대값 = 높이의 40%)."""
    n = len(years)
    colw = (x1 - x0) / n
    cxs = [x0 + colw * (i + 0.5) for i in range(n)]
    base = yA - 0.42
    # 범례(세로) + Step-by-step
    ly = yT
    for lab, col in legend:
        rect(s, x0, ly + 0.11, 0.26, 0.26, col, "범례 칸")
        text(s, x0 + 0.38, ly, 3.0, 0.46, [(lab, "Pretendard SemiBold", 10, TXT2)], PP_ALIGN.LEFT,
             MSO_ANCHOR.MIDDLE, "범례")
        ly += 0.5
    if step_text:
        text(s, x1 - 5.0, yT, 5.0, 0.46, [("≫  Step-by-step Growth", "Pretendard Medium", 9.5, GRAY)],
             PP_ALIGN.RIGHT, MSO_ANCHOR.MIDDLE, "Step-by-step")
    ng = len(groups)
    bw = 0.82 if ng == 2 else 1.0
    gap = 0.12
    totals = [sum(v for v, _ in st) for st in groups[0]]
    top_res = 2.35                       # 말풍선+라벨+점 자리
    H = base - (yT + top_res)
    k0 = H / max(totals)
    pts = []
    for i in range(n):
        gx = cxs[i] - (bw * ng + gap * (ng - 1)) / 2
        # 묶음 0 (쌓기)
        y = base
        for v, col in groups[0][i]:
            h = k0 * v
            rect(s, gx, y - h, bw, h, col, f"막대 {years[i]}")
            y -= h
        bar_top = y
        px, py = gx + bw / 2, bar_top - 0.7
        pts.append((px, py, bar_top))
        # 묶음 1 (별도 눈금)
        if ng == 2:
            vals = [st[0][0] for st in groups[1]]
            k1 = H * 0.40 / max(abs(v) for v in vals)
            v, col = groups[1][i][0]
            h = k1 * abs(v)
            bx = gx + bw + gap
            rect(s, bx, base - h if v >= 0 else base, bw, h, col, f"보조 막대 {years[i]}")
            ty = (base - h - 0.5) if v > 0 else (base - 0.5)
            text(s, bx - 0.6, ty, bw + 1.2, 0.46, [(f"{v:,}", "Pretendard Bold", 10.5 if i != hl else 11.5,
                                                   DEEP if i == hl else TXT2)], name=f"보조 값 {years[i]}")
    # 영역·추세선·낙하선·점
    area(s, [(p[0], p[1]) for p in pts], base)
    for i in range(n - 1):
        line(s, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], RED, 1.5, name="추세선")
    for i, (px, py, bt) in enumerate(pts):
        line(s, px, py, px, bt, GRAY, 0.75, MSO_LINE_DASH_STYLE.ROUND_DOT, "낙하선")
        ring(s, px, py, 0.24, RED, 1.5, "추세 점")
        val = line_vals[i] if line_vals else totals[i]
        big = i == hl
        text(s, px - 1.8, py - 0.9, 3.6, 0.62,
             [(val, "Pretendard ExtraBold", 15 if big else 12.5, RED if big else DARK),
              (unit, "Pretendard Bold", 9 if big else 8, RED if big else DARK)], name=f"추세 값 {years[i]}")
        if big and callout:
            pill(s, px, py - 1.72, callout, RED)
    # 연도 축: 점선 + 링 마커
    line(s, x0, yA, x1, yA, LINE, 0.75, MSO_LINE_DASH_STYLE.ROUND_DOT, "연도 축")
    for i, cx in enumerate(cxs):
        ring(s, cx, yA, 0.3, RED if i == hl else GRAY, 1.6, "연도 마커")
        text(s, cx - 1.2, yA + 0.24, 2.4, 0.46, [(years[i], "Pretendard Bold", 11, RED if i == hl else TXT2)],
             anchor=MSO_ANCHOR.TOP, name=f"연도 {years[i]}")


# ================= 10p =================
s10 = prs.slides[9]
for sh in list(s10.shapes):
    if sh.shape_id in range(108, 133):
        sh._element.getparent().remove(sh._element)
chart(s10, 20.58, 31.89, 10.3, 16.55,
      ["2023", "2024", "2025", "2026E"],
      [[[(82, PALE)], [(604, PALE)], [(1200, PALE)], [(2020, RED)]],
       [[(-16, GRAY)], [(100, TXT2)], [(130, TXT2)], [(0, DEEP)]]],
      [("매출액", PALE), ("영업이익 (별도 축)", TXT2)], 3, "한·미 진입",
      line_vals=["82", "604", "1,200", "2,020"], step_text=False)

# ================= 13p =================
s13 = prs.slides[12]
g = [x for x in s13.shapes if x.name == "그룹 13"][0]
keep = {}
bars = {}
for sh, (x, y, w, h) in leaves(g):
    if sh.shape_id in (145, 56):
        el = copy.deepcopy(sh._element)
        keep[sh.shape_id] = (el, x, y)
    if sh.name.startswith("막대 "):
        bars.setdefault(sh.name[3:], []).append((y, h, sh.fill.fore_color.rgb))
totals = {"2023": 0.8, "2024": 6.0, "2025": 11.6, "2026": 20.2, "2027": 60.0, "2028": 200.6, "2029": 505.8}
stacks = []
for yr in ["2023", "2024", "2025", "2026", "2027", "2028", "2029"]:
    segs = sorted(bars[yr], key=lambda t: -t[0])          # 아래부터
    hs = sum(t[1] for t in segs)
    stacks.append([(totals[yr] * t[1] / hs, t[2]) for t in segs])
g._element.getparent().remove(g._element)
for sid, (el, x, y) in keep.items():
    s13.shapes._spTree.append(el)
    sh = s13.shapes[-1]
    sh.left, sh.top = int(x), int(y)
chart(s13, 2.2, 14.75, 10.65, 16.95,
      ["2023", "2024", "2025", "2026E", "2027E", "2028E", "2029E"],
      [stacks], [("디바이스", DEV), ("코스메틱", RED), ("유통 순액", DEEP)], 6, "글로벌",
      unit="억", line_vals=["0.8", "6.0", "11.6", "20.2", "60.0", "200.6", "505.8"], step_text=False)

prs.save(OUT)
print("저장", OUT)
