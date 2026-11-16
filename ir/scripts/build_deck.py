"""deck.json + data CSV + 작업별 tokens + 스타일 선택 → 편집 가능한 PPTX.

사용: python ir/scripts/build_deck.py ir/deck.json
출력: output/ir-<name>/deck.pptx

deck.json 최상위:
  name, company, logo(이미지 경로, 선택), tokens(작업별 색 파일), style(스타일 선택 파일 또는 객체), template(선택),
  data_dir(선택: "data-<작업명>"이면 data/ 경로를 그 폴더로 바꿔 읽음)
슬라이드 type: cover, statement, process, chart, metrics, table, team, ask, closing,
  timeline(로드맵·연혁), tam(TAM/SAM/SOM 원), compare(O/△/X 비교표), product(제품 화면+설명), structure(서비스 구조도)
  카드·단계·항목에 icon(Lucide 이름 또는 assets/icons/custom 이름) 지정 가능
공통 필드: title, message, section("01 문제 인식"), summary(하단 요약 바 문구), source, notes
숫자는 data 파일만 가리킨다: value_ref "data/kpi.csv#mau", chart.data, table.data

스타일(design-kit/ir-styles/styles.json):
  typography(compact|standard|airy), cover(A–E), header(A–G), connector(F 기본·A–E), card(A–E),
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


INTERNAL_SRC = __import__("re").compile(r"^(원고|샘플|내부|고객 확인|TODO)")


def cite(row):
    """덱에 보여 줄 출처: cite 열이 있으면 그것, 없으면 source 중 내부 추적용(원고 슬라이드 N 등)은 숨김."""
    c = (row.get("cite") or row.get("source") or "").strip()
    return "" if INTERNAL_SRC.match(c) else c


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


def num_text(slide, x, y, w, h, value, unit="", size=44, color=INK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
             unit_ratio=0.45, prefix=""):
    """큰 숫자 + 작은 단위(같은 줄, 기준선 맞춤). 예: 12 + 억원, 30 + %."""
    x, y, w, h = (int(v) for v in (x, y, w, h))
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = False
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = 1.0
    if prefix:
        r0 = p.add_run(); r0.text = prefix
        style_run(r0, max(size * unit_ratio, MIN["body"]), "head", color)
    r = p.add_run(); r.text = str(value)
    style_run(r, size, "display", color)
    if unit:
        u = p.add_run(); u.text = unit if unit.startswith(("%", "x", "×")) else unit
        style_run(u, max(size * unit_ratio, MIN["body"]), "head", color)
    return tb


def split_value(row):
    return fmt(row["value"]), row.get("unit", "")


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


ICON_SIZE = Inches(0.42)


def icon_img(slide, name, x, y, size=None, color=None):
    """라인 아이콘(Lucide 이름, custom 이름, 또는 .svg 경로)을 브랜드 색 PNG로 넣는다."""
    if not name:
        return 0
    size = int(size or ICON_SIZE)
    col = "#" + str(color if color is not None else ACCENT)
    cand = [ROOT / name, ROOT / "assets/icons/custom" / f"{name}.svg", ROOT / "assets/icons/lucide" / f"{name}.svg"]
    svg = next((c for c in cand if c.suffix == ".svg" and c.exists()), None)
    if not svg:
        print(f"아이콘 없음: {name} → python tools/icon.py find ... 또는 python tools/gpt.py icon ...")
        return 0
    cache = ROOT / "output" / f"ir-{SPEC['name']}" / "_icons"
    png = cache / f"{svg.stem}-{col[1:]}.png"
    if not png.exists():
        sys.path.insert(0, str(ROOT / "tools"))
        import icon as _icon
        _icon.render(str(svg), col, str(png), 256)
    slide.shapes.add_picture(str(png), int(x), int(y), size, size)
    return size


def light_image(path, max_px=2400):
    """큰 사진은 2400px JPEG로 줄인 사본을 써서 PPT 용량을 낮춘다 (투명 PNG는 PNG 유지)."""
    from PIL import Image
    path = Path(path)
    im = Image.open(path)
    if max(im.size) <= max_px and path.stat().st_size < 1_500_000:
        return path
    cache = ROOT / "output" / f"ir-{SPEC['name']}" / "_img"
    cache.mkdir(parents=True, exist_ok=True)
    alpha = im.mode in ("RGBA", "LA") and im.getextrema()[-1][0] < 255
    out = cache / (path.stem + (".png" if alpha else ".jpg"))
    if not out.exists():
        im.thumbnail((max_px, max_px))
        if alpha:
            im.save(out, optimize=True)
        else:
            im.convert("RGB").save(out, quality=88, optimize=True)
    return out


def fill_crop(pic, path, w, h, focus=(0.5, 0.5)):
    """상자 비율에 맞춰 잘라서 채운다 (늘이지 않음). focus=(가로, 세로) 0~1, 남길 중심."""
    from PIL import Image
    iw, ih = Image.open(path).size
    box, img = w / h, iw / ih
    fx, fy = focus
    if img > box:            # 사진이 더 넓음 → 좌우를 자름
        cut = 1 - box / img
        l = cut * fx
        pic.crop_left, pic.crop_right = l, cut - l
    elif img < box:          # 사진이 더 높음 → 위아래를 자름
        cut = 1 - img / box
        t = cut * fy
        pic.crop_top, pic.crop_bottom = t, cut - t


def picture(slide, path, x, y, w, h, kind=None, name=None, focus=(0.5, 0.5)):
    """이미지 스타일(직각·둥근·원형) 적용. 파일이 없으면 같은 모양의 자리표시."""
    kind = kind or STY["image"]
    rad = CH["image"]["options"][kind]["radius"]
    x, y, w, h = (int(v) for v in (x, y, w, h))
    p = ROOT / path if path else None
    if p and p.exists():
        p = light_image(p)
        pic = slide.shapes.add_picture(str(p), x, y, w, h)
        fill_crop(pic, p, w, h, focus)
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


def two_tone(slide, x, y, w, h, title, size, color=None, align=PP_ALIGN.LEFT):
    """제목을 '|'로 나눠 앞은 진하게, 뒤는 회색으로 (예: '오우이 드라이어의 | 제품 & 기술 경쟁력')."""
    parts = [t for t in str(title).split("|")]
    x, y, w, h = (int(v) for v in (x, y, w, h))
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p_ = tf.paragraphs[0]
    p_.alignment = align
    for i, part in enumerate(parts):
        r = p_.add_run()
        r.text = part.strip(" ") if len(parts) == 1 else (part.rstrip(" ") + " " if i == 0 else part.strip(" "))
        style_run(r, size, "title", (color or INK) if i == 0 else MUTED)
    return tb


def image_grid(slide, images, x, y, w, h, gap=None, focus=(0.5, 0.45)):
    """이미지 여러 장을 상자 안에 격자로 (캡션 선택). images: [{image, caption, sub}] 또는 경로 문자열."""
    imgs = [i if isinstance(i, dict) else {"image": i} for i in images]
    n = len(imgs)
    if not n:
        return
    gap = gap or SP["s"]
    cols = {1: 1, 2: 2, 3: 3, 4: 2, 5: 3, 6: 3}.get(n, 4)
    rows = (n + cols - 1) // cols
    cap = any(i.get("caption") for i in imgs)
    cap_h = (Inches(0.28) + (Inches(0.24) if any(i.get("sub") for i in imgs) else 0)) if cap else 0
    cw = (w - gap * (cols - 1)) / cols
    rh = (h - gap * (rows - 1)) / rows
    for k, it in enumerate(imgs):
        cx = x + (k % cols) * (cw + gap)
        cy = y + (k // cols) * (rh + gap)
        picture(slide, it.get("image"), cx, cy, cw, rh - cap_h, focus=tuple(it.get("focus", focus)))
        if it.get("caption"):
            text(slide, cx, cy + rh - cap_h + Inches(0.04), cw, Inches(0.26), it["caption"], SIZE["small"], "head", INK,
                 PP_ALIGN.CENTER)
        if it.get("sub"):
            text(slide, cx, cy + rh - Inches(0.24), cw, Inches(0.24), it["sub"], role="caption", color=MUTED,
                 align=PP_ALIGN.CENTER)


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
            text(slide, X0 + Inches(0.2), Y0, Inches(6), Inches(0.28), sec, role="caption", color=ACCENT, bold=True)
        logo_mark(slide, Y0)
        text(slide, X0, Y0 + Inches(0.48), CW, Inches(0.7), d["title"], T, "title")
        if msg:
            text(slide, X0, Y0 + Inches(1.15), CW, Inches(0.45), msg, S, "body", INK_SOFT)
        divider(slide, X0, TOP - SP["s"], CW)
    elif kind == "H":     # 로고 + 탭 메뉴(현재 섹션 강조·밑줄) + 영문 섹션 표기 + 두 가지 색 제목
        logo = SPEC.get("logo")
        if logo and (ROOT / logo).exists():
            pic = slide.shapes.add_picture(str(ROOT / logo), int(X0), int(Y0 + Inches(0.05)), height=int(Inches(0.24)))
        else:
            text(slide, X0, Y0, Inches(3), Inches(0.3), SPEC.get("company", ""), SIZE["body"], "head", INK)
        tabs = SPEC.get("nav", [])
        cur = d.get("nav")
        tab_w = Inches(0.95)
        bar_y = Y0 + Inches(0.42)
        for i, t in enumerate(tabs):
            tx = X1 - tab_w * (len(tabs) - i)
            on = t == cur
            text(slide, tx, Y0 + Inches(0.02), tab_w, Inches(0.3), t, role="caption", color=ACCENT if on else MUTED,
                 align=PP_ALIGN.CENTER, bold=on)
            if on:
                seg(slide, tx + Inches(0.12), bar_y, tx + tab_w - Inches(0.12), bar_y, ACCENT, "bold")
        seg(slide, X0, bar_y + Inches(0.02), X1, bar_y + Inches(0.02), LINE_SOFT, "hair")
        if d.get("kicker") or sec:
            text(slide, X0, Y0 + Inches(0.66), CW, Inches(0.28), d.get("kicker") or sec, role="caption", color=ACCENT, bold=True)
        two_tone(slide, X0, Y0 + Inches(0.95), CW, Inches(0.6), d["title"], T)
        if msg:
            text(slide, X0, Y0 + Inches(1.5), CW, Inches(0.35), msg, SIZE["body"], "body", INK_SOFT)
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
def card(slide, x, y, w, h, head, body, i=0, label=None, icon=None, images=None):
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
        off = icon_img(slide, icon, tx, y + hh + pad)
        off = off + SP["s"] if off else 0
        text(slide, tx, y + hh + pad + off, tw, h - hh - 2 * pad - off, bl, role="body", color=INK_SOFT, bullets=len(bl) > 1)
        return
    if kind == "D":       # 알약 라벨(Phase형)
        lab = label or head
        if icon:
            icon_img(slide, icon, x + (w - ICON_SIZE) / 2, y)
            y, h = y + ICON_SIZE + SP["s"], h - ICON_SIZE - SP["s"]
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
    if kind == "G":       # 1차시안: 두꺼운 테두리 직각 상자 + Point 알약 + 제목 + 글머리 + 점선 + 이미지
        shape(slide, MSO_SHAPE.RECTANGLE, x, y, w, h, fill=WHITE, line=INK, lw="bold")
        py = y + pad
        if label:
            pw = Inches(0.35) + Inches(0.085) * len(label)
            shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, tx, py, pw, Inches(0.27), fill=ACCENT, radius=0.5)
            text(slide, tx, py, pw, Inches(0.27), label, role="caption", color=WHITE, align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE, bold=True)
            py += Inches(0.27) + SP["xs"]
        off = icon_img(slide, icon, tx, py) if icon else 0
        hx = tx + (off + SP["s"] if off else 0)
        text(slide, hx, py, tw - (hx - tx), Inches(0.42), head, SIZE["body"] + 4, "head", INK)
        py += Inches(0.42)
        n_lines = len(bl) if bl else 0
        body_h = Inches(0.27) * max(n_lines, 1) + SP["xs"] if bl else 0
        if bl:
            text(slide, tx, py, tw, body_h, bl, SIZE["small"] + 1, "body", INK_SOFT, bullets=len(bl) > 1)
            py += body_h
        if images:
            py += SP["s"]
            seg(slide, tx, py, tx + tw, py, LINE, "regular", MSO_LINE.DASH)
            py += SP["m"]
            image_grid(slide, images, tx, py, tw, y + h - pad - py)
        return
    if kind == "F":       # 에디토리얼: 박스 없음, 위쪽 굵은 선 + 제목 + 본문
        seg(slide, x, y, x + w, y, INK if i == 0 else LINE, "bold" if i == 0 else "regular")
        off = icon_img(slide, icon, x, y + SP["m"]) if icon else 0
        hy = y + SP["m"] + (off + SP["s"] if off else 0)
        if label:
            text(slide, x, hy, w, Inches(0.3), label, role="caption", color=MUTED, bold=True)
            hy += Inches(0.3) + SP["xs"]
        text(slide, x, hy, w, Inches(0.5), head, SIZE["body"] + 3, "head", INK)
        text(slide, x, hy + Inches(0.5) + SP["s"], w, y + h - hy - Inches(0.5) - SP["s"], bl, role="body",
             color=INK_SOFT, bullets=len(bl) > 1)
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
    off = icon_img(slide, icon, tx, y + pad, color=(WHITE if kind == "E" else None))
    off = off + SP["s"] if off else 0
    text(slide, tx, y + pad + off, tw, Inches(0.5), head, SIZE["body"] + 2, "head", hc)
    text(slide, tx, y + pad + off + Inches(0.5) + SP["xs"], tw, h - off - Inches(0.5) - 2 * pad - SP["xs"], bl,
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
    elif kind == "F":     # 기본: 선 + 열린 화살촉(→), 둥근 선 끝 (사용자 지정)
        m = Inches(0.08)
        c = seg(slide, x_from + m, y, x_to - m, y, ACCENT, "bold", None, "arrow")
        ln = c.line._get_or_add_ln()
        ln.set("cap", "rnd")
        te = ln.find(qn("a:tailEnd"))
        te.set("w", "lg")      # 참고 이미지처럼 큰 열린 화살촉
        te.set("len", "lg")
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
        card(slide, x, top, cw, bottom - top, it.get("head", ""), it.get("body", ""), i, it.get("label"), it.get("icon"),
             it.get("images"))
        if connectors and i < n - 1:
            cy = top + SP["m"] + Inches(0.55) if STY["card"] == "F" else (top + Inches(0.6) if STY["card"] == "G" else top + (bottom - top) / 2)
            connector(slide, x + cw, x + cw + gap, cy)


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
    elif kind == "F":     # 풀이미지 배경 + 글 (밝은 사진이면 검정 글씨, 어두우면 흰 글씨)
        from PIL import Image, ImageStat
        dark_txt = True
        if img and (ROOT / img).exists():
            li = light_image(ROOT / img)
            pic = slide.shapes.add_picture(str(li), 0, 0, int(W), int(H))
            fill_crop(pic, li, W, H, tuple(d.get("focus", (0.5, 0.5))))
            pic.name = "bleed:cover-image"
            im = Image.open(li).convert("L")
            side = d.get("side", "left")
            area = im.crop((0, 0, im.width // 2, im.height)) if side == "left" else im.crop((im.width // 2, 0, im.width, im.height))
            dark_txt = ImageStat.Stat(area).mean[0] > 140
        else:
            bg(slide, SURFACE)
        col = INK if dark_txt else WHITE
        sub = INK_SOFT if dark_txt else rgb(C["neutral"]["100"])
        tw = CW * 0.5
        tx = X0 if d.get("side", "left") == "left" else X1 - tw
        lines = big.splitlines() or [big]
        th = Pt(54 * 1.08 * len(lines))
        ty = int(H / 2 - th / 2 - Inches(0.4))
        text(slide, tx, ty, tw, th, lines if len(lines) > 1 else big, 54, "display", col)
        text(slide, tx, ty + th + SP["m"], tw * 0.9, Inches(1.0), tag, SIZE["subtitle"] + 2, "body", sub)
        text(slide, tx, FOOT_Y, tw, FOOT_H, meta, role="caption", color=sub)
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


def plot_layout(chart, x=0.02, y=0.2, w=0.96, h=0.7):
    """차트 안쪽(막대 영역)을 고정 위치로 — 막대 위 주석·선을 정확히 얹기 위해."""
    pa = chart._chartSpace.chart.plotArea
    lay = pa.find(qn("c:layout"))
    if lay is None:
        lay = pa.makeelement(qn("c:layout"), {})
        pa.insert(0, lay)
    for c in list(lay):
        lay.remove(c)
    ml = lay.makeelement(qn("c:manualLayout"), {})
    for tag, val in (("layoutTarget", "inner"), ("xMode", "edge"), ("yMode", "edge"),
                     ("x", x), ("y", y), ("w", w), ("h", h)):
        el = ml.makeelement(qn(f"c:{tag}"), {"val": str(val)})
        ml.append(el)
    lay.append(ml)
    return x, y, w, h


def chart_extras(slide, c, rows, cats, vals, fx, fy, fw, fh, lay, vmax):
    """막대 차트 위 장식: 실적/전망 구분선, 마일스톤 주석+작은 화살표, 비율 선(점+%)."""
    lx, ly, lw, lh = lay
    px, py, pw, ph = fx + fw * lx, fy + fh * ly, fw * lw, fh * lh
    n = len(cats)
    cx = lambda i: px + pw * (i + 0.5) / n
    top = lambda v: py + ph * (1 - v / vmax)
    # 실적 / 전망 구분
    if c.get("split") in cats:
        k = cats.index(c["split"])
        xs = px + pw * k / n
        seg(slide, xs, py - Inches(0.05), xs, py + ph, LINE, "hair", MSO_LINE.DASH)
        text(slide, xs - Inches(1.2), py - Inches(0.05), Inches(1.1), Inches(0.28), c.get("split_labels", ["실적", "전망"])[0],
             role="caption", color=MUTED, align=PP_ALIGN.RIGHT)
        text(slide, xs + Inches(0.1), py - Inches(0.05), Inches(1.1), Inches(0.28), c.get("split_labels", ["실적", "전망"])[1],
             role="caption", color=MUTED)
    # 마일스톤 주석 (막대 값 라벨 위)
    for cat, note in (c.get("notes") or {}).items():
        if cat not in cats:
            continue
        i = cats.index(cat)
        bw = pw / n * 1.6
        ty = top(vals[i]) - Inches(0.32) - Inches(0.62)
        ty = max(ty, fy)
        lines = note if isinstance(note, list) else [note]
        nx = min(max(cx(i) - bw / 2, X0), X1 - bw)          # 여백 안으로
        text(slide, nx, ty, bw, Inches(0.55), lines, SIZE["small"], "head", INK if i < n - 1 else ACCENT,
             PP_ALIGN.CENTER, MSO_ANCHOR.BOTTOM)
    # 비율 선 (예: 마진 %): 막대 위쪽 띠에 점과 값
    ln = c.get("line")
    if ln:
        lv = [float(str(r.get(ln["col"], "")).replace("%", "") or "nan") for r in rows]
        ok = [(i, v) for i, v in enumerate(lv) if v == v]
        if len(ok) > 1:
            lo, hi = min(v for _, v in ok), max(v for _, v in ok)
            band_top, band_h = fy + Inches(0.05), fh * ly * 0.55
            yv = lambda v: band_top + band_h * (1 - (v - lo) / ((hi - lo) or 1))
            for (i1, v1), (i2, v2) in zip(ok, ok[1:]):
                seg(slide, cx(i1), yv(v1), cx(i2), yv(v2), ACCENT, "regular")
            for i, v in ok:
                d = Inches(0.09)
                shape(slide, MSO_SHAPE.OVAL, cx(i) - d / 2, yv(v) - d / 2, d, d, fill=WHITE, line=ACCENT, lw="regular")
                text(slide, cx(i) - Inches(0.5), yv(v) - Inches(0.32), Inches(1.0), Inches(0.26), f"{v:g}{ln.get('unit', '%')}",
                     role="caption", color=ACCENT, align=PP_ALIGN.CENTER, bold=True)
            text(slide, fx, band_top - Inches(0.02), Inches(2.4), Inches(0.26), ln.get("label", ln["col"]), role="caption", color=ACCENT)


def s_chart(slide, d, idx):
    header(slide, d, idx)
    end = summary_bar(slide, d)
    c = d["chart"]
    rows = read_csv(c["data"])
    cats = [r[c["x"]] for r in rows]
    cd = CategoryChartData()
    cd.categories = cats
    for ycol in c["y"]:
        cd.add_series(c.get("labels", {}).get(ycol, ycol), [num(r[ycol]) for r in rows])
    kind = {"bar": XL_CHART_TYPE.COLUMN_CLUSTERED, "stacked": XL_CHART_TYPE.COLUMN_STACKED,
            "line": XL_CHART_TYPE.LINE_MARKERS, "hbar": XL_CHART_TYPE.BAR_CLUSTERED}[c.get("kind", "bar")]
    top = TOP
    # 헤드라인 숫자: CAGR (데이터에서 계산) — "매출 CAGR (2025–2029E) 157%"
    if c.get("cagr") and len(c["y"]) == 1:
        a_, b_ = c["cagr"]
        va_, vb_ = num(rows[cats.index(a_)][c["y"][0]]), num(rows[cats.index(b_)][c["y"][0]])
        yrs = cats.index(b_) - cats.index(a_)
        cg = ((vb_ / va_) ** (1 / yrs) - 1) * 100
        text(slide, X0, top, Inches(5), Inches(0.3), f"{c.get('labels', {}).get(c['y'][0], c['y'][0])} CAGR ({a_}–{b_})",
             role="body", color=INK_SOFT)
        num_text(slide, X0, top + Inches(0.3), Inches(4), Inches(0.75), f"{cg:,.0f}", "%", 40, ACCENT)
        top += Inches(1.15)
    elif c.get("unit"):
        top += Inches(0.35)
    if c.get("unit"):
        text(slide, X1 - Inches(3), TOP, Inches(3), Inches(0.28), f"단위: {c['unit']}", role="caption", color=MUTED,
             align=PP_ALIGN.RIGHT)
    fx, fy, fw, fh = X0, top, CW, end - top
    gf = slide.shapes.add_chart(kind, int(fx), int(fy), int(fw), int(fh), cd)
    ch = gf.chart
    small = Pt(max(SIZE["small"], MIN["body"]))
    ch.font.name, ch.font.size, ch.font.color.rgb = face("body")[0], small, INK_SOFT
    ch.has_title = False
    ch.has_legend = len(c["y"]) > 1
    if ch.has_legend:
        ch.legend.position, ch.legend.include_in_layout = XL_LEGEND_POSITION.TOP, False
    vals = [num(r[c["y"][0]]) for r in rows]
    simple = kind == XL_CHART_TYPE.COLUMN_CLUSTERED and len(c["y"]) == 1
    vmax = max(vals) * (1.0 if not (c.get("notes") or c.get("line")) else 1.0)
    va = ch.value_axis
    va.has_major_gridlines = False
    va.visible = False
    if simple:
        va.minimum_scale, va.maximum_scale = 0, vmax
    ca = ch.category_axis
    ca.format.line.color.rgb, ca.format.line.width = LINE, LW["hair"]
    ca.has_major_gridlines = False
    if kind == XL_CHART_TYPE.BAR_CLUSTERED:
        ca.reverse_order = True
    plot = ch.plots[0]
    plot.has_data_labels = True
    dl = plot.data_labels
    has_dec = any("." in str(r[y]) and not str(r[y]).endswith(".0") for r in rows for y in c["y"])
    dl.number_format, dl.number_format_is_linked = ("#,##0.0" if has_dec else "#,##0"), False
    dl.font.size, dl.font.bold, dl.font.color.rgb = small, True, INK
    if kind != XL_CHART_TYPE.LINE_MARKERS:
        dl.position = XL_LABEL_POSITION.CENTER if kind == XL_CHART_TYPE.COLUMN_STACKED else XL_LABEL_POSITION.OUTSIDE_END
        plot.gap_width = c.get("gap", 90)
    hi = c.get("highlight")
    split_i = cats.index(c["split"]) if c.get("split") in cats else None
    for si, series in enumerate(plot.series):
        if kind == XL_CHART_TYPE.LINE_MARKERS:
            series.format.line.color.rgb = SERIES[si % len(SERIES)] if len(c["y"]) > 1 else ACCENT
            series.format.line.width = LW["bold"]
            series.smooth = False
            continue
        base = SERIES[si % len(SERIES)] if len(c["y"]) > 1 else (mix(C["neutral"]["500"], "#FFFFFF", 0.15) if hi else ACCENT)
        series.format.fill.solid()
        series.format.fill.fore_color.rgb = base
        if len(c["y"]) == 1:
            for pi, cat in enumerate(cats):
                pt = series.points[pi]
                pt.format.fill.solid()
                if hi and str(cat) == str(hi):
                    pt.format.fill.fore_color.rgb = ACCENT
                elif split_i is not None and pi >= split_i:
                    pt.format.fill.fore_color.rgb = LINE          # 전망은 연하게
                else:
                    pt.format.fill.fore_color.rgb = mix(C["neutral"]["700"], "#FFFFFF", 0.35)
    if simple:
        extra = c.get("notes") or c.get("line")
        head_room = min(0.45, (Inches(1.05) / fh)) if extra else 0.1    # 값 라벨 + 주석 두 줄이 들어갈 높이
        lay = plot_layout(ch, 0.02, head_room, 0.96, 0.9 - head_room)
        chart_extras(slide, c, rows, cats, vals, fx, fy, fw, fh, lay, vmax)
    src = d.get("source") or "; ".join(sorted({cite(r) for r in rows if cite(r)}))
    footer(slide, idx, src or None)


def s_metrics(slide, d, idx):
    header(slide, d, idx)
    end = summary_bar(slide, d)
    items = [resolve(i["value_ref"]) | {"label_override": i.get("label")} for i in d["items"]][:4]
    n, gap = len(items), SP["l"]
    cw = (CW - gap * (n - 1)) / n
    h = min(end - TOP, Inches(3.0))
    if d.get("strip"):        # 아래쪽 이미지 띠: 남는 여백을 사진으로
        h = min(h, Inches(2.25))
        sy = TOP + h + SP["l"]
        image_grid(slide, d["strip"], X0, sy, CW, end - sy, focus=(0.5, 0.3)) if len(d["strip"]) <= 6 else None
        if len(d["strip"]) > 6:
            k = len(d["strip"]); sw = (CW - SP["s"] * (k - 1)) / k
            for j, im in enumerate(d["strip"]):
                picture(slide, im if isinstance(im, str) else im["image"], X0 + j * (sw + SP["s"]), sy, sw, end - sy, focus=(0.5, 0.3))
    kind = STY["card"]
    rad = CH["card"]["options"][kind]["radius"]
    dark = kind == "E"
    srcs = set()
    for i, r in enumerate(items):
        x = X0 + i * (cw + gap)
        if kind in ("B", "C"):
            shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, TOP, cw, h, fill=WHITE, line=LINE, lw="regular", radius=min(rad, 0.08))
        elif kind == "F":
            seg(slide, x, TOP, x + cw, TOP, INK if i == 0 else LINE, "bold" if i == 0 else "regular")
        elif kind == "G":
            shape(slide, MSO_SHAPE.RECTANGLE, x, TOP, cw, h, fill=WHITE, line=INK, lw="bold")
        elif kind != "D":
            shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, TOP, cw, h, fill=DARK if dark else SURFACE, radius=rad)
        pad = 0 if kind == "F" else SP["m"]
        if r.get("_label_pill"):
            pass
        num_text(slide, x + pad, TOP + SP["m"], cw - 2 * pad, Inches(1.0), fmt(r["value"]),
                 r.get("unit", ""), 48 if n <= 3 else 36, WHITE if dark else (ACCENT if i == 0 else INK))
        divider(slide, x + pad, TOP + SP["m"] + Inches(1.05), cw - 2 * pad)
        text(slide, x + pad, TOP + SP["m"] + Inches(1.2), cw - 2 * pad, Inches(0.8),
             r["label_override"] or r.get("label", r["key"]), role="body", color=PALE if dark else INK_SOFT)
        if r.get("as_of"):
            text(slide, x + pad, TOP + SP["m"] + Inches(1.6), cw - 2 * pad, Inches(0.25), f"기준 {r['as_of']}",
                 role="caption", color=MUTED)
        if cite(r):
            srcs.add(cite(r))
    footer(slide, idx, d.get("source") or "; ".join(sorted(srcs)) or None)


NUMERIC = __import__("re").compile(r"^[~+\-약 ]*[\d,.]+\s*(%|억원|억|만원|만 대|만|대|원|x|배)?$")


def table_editorial(slide, rows, cols, labels, hi, top, end):
    """박스 없는 표: 굵은 위 선 + 가는 행 구분선, 숫자 열은 오른쪽 정렬, 강조 행은 연한 띠 + 굵게."""
    n_r = len(rows) + 1
    row_h = min(Inches(1.0), (end - top) / n_r)      # 행이 적으면 늘려서 아래 빈 공간을 줄임
    first_w = CW * (0.22 if len(cols) > 3 else 0.3)
    rest = (CW - first_w) / max(len(cols) - 1, 1)
    is_num = [all(NUMERIC.match(str(r[c]).strip() or "0") for r in rows) for c in cols]
    seg(slide, X0, top, X1, top, INK, "bold")
    for i in range(n_r):
        y = top + row_h * i
        hl = i > 0 and hi and rows[i - 1][cols[0]] == hi
        if hl:
            rect(slide, X0, y + Inches(0.03), CW, row_h - Inches(0.06), ACCENT_SOFT)
        for j, col in enumerate(cols):
            x = X0 if j == 0 else X0 + first_w + rest * (j - 1)
            w = first_w if j == 0 else rest
            val = labels.get(col, col) if i == 0 else rows[i - 1][col]
            al = PP_ALIGN.RIGHT if (j > 0 and is_num[j]) else PP_ALIGN.LEFT
            pad = SP["s"]
            if i == 0:
                text(slide, x + pad, y, w - 2 * pad, row_h, val, SIZE["small"], "head", MUTED, al, MSO_ANCHOR.MIDDLE)
            else:
                role = "head" if (hl or j == 0) else "body"
                text(slide, x + pad, y, w - 2 * pad, row_h, val, SIZE["small"], role, ACCENT if hl and j == 0 else INK,
                     al, MSO_ANCHOR.MIDDLE)
        if 0 < i < n_r - 1:
            seg(slide, X0, y + row_h, X1, y + row_h, LINE_SOFT, "hair")
        elif i == 0:
            seg(slide, X0, y + row_h, X1, y + row_h, LINE, "hair")
    seg(slide, X0, top + row_h * n_r, X1, top + row_h * n_r, LINE, "hair")


def s_table(slide, d, idx):
    header(slide, d, idx)
    end = summary_bar(slide, d)
    rows = read_csv(d["table"]["data"])
    cols = d["table"].get("columns") or [k for k in rows[0] if k != "source"]
    hi = d["table"].get("highlight_row")
    top_ = TOP
    if d.get("banner"):
        bh = Inches(0.75)
        picture(slide, d["banner"], X0, TOP, CW, bh, focus=(0.5, 0.5))
        if d.get("banner_label"):
            text(slide, X0 + SP["m"], TOP, Inches(5), bh, d["banner_label"], SIZE["subtitle"] + 2, "head", WHITE,
                 anchor=MSO_ANCHOR.MIDDLE)
        top_ = TOP + bh + SP["m"]
    if STY["card"] in ("F", "G"):
        table_editorial(slide, rows, cols, d["table"].get("labels", {}), hi, top_, end)
        srcs = sorted({cite(r) for r in rows if cite(r)})
        footer(slide, idx, d.get("source") or "; ".join(srcs) or None)
        return
    if STY["card"] == "F":
        table_editorial(slide, rows, cols, d["table"].get("labels", {}), hi, TOP, end)
        srcs = sorted({cite(r) for r in rows if cite(r)})
        footer(slide, idx, d.get("source") or "; ".join(srcs) or None)
        return
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
    srcs = sorted({cite(r) for r in rows if cite(r)})
    footer(slide, idx, d.get("source") or "; ".join(srcs) or None)


def s_team(slide, d, idx):
    header(slide, d, idx)
    people = d["people"][:6]
    has_photo = any(p.get("photo") for p in people)
    per_row = (len(people) if len(people) <= 5 else 3) if STY["card"] == "G" else (4 if len(people) <= 4 else 3)
    rows = (len(people) + per_row - 1) // per_row
    gap = SP["l"]
    cw = (CW - gap * (per_row - 1)) / per_row
    rh = (BOTTOM - TOP - SP["l"] * (rows - 1)) / rows
    ph = Inches(1.3) if has_photo else 0
    for i, p in enumerate(people):
        x = X0 + (i % per_row) * (cw + gap)
        y0 = TOP + (i // per_row) * (rh + SP["l"])
        if has_photo:
            picture(slide, p.get("photo"), x, y0, ph, ph)
        y = y0 + (ph + SP["s"] if has_photo else 0)
        if STY["card"] == "G":
            shape(slide, MSO_SHAPE.RECTANGLE, x, y0, cw, rh, fill=WHITE, line=INK, lw="bold")
            x, cw_ = x + SP["m"], cw - 2 * SP["m"]
            y += SP["m"]
        else:
            seg(slide, x, y, x + cw, y, INK if i == 0 else LINE, "bold" if i == 0 else "regular")
            cw_ = cw
            y += SP["s"]
        text(slide, x, y, cw_, Inches(0.4), p["name"], SIZE["body"] + 3, "head")
        text(slide, x, y + Inches(0.4), cw_, Inches(0.3), p["role"], role="caption", color=ACCENT, bold=True)
        bio = p.get("bio", "")
        by = y + Inches(0.4) + Inches(0.3) + SP["s"]
        text(slide, x, by, cw_, y0 + rh - by - SP["s"], bio, SIZE["small"], "body", INK_SOFT,
             bullets=isinstance(bio, list) and len(bio) > 1)
    footer(slide, idx)


def s_ask(slide, d, idx):
    bg(slide, DARK)
    r = resolve(d["amount_ref"])
    text(slide, X0, Y0, CW, Inches(0.7), d["title"], SIZE["title"], "title", WHITE)
    num_text(slide, X0, Y0 + Inches(0.9), CW, Inches(1.4), fmt(r["value"]), r.get("unit", ""), 80, WHITE)
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


def s_timeline(slide, d, idx):
    """로드맵·연혁: items [{when, head, body, icon}], current(강조할 순번, 0부터)."""
    header(slide, d, idx)
    end = summary_bar(slide, d)
    items = d["items"][:6]
    n = len(items)
    cur = d.get("current", -1)
    y_line = TOP + Inches(0.9)
    seg(slide, X0, y_line, X1, y_line, LINE, "regular")
    colw = CW / n
    for i, it in enumerate(items):
        cx = X0 + colw * i + colw / 2
        r = Inches(0.11) if i != cur else Inches(0.15)
        done = cur < 0 or i <= cur
        shape(slide, MSO_SHAPE.OVAL, cx - r, y_line - r, 2 * r, 2 * r, fill=ACCENT if done else WHITE,
              line=ACCENT, lw="regular")
        text(slide, cx - colw / 2, TOP, colw, Inches(0.45), it["when"], SIZE["body"] + 2, "head",
             ACCENT if i == cur else INK, PP_ALIGN.CENTER)
        x = cx - colw / 2 + SP["xs"]
        w = colw - 2 * SP["xs"]
        off = icon_img(slide, it.get("icon"), cx - ICON_SIZE / 2, y_line + SP["m"]) if it.get("icon") else 0
        ty = y_line + SP["m"] + (off + SP["s"] if off else 0)
        text(slide, x, ty, w, Inches(0.45), it.get("head", ""), SIZE["body"], "head", INK, PP_ALIGN.CENTER)
        body = it.get("body", "")
        text(slide, x, ty + Inches(0.45), w, end - ty - Inches(0.45), body, role="body", color=INK_SOFT,
             align=PP_ALIGN.LEFT if isinstance(body, list) else PP_ALIGN.CENTER,
             bullets=isinstance(body, list) and len(body) > 1)
    footer(slide, idx, d.get("source"))


def s_tam(slide, d, idx):
    """TAM/SAM/SOM 겹친 원: data CSV (segment,size[,label,source]), unit."""
    header(slide, d, idx)
    end = summary_bar(slide, d)
    rows = read_csv(d["data"])[:3]
    avail = end - TOP
    big = min(avail, CW * 0.48)
    cx0 = X0 + big / 2
    bottom_y = TOP + big
    fills = [ACCENT_SOFT, mix(BR["primary"], "#FFFFFF", 0.6), ACCENT]
    for i, r in enumerate(rows):
        dia = big * (1, 0.68, 0.38)[i]
        shape(slide, MSO_SHAPE.OVAL, cx0 - dia / 2, bottom_y - dia, dia, dia, fill=fills[i])
        lab_y = bottom_y - dia + (Inches(0.12) if i < 2 else dia / 2 - Inches(0.2))
        text(slide, cx0 - dia / 2, lab_y, dia, Inches(0.35), r["segment"], SIZE["small"], "head",
             WHITE if i == 2 else INK, PP_ALIGN.CENTER)
    tx = X0 + big + SP["xl"]
    tw = X1 - tx
    unit = d.get("unit", "")
    ty = TOP + Inches(0.2)
    rowh = (avail - Inches(0.4)) / max(len(rows), 1)
    for i, r in enumerate(rows):
        y = ty + rowh * i
        text(slide, tx, y, tw, Inches(0.35), r.get("label") or r["segment"], role="body", color=INK_SOFT)
        num_text(slide, tx, y + Inches(0.35), tw, Inches(0.7), fmt(r["size"]), unit, 34,
                 ACCENT if i == len(rows) - 1 else INK)
        if i < len(rows) - 1:
            divider(slide, tx, y + rowh - SP["s"], tw)
    srcs = sorted({cite(r) for r in rows if cite(r)})
    footer(slide, idx, d.get("source") or "; ".join(srcs) or None)


def s_compare(slide, d, idx):
    """O/△/X 비교표: data CSV(첫 열=비교 대상), highlight_row(우리 회사). 셀 값 O·△·X는 기호로 그린다."""
    header(slide, d, idx)
    end = summary_bar(slide, d)
    rows = read_csv(d["data"])
    cols = d.get("columns") or [k for k in rows[0] if k != "source"]
    hi = d.get("highlight_row")
    n_r, n_c = len(rows) + 1, len(cols)
    row_h = min(Inches(0.62), (end - TOP) / n_r)
    first_w = CW * 0.26
    cw = (CW - first_w) / (n_c - 1)
    for i in range(n_r):
        y = TOP + row_h * i
        is_hi = i > 0 and rows[i - 1][cols[0]] == hi
        if is_hi:
            shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, X0, y + Inches(0.04), CW, row_h - Inches(0.08),
                  fill=ACCENT_SOFT, radius=0.2)
        for j, col in enumerate(cols):
            x = X0 if j == 0 else X0 + first_w + cw * (j - 1)
            w = first_w if j == 0 else cw
            if i == 0:
                text(slide, x, y, w, row_h, col if j else "", SIZE["small"], "head", INK_SOFT,
                     PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
                continue
            v = rows[i - 1][col].strip()
            if j == 0:
                text(slide, x + SP["s"], y, w - SP["s"], row_h, v, SIZE["body"], "head", ACCENT if is_hi else INK,
                     anchor=MSO_ANCHOR.MIDDLE)
                continue
            mark = {"O": "○", "o": "○", "△": "△", "X": "✕", "x": "✕"}.get(v)
            c_ = ACCENT if (mark == "○" and is_hi) else (INK if mark == "○" else (MUTED if mark else INK_SOFT))
            text(slide, x, y, w, row_h, mark or v, SIZE["body"] + (4 if mark else 0), "head" if mark else "body",
                 c_, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
        if i < n_r - 1:
            divider(slide, X0, y + row_h, CW)
    srcs = sorted({cite(r) for r in rows if cite(r)})
    footer(slide, idx, d.get("source") or "; ".join(srcs) or None)


def s_product(slide, d, idx):
    """제품 화면 + 설명: image(왼쪽), points [{icon, head, body}](오른쪽)."""
    header(slide, d, idx)
    end = summary_bar(slide, d)
    img_w = CW * 0.42
    picture(slide, d.get("image"), X0, TOP, img_w, end - TOP)
    tx = X0 + img_w + SP["xl"]
    tw = X1 - tx
    pts = d.get("points", [])[:4]
    rowh = (end - TOP) / max(len(pts), 1)
    for i, pt in enumerate(pts):
        y = TOP + rowh * i
        off = icon_img(slide, pt.get("icon"), tx, y) if pt.get("icon") else 0
        x2 = tx + (off + SP["m"] if off else 0)
        text(slide, x2, y, tw - (x2 - tx), Inches(0.42), pt.get("head", ""), SIZE["body"] + 2, "head")
        body = pt.get("body", "")
        text(slide, x2, y + Inches(0.42), tw - (x2 - tx), rowh - Inches(0.42) - SP["s"], body,
             role="body", color=INK_SOFT, bullets=isinstance(body, list) and len(body) > 1)
        if i < len(pts) - 1:
            divider(slide, tx, y + rowh - SP["s"], tw)
    footer(slide, idx, d.get("source"))


def s_structure(slide, d, idx):
    """서비스 구조도: left[{icon, head, body}] → center{icon, head, body} → right[...], 연결은 선택한 화살표 스타일."""
    header(slide, d, idx)
    end = summary_bar(slide, d)
    gap = SP["xl"]
    colw = (CW - 2 * gap) / 3
    left, right, center = d.get("left", [])[:4], d.get("right", [])[:4], d.get("center", {})
    avail = end - TOP
    cy = TOP + avail / 2

    def column(items, x):
        n = max(len(items), 1)
        h = (avail - SP["s"] * (n - 1)) / n
        mids = []
        for i, it in enumerate(items):
            y = TOP + i * (h + SP["s"])
            shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, colw, h, fill=WHITE, line=LINE, lw="regular", radius=0.08)
            off = icon_img(slide, it.get("icon"), x + SP["m"], y + (h - ICON_SIZE) / 2) if it.get("icon") else 0
            tx = x + SP["m"] + (off + SP["s"] if off else 0)
            lines = [it.get("head", "")] + ([it["body"]] if it.get("body") else [])
            text(slide, tx, y, colw - (tx - x) - SP["s"], h, lines, SIZE["small"], "head", INK, anchor=MSO_ANCHOR.MIDDLE)
            mids.append(y + h / 2)
        return mids

    lm = column(left, X0)
    rx = X0 + 2 * (colw + gap)
    rm_ = column(right, rx)
    ch = min(avail, Inches(2.6))
    cx = X0 + colw + gap
    shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, cx, cy - ch / 2, colw, ch, fill=ACCENT, radius=0.08)
    off = icon_img(slide, center.get("icon"), cx + (colw - ICON_SIZE) / 2, cy - ch / 2 + SP["m"], color=WHITE) if center.get("icon") else 0
    ty = cy - ch / 2 + SP["m"] + (off + SP["s"] if off else 0)
    text(slide, cx + SP["m"], ty, colw - 2 * SP["m"], Inches(0.5), center.get("head", SPEC.get("company", "")),
         SIZE["body"] + 4, "head", WHITE, PP_ALIGN.CENTER)
    text(slide, cx + SP["m"], ty + Inches(0.55), colw - 2 * SP["m"], cy + ch / 2 - ty - Inches(0.55) - SP["m"],
         center.get("body", ""), role="body", color=WHITE, align=PP_ALIGN.CENTER)
    for y in lm:
        connector(slide, X0 + colw, cx, y if abs(y - cy) < ch / 2 else cy)
    for y in rm_:
        connector(slide, cx + colw, rx, y if abs(y - cy) < ch / 2 else cy)
    footer(slide, idx, d.get("source"))


def s_hero(slide, d, idx):
    """풀블리드 사진 + 글. side: left|right (글 위치), dark: true면 어둡게 덮고 흰 글씨."""
    img = d.get("image")
    dark = d.get("dark", True)
    if img and (ROOT / img).exists():
        li = light_image(ROOT / img)
        pic = slide.shapes.add_picture(str(li), 0, 0, int(W), int(H))
        fill_crop(pic, li, W, H, tuple(d.get("focus", (0.5, 0.5))))
        pic.name = "bleed:hero-image"
        if dark:
            set_alpha(rect(slide, 0, 0, W, H, DARK, name="bleed:overlay"), d.get("overlay", 35))
    else:
        bg(slide, DARK if dark else SURFACE)
    col, sub = (WHITE, rgb(C["neutral"]["100"])) if dark else (INK, INK_SOFT)
    tw = CW * 0.45
    tx = X0 if d.get("side", "left") == "left" else X1 - tw
    if d.get("section"):
        text(slide, tx, Y0, tw, Inches(0.28), d["section"], role="caption", color=sub, bold=True)
    text(slide, tx, Inches(2.5), tw, Inches(1.4), d["title"], 36, "display", col)
    if d.get("message"):
        text(slide, tx, Inches(3.9), tw, Inches(1.6), d["message"], SIZE["body"], "body", sub)
    text(slide, X1 - Inches(1), FOOT_Y, Inches(1), FOOT_H, str(idx), role="caption", color=sub, align=PP_ALIGN.RIGHT)


def s_gallery(slide, d, idx):
    """사진 여러 장(캡션·설명) + 선택: 왼쪽 큰 숫자(stats: value_ref 목록)와 인용문(quote)."""
    header(slide, d, idx)
    end = summary_bar(slide, d)
    items = d["items"][:8]
    x0 = X0
    if d.get("stats") or d.get("quote"):
        lw = CW * 0.3
        y = TOP
        for ref in d.get("stats", [])[:2]:
            r = resolve(ref)
            num_text(slide, X0, y, lw, Inches(0.9), fmt(r["value"]), r.get("unit", ""), 52, INK)
            text(slide, X0, y + Inches(0.9), lw, Inches(0.35), r.get("label", ""), role="body", color=INK_SOFT)
            y += Inches(1.45)
        if d.get("quote"):
            seg(slide, X0, y, X0 + Inches(0.6), y, INK, "bold")
            text(slide, X0, y + SP["s"], lw, end - y - SP["s"], d["quote"], SIZE["body"], "body", INK_SOFT)
        x0 = X0 + lw + SP["xl"]
    n = len(items)
    per_row = n if n <= 4 else (n + 1) // 2
    rows = (n + per_row - 1) // per_row
    gap = SP["m"]
    cw = (X1 - x0 - gap * (per_row - 1)) / per_row

    def cap_of(row_items):
        if not any(it.get("caption") for it in row_items):
            return 0
        return Inches(0.36) + (Inches(0.3) if any(it.get("body") for it in row_items) else 0)

    row_items = [items[r * per_row:(r + 1) * per_row] for r in range(rows)]
    caps = [cap_of(ri) for ri in row_items]
    img_total = end - TOP - gap * (rows - 1) - sum(caps) - SP["s"] * sum(1 for c_ in caps if c_)
    ih = img_total / rows
    y = TOP
    for r, ri in enumerate(row_items):
        for j, it in enumerate(ri):
            x = x0 + j * (cw + gap)
            picture(slide, it.get("image"), x, y, cw, ih, focus=tuple(it.get("focus", (0.5, 0.4))))
            if caps[r]:
                cy = y + ih + SP["s"]
                text(slide, x, cy, cw, Inches(0.33), it.get("caption", ""), SIZE["small"], "head", INK)
                if it.get("body"):
                    text(slide, x, cy + Inches(0.33), cw, Inches(0.3), it["body"], SIZE["small"], "body", INK_SOFT)
        y += ih + (caps[r] + SP["s"] if caps[r] else 0) + gap
    footer(slide, idx, d.get("source"))


def s_share(slide, d, idx):
    """100% 가로 막대로 비중 표현. total_ref(전체), segments [{label, pct_ref, value_ref, highlight}]."""
    header(slide, d, idx)
    end = summary_bar(slide, d)
    y = TOP
    if d.get("total_ref"):
        t = resolve(d["total_ref"])
        text(slide, X0, y, Inches(5), Inches(0.3), t.get("label", ""), role="body", color=INK_SOFT)
        num_text(slide, X0, y + Inches(0.3), Inches(5), Inches(0.8), fmt(t["value"]), t.get("unit", ""), 40, INK)
        y += Inches(1.35)
    segs = d["segments"]
    pcts = [num(resolve(sg["pct_ref"])["value"]) for sg in segs]
    tot = sum(pcts) or 1
    bar_h = Inches(0.62)
    x = X0
    for sg, pc in zip(segs, pcts):
        w = CW * pc / tot
        hl = sg.get("highlight")
        rect(slide, x, y, w - (Inches(0.04) if x + w < X1 - 10 else 0), bar_h, ACCENT if hl else LINE_SOFT)
        num_text(slide, x + SP["m"], y, w - SP["m"], bar_h, fmt(pc), "%", 22, WHITE if hl else INK_SOFT,
                 anchor=MSO_ANCHOR.MIDDLE)
        ty = y + bar_h + SP["m"]
        seg(slide, x, ty, x + min(w, Inches(3.2)) - SP["s"], ty, INK if hl else LINE, "bold" if hl else "regular")
        text(slide, x, ty + SP["s"], min(w, Inches(3.5)), Inches(0.3), sg["label"], role="body",
             color=INK if hl else INK_SOFT, bold=bool(hl))
        if sg.get("value_ref"):
            v = resolve(sg["value_ref"])
            num_text(slide, x, ty + SP["s"] + Inches(0.32), min(w, Inches(3.5)), Inches(0.8), fmt(v["value"]),
                     v.get("unit", ""), 40, ACCENT if hl else INK)
        by = ty + SP["s"] + Inches(1.15)
        if sg.get("body"):
            text(slide, x, by, min(w, Inches(3.5)) - SP["s"], Inches(0.3), sg["body"], SIZE["small"], "body", INK_SOFT)
        if sg.get("images"):
            iy = by + Inches(0.4)
            iw = w - SP["m"]
            imgs = sg["images"]
            k = len(imgs); sw = (iw - SP["s"] * (k - 1)) / k
            for j, im in enumerate(imgs):
                picture(slide, im, x + j * (sw + SP["s"]), iy, sw, end - iy, focus=(0.5, 0.35))
        x += w
    footer(slide, idx, d.get("source"))


BUILDERS = {"cover": s_cover, "statement": s_statement, "process": s_process, "chart": s_chart,
            "metrics": s_metrics, "table": s_table, "team": s_team, "ask": s_ask, "closing": s_closing,
            "timeline": s_timeline, "tam": s_tam, "compare": s_compare, "product": s_product, "structure": s_structure,
            "hero": s_hero, "gallery": s_gallery, "share": s_share}


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
