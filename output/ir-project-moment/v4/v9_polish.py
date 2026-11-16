"""v9: 사용자 저장본(v8 수정) 기준, 대지 밖으로 빼 둔 6·7·10·11·13·15p 요소 디벨롭.

입력: work_v9_src.pptx (바탕화면 '프로젝트모먼트_IR_1차시안_v8.pptx' 사본)
출력: 프로젝트모먼트_IR_1차시안_v9.pptx
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Pt, Cm, Emu

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
W9 = HERE / "work9"
SRC = HERE / "work_v9_src.pptx"
OUT = HERE / "프로젝트모먼트_IR_1차시안_v9.pptx"

RED = RGBColor(0xC7, 0x35, 0x44)
DARK = RGBColor(0x17, 0x1A, 0x1F)
TXT2 = RGBColor(0x45, 0x4C, 0x56)
GRAY = RGBColor(0x84, 0x8C, 0x97)
LIGHT = RGBColor(0xE8, 0xEB, 0xEF)
LINE = RGBColor(0xC3, 0xC9, 0xD1)

prs = Presentation(SRC)
SW = prs.slide_width


def off_group(slide):
    return [sh for sh in slide.shapes if sh.shape_type == 6 and (sh.left < 0 or sh.left >= SW - Cm(0.2))]


def restore(g):
    """대지 밖 그룹을 원래 자리(chOff)로, 배율 1로 되돌린다."""
    x = g._element.grpSpPr.xfrm
    x.off.x, x.off.y = x.chOff.x, x.chOff.y
    x.ext.cx, x.ext.cy = x.chExt.cx, x.chExt.cy


def remove(sh):
    sh._element.getparent().remove(sh._element)


def child(g, sid):
    return next(c for c in g.shapes if c.shape_id == sid)


def text(slide, x, y, w, h, s, size, font="Pretendard SemiBold", color=DARK, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, name=None):
    tb = slide.shapes.add_textbox(Cm(x), Cm(y), Cm(w), Cm(h))
    if name:
        tb.name = name
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    lines = s if isinstance(s, list) else [s]
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = 1.15
        segs = ln if isinstance(ln, list) else [(ln, color)]
        for t, c in segs:
            r = p.add_run()
            r.text = t
            r.font.name = font
            r.font.size = Pt(size)
            r.font.color.rgb = c
            rpr = r.font._element.get_or_add_rPr() if hasattr(r.font._element, "get_or_add_rPr") else r._r.get_or_add_rPr()
            for tag in ("ea", "cs"):
                el = rpr.find(f"{{http://schemas.openxmlformats.org/drawingml/2006/main}}{tag}")
                if el is None:
                    el = etree.SubElement(rpr, f"{{http://schemas.openxmlformats.org/drawingml/2006/main}}{tag}")
                el.set("typeface", font)
    return tb


def picture(slide, path, x, y, h=None, w=None, name=None):
    im = Image.open(path)
    if h is not None and w is None:
        w = h * im.width / im.height
    if w is not None and h is None:
        h = w * im.height / im.width
    pic = slide.shapes.add_picture(str(path), Cm(x), Cm(y), Cm(w), Cm(h))
    if name:
        pic.name = name
    return pic


# ---------------- 6p: 상단 '2,200만 가구' + 가족 한 장면 ----------------
s6 = prs.slides[5]
for g in off_group(s6):
    remove(g)
fam = Image.open(ROOT / "assets/generated/pm-ir-v9-p6-households-v2.png").convert("RGB")
# 사람이 모인 가로 띠만 잘라 쓴다 (세로 260~850px)
band = fam.crop((40, 250, 1500, 850))
band_p = W9 / "p6_family_band.jpg"
band.save(band_p, quality=92)
IMG_H = 3.0
img_w = IMG_H * band.width / band.height
img_x = 32.36 - img_w
picture(s6, band_p, img_x, 4.55, h=IMG_H, name="생애 단계 가족 이미지")
text(s6, 1.53, 4.55, 9.0, 0.6, "생애 단계별 가구 예시", 12, "Pretendard ExtraBold", DARK, name="라벨")
text(s6, 1.53, 5.05, 10.0, 1.3, "2,200만 가구", 30, "Pretendard ExtraBold", RED, name="2,200만 가구")
# 생애 단계 흐름: 점선 연결 + 점 + 이름
stages = ["청년 1인 가구", "부부·파트너", "영유아 양육", "학령기 자녀", "시니어 가구"]
tl_x0, tl_x1 = 12.2, img_x - 1.6
ly = 5.95
ln = s6.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Cm(tl_x0), Cm(ly), Cm(tl_x1), Cm(ly))
ln.line.color.rgb = LINE
ln.line.width = Pt(0.8)
ln.name = "생애 단계 연결선"
step = (tl_x1 - tl_x0) / (len(stages) - 1)
for i, st in enumerate(stages):
    cx = tl_x0 + step * i
    d = s6.shapes.add_shape(MSO_SHAPE.OVAL, Cm(cx - 0.11), Cm(ly - 0.11), Cm(0.22), Cm(0.22))
    d.fill.solid(); d.fill.fore_color.rgb = RED; d.line.fill.background(); d.name = "단계 점"
    al = PP_ALIGN.CENTER
    bw = step
    bx = cx - bw / 2
    text(s6, bx, ly + 0.25, bw, 0.55, st, 11, "Pretendard SemiBold", TXT2, al, name="단계 이름")

# ---------------- 7p: 70% / 30% 도넛 ----------------
s7 = prs.slides[6]
g7 = off_group(s7)[0]
restore(g7)


def donut(slide, x, y, d, val, color, label):
    cd = CategoryChartData()
    cd.categories = ["share", "rest"]
    cd.add_series("s", (val, 1 - val))
    gf = slide.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, Cm(x), Cm(y), Cm(d), Cm(d), cd)
    gf.name = f"도넛 {label}"
    ch = gf.chart
    ch.has_legend = False
    ch.has_title = False
    plot = ch.plots[0]
    plot.has_data_labels = False
    ser = plot.series[0]
    for i, c in enumerate((color, LIGHT)):
        pt = ser.points[i]
        pt.format.fill.solid(); pt.format.fill.fore_color.rgb = c
        pt.format.line.fill.background()
    # 구멍 크기·시작 각도
    dn = ch._chartSpace.xpath(".//c:doughnutChart")[0]
    ns = "http://schemas.openxmlformats.org/drawingml/2006/chart"
    for tag, v in (("firstSliceAng", "0"), ("holeSize", "74")):
        el = dn.find(f"{{{ns}}}{tag}")
        if el is None:
            el = etree.SubElement(dn, f"{{{ns}}}{tag}")
        el.set("val", v)
    # 차트 바탕·테두리 없애고 그림 영역을 꽉 채우기
    cs = ch._chartSpace
    ns_a = "http://schemas.openxmlformats.org/drawingml/2006/main"
    pa = cs.xpath(".//c:plotArea")[0]
    lay = pa.find(f"{{{ns}}}layout")
    if lay is None:
        lay = etree.SubElement(pa, f"{{{ns}}}layout"); pa.remove(lay); pa.insert(0, lay)
    lay.clear()
    ml = etree.SubElement(lay, f"{{{ns}}}manualLayout")
    for t, v in (("layoutTarget", "inner"), ("xMode", "edge"), ("yMode", "edge"), ("x", "0"), ("y", "0"), ("w", "1"), ("h", "1")):
        etree.SubElement(ml, f"{{{ns}}}{t}").set("val", v)
    sp = cs.find(f"{{{ns}}}spPr")
    if sp is None:
        sp = etree.SubElement(cs, f"{{{ns}}}spPr")
    sp.clear()
    etree.SubElement(sp, f"{{{ns_a}}}noFill")
    lnn = etree.SubElement(sp, f"{{{ns_a}}}ln"); etree.SubElement(lnn, f"{{{ns_a}}}noFill")
    text(slide, x, y, d, d, f"{int(round(val * 100))}%", 12.5, "Pretendard ExtraBold", color,
         PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, name=f"도넛 값 {label}")
    return gf


# 기존 큰 숫자 대신 도넛 (태그 아래, 구분선 위)
remove(child(g7, 38)); remove(child(g7, 42))
D = 2.3
donut(s7, 2.12, 6.55, D, 0.70, DARK, "카피캣")
donut(s7, 15.45, 6.55, D, 0.30, RED, "owooii")
for sid, x in ((39, 2.12 + D + 0.55), (43, 15.45 + D + 0.55)):
    c = child(g7, sid)
    c.left = Cm(x)
    c.top = Cm(6.55 + D / 2 - 0.85)
cap_y = 6.55 + D / 2 + 0.2
text(s7, 2.12 + D + 0.55, cap_y, 5.5, 0.5, "카테고리 점유율 · 매출 규모", 10.5, "Pretendard Medium", GRAY, name="도넛 설명")
text(s7, 15.45 + D + 0.55, cap_y, 5.5, 0.5, "카테고리 점유율 목표 · 매출 규모", 10.5, "Pretendard Medium", GRAY, name="도넛 설명")

# ---------------- 10p: 실제 아이폰 목업 5대 ----------------
s10 = prs.slides[9]
for g in off_group(s10):
    remove(g)
PH = 5.75
pw = PH * 0.497
gap = 0.5
total = pw * 5 + gap * 4
x0 = 1.55 + (18.2 - total) / 2
for i, n in enumerate(("image24", "image25", "image26", "image27", "image30")):
    picture(s10, W9 / f"phones/p10_{n}.png", x0 + i * (pw + gap), 11.35, h=PH, name=f"원고 {n} (아이폰 목업)")

# ---------------- 11p: 원위치 + 여백에 핵심 포인트(라인 아이콘) ----------------
s11 = prs.slides[10]
g11 = off_group(s11)[0]
restore(g11)


def icon_list(slide, x, y, w, title, items):
    text(slide, x, y, w, 0.5, title, 10.5, "Pretendard Bold", GRAY, name="포인트 제목")
    yy = y + 0.75
    for ic, t in items:
        picture(slide, W9 / f"icons/{ic}.png", x, yy + 0.02, h=0.55, name=f"아이콘 {ic}")
        text(slide, x + 0.85, yy, w - 0.85, 1.2, t, 12, "Pretendard SemiBold", DARK,
             anchor=MSO_ANCHOR.TOP, name="포인트")
        yy += 1.3


icon_list(s11, 11.15, 12.4, 4.75, "핵심 기능", [
    ("fan", "BLDC 듀얼 고속 모터"),
    ("volume-1", "최대 65dB 저소음"),
    ("baby", "키즈·애견 모드"),
])
icon_list(s11, 27.98, 12.4, 4.2, "2026 하반기 라인업", [
    ("droplets", "드라이기 전용 에센스"),
    ("sparkles", "헤어팩"),
    ("calendar", "프리볼트 드라이기"),
])

# ---------------- 13p: 원위치 ----------------
for g in off_group(prs.slides[12]):
    restore(g)

# ---------------- 15p: 기부 사진 + 실제 아이폰 2대 ----------------
s15 = prs.slides[14]
for g in off_group(s15):
    remove(g)
H15 = 8.7
y15 = 6.5
photo = W9 / "s15_49.png"
im = Image.open(photo)
ph_w = H15 * im.width / im.height
pw15 = H15 * 0.497
gap15 = 0.6
tot = ph_w + pw15 * 2 + gap15 * 2
x15 = 1.55 + (18.77 - tot) / 2
pic = picture(s15, photo, x15, y15 + 0.25, h=H15 - 0.5, name="기부 사진")
ph_w = H15 - 0.5
ph_w = (H15 - 0.5) * im.width / im.height
x_next = x15 + ph_w + gap15 + (H15 * im.width / im.height - ph_w) / 2
picture(s15, W9 / "phones/p15_video.png", x_next, y15, h=H15, name="기부 영상 (아이폰 목업)")
picture(s15, W9 / "phones/p15_post.png", x_next + pw15 + gap15, y15, h=H15, name="기부 후기 (아이폰 목업)")

prs.save(OUT)
print("저장:", OUT.name)
