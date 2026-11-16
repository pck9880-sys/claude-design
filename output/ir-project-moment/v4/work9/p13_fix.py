"""13p 재구성: 상단 성장 타임라인(연도 상자 4개 + 성장 스토리 통합), 하단 차트·표 상자 2개."""
import copy
import sys
sys.stdout.reconfigure(encoding="utf-8")
from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Cm, Pt, Emu

SRC, OUT = sys.argv[1], sys.argv[2]
RED = RGBColor(0xC7, 0x35, 0x44)
DEEP = RGBColor(0x8E, 0x24, 0x30)
DARK = RGBColor(0x17, 0x1A, 0x1F)
TXT2 = RGBColor(0x45, 0x4C, 0x56)
GRAY = RGBColor(0x84, 0x8C, 0x97)
LINE = RGBColor(0xC3, 0xC9, 0xD1)
A = "http://schemas.openxmlformats.org/drawingml/2006/main"

prs = Presentation(SRC)
s = prs.slides[12]
by_id = {sh.shape_id: sh for sh in s.shapes}
box_xml = copy.deepcopy(by_id[5]._element)          # 두꺼운 테두리 상자 스타일
grp = by_id[26]
kids = {c.shape_id: c for c in grp.shapes}


def setfont(r, font, size, color):
    r.font.name = font
    r.font.size = Pt(size)
    r.font.color.rgb = color
    rpr = r._r.get_or_add_rPr()
    for tag in ("ea", "cs"):
        el = rpr.find(f"{{{A}}}{tag}")
        if el is None:
            el = etree.SubElement(rpr, f"{{{A}}}{tag}")
        el.set("typeface", font)


def text(x, y, w, h, lines, size, font="Pretendard SemiBold", color=DARK, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, name="텍스트", spacing=1.15):
    tb = s.shapes.add_textbox(Cm(x), Cm(y), Cm(w), Cm(h))
    tb.name = name
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for i, ln in enumerate(lines if isinstance(lines, list) else [lines]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        for t, f, sz, c in (ln if isinstance(ln, list) else [(ln, font, size, color)]):
            r = p.add_run(); r.text = t; setfont(r, f, sz, c)
    return tb


def pill(x, y, label, fill, w=None):
    w = w or (0.55 + 0.3 * len(label))
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Cm(x), Cm(y), Cm(w), Cm(0.64))
    sh.adjustments[0] = 0.5
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    sh.line.fill.background()
    sh.name = "태그"
    tf = sh.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = label; setfont(r, "Pretendard SemiBold", 10.5, RGBColor(255, 255, 255))
    return sh


def box(x, y, w, h, name):
    el = copy.deepcopy(box_xml)
    s.shapes._spTree.append(el)
    sh = s.shapes[-1]
    sh.left, sh.top, sh.width, sh.height = Cm(x), Cm(y), Cm(w), Cm(h)
    sh.name = name
    return sh


# ---- 1) 기존 연도 상자 4개 삭제 ----
for sid in range(5, 25):
    if sid in by_id:
        el = by_id[sid]._element
        el.getparent().remove(el)

# ---- 2) 아이브로 정리 (요약, 중복 수치 제거) ----
eb = by_id[54].text_frame.paragraphs[0]
runs = eb.runs
runs[0].text = "FINANCIAL FORECAST — 실적 3개년 + 예측 4개년"
for r in runs[1:]:
    r._r.getparent().remove(r._r)

# ---- 3) 상단 성장 타임라인 ----
L, R = 1.53, 32.34
cols = [
    ("2023–25 실적", DARK, "11.6억", DARK, ["한국 검증 · 흑자 전환", "0.8 → 11.6억"]),
    ("2026E", RED, "20억", DARK, ["한·미 진입 · BEP", "공동구매 중심"]),
    ("2027E", RED, "60억", DARK, ["미디어 상시판매 전환", "라인업 확장 · +197%"]),
    ("2028E", RED, "201억", DARK, ["풀 브랜드", "+235%"]),
    ("2029E", DEEP, "506억", DEEP, ["글로벌 확장", "+152% · GP 57%"]),
]
cw = (R - L) / len(cols)
LY = 5.75
ln = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Cm(L + 0.11), Cm(LY), Cm(R - 0.3), Cm(LY))
ln.line.color.rgb = LINE; ln.line.width = Pt(0.8); ln.name = "타임라인 선"
# 실적 구간은 진하게
la = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Cm(L + 0.11), Cm(LY), Cm(L + cw + 0.11), Cm(LY))
la.line.color.rgb = DARK; la.line.width = Pt(1.6); la.name = "타임라인 실적 구간"
for i, (yr, pc, num, nc, cap) in enumerate(cols):
    x = L + i * cw
    pill(x, 4.72, yr, pc)
    d = s.shapes.add_shape(MSO_SHAPE.OVAL, Cm(x), Cm(LY - 0.11), Cm(0.22), Cm(0.22))
    d.fill.solid(); d.fill.fore_color.rgb = pc; d.line.fill.background(); d.name = "타임라인 점"
    if i:
        # 연결 화살표 느낌의 작은 쉐브론 대신 점 사이 간격 유지
        pass
    num_val, unit = num[:-1], num[-1]
    text(x, 6.05, cw - 0.3, 1.3, [[(num_val, "Pretendard ExtraBold", 32, nc), (unit, "Pretendard Bold", 16, nc)]],
         32, name=f"타임라인 수치 {yr}", spacing=1.0)
    text(x, 7.4, cw - 0.3, 1.0, cap, 11, "Pretendard Medium", TXT2, name=f"타임라인 설명 {yr}")

# ---- 4) 하단 상자 2개 ----
BY, BH = 9.0, 8.45
GAP = 0.4
LW = 14.9
lb = box(L, BY, LW, BH, "차트 상자")
rb = box(L + LW + GAP, BY, R - L - LW - GAP, BH, "표 상자")
pill(L + 0.4, BY + 0.38, "매출 성장 (억원)", RED)
cagr = kids[56]
pill(L + LW + GAP + 0.4, BY + 0.38, "요약 손익 (억원)", RED)

# 그룹 안 요소를 슬라이드로 꺼내 위치 변환
drop = {37, 38, 41, 114, 115, 116, 117, 118, 119, 120, 121, 122, 3, 4, 25, 109, 110, 111, 112}
for sid in list(kids):
    nm = kids[sid].name
    if nm.startswith("YoY") or nm.startswith("코스메틱 20"):
        drop.add(sid)
chart_ids = [sid for sid in kids if sid not in drop and sid not in (31, 113, 56)]
# 차트 원래 범위 → 새 범위
cx0, cy0, cx1, cy1 = 1.55, 9.24, 16.08, 14.31
nx0, ny0, nx1, ny1 = L + 0.45, BY + 1.35, L + LW - 0.45, BY + BH - 0.45
sx, sy = (nx1 - nx0) / (cx1 - cx0), (ny1 - ny0) / (cy1 - cy0)
spTree = s.shapes._spTree


def move_out(c):
    el = c._element
    el.getparent().remove(el)
    spTree.append(el)


for sid in chart_ids:
    c = kids[sid]
    x, y, w, h = c.left / 360000, c.top / 360000, c.width / 360000, c.height / 360000
    is_text = c.has_text_frame and c.text_frame.text.strip() and not c.name.startswith("막대")
    nx = nx0 + (x - cx0) * sx
    if c.name.startswith("범례"):
        c.left = Cm(nx0 + (x - cx0)); c.top = Cm(ny0 + (y - cy0))
    elif is_text:   # 글자는 크기 유지, 가운데 기준 이동
        ncx = nx0 + (x + w / 2 - cx0) * sx
        ncy = ny0 + (y + h / 2 - cy0) * sy
        c.left, c.top = Cm(ncx - w / 2), Cm(ncy - h / 2)
    elif c.name.startswith("막대"):
        # 막대: 폭은 sx, 높이·위치는 sy (기준선 기준)
        c.left, c.width = Cm(nx), Cm(w * sx)
        c.top, c.height = Cm(ny0 + (y - cy0) * sy), Cm(h * sy)
    elif c.name.startswith("범례"):
        c.left = Cm(nx0 + (x - cx0)); c.top = Cm(ny0 + (y - cy0))
    else:
        c.left, c.top = Cm(nx), Cm(ny0 + (y - cy0) * sy)
        c.width, c.height = Cm(max(w * sx, 0)), Cm(h * sy)
    move_out(c)
# 범례는 왼쪽 위 그대로, 연도·값 라벨은 위 변환으로
# CAGR: 차트 상자 오른쪽 위
cagr.left = Cm(L + LW - 0.4 - cagr.width / 360000); cagr.top = Cm(BY + 0.4)
move_out(cagr)
for p in cagr.text_frame.paragraphs:
    p.alignment = PP_ALIGN.RIGHT

# 표: 오른쪽 상자 안 채우기
tbl_gf = kids[31]
tx0, ty0 = L + LW + GAP + 0.45, BY + 1.35
tw, th = R - tx0 - 0.45, BY + BH - 0.45 - ty0
tbl = tbl_gf.table
old_w = sum(col.width for col in tbl.columns)
for col in tbl.columns:
    col.width = Emu(int(col.width * Cm(tw) / old_w))
for row in tbl.rows:
    row.height = Emu(int(Cm(th) / len(tbl.rows)))
tbl_gf.left, tbl_gf.top = Cm(tx0), Cm(ty0)
tbl_gf.width, tbl_gf.height = Cm(tw), Cm(th)
move_out(tbl_gf)
hl = kids[113]
last = tbl.columns[len(tbl.columns) - 1].width
hl.left = Emu(Cm(tx0) + sum(c.width for c in tbl.columns) - last)
hl.top, hl.width, hl.height = Cm(ty0), Emu(last), Cm(th)
move_out(hl)

# 남은 그룹(삭제 대상) 제거
grp._element.getparent().remove(grp._element)
prs.save(OUT)
print("저장", OUT)
