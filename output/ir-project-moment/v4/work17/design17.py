"""v17 리디자인 시안: 딥 네이비 포인트, 라인 박스 없음, 새 상단바, 같은 여백.
python design17.py <src.pptx> <out.pptx> [all|sample]
sample: 1·7·13p 만 남긴 시안 파일
"""
import io
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import numpy as np
from lxml import etree
from PIL import Image, ImageFont
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Cm, Pt, Emu

HERE = Path(__file__).parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / "work13"))
from leaves import leaves  # noqa: E402

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
C_NS = "http://schemas.openxmlformats.org/drawingml/2006/chart"
NAVY = RGBColor(0x1C, 0x54, 0x70)
NAVY2 = RGBColor(0x5F, 0x87, 0x99)
NAVY_L = RGBColor(0xE3, 0xEE, 0xF2)
INK = RGBColor(0x1A, 0x1A, 0x1A)
G1 = RGBColor(0x5B, 0x62, 0x70)
G2 = RGBColor(0x9A, 0xA0, 0xAA)
G3 = RGBColor(0xD5, 0xD9, 0xE0)
RULE = RGBColor(0xE3, 0xE6, 0xEB)
WHITE = RGBColor(255, 255, 255)
L, R, TOP_C, BOT_C = 1.53, 32.34, 5.0, 17.52
MENU = ["Problem", "Brand", "Product", "Market", "Strategy", "Traction", "Financials", "Team"]
FONT_DIR = ROOT / "assets/fonts/Pretendard"


def cm(e):
    return e / 360000


def tw(t, size, weight="Medium"):
    f = ImageFont.truetype(str(FONT_DIR / f"Pretendard-{weight}.ttf"), 200)
    return f.getlength(t) / 200 * size * 0.03528


def setfont(r, font, size, color, spc=None):
    r.font.name = font; r.font.size = Pt(size); r.font.color.rgb = color
    rpr = r._r.get_or_add_rPr()
    for tag in ("ea", "cs"):
        el = rpr.find(f"{{{A}}}{tag}")
        if el is None:
            el = etree.SubElement(rpr, f"{{{A}}}{tag}")
        el.set("typeface", font)
    if spc is not None:
        rpr.set("spc", str(spc))


def text(s, x, y, w, h, lines, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, name="텍스트", spacing=1.15,
         wrap=True):
    tb = s.shapes.add_textbox(Cm(x), Cm(y), Cm(w), Cm(h)); tb.name = name
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.word_wrap = wrap; tf.vertical_anchor = anchor
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.line_spacing = spacing
        for run in ln:
            t, f, sz, c = run[:4]
            r = p.add_run(); r.text = t; setfont(r, f, sz, c, run[4] if len(run) > 4 else None)
    return tb


def rect(s, x, y, w, h, color, name="면", shape=MSO_SHAPE.RECTANGLE):
    sh = s.shapes.add_shape(shape, Cm(x), Cm(y), Cm(w), Cm(max(h, 0.02)))
    sh.fill.solid(); sh.fill.fore_color.rgb = color; sh.line.fill.background(); sh.name = name
    return sh


def line(s, x0, y0, x1, y1, color=RULE, wpt=0.5, dash=None, name="선"):
    ln = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Cm(x0), Cm(y0), Cm(x1), Cm(y1))
    ln.line.color.rgb = color; ln.line.width = Pt(wpt); ln.name = name
    if dash:
        ln.line.dash_style = dash
    return ln


def dot(s, cx, cy, d, color, name="점", ring=False, wpt=1.5):
    o = s.shapes.add_shape(MSO_SHAPE.OVAL, Cm(cx - d / 2), Cm(cy - d / 2), Cm(d), Cm(d)); o.name = name
    if ring:
        o.fill.solid(); o.fill.fore_color.rgb = WHITE; o.line.color.rgb = color; o.line.width = Pt(wpt)
    else:
        o.fill.solid(); o.fill.fore_color.rgb = color; o.line.fill.background()
    return o


def remove(sh):
    sh._element.getparent().remove(sh._element)


def section_label(s, x, y, label, color=INK, right_to=None):
    rect(s, x, y + 0.08, 0.08, 0.36, NAVY, "섹션 막대")
    text(s, x + 0.28, y, 10, 0.52, [[(label, "Pretendard Bold", 11.5, color)]], anchor=MSO_ANCHOR.MIDDLE,
         name="섹션 제목", wrap=False)


# ---------------- 공통: 상단바·제목 ----------------
def header(s, page, total, active):
    for sh in list(s.shapes):
        if sh.name in ("상단선", "메뉴", "활성 표시"):
            remove(sh)
    # 페이지 번호
    line(s, 3.78, 0.6, 3.78, 1.12, RULE, 0.75, name="상단 구분")
    text(s, 4.05, 0.58, 2.5, 0.56, [[(f"{page:02d}", "Pretendard Bold", 10, NAVY),
                                    (f" / {total:02d}", "Pretendard Medium", 10, G2)]],
         anchor=MSO_ANCHOR.MIDDLE, name="페이지 번호", wrap=False)
    # 메뉴 (오른쪽 정렬)
    x = R
    gap = 0.72
    items = []
    for m in reversed(MENU):
        bold = m == active
        w = tw(m, 9.5, "Bold" if bold else "Medium")
        x -= w
        items.append((m, x, w, bold))
        x -= gap
    for m, mx, w, bold in items:
        text(s, mx, 0.6, w + 0.1, 0.52, [[(m, "Pretendard Bold" if bold else "Pretendard Medium", 9.5,
                                           NAVY if bold else G2)]], anchor=MSO_ANCHOR.MIDDLE, name="메뉴",
             wrap=False)
        if bold:
            dot(s, mx - 0.22, 0.86, 0.13, NAVY, "활성 표시")
    line(s, L, 1.5, R, 1.5, RULE, 0.5, name="상단선")
    # 아이브로·타이틀 색
    for sh in s.shapes:
        if sh.name == "아이브로" and sh.has_text_frame:
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    setfont(r, "Pretendard Bold", 10.5, NAVY, 60)


# ---------------- 이미지 자르기 ----------------
def round_none(p):
    p.auto_shape_type = MSO_SHAPE.RECTANGLE


def cover(p, x, y, w, h, trim=False, ax=0.5, ay=0.5):
    im = Image.open(io.BytesIO(p.image.blob)).convert("RGB")
    l, t, r, b = 0, 0, im.width, im.height
    if trim:
        a = np.asarray(im).astype(int)
        ys, xs = np.where(a.min(axis=2) < 245)            # 흰 여백 제거
        l, t, r, b = xs.min(), ys.min(), xs.max(), ys.max()
        sub = a[t:b, l:r]
        bg2 = sub[int(sub.shape[0] * 0.02), int(sub.shape[1] * 0.5)] if False else sub[3, sub.shape[1] // 2]
        ys2, xs2 = np.where(np.abs(sub - sub[3, 3]).sum(axis=2) > 24)   # 회색 패널 안쪽 여백 제거
        l, t, r, b = l + xs2.min() + 1, t + ys2.min() + 1, l + xs2.max() - 1, t + ys2.max() - 1
    cw, ch = r - l, b - t
    if cw / ch > w / h:
        nw = ch * w / h; l += (cw - nw) * ax; r = l + nw
    else:
        nh = cw * h / w; t += (ch - nh) * ay; b = t + nh
    p.crop_left, p.crop_right = l / im.width, 1 - r / im.width
    p.crop_top, p.crop_bottom = t / im.height, 1 - b / im.height
    p.left, p.top, p.width, p.height = Cm(x), Cm(y), Cm(w), Cm(h)
    round_none(p)


# ---------------- 표지 ----------------
def cover_slide(s):
    for sh in s.shapes:
        if sh.name == "헤드라인":
            top = cm(sh.top)
            rect(s, L, top - 0.55, 1.4, 0.13, NAVY, "표지 포인트 막대")
        if sh.name == "서브":
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    r.font.color.rgb = NAVY


# ---------------- 7p ----------------
def ungroup(s):
    tree = s.shapes._spTree
    for g in [x for x in s.shapes if x.shape_type == 6]:
        for sh, (x, y, w, h) in list(leaves(g)):
            el = sh._element
            el.getparent().remove(el)
            tree.append(el)
            sh.left, sh.top, sh.width, sh.height = int(x), int(y), int(w), int(h)
        g._element.getparent().remove(g._element)


def slide7(s):
    ungroup(s)
    pics = {}
    for top in list(s.shapes):
        if top.shape_type == 13:
            pics[top.shape_id] = top
    copycat = [pics[i] for i in (17, 18, 19, 20, 21, 22, 23)]
    main, land, side2, logo = pics[6], pics[8], pics[10], pics[12]
    for sh in list(s.shapes):
        if sh.shape_id in (35, 36, 37, 41, 59, 60, 61, 62, 63, 64, 39, 43, 44, 15):
            remove(sh)
    # 왼쪽: 도넛 + 범례 + 메시지
    lw = 9.6
    text(s, L, TOP_C, lw, 0.5, [[("카테고리 점유율", "Pretendard SemiBold", 10.5, G1)]], name="라벨")
    D = 5.8
    cd = CategoryChartData(); cd.categories = ["owooii", "copycat"]; cd.add_series("s", (0.30, 0.70))
    gf = s.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, Cm(L), Cm(TOP_C + 0.75), Cm(D), Cm(D), cd)
    gf.name = "점유율 도넛"
    ch = gf.chart; ch.has_legend = False; ch.has_title = False
    ser = ch.plots[0].series[0]; ch.plots[0].has_data_labels = False
    for i, c in enumerate((NAVY, G3)):
        pt = ser.points[i]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = c
        pt.format.line.color.rgb = WHITE; pt.format.line.width = Pt(2)
    dn = ch._chartSpace.xpath(".//c:doughnutChart")[0]
    for tag, v in (("firstSliceAng", "0"), ("holeSize", "74")):
        el = dn.find(f"{{{C_NS}}}{tag}")
        if el is None:
            el = etree.SubElement(dn, f"{{{C_NS}}}{tag}")
        el.set("val", v)
    pa = ch._chartSpace.xpath(".//c:plotArea")[0]
    lay = pa.find(f"{{{C_NS}}}layout")
    if lay is None:
        lay = etree.Element(f"{{{C_NS}}}layout"); pa.insert(0, lay)
    lay.clear(); ml = etree.SubElement(lay, f"{{{C_NS}}}manualLayout")
    for t_, v in (("layoutTarget", "inner"), ("xMode", "edge"), ("yMode", "edge"), ("x", "0"), ("y", "0"),
                  ("w", "1"), ("h", "1")):
        etree.SubElement(ml, f"{{{C_NS}}}{t_}").set("val", v)
    sp = ch._chartSpace.find(f"{{{C_NS}}}spPr")
    if sp is None:
        sp = etree.SubElement(ch._chartSpace, f"{{{C_NS}}}spPr")
    sp.clear(); etree.SubElement(sp, f"{{{A}}}noFill")
    ln_ = etree.SubElement(sp, f"{{{A}}}ln"); etree.SubElement(ln_, f"{{{A}}}noFill")
    cy = TOP_C + 0.75 + D / 2
    text(s, L, cy - 1.0, D, 1.3, [[("30", "Pretendard ExtraBold", 34, NAVY), ("%", "Pretendard Bold", 16, NAVY)]],
         PP_ALIGN.CENTER, MSO_ANCHOR.BOTTOM, "도넛 값", 1.0)
    text(s, L, cy + 0.38, D, 0.5, [[("owooii 목표", "Pretendard Medium", 9.5, G1)]], PP_ALIGN.CENTER,
         name="도넛 설명")
    # 범례 2줄
    ly = TOP_C + 0.75 + D + 0.75
    for i, (lab, val, col, vc) in enumerate((("저가형 카피캣", "70% · 420억", G3, INK),
                                             ("owooii", "30% · 180억", NAVY, NAVY))):
        y = ly + i * 0.85
        rect(s, L, y + 0.15, 0.26, 0.26, col, "범례 칸")
        text(s, L + 0.45, y, 4.5, 0.56, [[(lab, "Pretendard SemiBold", 11, G1)]], anchor=MSO_ANCHOR.MIDDLE,
             name="범례")
        text(s, L, y, lw, 0.56, [[(val, "Pretendard Bold", 12, vc)]], PP_ALIGN.RIGHT, MSO_ANCHOR.MIDDLE, "범례 값")
        line(s, L, y + 0.72, L + lw, y + 0.72, RULE, 0.5)
    # 메시지 (하단 정렬)
    text(s, L, BOT_C - 1.75, lw, 1.75,
         [[("프리미엄 포지셔닝으로", "Pretendard Bold", 16, INK)],
          [("카테고리에서 ", "Pretendard Bold", 16, INK), ("30% 마켓 쉐어", "Pretendard ExtraBold", 16, NAVY),
           (" 확보 목표", "Pretendard Bold", 16, INK)]], anchor=MSO_ANCHOR.BOTTOM, name="메시지", spacing=1.3)
    # 오른쪽: 이미지
    rx = 12.2
    rw = R - rx
    gap = 0.18
    text(s, rx, TOP_C, 6, 0.5, [[("저가형 카피캣", "Pretendard Bold", 11, G1)]], anchor=MSO_ANCHOR.MIDDLE,
         name="이미지 라벨", wrap=False)
    line(s, rx + tw("저가형 카피캣", 11, "Bold") + 0.35, TOP_C + 0.25, R, TOP_C + 0.25, RULE, 0.5)
    tw_ = (rw - gap * 6) / 7
    th_ = 3.35
    for i, p in enumerate(copycat):
        cover(p, rx + i * (tw_ + gap), TOP_C + 0.7, tw_, th_)
    oy = TOP_C + 0.7 + th_ + 0.6
    text(s, rx, oy, 6, 0.5, [[("owooii", "Pretendard Bold", 11, NAVY)]], anchor=MSO_ANCHOR.MIDDLE,
         name="이미지 라벨", wrap=False)
    line(s, rx + tw("owooii", 11, "Bold") + 0.35, oy + 0.25, R, oy + 0.25, RULE, 0.5)
    iy = oy + 0.7
    ih = BOT_C - iy
    mim = Image.open(io.BytesIO(main.image.blob)).convert("RGB")
    a_ = np.asarray(mim).astype(int)
    ys_, xs_ = np.where(a_.min(axis=2) < 245)
    sub_ = a_[ys_.min():ys_.max(), xs_.min():xs_.max()]
    ys2, xs2 = np.where(np.abs(sub_ - sub_[3, 3]).sum(axis=2) > 24)
    ratio = (xs2.max() - xs2.min()) / (ys2.max() - ys2.min())
    mw = min(ih * ratio, rw - 6.2)
    cover(main, rx, iy, mw, ih, trim=True)
    sx = rx + mw + gap
    sw = R - sx
    th1 = sw / 2.07
    cover(land, sx, iy, sw, th1)
    bw = (sw - gap) / 2
    bh = ih - th1 - gap
    cover(side2, sx + bw + gap, iy + th1 + gap, bw, bh, ax=0.5)
    # 로고 타일: 검은 바탕에 로고를 다시 앉힘
    im = Image.open(io.BytesIO(logo.image.blob)).convert("RGB")
    a = np.asarray(im).astype(int)
    ys, xs = np.where(a.sum(axis=2) > 120)
    lg = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    PX = 600
    canvas = Image.new("RGB", (PX, int(PX * bh / bw)), tuple(int(v) for v in a[3, 3]))
    sc = min(PX * 0.62 / lg.width, canvas.height * 0.62 / lg.height)
    lg2 = lg.resize((int(lg.width * sc), int(lg.height * sc)), Image.LANCZOS)
    canvas.paste(lg2, ((PX - lg2.width) // 2, (canvas.height - lg2.height) // 2))
    lp = HERE / "p7_logo_square.png"; canvas.save(lp)
    np_ = s.shapes.add_picture(str(lp), Cm(sx), Cm(iy + th1 + gap), Cm(bw), Cm(bh)); np_.name = "owooii 로고 타일"
    remove(logo)


# ---------------- 13p ----------------
def chart13(s, x0, x1, yT, yA, years, stacks, labels, hl, callout):
    n = len(years); colw = (x1 - x0) / n
    cxs = [x0 + colw * (i + 0.5) for i in range(n)]
    base = yA - 0.42
    totals = [sum(v for v, _ in st) for st in stacks]
    H = base - (yT + 2.1)
    k = H / max(totals)
    bw = 0.95
    pts = []
    for i in range(n):
        y = base
        for v, col in stacks[i]:
            h = k * v
            rect(s, cxs[i] - bw / 2, y - h, bw, h, col, f"막대 {years[i]}")
            y -= h
        pts.append((cxs[i], y - 0.7, y))
    # 옅은 영역
    ff = s.shapes.build_freeform(Cm(pts[0][0]), Cm(base), scale=1.0)
    ff.add_line_segments([(Cm(px), Cm(py)) for px, py, _ in pts] + [(Cm(pts[-1][0]), Cm(base))], close=True)
    ar = ff.convert_to_shape(); ar.name = "추세 영역"; ar.line.fill.background()
    spPr = ar._element.spPr
    for el in spPr.findall(f"{{{A}}}solidFill"):
        spPr.remove(el)
    grad = etree.Element(f"{{{A}}}gradFill"); grad.set("rotWithShape", "1")
    gl = etree.SubElement(grad, f"{{{A}}}gsLst")
    for pos, alpha in (("0", "22000"), ("100000", "0")):
        gs = etree.SubElement(gl, f"{{{A}}}gs"); gs.set("pos", pos)
        c = etree.SubElement(gs, f"{{{A}}}srgbClr"); c.set("val", "1C5470")
        etree.SubElement(c, f"{{{A}}}alpha").set("val", alpha)
    lin = etree.SubElement(grad, f"{{{A}}}lin"); lin.set("ang", "5400000"); lin.set("scaled", "0")
    spPr.find(f"{{{A}}}custGeom").addnext(grad)
    for i in range(n - 1):
        line(s, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], NAVY, 1.5, name="추세선")
    for i, (px, py, bt) in enumerate(pts):
        line(s, px, py, px, bt, G2, 0.75, MSO_LINE_DASH_STYLE.ROUND_DOT, "낙하선")
        dot(s, px, py, 0.22, NAVY, "추세 점", ring=True)
        big = i == hl
        text(s, px - 1.8, py - 0.88, 3.6, 0.62, [[(labels[i], "Pretendard ExtraBold", 15 if big else 11.5,
                                                  NAVY if big else INK),
                                                 ("억", "Pretendard Bold", 9 if big else 8, NAVY if big else INK)]],
             PP_ALIGN.CENTER, MSO_ANCHOR.BOTTOM, f"추세 값 {years[i]}", wrap=False)
        if big:
            w = 0.6 + 0.34 * len(callout)
            pl = rect(s, px - w / 2, py - 1.72, w, 0.58, NAVY, "말풍선", MSO_SHAPE.ROUNDED_RECTANGLE)
            pl.adjustments[0] = 0.5
            tf = pl.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
            r = p.add_run(); r.text = callout; setfont(r, "Pretendard Bold", 10, WHITE)
    line(s, x0, yA, x1, yA, RULE, 0.75, name="연도 축")
    for i, cx in enumerate(cxs):
        text(s, cx - 1.2, yA + 0.15, 2.4, 0.46, [[(years[i], "Pretendard SemiBold", 10.5,
                                                   NAVY if i == hl else G1)]], PP_ALIGN.CENTER, name=f"연도 {years[i]}")


def cell_style(cell, fill=None, bottom=None, top=None):
    tcPr = cell._tc.get_or_add_tcPr()
    for tag in ("lnL", "lnR", "lnT", "lnB"):
        for el in tcPr.findall(f"{{{A}}}{tag}"):
            tcPr.remove(el)
    for el in tcPr.findall(f"{{{A}}}solidFill") + tcPr.findall(f"{{{A}}}noFill"):
        tcPr.remove(el)

    def ln(tag, spec):
        el = etree.SubElement(tcPr, f"{{{A}}}{tag}")
        if spec is None:
            el.set("w", "0"); etree.SubElement(el, f"{{{A}}}noFill")
        else:
            w, col = spec
            el.set("w", str(int(w * 12700)))
            sf = etree.SubElement(el, f"{{{A}}}solidFill"); etree.SubElement(sf, f"{{{A}}}srgbClr").set("val", col)
    ln("lnL", None); ln("lnR", None); ln("lnT", top); ln("lnB", bottom)
    if fill:
        sf = etree.SubElement(tcPr, f"{{{A}}}solidFill"); etree.SubElement(sf, f"{{{A}}}srgbClr").set("val", fill)
    else:
        etree.SubElement(tcPr, f"{{{A}}}noFill")


def slide13(s):
    ungroup(s)
    shs = list(s.shapes)
    # 타임라인 재구성
    nums = [x for x in shs if x.name.startswith("타임라인 수치")]
    descs = [x for x in shs if x.name.startswith("타임라인 설명")]
    nums.sort(key=lambda x: x.left); descs.sort(key=lambda x: x.left)
    yrs = [x.name.replace("타임라인 수치 ", "") for x in nums]
    for x in shs:
        if x.name in ("타임라인 선", "타임라인 실적 구간", "타임라인 점") or (x.name == "태그" and cm(x.top) < 6):
            remove(x)
    n = len(nums); colw = (R - L) / n
    line(s, L, 5.62, R, 5.62, RULE, 0.75, name="타임라인 선")
    line(s, L, 5.62, L + colw, 5.62, INK, 1.6, name="타임라인 실적 구간")
    for i, (nb, ds, yr) in enumerate(zip(nums, descs, yrs)):
        x = L + i * colw
        last = i == n - 1
        col = INK if i == 0 else (NAVY if last else NAVY2)
        text(s, x, TOP_C - 0.05, colw - 0.3, 0.5, [[(yr, "Pretendard Bold", 11, col)]], anchor=MSO_ANCHOR.MIDDLE,
             name="타임라인 연도", wrap=False)
        dot(s, x + 0.08, 5.62, 0.18, col, "타임라인 점")
        nb.left, nb.top, nb.width = Cm(x), Cm(5.95), Cm(colw - 0.3)
        ds.left, ds.top, ds.width = Cm(x), Cm(7.3), Cm(colw - 0.3)
        for p in nb.text_frame.paragraphs:
            p.alignment = PP_ALIGN.LEFT
            for r in p.runs:
                r.font.color.rgb = NAVY if last else INK
        for p in ds.text_frame.paragraphs:
            p.alignment = PP_ALIGN.LEFT
            for r in p.runs:
                r.font.color.rgb = G1
    # 기존 막대 → 값 복원
    bars = {}
    for x in shs:
        if x.name.startswith("막대 "):
            col = str(x.fill.fore_color.rgb)
            bars.setdefault(x.name[3:], []).append((cm(x.top), cm(x.height), col))
    totals = [0.8, 6.0, 11.6, 20.2, 60.0, 200.6, 505.8]
    years = ["2023", "2024", "2025", "2026E", "2027E", "2028E", "2029E"]
    cmap = {"C3C9D1": G3, "C73544": NAVY2, "8E2430": NAVY}
    stacks = []
    for yv, tot in zip(years, totals):
        segs = sorted(bars[yv], key=lambda t: -t[0])
        hs = sum(t[1] for t in segs)
        stacks.append([(tot * t[1] / hs, cmap.get(t[2], G3)) for t in segs])
    keep_names = ("표 30",)
    for x in list(s.shapes):
        if cm(x.top) > 8.8 and x.name not in keep_names and x.shape_type != 19:
            remove(x)
    # 섹션 제목
    cx1 = 15.2
    section_label(s, L, 9.25, "매출 성장 (억원)")
    text(s, L, 9.25, cx1 - L, 0.52, [[("매출 CAGR ('25–'29E) ", "Pretendard Medium", 10, G1),
                                     ("157", "Pretendard ExtraBold", 15, NAVY), ("%", "Pretendard Bold", 10, NAVY)]],
         PP_ALIGN.RIGHT, MSO_ANCHOR.MIDDLE, "CAGR")
    # 범례
    lx = L
    for lab, col in (("디바이스", G3), ("코스메틱", NAVY2), ("유통 순액", NAVY)):
        rect(s, lx, 10.2 + 0.12, 0.24, 0.24, col, "범례 칸")
        text(s, lx + 0.36, 10.2, 2.5, 0.48, [[(lab, "Pretendard Medium", 9.5, G1)]], anchor=MSO_ANCHOR.MIDDLE,
             name="범례", wrap=False)
        lx += 0.36 + tw(lab, 9.5) + 0.6
    chart13(s, L, cx1, 10.95, 16.95, years, stacks, ["0.8", "6.0", "11.6", "20.2", "60.0", "200.6", "505.8"],
            6, "글로벌")
    # 표
    tx = 16.6
    section_label(s, tx, 9.25, "요약 손익 (억원)")
    gf = [x for x in s.shapes if x.shape_type == 19][0]
    tbl = gf.table
    nrow, ncol = len(tbl.rows), len(tbl.columns)
    tw_tot = R - tx
    first = 3.6
    rest = (tw_tot - first) / (ncol - 1)
    for j, col in enumerate(tbl.columns):
        col.width = Cm(first if j == 0 else rest)
    th_ = BOT_C - 10.2
    for row in tbl.rows:
        row.height = Cm(th_ / nrow)
    gf.left, gf.top = Cm(tx), Cm(10.2)
    for i in range(nrow):
        for j in range(ncol):
            c = tbl.cell(i, j)
            last = j == ncol - 1
            head = i == 0
            fill = "E3EEF2" if last else None
            bottom = (1.0, "1A1A1A") if head else ((0.5, "E3E6EB") if i < nrow - 1 else (1.0, "1A1A1A"))
            cell_style(c, fill, bottom, (1.0, "1A1A1A") if head else None)
            c.margin_left = c.margin_right = Cm(0.25)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            for p in c.text_frame.paragraphs:
                p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.RIGHT
                for r in p.runs:
                    if head:
                        setfont(r, "Pretendard Bold", 10.5, NAVY if last else G1)
                    elif j == 0:
                        setfont(r, "Pretendard SemiBold", 10.5, INK)
                    else:
                        setfont(r, "Pretendard ExtraBold" if last else "Pretendard Medium", 11 if last else 10.5,
                                NAVY if last else INK)


def drop_slides(prs, keep):
    sldIdLst = prs.slides._sldIdLst
    for i, sid in reversed(list(enumerate(list(sldIdLst)))):
        if i + 1 not in keep:
            rId = sid.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
            prs.part.drop_rel(rId)
            sldIdLst.remove(sid)


if __name__ == "__main__":
    src, out, mode = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else "sample")
    prs = Presentation(src)
    total = len(prs.slides)
    act = {7: "Market", 13: "Financials"}
    cover_slide(prs.slides[0])
    for pg in (7, 13):
        header(prs.slides[pg - 1], pg, total, act[pg])
    slide7(prs.slides[6])
    slide13(prs.slides[12])
    if mode == "sample":
        drop_slides(prs, {1, 7, 13})
    prs.save(out)
    print("저장", out)
