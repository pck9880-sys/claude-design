"""v8: 10~13p 디벨롭 (원본 스타일 유지)."""
import sys, io, copy
sys.stdout.reconfigure(encoding="utf-8")
from pptx import Presentation
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.dml import MSO_LINE
from pptx.oxml.ns import qn
from pptx.oxml import parse_xml
from PIL import Image

SRC = sys.argv[1]
OUT = sys.argv[2]
E = 360000
cm = lambda v: int(round(v * E))
P, D, INK, BODY, MUTED = "C73544", "8E2430", "262626", "404040", "7F7F7F"
G300, G100 = "C3C9D1", "E8EBEF"


def mix(h, t, base="FFFFFF"):
    a = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(base[i:i + 2], 16) for i in (0, 2, 4)]
    return "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


T92, T95 = mix(P, 0.92), mix(P, 0.95)
FONT = {"xb": "Pretendard ExtraBold", "sb": "Pretendard SemiBold", "md": "Pretendard Medium"}

prs = Presentation(SRC)


def nostyle(sh):
    st = sh._element.find(qn("p:style"))
    if st is not None:
        sh._element.remove(st)


def font(run, size, w="md", color=INK):
    f = run.font
    f.size = Pt(size)
    f.name = FONT[w]
    f.color.rgb = RGBColor.from_string(color)
    rPr = run._r.get_or_add_rPr()
    rPr.set("spc", str(int(-0.02 * size * 100)))
    for tag in ("a:ea", "a:cs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = parse_xml(f'<{tag} xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" typeface="{FONT[w]}"/>')
            rPr.append(el)
        else:
            el.set("typeface", FONT[w])


def rect(s, x, y, w, h, fill=None, line=None, lw=0.5, dash=False, kind=MSO_SHAPE.RECTANGLE, name=None):
    sh = s.shapes.add_shape(kind, cm(x), cm(y), cm(w), cm(h))
    nostyle(sh)
    if fill:
        sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor.from_string(fill)
    else:
        sh.fill.background()
    if line:
        sh.line.color.rgb = RGBColor.from_string(line); sh.line.width = Pt(lw)
        if dash:
            sh.line.dash_style = MSO_LINE.DASH
    else:
        sh.line.fill.background()
    if name:
        sh.name = name
    return sh


def line(s, x1, y1, x2, y2, color=G300, lw=0.5, dash=False, name="선"):
    c = s.shapes.add_connector(1, cm(x1), cm(y1), cm(x2), cm(y2))
    nostyle(c)
    c.line.color.rgb = RGBColor.from_string(color); c.line.width = Pt(lw)
    if dash:
        c.line.dash_style = MSO_LINE.DASH
    c.name = name
    return c


def text(s, x, y, w, h, parts, size=10.5, w_="md", color=INK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, ls=None, name=None):
    """parts: str 또는 [(문자열, size, weight, color)] 목록. '\n'은 새 문단."""
    tb = s.shapes.add_textbox(cm(x), cm(y), cm(w), cm(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    if isinstance(parts, str):
        parts = [(parts, size, w_, color)]
    p = tf.paragraphs[0]
    p.alignment = align
    if ls:
        p.line_spacing = ls
    for t, sz, ww, col in parts:
        chunks = t.split("\n")
        for i, ch in enumerate(chunks):
            if i > 0:
                p = tf.add_paragraph(); p.alignment = align
                if ls:
                    p.line_spacing = ls
            if ch:
                r = p.add_run(); r.text = ch; font(r, sz, ww, col)
    if name:
        tb.name = name
    return tb


def by_id(s, i):
    return next(sh for sh in s.shapes if sh.shape_id == i)


def drop(sh):
    sh._element.getparent().remove(sh._element)


def put(sh, x=None, y=None, w=None, h=None):
    if x is not None: sh.left = cm(x)
    if y is not None: sh.top = cm(y)
    if w is not None: sh.width = cm(w)
    if h is not None: sh.height = cm(h)


def break_line(shape, after_text):
    """after_text 로 끝나는 지점 뒤에서 줄바꿈 (같은 문단 안 <a:br/>)."""
    p = shape.text_frame.paragraphs[0]
    for r in p.runs:
        if after_text in r.text:
            head, tail = r.text.split(after_text, 1)
            r.text = head + after_text.rstrip()
            br = parse_xml('<a:br xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"/>')
            rpr = r._r.find(qn("a:rPr"))
            if rpr is not None:
                br.append(copy.deepcopy(rpr))
            r._r.addnext(br)
            if tail.strip():
                nr = copy.deepcopy(r._r)
                nr.find(qn("a:t")).text = tail.lstrip()
                br.addnext(nr)
            return True
    return False


# ───────────────── 10p: 왼쪽 상자 넓힘(2단 + 큰 목업), 오른쪽 차트 축소·직접 그림
s = prs.slides[9]
L, R = by_id(s, 27), by_id(s, 28)
put(L, x=1.55, w=18.2)
put(R, x=20.35, w=12.1)
c1, c2, cw = 2.12, 9.75, 9.4
put(by_id(s, 30), x=c1, y=6.42, w=6.8, h=2.2); break_line(by_id(s, 30), "매출 ")
put(by_id(s, 31), x=c1, y=8.8, w=6.8, h=2.2)
put(by_id(s, 33), x=c2, y=5.46)
put(by_id(s, 34), x=c2, y=6.42, w=cw, h=2.2); break_line(by_id(s, 34), ", ")
put(by_id(s, 35), x=c2, y=8.8, w=cw, h=2.2)
dv = by_id(s, 32)
drop(dv)
line(s, 9.2, 5.46, 9.2, 10.4, color="7F7F7F", lw=0.8, dash=True, name="구분선 세로")
phones = sorted([sh for sh in s.shapes if "(목업 phone)" in sh.name], key=lambda x: x.left)
top, bot = 11.4, 17.04
ph = bot - top
asp = phones[0].width / phones[0].height
pw = ph * asp
gap = 0.4
tot = pw * len(phones) + gap * (len(phones) - 1)
x = 1.55 + (18.2 - tot) / 2
for sh in phones:
    put(sh, x=x, y=top, w=pw, h=ph); x += pw + gap

drop(by_id(s, 23))                                   # 기존 차트
unit = by_id(s, 36); put(unit, x=31.88 - 7.2)
ix0, ix1 = 20.92, 31.88
years = ["2023", "2024", "2025", "2026E"]
rev = [82, 604, 1200, 2020]
op = [-16, 100, 130, 0]
slot = (ix1 - ix0) / 4
base, topv = 14.3, 7.3
k = (base - topv) / max(rev)
bw = 1.5
# 2026E 강조 띠
rect(s, ix0 + slot * 3 + 0.1, 6.15, slot - 0.2, 10.9, fill=T95, name="강조 띠 2026E")
rect(s, ix0, 5.5, 0.28, 0.28, fill=P, name="범례 칸")
text(s, ix0 + 0.4, 5.39, 3, 0.5, "매출액", 10.5, "sb", MUTED, anchor=MSO_ANCHOR.MIDDLE, name="범례")
shades = [mix(P, 0.72), mix(P, 0.5), mix(P, 0.25), P]
for i, (yv, r_, o_) in enumerate(zip(years, rev, op)):
    cx = ix0 + slot * i + slot / 2
    h = max(0.06, r_ * k)
    rect(s, cx - bw / 2, base - h, bw, h, fill=shades[i], name=f"막대 {yv}")
    last = i == 3
    text(s, cx - 1.4, base - h - (0.75 if last else 0.6), 2.8, 0.6 if last else 0.5, f"{r_:,}",
         16 if last else 12, "xb", P if last else INK, PP_ALIGN.CENTER, MSO_ANCHOR.BOTTOM, name=f"값 {yv}")
    text(s, cx - 1.3, base + 0.2, 2.6, 0.45, yv, 10.5, "xb" if last else "sb", P if last else MUTED, PP_ALIGN.CENTER, name=f"연도 {yv}")
    text(s, cx - 1.3, 15.55, 2.6, 0.4, "영업이익", 9, "md", MUTED, PP_ALIGN.CENTER, name="영업이익 라벨")
    text(s, cx - 1.3, 15.95, 2.6, 0.55, f"{o_:,}", 13, "xb", D if o_ >= 0 else MUTED, PP_ALIGN.CENTER, name=f"영업이익 {yv}")
line(s, ix0, base, ix1, base, G300, 0.5, name="기준선")
line(s, ix0, 15.25, ix1, 15.25, G100, 0.5, dash=True, name="구분선 영업이익")

# ───────────────── 11p: 두 상자 글 묶음을 같은 높이로 정렬 (세로 가운데)
s = prs.slides[10]
img_top, img_h = 5.38, 11.68
head_h = 2.96
grp = 0.64 + 0.4 + head_h + 0.6 + 0.6 + 1.6
T = img_top + (img_h - grp) / 2
for tag, head, dvd, msg in [(24, 25, 26, 27), (28, 29, 30, 31)]:
    put(by_id(s, tag), y=T)
    hd = by_id(s, head); put(hd, y=T + 1.04, h=head_h); hd.text_frame.vertical_anchor = MSO_ANCHOR.BOTTOM
    put(by_id(s, dvd), y=T + 1.04 + head_h + 0.6)
    put(by_id(s, msg), y=T + 1.04 + head_h + 1.2, h=1.6)
put(by_id(s, 30), w=by_id(s, 29).width / E)

# ───────────────── 12p: 크로스셀링 이미지 3장으로 폭 채우기 + 행간 정리
s = prs.slides[11]
old11, old12 = [sh for sh in s.shapes if sh.name == "그림 11"][0], [sh for sh in s.shapes if sh.name == "그림 12"][0]
woman = Image.open(io.BytesIO(old11.image.blob)).convert("RGB")
sheet = Image.open(io.BytesIO(old12.image.blob)).convert("RGB")
y0, H = 7.18, 4.35
ws = [4.0, 5.6]
ws.append(14.01 - 0.28 * 2 - sum(ws))


def crop_to(im, ratio, fy=0.3):
    w, h = im.size
    if w / h > ratio:
        nw = int(h * ratio); x = (w - nw) // 2
        return im.crop((x, 0, x + nw, h))
    nh = int(w / ratio); y = int((h - nh) * fy)
    return im.crop((0, y, w, y + nh))


p1 = sheet.crop((0, 0, 818, 1086))
p2 = sheet.crop((835, 0, 1446, 1086))
imgs = [crop_to(woman, ws[0] / H, 0.25), crop_to(p1, ws[1] / H, 0.33), crop_to(p2, ws[2] / H, 0.0)]
x = 2.12
for n, (im, w) in enumerate(zip(imgs, ws)):
    b = io.BytesIO(); im.save(b, "JPEG", quality=92)
    pic = s.shapes.add_picture(b, cm(x), cm(y0), cm(w), cm(H)); pic.name = f"크로스셀링 이미지 {n + 1}"
    x += w + 0.28
drop(old11); drop(old12)
for sid in (51, 52):
    tf = by_id(s, sid).text_frame
    for i, p in enumerate(tf.paragraphs):
        p.line_spacing = 1.2
        if i > 0:
            p.space_before = Pt(5.7)

# ───────────────── 13p: 차트 직접 그림 + 표 재스타일 + 하단 성장 스토리 재구성
s = prs.slides[12]
drop(by_id(s, 26))
for sid in (39, 40, 42):
    drop(by_id(s, sid))
yrs = ["2023", "2024", "2025", "2026", "2027", "2028", "2029"]
dev = [0.8, 6.0, 11.6, 20.2, 51.6, 165.4, 411.8]
cos = [0, 0, 0, 0, 7.4, 30.2, 84.0]
net = [0, 0, 0, 0, 1.0, 5.0, 10.0]
tot = [0.8, 6.0, 11.6, 20.2, 60.0, 200.6, 505.8]
yoy = ["", "+650%", "+93%", "+74%", "+197%", "+235%", "+152%"]
csh = ["–", "–", "–", "0%", "12%", "15%", "17%"]
lx, sx0, sx1 = 1.55, 3.75, 16.08
slot = (sx1 - sx0) / 7
base, topv = 13.35, 10.35
k = (base - topv) / max(tot)
bw = 1.0
# 범례
lg = [("디바이스", G300), ("코스메틱", P), ("유통 순액", D)]
x = lx
for name, col in lg:
    rect(s, x, 8.92, 0.26, 0.26, fill=col, name="범례 칸")
    text(s, x + 0.36, 8.82, 2.0, 0.46, name, 9, "md", MUTED, anchor=MSO_ANCHOR.MIDDLE, name="범례")
    x += 2.25
# 2029 강조 띠
rect(s, sx0 + slot * 6 + 0.05, 9.2, slot - 0.1, 5.7, fill=T95, line=P, lw=0.5, name="강조 띠 2029")
# 실적 | 전망 구분
bx = sx0 + slot * 3
line(s, bx, 9.45, bx, base, G300, 0.5, dash=True, name="실적 전망 구분")
text(s, bx - 1.6, 9.4, 1.45, 0.4, "실적", 9, "md", MUTED, PP_ALIGN.RIGHT, name="실적")
text(s, bx + 0.15, 9.4, 1.45, 0.4, "전망", 9, "md", MUTED, name="전망")
for i, y in enumerate(yrs):
    cx = sx0 + slot * i + slot / 2
    yb = base
    for v, col in ((dev[i], G300), (cos[i], P), (net[i], D)):
        if v <= 0:
            continue
        h = max(0.05, v * k)
        rect(s, cx - bw / 2, yb - h, bw, h, fill=col, name=f"막대 {y}")
        yb -= h
    last = i == 6
    lab = f"{tot[i]:,.1f}"
    text(s, cx - slot / 2 - (0.6 if last else 0), yb - (0.62 if last else 0.48), slot + (1.2 if last else 0), 0.55 if last else 0.42, lab,
         14 if last else 10, "xb", P if last else INK, PP_ALIGN.CENTER, MSO_ANCHOR.BOTTOM, name=f"값 {y}")
    text(s, cx - slot / 2, base + 0.12, slot, 0.42, y if i < 3 else y + "E", 10, "xb" if last else "sb", P if last else BODY, PP_ALIGN.CENTER, name=f"연도 {y}")
    text(s, cx - slot / 2, 14.0, slot, 0.38, yoy[i], 9, "sb", P if last else MUTED, PP_ALIGN.CENTER, name=f"YoY {y}")
    text(s, cx - slot / 2, 14.45, slot, 0.38, csh[i], 9, "sb", P if (last or csh[i] not in ("–",)) else MUTED, PP_ALIGN.CENTER, name=f"코스메틱 {y}")
line(s, lx, base, sx1, base, G300, 0.5, name="기준선")
text(s, lx, 14.0, 2.1, 0.38, "YoY", 9, "sb", BODY, name="행 이름")
text(s, lx, 14.45, 2.1, 0.38, "코스메틱 비중", 9, "sb", BODY, name="행 이름")
line(s, lx, 13.97, sx1, 13.97, G100, 0.5, name="행 구분")
line(s, lx, 14.42, sx1, 14.42, G100, 0.5, name="행 구분")

# 표
tshape = by_id(s, 31)
tbl = tshape.table
nrows = len(tbl.rows)
rh = (14.9 - 8.92) / nrows
for r in tbl.rows:
    r.height = cm(rh)
tbl.first_row = True
tbl.horz_banding = False
tbl.vert_banding = False
A = "http://schemas.openxmlformats.org/drawingml/2006/main"


def borders(cell, spec):
    tcPr = cell._tc.get_or_add_tcPr()
    for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        for el in tcPr.findall(qn(tag)):
            tcPr.remove(el)
    els = []
    for tag in ("lnL", "lnR", "lnT", "lnB"):
        w, col = spec.get(tag, (0, None))
        if col:
            els.append(parse_xml(f'<a:{tag} xmlns:a="{A}" w="{int(w * 12700)}" cap="flat" cmpd="sng" algn="ctr">'
                                 f'<a:solidFill><a:srgbClr val="{col}"/></a:solidFill><a:prstDash val="solid"/></a:{tag}>'))
        else:
            els.append(parse_xml(f'<a:{tag} xmlns:a="{A}" w="0"><a:noFill/></a:{tag}>'))
    for el in reversed(els):
        tcPr.insert(0, el)


ncol = len(tbl.columns)
for ri, row in enumerate(tbl.rows):
    for ci, cell in enumerate(row.cells):
        lastc = ci == ncol - 1
        if ri == 0:
            fill = P if lastc else (None if ci == 0 else T92)
            col, w_, sz = ("FFFFFF" if lastc else (INK if ci == 0 else P)), "xb", 11
        elif ci == 0:
            fill, col, w_, sz = T95, D, "xb", 11
        else:
            fill, col, w_, sz = (T95 if lastc else None), (P if lastc else INK), ("xb" if lastc else "md"), 11
        if fill:
            cell.fill.solid(); cell.fill.fore_color.rgb = RGBColor.from_string(fill)
        else:
            cell.fill.background()
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.margin_left = cell.margin_right = cm(0.2)
        cell.margin_top = cell.margin_bottom = 0
        for p in cell.text_frame.paragraphs:
            p.alignment = PP_ALIGN.CENTER
            for r in p.runs:
                font(r, sz, w_, col)
        borders(cell, {"lnB": (0.5, G300), "lnT": (0.8 if ri == 0 else 0.5, INK if ri == 0 else G300),
                       "lnL": (0.5, G100) if ci > 0 else (0, None), "lnR": (0.5, G100) if ci < ncol - 1 else (0, None)})
cws = [c.width for c in tbl.columns]
rect(s, (tshape.left + sum(cws[:-1])) / E, tshape.top / E, cws[-1] / E, rh * nrows, line=P, lw=1.6, name="강조 테두리 2029")

# 성장 스토리: 4단계 흐름
tag = by_id(s, 41)
line(s, 1.55, 15.4, 32.37, 15.4, G300, 0.5, name="구분선 성장 스토리")
put(tag, x=1.55, y=15.75)
steps = [("2023–25", "한국 검증\n0.8→11.6억 흑자"),
         ("2026", "한·미 진입\n공동구매 중심, BEP"),
         ("2027~", "미디어 상시판매 전환\n고마진 코스메틱 확대로 GP 51→57%"),
         ("2029", "글로벌 506억")]
arrow_src = by_id(prs.slides[11], 67)._element
sx, ex, ag = 4.75, 32.37, 0.9
sw = (ex - sx - ag * 3) / 4
maxid = max(int(e.get("id")) for e in s._element.iter(qn("p:cNvPr")))
for i, (yr, desc) in enumerate(steps):
    x = sx + i * (sw + ag)
    last = i == 3
    text(s, x, 15.75, sw, 0.5, yr, 11, "xb", P if last else D, name=f"스토리 {yr}")
    text(s, x, 16.3, sw, 1.2, [(desc.split("\n")[0], 10.5, "sb", INK), ("\n" + desc.split("\n")[1], 10.5, "md", BODY)] if "\n" in desc else desc,
         10.5, "sb", INK, ls=1.2, name=f"스토리 설명 {yr}")
    if i < 3:
        el = copy.deepcopy(arrow_src)
        maxid += 1
        el.find(".//" + qn("p:cNvPr")).set("id", str(maxid))
        s.shapes._spTree.append(el)
        a = s.shapes[-1]
        put(a, x=x + sw + (ag - 0.32) / 2, y=15.84)

prs.save(OUT)
print("저장:", OUT)
