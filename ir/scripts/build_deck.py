"""deck.json + data CSV + 작업별 tokens + 스타일 선택 → 편집 가능한 PPTX.

사용: python ir/scripts/build_deck.py ir/deck.json
출력: output/ir-<name>/deck.pptx

deck.json 최상위:
  name, company, logo(이미지 경로, 선택), tokens(작업별 색 파일), style(스타일 선택 파일 또는 객체), template(선택),
  data_dir(선택: "data-<작업명>"이면 data/ 경로를 그 폴더로 바꿔 읽음)
슬라이드 type: cover, statement, process, chart, metrics, table, team, ask, closing
공통 필드: title, message, section("01 문제 인식"), summary(하단 요약 바 문구), source, notes
숫자는 data 파일만 가리킨다: value_ref "data/kpi.csv#mau", chart.data, table.data

스타일(design-kit/ir-styles/styles.json):
  typography(compact|standard|airy), cover(A–E), header(A–G), connector(A–E), card(A–E),
  image(A–C), bullet(dot|dash|check|number), divider(solid|dot|dash|none), summary_bar(pill|band|none)
여백은 tokens.json slide.margin_cm(상하좌우 1.5cm) 안전 영역을 벗어나지 않는다. 꽉 찬 배경은 이름 "bleed:".
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")
import csv
import json
import sys
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.enum.dml import MSO_LINE
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt, Emu, Cm

ROOT = Path(__file__).resolve().parents[2]
IR = ROOT / "ir"

# ======================= 설정 읽기 =======================
SPEC_PATH = Path(sys.argv[1] if len(sys.argv) > 1 else IR / "deck.json")
SPEC = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
TOKENS_PATH = ROOT / (SPEC.get("tokens") or "tokens.json")
tok = json.loads(TOKENS_PATH.read_text(encoding="utf-8"))
C = tok["color"]
CAT = json.loads((ROOT / "design-kit/ir-styles/styles.json").read_text(encoding="utf-8"))
CH = {c["id"]: c for c in CAT["chapters"]}
_style = SPEC.get("style") or {}
if isinstance(_style, str):
    _style = json.loads((ROOT / _style).read_text(encoding="utf-8"))
STY = {**CAT["defaults"], **{k: v for k, v in _style.items() if not k.startswith("_")}}
TYPO = CH["typography"]["options"][STY["typography"]]
FIX = CAT["fixed"]
SP = {k: Cm(v) for k, v in FIX["spacing_cm"].items()}
LW = {k: Pt(v) for k, v in FIX["line_pt"].items()}
DATA_DIR = SPEC.get("data_dir", "")


def rgb(h):
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def mix(h1, h2, t):
    a, b = rgb(h1), rgb(h2)
    return RGBColor(*(round(a[i] + (b[i] - a[i]) * t) for i in range(3)))


BR = C["brand"]
ACCENT = rgb(BR.get("primaryHover", BR["primary"]))
ACCENT_SOFT = mix(BR["primary"], "#FFFFFF", 0.88)
INK, INK_SOFT = rgb(C["text"]["primary"]), rgb(C["text"]["secondary"])
MUTED, LINE = rgb(C["neutral"]["500"]), rgb(C["neutral"]["300"])
LINE_SOFT, SURFACE = rgb(C["neutral"]["100"]), rgb(C["neutral"]["50"])
WHITE = rgb("#FFFFFF")
PALE = rgb(C["neutral"]["300"])
DARK = rgb(BR.get("secondary", C["text"]["primary"]))
SERIES = [ACCENT, rgb(C["neutral"]["700"]), LINE, MUTED]
FAMILY = tok["font"]["family"]["heading"].split(",")[0].strip().strip('"')
WEIGHT = TYPO.get("weight", {})
SIZE, MIN = TYPO["size"], TYPO["min_pt"]

# ======================= 여백·격자 =======================
W, H = Inches(13.333), Inches(7.5)
_mg = tok.get("slide", {}).get("margin_cm", {"top": 1.5, "right": 1.5, "bottom": 1.5, "left": 1.5})
X0, Y0 = Cm(_mg["left"]), Cm(_mg["top"])
X1, Y1 = W - Cm(_mg["right"]), H - Cm(_mg["bottom"])
CW = X1 - X0
FOOT_H = Inches(0.28)
FOOT_Y = Y1 - FOOT_H
TOP = Y0 + Inches(1.9)                       # 모든 상단 스타일 공통 본문 시작선
BOTTOM = FOOT_Y - SP["s"]                    # 본문 끝 (꼬리말 위)
SUMMARY_H = Inches(0.5)


# ======================= 데이터 =======================
def _p(rel):
    if DATA_DIR and rel.startswith("data/"):
        return IR / DATA_DIR / rel[len("data/"):]
    return IR / rel


def read_csv(rel):
    with open(_p(rel), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def resolve(ref):
    path, key = ref.split("#")
    for row in read_csv(path):
        if row.get("key") == key:
            return row
    raise KeyError(f"{ref} 없음")


def num(v):
    return float(str(v).replace(",", ""))


def fmt(v):
    n = num(v)
    return f"{n:,.0f}" if n == int(n) else f"{n:,.1f}"


# ======================= 글자 =======================
def face(role):
    w = WEIGHT.get(role if role in WEIGHT else ("title" if role == "display" else "body"), "")
    if FAMILY == "Pretendard" and w and w not in ("Regular", "Bold"):
        return f"Pretendard {w}", False
    return FAMILY, w in ("Bold", "ExtraBold", "Black", "SemiBold")


def style_run(run, size, role, color, bold=None):
    name, b = face(role)
    size = max(size, MIN["caption"] if role == "caption" else MIN["body"])   # 최소 글자 크기 강제
    f = run.font
    f.name, f.size, f.color.rgb = name, Pt(size), color
    f.bold = b if bold is None else bold
    rPr = run._r.get_or_add_rPr()
    rPr.set("spc", str(round(size * TYPO["tracking_pct"])))                 # 자간: 크기의 % (1/100pt)
    for tag in ("ea", "cs"):
        el = rPr.find(qn(f"a:{tag}"))
        if el is None:
            el = rPr.makeelement(qn(f"a:{tag}"), {})
            rPr.append(el)
        el.set("typeface", name)


def add_bullet(p):
    kind = STY["bullet"]
    pPr = p._p.get_or_add_pPr()
    pPr.set("marL", str(int(Cm(0.45))))
    pPr.set("indent", str(-int(Cm(0.45))))
    clr = pPr.makeelement(qn("a:buClr"), {})
    clr.append(clr.makeelement(qn("a:srgbClr"), {"val": str(ACCENT)}))
    pPr.append(clr)
    if kind == "number":
        pPr.append(pPr.makeelement(qn("a:buAutoNum"), {"type": "arabicPeriod"}))
    else:
        pPr.append(pPr.makeelement(qn("a:buChar"), {"char": {"dot": "•", "dash": "–", "check": "✓"}[kind]}))


def text(slide, x, y, w, h, s, size=None, role="body", color=INK, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, bold=None, bullets=False):
    size = size or SIZE.get(role, SIZE["body"])
    x, y, w, h = (int(v) for v in (x, y, w, h))
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    lines = s if isinstance(s, list) else [s]
    lead = TYPO["leading_pct"]["title" if role in ("title", "display") else "body"] / 100
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = lead
        if bullets:
            add_bullet(p)
            if i:
                p.space_before = Pt(size * 0.4)
        r = p.add_run()
        r.text = str(line)
        style_run(r, size, role, color, bold)
    return tb


# ======================= 도형 =======================
def shape(slide, kind, x, y, w, h, fill=None, line=None, lw="regular", radius=None, name=None):
    x, y, w, h = (int(v) for v in (x, y, w, h))
    s = slide.shapes.add_shape(kind, x, y, w, h)
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = LW[lw]
    s.shadow.inherit = False
    st = s._element.find(qn("p:style"))      # 기본 테마 효과(그림자 등) 제거
    if st is not None:
        s._element.remove(st)
    if radius is not None and kind in (MSO_SHAPE.ROUNDED_RECTANGLE, MSO_SHAPE.ROUND_2_SAME_RECTANGLE):
        s.adjustments[0] = radius
    if name:
        s.name = name
    return s


def rect(slide, x, y, w, h, fill, name=None):
    return shape(slide, MSO_SHAPE.RECTANGLE, x, y, w, h, fill=fill, name=name)


def seg(slide, x1, y1, x2, y2, color=LINE, lw="hair", dash=None, end=None):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, *(int(v) for v in (x1, y1, x2, y2)))
    c.line.color.rgb, c.line.width = color, LW[lw]
    st = c._element.find(qn("p:style"))
    if st is not None:
        c._element.remove(st)
    if dash:
        c.line.dash_style = dash
    if end:
        ln = c.line._get_or_add_ln()
        ln.append(ln.makeelement(qn("a:tailEnd"), {"type": end, "w": "med", "len": "med"}))
    return c


def divider(slide, x, y, w, color=LINE):
    kind = STY["divider"]
    if kind != "none":
        seg(slide, x, y, x + w, y, color, "hair", {"solid": None, "dot": MSO_LINE.ROUND_DOT, "dash": MSO_LINE.DASH}[kind])


def set_alpha(shp, alpha_pct):
    clr = shp.fill._xPr.find(qn("a:solidFill"))[0]
    clr.append(clr.makeelement(qn("a:alpha"), {"val": str(int(alpha_pct * 1000))}))


def picture(slide, path, x, y, w, h, kind=None, name=None):
    """이미지 스타일(직각·둥근·원형) 적용. 파일이 없으면 같은 모양의 자리표시."""
    kind = kind or STY["image"]
    rad = CH["image"]["options"][kind]["radius"]
    x, y, w, h = (int(v) for v in (x, y, w, h))
    p = ROOT / path if path else None
    if p and p.exists():
        pic = slide.shapes.add_picture(str(p), x, y, w, h)
        if rad:
            geom = pic._element.spPr.find(qn("a:prstGeom"))
            geom.set("prst", "ellipse" if rad == "circle" else "roundRect")
            if rad != "circle":
                av = geom.find(qn("a:avLst"))
                av.append(av.makeelement(qn("a:gd"), {"name": "adj", "fmla": f"val {int(rad * 100000)}"}))
        if name:
            pic.name = name
        return pic
    ks = MSO_SHAPE.OVAL if rad == "circle" else (MSO_SHAPE.ROUNDED_RECTANGLE if rad else MSO_SHAPE.RECTANGLE)
    shape(slide, ks, x, y, w, h, fill=LINE_SOFT, radius=rad if rad and rad != "circle" else None, name=name)
    text(slide, x, y, w, h, "이미지 자리", role="caption", color=MUTED, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


# ======================= 상단(헤더) =======================
def logo_mark(slide, y, color=MUTED):
    if SPEC.get("logo") and (ROOT / SPEC["logo"]).exists():
        pic = slide.shapes.add_picture(str(ROOT / SPEC["logo"]), X1 - Inches(1.4), y, height=Inches(0.28))
        pic.left = X1 - pic.width
    elif SPEC.get("company"):
        text(slide, X1 - Inches(3), y, Inches(3), Inches(0.28), SPEC["company"], role="caption", color=color,
             align=PP_ALIGN.RIGHT, bold=True)


def header(slide, d, idx):
    kind = STY["header"]
    sec = d.get("section", "")
    T, S = SIZE["title"], SIZE["subtitle"]
    msg = d.get("message")
    if kind == "A":       # 라벨줄 + 가운데 제목
        if sec:
            text(slide, X0, Y0, Inches(5), Inches(0.28), sec, role="caption", color=MUTED)
        logo_mark(slide, Y0)
        text(slide, X0, Y0 + Inches(0.5), CW, Inches(0.7), d["title"], T, "title", align=PP_ALIGN.CENTER)
        if msg:
            text(slide, X0, Y0 + Inches(1.2), CW, Inches(0.5), msg, S, "body", INK_SOFT, PP_ALIGN.CENTER)
    elif kind == "B":     # 알약 칩 + 왼쪽 제목
        if sec:
            cw_ = Inches(0.36) + Inches(0.1) * len(sec)
            shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, X0, Y0, cw_, Inches(0.3), fill=ACCENT, radius=0.5)
            text(slide, X0, Y0, cw_, Inches(0.3), sec, role="caption", color=WHITE, align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE, bold=True)
        logo_mark(slide, Y0)
        text(slide, X0, Y0 + Inches(0.45), CW, Inches(0.7), d["title"], T, "title")
        if msg:
            text(slide, X0, Y0 + Inches(1.15), CW, Inches(0.5), msg, S, "body", INK_SOFT)
    elif kind == "C":     # 위쪽 컬러 띠
        rect(slide, 0, 0, W, Y0 + Inches(0.32), DARK, name="bleed:header-band")
        if sec:
            text(slide, X0, Y0, Inches(6), Inches(0.28), sec, role="caption", color=WHITE, bold=True)
        logo_mark(slide, Y0, color=WHITE)
        text(slide, X0, Y0 + Inches(0.6), CW, Inches(0.7), d["title"], T, "title")
        if msg:
            text(slide, X0, Y0 + Inches(1.28), CW, Inches(0.5), msg, S, "body", INK_SOFT)
    elif kind == "D":     # 큰 섹션 번호 + 왼쪽 제목
        no = sec.split()[0] if sec else f"{idx:02d}"
        text(slide, X0, Y0 - Inches(0.05), Inches(1.1), Inches(0.9), no, 44, "display", ACCENT)
        text(slide, X0 + Inches(1.25), Y0 + Inches(0.05), CW - Inches(1.25), Inches(0.7), d["title"], T, "title")
        if msg:
            text(slide, X0 + Inches(1.25), Y0 + Inches(0.78), CW - Inches(1.25), Inches(0.5), msg, S, "body", INK_SOFT)
        divider(slide, X0, TOP - SP["s"], CW)
    elif kind == "E":     # Chapter 표기 + 가운데 제목 + 가는 선
        lab = sec or f"Chapter {idx:02d}"
        text(slide, X0, Y0, CW, Inches(0.28), lab, role="caption", color=ACCENT, align=PP_ALIGN.CENTER, bold=True)
        mid = X0 + CW / 2
        seg(slide, mid - Inches(2.6), Y0 + Inches(0.14), mid - Inches(1.0), Y0 + Inches(0.14))
        seg(slide, mid + Inches(1.0), Y0 + Inches(0.14), mid + Inches(2.6), Y0 + Inches(0.14))
        text(slide, X0, Y0 + Inches(0.42), CW, Inches(0.7), d["title"], T, "title", align=PP_ALIGN.CENTER)
        if msg:
            text(slide, X0, Y0 + Inches(1.12), CW, Inches(0.5), msg, S, "body", INK_SOFT, PP_ALIGN.CENTER)
    elif kind == "F":     # 작은 섹션 표기 + 로고 + 왼쪽 제목 + 구분선
        if sec:
            rect(slide, X0, Y0 + Inches(0.08), Inches(0.12), Inches(0.12), ACCENT)
            text(slide, X0 + Inches(0.2), Y0, Inches(6), Inches(0.28), sec, role="caption", color=INK_SOFT, bold=True)
        logo_mark(slide, Y0)
        text(slide, X0, Y0 + Inches(0.48), CW, Inches(0.7), d["title"], T, "title")
        if msg:
            text(slide, X0, Y0 + Inches(1.15), CW, Inches(0.45), msg, S, "body", INK_SOFT)
        divider(slide, X0, TOP - SP["s"], CW)
    else:                 # G 진행 막대 + 왼쪽 제목
        secs = SPEC.get("_sections", [])
        cur = secs.index(sec) if sec in secs else -1
        n = max(len(secs), 1)
        sw, gap = Inches(0.42), Inches(0.06)
        for i in range(n):
            shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, X0 + i * (sw + gap), Y0 + Inches(0.1), sw, Inches(0.07),
                  fill=ACCENT if i == cur else LINE_SOFT, radius=0.5)
        if sec:
            text(slide, X0 + n * (sw + gap) + Inches(0.1), Y0, Inches(5), Inches(0.28), sec, role="caption", color=MUTED)
        logo_mark(slide, Y0)
        text(slide, X0, Y0 + Inches(0.48), CW, Inches(0.7), d["title"], T, "title")
        if msg:
            text(slide, X0, Y0 + Inches(1.15), CW, Inches(0.45), msg, S, "body", INK_SOFT)


def footer(slide, idx, source=None, dark=False):
    col = PALE if dark else MUTED
    if source:
        text(slide, X0, FOOT_Y, CW - Inches(1.2), FOOT_H, f"출처: {source}", role="caption", color=col)
    text(slide, X1 - Inches(1), FOOT_Y, Inches(1), FOOT_H, str(idx), role="caption", color=col, align=PP_ALIGN.RIGHT)


def summary_bar(slide, d):
    """하단 요약 바. 있으면 본문 끝을 그만큼 올린 값을 돌려준다."""
    if not d.get("summary"):
        return BOTTOM
    kind = STY["summary_bar"]
    y = BOTTOM - SUMMARY_H
    if kind == "pill":
        shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, X0, y, CW, SUMMARY_H, fill=ACCENT, radius=0.5)
        text(slide, X0, y, CW, SUMMARY_H, d["summary"], SIZE["body"], "head", WHITE, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    elif kind == "band":
        rect(slide, X0, y, CW, SUMMARY_H, DARK)
        text(slide, X0 + SP["m"], y, CW - 2 * SP["m"], SUMMARY_H, d["summary"], SIZE["body"], "head", WHITE,
             anchor=MSO_ANCHOR.MIDDLE)
    else:
        text(slide, X0, y, CW, SUMMARY_H, d["summary"], SIZE["body"], "head", ACCENT, anchor=MSO_ANCHOR.MIDDLE)
    return y - SP["m"]


# ======================= 카드·연결 =======================
def card(slide, x, y, w, h, head, body, i=0, label=None):
    kind = STY["card"]
    rad = CH["card"]["options"][kind].get("radius", 0.06)
    pad = SP["m"]
    bl = body if isinstance(body, list) else ([body] if body else [])
    tx, tw = x + pad, w - 2 * pad
    if kind == "C":       # 위쪽 컬러 헤더
        hh = Inches(0.5)
        shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=WHITE, line=LINE, lw="hair", radius=rad)
        shape(slide, MSO_SHAPE.ROUND_2_SAME_RECTANGLE, x, y, w, hh, fill=ACCENT if i == 0 else DARK, radius=rad * 2)
        text(slide, tx, y, tw, hh, head, SIZE["body"] + 1, "head", WHITE, anchor=MSO_ANCHOR.MIDDLE)
        text(slide, tx, y + hh + pad, tw, h - hh - 2 * pad, bl, role="body", color=INK_SOFT, bullets=len(bl) > 1)
        return
    if kind == "D":       # 알약 라벨(Phase형)
        lab = label or head
        pw = min(w, Inches(0.5) + Inches(0.12) * len(lab))
        shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x + (w - pw) / 2, y, pw, Inches(0.36), fill=ACCENT, radius=0.5)
        text(slide, x, y, w, Inches(0.36), lab, role="caption", color=WHITE, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE, bold=True)
        top = y + Inches(0.36) + SP["s"]
        if label:
            text(slide, x, top, w, Inches(0.5), head, SIZE["body"] + 2, "head", align=PP_ALIGN.CENTER)
            top += Inches(0.5) + SP["xs"]
        divider(slide, x, top, w)
        top += SP["s"]
        text(slide, x, top, w, y + h - top, bl, role="body", color=INK_SOFT,
             align=PP_ALIGN.CENTER if len(bl) <= 1 else PP_ALIGN.LEFT, bullets=len(bl) > 1)
        return
    if kind == "A":       # 연한 면
        shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=SURFACE, radius=rad)
        hc, bc = (ACCENT if i == 0 else INK), INK_SOFT
    elif kind == "B":     # 흰 바탕 + 테두리
        shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=WHITE, line=LINE, lw="regular", radius=rad)
        hc, bc = (ACCENT if i == 0 else INK), INK_SOFT
    else:                 # E 진한 채움
        shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=DARK, radius=rad)
        hc, bc = WHITE, PALE
    text(slide, tx, y + pad, tw, Inches(0.5), head, SIZE["body"] + 2, "head", hc)
    text(slide, tx, y + pad + Inches(0.5) + SP["xs"], tw, h - Inches(0.5) - 2 * pad - SP["xs"], bl,
         role="body", color=bc, bullets=len(bl) > 1)


def connector(slide, x_from, x_to, y):
    kind = STY["connector"]
    gap = x_to - x_from
    if kind == "A":       # 작은 셰브론
        s = Inches(0.16)
        shp = shape(slide, MSO_SHAPE.CHEVRON, x_from + (gap - s) / 2, y - s / 2, s, s, fill=ACCENT)
        shp.adjustments[0] = 0.55
    elif kind == "D":     # 블록 화살표
        s = min(gap - Inches(0.08), Inches(0.4))
        shape(slide, MSO_SHAPE.RIGHT_ARROW, x_from + (gap - s) / 2, y - Inches(0.16), s, Inches(0.32), fill=ACCENT_SOFT)
    else:
        m = Inches(0.06)
        end = {"B": "oval", "C": "stealth", "E": "triangle"}[kind]
        seg(slide, x_from + m, y, x_to - m, y, ACCENT, "regular", MSO_LINE.DASH if kind == "E" else None, end)


def cards_row(slide, items, top, bottom, connectors=False):
    n = len(items)
    gap = SP["l"] + (Inches(0.15) if connectors else 0)
    cw = (CW - gap * (n - 1)) / n
    for i, it in enumerate(items):
        x = X0 + i * (cw + gap)
        card(slide, x, top, cw, bottom - top, it.get("head", ""), it.get("body", ""), i, it.get("label"))
        if connectors and i < n - 1:
            connector(slide, x + cw, x + cw + gap, top + (bottom - top) / 2)


# ======================= 슬라이드 =======================
def bg(slide, color, name="bleed:background"):
    rect(slide, 0, 0, W, H, color, name=name)


def s_cover(slide, d, idx):
    kind = STY["cover"]
    img = d.get("image")
    tag, meta = d.get("subtitle", ""), d.get("meta", "")
    big = d.get("title") or SPEC.get("company", "")
    if kind == "A":       # 다크 키비주얼 + 왼쪽 큰 로고
        bg(slide, DARK)
        if img and (ROOT / img).exists():
            slide.shapes.add_picture(str(ROOT / img), 0, 0, W, H).name = "bleed:cover-image"
            set_alpha(rect(slide, 0, 0, W, H, DARK, name="bleed:overlay"), 55)
        text(slide, X0, Inches(2.6), CW * 0.7, Inches(1.4), big, 60, "display", WHITE)
        text(slide, X0, Inches(4.05), CW * 0.6, Inches(0.8), tag, SIZE["subtitle"] + 2, "body", rgb(C["neutral"]["100"]))
        text(slide, X0, FOOT_Y, CW, FOOT_H, meta, role="caption", color=PALE)
    elif kind == "B":     # 왼쪽 글 + 오른쪽 목업·사진
        half = CW * 0.46
        text(slide, X0, Inches(2.4), half, Inches(1.3), big, 48, "display", INK)
        rect(slide, X0, Inches(3.8), Inches(0.6), Inches(0.06), ACCENT)
        text(slide, X0, Inches(4.0), half, Inches(1.0), tag, SIZE["subtitle"] + 2, "body", INK_SOFT)
        picture(slide, img, X0 + CW * 0.52, Y0, CW * 0.48, Y1 - Y0)
        text(slide, X0, FOOT_Y, half, FOOT_H, meta, role="caption", color=MUTED)
    elif kind == "C":     # 밝은 배경 + 오브젝트
        bg(slide, SURFACE)
        r = Inches(4.4)
        shape(slide, MSO_SHAPE.OVAL, X1 - r, Y0 + Inches(0.3), r, r, fill=ACCENT_SOFT)
        if img:
            picture(slide, img, X1 - r + Inches(0.4), Y0 + Inches(0.7), r - Inches(0.8), r - Inches(0.8), kind="C")
        text(slide, X0, Inches(2.6), CW * 0.55, Inches(1.4), big, 54, "display", ACCENT)
        text(slide, X0, Inches(4.05), CW * 0.5, Inches(0.8), tag, SIZE["subtitle"] + 2, "body", INK_SOFT)
        text(slide, X0, FOOT_Y, CW, FOOT_H, meta, role="caption", color=MUTED)
    elif kind == "D":     # 가운데 로고 + 코너 프레임
        bg(slide, DARK)
        arm = Inches(0.45)
        for (cx, cy, dx, dy) in ((X0, Y0, 1, 1), (X1, Y0, -1, 1), (X0, Y1, 1, -1), (X1, Y1, -1, -1)):
            seg(slide, cx, cy, cx + dx * arm, cy, PALE, "regular")
            seg(slide, cx, cy, cx, cy + dy * arm, PALE, "regular")
        text(slide, X0, Inches(2.75), CW, Inches(1.2), big, 54, "display", WHITE, PP_ALIGN.CENTER)
        text(slide, X0, Inches(3.95), CW, Inches(0.6), tag, SIZE["subtitle"], "body", rgb(C["neutral"]["100"]), PP_ALIGN.CENTER)
        text(slide, X0, FOOT_Y - Inches(0.35), CW, FOOT_H, meta, role="caption", color=PALE, align=PP_ALIGN.CENTER)
    else:                 # E 컬러 배경 + 대형 타이포
        bg(slide, ACCENT)
        text(slide, X0, Y0, CW * 0.6, Inches(0.8), tag, SIZE["subtitle"] + 2, "body", WHITE)
        text(slide, X1 - Inches(4), Y0, Inches(4), FOOT_H, meta, role="caption", color=WHITE, align=PP_ALIGN.RIGHT)
        text(slide, X0, Y1 - Inches(1.9), CW, Inches(1.9), big, 110, "display", WHITE, anchor=MSO_ANCHOR.BOTTOM)


def s_statement(slide, d, idx):
    header(slide, d, idx)
    end = summary_bar(slide, d)
    if d.get("points"):
        cards_row(slide, d["points"][:4], TOP, end)
    footer(slide, idx, d.get("source"))


def s_process(slide, d, idx):
    header(slide, d, idx)
    end = summary_bar(slide, d)
    cards_row(slide, d["steps"][:5], TOP, end, connectors=True)
    footer(slide, idx, d.get("source"))


def s_chart(slide, d, idx):
    header(slide, d, idx)
    end = summary_bar(slide, d)
    c = d["chart"]
    rows = read_csv(c["data"])
    cd = CategoryChartData()
    cd.categories = [r[c["x"]] for r in rows]
    for ycol in c["y"]:
        cd.add_series(c.get("labels", {}).get(ycol, ycol), [num(r[ycol]) for r in rows])
    kind = {"bar": XL_CHART_TYPE.COLUMN_CLUSTERED, "stacked": XL_CHART_TYPE.COLUMN_STACKED,
            "line": XL_CHART_TYPE.LINE_MARKERS, "hbar": XL_CHART_TYPE.BAR_CLUSTERED}[c.get("kind", "bar")]
    top = TOP + (Inches(0.35) if c.get("unit") else 0)
    ch = slide.shapes.add_chart(kind, int(X0), int(top), int(CW), int(end - top), cd).chart
    small = Pt(max(SIZE["small"], MIN["body"]))
    ch.font.name, ch.font.size, ch.font.color.rgb = face("body")[0], small, INK_SOFT
    ch.has_title = False
    ch.has_legend = len(c["y"]) > 1
    if ch.has_legend:
        ch.legend.position, ch.legend.include_in_layout = XL_LEGEND_POSITION.TOP, False
    ch.value_axis.has_major_gridlines = False
    ch.value_axis.visible = False
    ca = ch.category_axis
    ca.format.line.color.rgb, ca.format.line.width = LINE, LW["hair"]
    ca.has_major_gridlines = False
    if kind == XL_CHART_TYPE.BAR_CLUSTERED:
        ca.reverse_order = True
    plot = ch.plots[0]
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.number_format, dl.number_format_is_linked = "#,##0", False
    dl.font.size, dl.font.bold, dl.font.color.rgb = small, True, INK
    if kind != XL_CHART_TYPE.LINE_MARKERS:
        dl.position = XL_LABEL_POSITION.CENTER if kind == XL_CHART_TYPE.COLUMN_STACKED else XL_LABEL_POSITION.OUTSIDE_END
        plot.gap_width = 60
    hi = c.get("highlight")
    for si, series in enumerate(plot.series):
        base = SERIES[si % len(SERIES)] if len(c["y"]) > 1 else (LINE if hi else ACCENT)
        if kind == XL_CHART_TYPE.LINE_MARKERS:
            series.format.line.color.rgb = base if len(c["y"]) > 1 else ACCENT
            series.format.line.width = LW["bold"]
            series.smooth = False
            continue
        series.format.fill.solid()
        series.format.fill.fore_color.rgb = base
        if hi and len(c["y"]) == 1:
            for pi, cat in enumerate(cd.categories):
                if str(cat.label) == str(hi):
                    pt = series.points[pi]
                    pt.format.fill.solid()
                    pt.format.fill.fore_color.rgb = ACCENT
    if c.get("unit"):
        text(slide, X0, TOP, Inches(4), Inches(0.28), f"단위: {c['unit']}", role="caption", color=MUTED)
    src = d.get("source") or "; ".join(sorted({r.get("source", "") for r in rows if r.get("source")}))
    footer(slide, idx, src or None)


def s_metrics(slide, d, idx):
    header(slide, d, idx)
    end = summary_bar(slide, d)
    items = [resolve(i["value_ref"]) | {"label_override": i.get("label")} for i in d["items"]][:4]
    n, gap = len(items), SP["l"]
    cw = (CW - gap * (n - 1)) / n
    h = min(end - TOP, Inches(3.0))
    kind = STY["card"]
    rad = CH["card"]["options"][kind]["radius"]
    dark = kind == "E"
    srcs = set()
    for i, r in enumerate(items):
        x = X0 + i * (cw + gap)
        if kind in ("B", "C"):
            shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, TOP, cw, h, fill=WHITE, line=LINE, lw="regular", radius=min(rad, 0.08))
        elif kind != "D":
            shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, TOP, cw, h, fill=DARK if dark else SURFACE, radius=rad)
        pad = SP["m"]
        text(slide, x + pad, TOP + pad, cw - 2 * pad, Inches(1.0), f"{fmt(r['value'])}{r.get('unit', '')}",
             44, "display", WHITE if dark else (ACCENT if i == 0 else INK))
        divider(slide, x + pad, TOP + pad + Inches(1.1), cw - 2 * pad)
        text(slide, x + pad, TOP + pad + Inches(1.25), cw - 2 * pad, Inches(0.8),
             r["label_override"] or r.get("label", r["key"]), role="body", color=PALE if dark else INK_SOFT)
        if r.get("as_of"):
            text(slide, x + pad, TOP + h - pad - Inches(0.25), cw - 2 * pad, Inches(0.25), f"기준 {r['as_of']}",
                 role="caption", color=MUTED)
        if r.get("source"):
            srcs.add(r["source"])
    footer(slide, idx, d.get("source") or "; ".join(sorted(srcs)) or None)


def s_table(slide, d, idx):
    header(slide, d, idx)
    end = summary_bar(slide, d)
    rows = read_csv(d["table"]["data"])
    cols = d["table"].get("columns") or [k for k in rows[0] if k != "source"]
    hi = d["table"].get("highlight_row")
    n_r, n_c = len(rows) + 1, len(cols)
    row_h = min(Inches(0.5), int((end - TOP) / n_r))
    tbl = slide.shapes.add_table(n_r, n_c, int(X0), int(TOP), int(CW), int(row_h * n_r)).table
    for i in range(n_r):
        for j in range(n_c):
            cell = tbl.cell(i, j)
            is_hi = i > 0 and hi and rows[i - 1][cols[0]] == hi
            cell.text = d["table"].get("labels", {}).get(cols[j], cols[j]) if i == 0 else rows[i - 1][cols[j]]
            cell.fill.solid()
            cell.fill.fore_color.rgb = DARK if i == 0 else (ACCENT_SOFT if is_hi else WHITE)
            cell.margin_left = cell.margin_right = SP["s"]
            for p in cell.text_frame.paragraphs:
                for run in p.runs:
                    style_run(run, SIZE["small"], "head" if (i == 0 or (is_hi and j == 0)) else "body",
                              WHITE if i == 0 else INK)
    srcs = sorted({r.get("source", "") for r in rows if r.get("source")})
    footer(slide, idx, d.get("source") or "; ".join(srcs) or None)


def s_team(slide, d, idx):
    header(slide, d, idx)
    people = d["people"][:4]
    n, gap = len(people), SP["l"]
    cw = (CW - gap * (n - 1)) / n
    ph = Inches(1.3)
    for i, p in enumerate(people):
        x = X0 + i * (cw + gap)
        picture(slide, p.get("photo"), x, TOP, ph, ph)
        y = TOP + ph + SP["s"]
        text(slide, x, y, cw, Inches(0.45), p["name"], SIZE["body"] + 4, "head")
        text(slide, x, y + Inches(0.45), cw, Inches(0.35), p["role"], role="body", color=ACCENT)
        divider(slide, x, y + Inches(0.88), cw)
        bio = p.get("bio", "")
        text(slide, x, y + Inches(1.0), cw, BOTTOM - y - Inches(1.0), bio, role="body", color=INK_SOFT,
             bullets=isinstance(bio, list) and len(bio) > 1)
    footer(slide, idx)


def s_ask(slide, d, idx):
    bg(slide, DARK)
    r = resolve(d["amount_ref"])
    text(slide, X0, Y0, CW, Inches(0.7), d["title"], SIZE["title"], "title", WHITE)
    text(slide, X0, Y0 + Inches(0.9), CW, Inches(1.4), f"{fmt(r['value'])}{r.get('unit', '')}", 72, "display", WHITE)
    if d.get("message"):
        text(slide, X0, Y0 + Inches(2.35), Inches(8), Inches(0.6), d["message"], SIZE["subtitle"], "body", PALE)
    if d.get("use_of_funds"):
        y = Y0 + Inches(3.3)
        for row in read_csv(d["use_of_funds"]):
            text(slide, X0, y, Inches(5), Inches(0.4), row["label"], role="body", color=WHITE)
            text(slide, X0 + Inches(5), y, Inches(1.5), Inches(0.4), f"{fmt(row['value'])}{row.get('unit', '%')}",
                 role="head", color=WHITE, align=PP_ALIGN.RIGHT)
            divider(slide, X0, y + Inches(0.47), Inches(6.5), color=MUTED)
            y += Inches(0.6)
    footer(slide, idx, dark=True)


def s_closing(slide, d, idx):
    text(slide, X0, Inches(2.6), CW, Inches(1.0), d["title"], 40, "display")
    if d.get("message"):
        text(slide, X0, Inches(3.7), CW, Inches(0.8), d["message"], SIZE["subtitle"], "body", INK_SOFT)
    if d.get("contact"):
        text(slide, X0, FOOT_Y, CW, FOOT_H, d["contact"], role="body", color=MUTED)


BUILDERS = {"cover": s_cover, "statement": s_statement, "process": s_process, "chart": s_chart,
            "metrics": s_metrics, "table": s_table, "team": s_team, "ask": s_ask, "closing": s_closing}


def main():
    SPEC["_sections"] = list(dict.fromkeys(s["section"] for s in SPEC["slides"] if s.get("section")))
    tpl = SPEC.get("template")
    prs = Presentation(str(ROOT / tpl)) if tpl else Presentation()
    if not tpl:
        prs.slide_width, prs.slide_height = W, H
    blank = prs.slide_layouts[6] if len(prs.slide_layouts) > 6 else prs.slide_layouts[-1]
    for i, d in enumerate(SPEC["slides"], 1):
        slide = prs.slides.add_slide(blank)
        BUILDERS[d["type"]](slide, d, i)
        if d.get("notes"):
            slide.notes_slide.notes_text_frame.text = d["notes"]
    out_dir = ROOT / "output" / f"ir-{SPEC['name']}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / (SPEC.get("out_file") or "deck.pptx")
    prs.save(out)
    pick = ", ".join(f"{k}={STY[k]}" for k in ("typography", "cover", "header", "connector", "card", "image", "bullet", "divider", "summary_bar"))
    print(f"생성: {out.relative_to(ROOT)} ({len(SPEC['slides'])}장 | 색: {TOKENS_PATH.relative_to(ROOT)} | 스타일: {pick})")


if __name__ == "__main__":
    main()
