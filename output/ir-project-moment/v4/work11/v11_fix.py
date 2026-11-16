"""v11: 사용자 v10 기준 10·14·15p 재구성.
10p 상단 실적 타임라인 + 하단 SNS 목업 상자 / 매출·영업이익 2단 그래프 상자
14p 이름 아래 핵심 이력 키워드 칩 + 제목 보강, 중복 '現' 줄 제거
15p Donation 확대(문구 상단 이동, 사진 라운드), Support 축소
"""
import copy
import io
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from lxml import etree
from PIL import Image, ImageFont
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.util import Cm, Pt, Emu

ROOT = Path(r"C:\Users\admin\클로드")
SRC, OUT = sys.argv[1], sys.argv[2]
RED = RGBColor(0xC7, 0x35, 0x44)
DEEP = RGBColor(0x8E, 0x24, 0x30)
PALE = RGBColor(0xE7, 0xA2, 0xAA)
DARK = RGBColor(0x17, 0x1A, 0x1F)
TXT2 = RGBColor(0x45, 0x4C, 0x56)
GRAY = RGBColor(0x84, 0x8C, 0x97)
LINE = RGBColor(0xC3, 0xC9, 0xD1)
WHITE = RGBColor(255, 255, 255)
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
L, R = 1.53, 32.34
FONT_FILE = str(ROOT / "assets/fonts/Pretendard/Pretendard-SemiBold.ttf")

prs = Presentation(SRC)


def setfont(r, font, size, color):
    r.font.name = font; r.font.size = Pt(size); r.font.color.rgb = color
    rpr = r._r.get_or_add_rPr()
    for tag in ("ea", "cs"):
        el = rpr.find(f"{{{A}}}{tag}")
        if el is None:
            el = etree.SubElement(rpr, f"{{{A}}}{tag}")
        el.set("typeface", font)


def text(s, x, y, w, h, lines, size, font="Pretendard SemiBold", color=DARK, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, name="텍스트", spacing=1.15):
    tb = s.shapes.add_textbox(Cm(x), Cm(y), Cm(w), Cm(h)); tb.name = name
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.word_wrap = True; tf.vertical_anchor = anchor
    for i, ln in enumerate(lines if isinstance(lines, list) else [lines]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.line_spacing = spacing
        for t, f, sz, c in (ln if isinstance(ln, list) else [(ln, font, size, color)]):
            r = p.add_run(); r.text = t; setfont(r, f, sz, c)
    return tb


def pill(s, x, y, label, fill, outline=False, size=10.5, h=0.64, pad=0.55):
    w = ImageFont.truetype(FONT_FILE, 100).getlength(label) / 100 * size * 0.03528 + pad
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Cm(x), Cm(y), Cm(w), Cm(h))
    sh.adjustments[0] = 0.5; sh.name = "태그"
    if outline:
        sh.fill.background(); sh.line.color.rgb = fill; sh.line.width = Pt(0.8)
    else:
        sh.fill.solid(); sh.fill.fore_color.rgb = fill; sh.line.fill.background()
    tf = sh.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE; tf.word_wrap = False
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = label; setfont(r, "Pretendard SemiBold", size, fill if outline else WHITE)
    return sh, w


def rect(s, x, y, w, h, color, name):
    sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Cm(x), Cm(y), Cm(w), Cm(max(h, 0.03)))
    sh.fill.solid(); sh.fill.fore_color.rgb = color; sh.line.fill.background(); sh.name = name
    return sh


def hline(s, x0, x1, y, color=LINE, wpt=0.8, dash=False, name="선"):
    ln = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Cm(x0), Cm(y), Cm(x1), Cm(y))
    ln.line.color.rgb = color; ln.line.width = Pt(wpt); ln.name = name
    if dash:
        ln.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    return ln


def delete(s, ids):
    for sh in list(s.shapes):
        if sh.shape_id in ids:
            sh._element.getparent().remove(sh._element)


def timeline(s, cols, y0=4.72):
    cw = (R - L) / len(cols)
    LY = y0 + 1.03
    hline(s, L + 0.11, R - 0.3, LY, name="타임라인 선")
    n_act = sum(1 for c in cols if c[1] is DARK)
    if n_act:
        end = L + (n_act - 1) * cw + 0.11 + (cw if n_act < len(cols) else 0)
        hline(s, L + 0.11, end, LY, DARK, 1.6, name="타임라인 실적 구간")
    for i, (yr, pc, num, nc, cap) in enumerate(cols):
        x = L + i * cw
        pill(s, x, y0, yr, pc)
        d = s.shapes.add_shape(MSO_SHAPE.OVAL, Cm(x), Cm(LY - 0.11), Cm(0.22), Cm(0.22))
        d.fill.solid(); d.fill.fore_color.rgb = pc; d.line.fill.background(); d.name = "타임라인 점"
        v, u = num
        text(s, x, y0 + 1.33, cw - 0.3, 1.3, [[(v, "Pretendard ExtraBold", 32, nc), (u, "Pretendard Bold", 16, nc)]],
             32, name=f"타임라인 수치 {yr}", spacing=1.0)
        text(s, x, y0 + 2.68, cw - 0.3, 1.0, cap, 11, "Pretendard Medium", TXT2, name=f"타임라인 설명 {yr}")


# =============== 10p ===============
s10 = prs.slides[9]
ids = {sh.shape_id: sh for sh in s10.shapes}
box_xml = copy.deepcopy(ids[27]._element)
phones = [sh for sh in s10.shapes if "아이폰 목업" in sh.name]
delete(s10, set(range(27, 37)) | set(range(57, 81)))


def box(s, x, y, w, h, name):
    el = copy.deepcopy(box_xml); s.shapes._spTree.insert(2, el)
    sh = [x_ for x_ in s.shapes if x_._element is el][0]
    sh.left, sh.top, sh.width, sh.height = Cm(x), Cm(y), Cm(w), Cm(h); sh.name = name
    return sh


timeline(s10, [
    ("2023", DARK, ("0.8", "억"), DARK, ["첫 매출", "영업이익 -0.16억"]),
    ("2024", DARK, ("6", "억"), DARK, ["누적 판매 약 4,000대", "영업이익 1.0억"]),
    ("2025", DARK, ("12", "억"), RED, ["누적 판매 약 10,000대", "영업이익 1.3억"]),
    ("2026E", RED, ("20", "억"), DEEP, ["한·미 진입 · BEP"]),
])
BY, BH = 9.0, 8.45
LW = 18.2
box(s10, L, BY, LW, BH, "SNS 상자")
box(s10, L + LW + 0.4, BY, R - L - LW - 0.4, BH, "그래프 상자")
# 왼쪽: SNS 바이럴
pill(s10, L + 0.45, BY + 0.4, "SNS 바이럴", RED)
text(s10, L + 0.45, BY + 1.22, LW - 0.9, 0.8,
     [[("SNS 총 View 수 ", "Pretendard Bold", 15, DARK), ("+3,000만 뷰", "Pretendard ExtraBold", 15, RED),
       (" · ", "Pretendard Bold", 15, DARK), ("+10만 건 공유", "Pretendard ExtraBold", 15, RED)]], 15, name="SNS 성과")
PH = 5.55
pw = PH * 0.497
gap = (LW - 0.9 - pw * 5) / 4
gap = min(gap, 0.45)
x0 = L + (LW - (pw * 5 + gap * 4)) / 2
for i, ph in enumerate(phones):
    ph.left, ph.top, ph.width, ph.height = Cm(x0 + i * (pw + gap)), Cm(BY + BH - 0.4 - PH), Cm(pw), Cm(PH)
# 오른쪽: 매출·영업이익 2단 그래프
gx = L + LW + 0.4
gw = R - gx
pill(s10, gx + 0.45, BY + 0.4, "매출 · 영업이익", RED)
text(s10, gx + gw - 4.45, BY + 0.47, 4.0, 0.5, "(단위: 백만원)", 10, "Pretendard Medium", GRAY, PP_ALIGN.RIGHT,
     name="단위")
years = ["2023", "2024", "2025", "2026E"]
rev = [82, 604, 1200, 2020]
op = [-16, 100, 130, 0]
lab_w = 1.9
px0, px1 = gx + 0.45 + lab_w, gx + gw - 0.45
colw = (px1 - px0) / 4
bw = 1.05
# 1단: 매출
r_base, r_h = BY + 4.85, 2.85
text(s10, gx + 0.45, r_base - 0.5, lab_w, 0.5, "매출액", 11, "Pretendard Bold", DARK, name="행 이름")
for i, v in enumerate(rev):
    cx = px0 + colw * (i + 0.5)
    h = r_h * v / max(rev)
    c = RED if i == 3 else PALE
    rect(s10, cx - bw / 2, r_base - h, bw, h, c, f"매출 막대 {years[i]}")
    text(s10, cx - 1.2, r_base - h - 0.55, 2.4, 0.5, f"{v:,}", 12.5 if i == 3 else 11.5,
         "Pretendard ExtraBold" if i == 3 else "Pretendard Bold", RED if i == 3 else DARK, PP_ALIGN.CENTER,
         name=f"매출 값 {years[i]}")
hline(s10, px0 - 0.2, px1, r_base, LINE, 0.8, name="매출 기준선")
hline(s10, gx + 0.45, px1, r_base + 0.4, LINE, 0.5, dash=True, name="그래프 구분선")
# 2단: 영업이익 (따로 눈금)
o_base, o_h = BY + 7.0, 1.35
text(s10, gx + 0.45, o_base - 0.5, lab_w, 0.5, "영업이익", 11, "Pretendard Bold", DARK, name="행 이름")
mx = max(abs(v) for v in op)
for i, v in enumerate(op):
    cx = px0 + colw * (i + 0.5)
    h = o_h * abs(v) / mx
    c = DEEP if i == 3 else (GRAY if v < 0 else TXT2)
    top = o_base - h if v >= 0 else o_base
    rect(s10, cx - bw / 2, top, bw, h, c, f"영업이익 막대 {years[i]}")
    ty = (o_base - h - 0.55) if v >= 0 else (o_base + h + 0.05)
    if v < 0:
        ty = o_base - 0.55
    text(s10, cx - 1.2, ty, 2.4, 0.5, f"{v:,}", 12.5 if i == 3 else 11.5,
         "Pretendard ExtraBold" if i == 3 else "Pretendard Bold", DEEP if i == 3 else DARK, PP_ALIGN.CENTER,
         name=f"영업이익 값 {years[i]}")
hline(s10, px0 - 0.2, px1, o_base, LINE, 0.8, name="영업이익 기준선")
for i, yv in enumerate(years):
    cx = px0 + colw * (i + 0.5)
    text(s10, cx - 1.2, BY + BH - 0.95, 2.4, 0.5, yv, 11.5, "Pretendard Bold", RED if i == 3 else TXT2,
         PP_ALIGN.CENTER, name=f"연도 {yv}")

# =============== 14p ===============
s14 = prs.slides[13]
t14 = [sh for sh in s14.shapes if sh.name == "타이틀"][0]
p = t14.text_frame.paragraphs[0]
base_run = p.runs[0]
r2 = copy.deepcopy(base_run._r); p._p.append(r2)
from pptx.text.text import _Run
run2 = _Run(r2, p); run2.text = "  글로벌 소비재·전략·브랜드 전문가"
run2.font.color.rgb = RGBColor(0x84, 0x84, 0x84)
chips = {
    "이준영": ["P&G", "Pfizer", "BCG", "Deloitte", "효원CNC"],
    "서송희": ["Georgetown MBA", "호텔신라", "뉴스1", "우나스텔라"],
    "최정원": ["SPC Group", "Grey Global NY", "SVA"],
    "한재혁": ["오슈마켓", "홍익대"],
    "김수정": ["비비앤다"],
}
shapes = list(s14.shapes)
for i, sh in enumerate(shapes):
    if sh.name != "이름":
        continue
    name = sh.text_frame.text.strip()
    div = next(x for x in shapes[i:] if x.name == "구분선")
    car = next(x for x in shapes[i:] if x.name == "경력")
    # 첫 줄 '現 …프로젝트모먼트…' 는 직함 태그와 겹쳐서 제거
    ps = car.text_frame.paragraphs
    if ps[0].text.strip().startswith("現"):
        ps[0]._p.getparent().remove(ps[0]._p)
    cx = div.left / 360000
    cy = div.top / 360000 + 0.22
    for kw in chips[name]:
        _, w = pill(s14, cx, cy, kw, RED, outline=True, size=10, h=0.6, pad=0.5)
        cx += w + 0.18
    car.top = Cm(cy + 0.6 + 0.15)

# 상자 높이 조정: 위 상자 +0.17, 아래 행 전체 0.13 아래로
top_box = [x for x in s14.shapes if x.name == "직사각형" and abs(x.top / 360000 - 4.8) < 0.05]
for b in top_box:
    b.height = b.height + Cm(0.17)
for x in s14.shapes:
    if x.top / 360000 > 11.6 and x.top / 360000 < 18:
        x.top = x.top + Cm(0.13)

# =============== 15p ===============
s15 = prs.slides[14]
ids = {sh.shape_id: sh for sh in s15.shapes}
quote = ids[19]
q_lines = ["“사랑으로 성장하고 현재에 감사하며 어제보다 행복한 내일을 꿈꾸는", "건강하고 아름다운 사회를 소망합니다.”"]
delete(s15, {19})
TOP, BOT = 4.8, 17.45
DW = 21.0
don, sup = ids[24], ids[25]
don.left, don.top, don.width, don.height = Cm(1.55), Cm(TOP), Cm(DW), Cm(BOT - TOP)
sx0 = 1.55 + DW + 0.4
sup.left, sup.top, sup.width, sup.height = Cm(sx0), Cm(TOP), Cm(R - sx0), Cm(BOT - TOP)
ids[27].left = Cm(sx0 + 0.57)
text(s15, 2.12, 6.2, DW - 1.14, 1.6,
     [[(q_lines[0], "Pretendard Bold", 15, DARK)], [(q_lines[1], "Pretendard Bold", 15, DARK)]], 15,
     name="기부 문구", spacing=1.25)
# 사진·아이폰
IY, IH = 8.35, BOT - 0.5 - 8.35
photo, vid, post = ids[69], ids[70], ids[71]
im = Image.open(io.BytesIO(photo.image.blob))
pwid = IH * 0.92
# 아래쪽을 잘라 비율 맞춤 (위쪽 드라이어·인물 유지)
keep_h = (im.width / 0.92) / im.height
photo.crop_top, photo.crop_bottom, photo.crop_left, photo.crop_right = 0, max(0, 1 - keep_h), 0, 0
phw = IH * 0.497
gap = 0.6
tot = pwid + phw * 2 + gap * 2
ix = 1.55 + (DW - tot) / 2
photo.left, photo.top, photo.width, photo.height = Cm(ix), Cm(IY), Cm(pwid), Cm(IH)
photo.auto_shape_type = MSO_SHAPE.ROUNDED_RECTANGLE
geom = photo._element.spPr.find(f"{{{A}}}prstGeom")
av = geom.find(f"{{{A}}}avLst")
if av is None:
    av = etree.SubElement(geom, f"{{{A}}}avLst")
av.clear(); gd = etree.SubElement(av, f"{{{A}}}gd"); gd.set("name", "adj"); gd.set("fmla", f"val {int(0.35 / IH * 100000)}")
for k, ph in enumerate((vid, post)):
    ph.left, ph.top, ph.width, ph.height = Cm(ix + pwid + gap + k * (phw + gap)), Cm(IY), Cm(phw), Cm(IH)
# 로고 타일 2열 재배치
tiles = [ids[t] for t in (58, 6, 7, 8, 9, 10, 11, 12, 13, 14)]
logos = [ids[t] for t in (59, 60, 61, 62, 63, 64, 65, 66, 67, 68)]
tw = (R - sx0 - 1.14 - 0.3) / 2
ty0 = 6.35
step = (BOT - 0.5 - ty0 + 0.3) / 5
th = step - 0.3
for k, (t, lg) in enumerate(zip(tiles, logos)):
    tx = sx0 + 0.57 + (k % 2) * (tw + 0.3)
    ty = ty0 + (k // 2) * step
    t.left, t.top, t.width, t.height = Cm(tx), Cm(ty), Cm(tw), Cm(th)
    lw, lh = lg.width / 360000, lg.height / 360000
    sc = min((tw - 0.7) / lw, (th - 0.6) / lh, 1.15)
    nw, nh = lw * sc, lh * sc
    lg.left, lg.top, lg.width, lg.height = Cm(tx + (tw - nw) / 2), Cm(ty + (th - nh) / 2), Cm(nw), Cm(nh)

prs.save(OUT)
print("저장", OUT)
