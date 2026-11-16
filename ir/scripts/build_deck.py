"""deck.json + ir/data/*.csv + tokens.json → 편집 가능한 PPTX.

사용: python ir/scripts/build_deck.py ir/deck.json
출력: output/ir-<name>/deck.pptx

슬라이드 type: cover, statement, chart, metrics, table, team, ask, closing
숫자는 직접 쓰지 말고 data 파일을 가리킨다:
  - "value_ref": "data/kpi.csv#mau"   (kpi.csv 의 key 열이 mau 인 행)
  - chart.data / table.data: "data/revenue.csv"
차트는 PowerPoint 기본 차트로 만들어 고객이 직접 숫자를 고칠 수 있다.
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
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt, Emu

ROOT = Path(__file__).resolve().parents[2]
IR = ROOT / "ir"

# ---------- 토큰 ----------
# deck.json 의 "tokens"(작업별 색 파일)가 있으면 그것을, 없으면 기본 tokens.json(중립색)을 쓴다.
_SPEC_PATH = Path(sys.argv[1] if len(sys.argv) > 1 else IR / "deck.json")
_tok_rel = json.loads(_SPEC_PATH.read_text(encoding="utf-8")).get("tokens") if _SPEC_PATH.exists() else None
TOKENS_PATH = ROOT / (_tok_rel or "tokens.json")
tok = json.loads(TOKENS_PATH.read_text(encoding="utf-8"))
C = tok["color"]


def rgb(h):
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


ACCENT = rgb(C["brand"].get("primaryHover", C["brand"]["primary"]))   # 흰 글씨 대비 확보된 진한 색
INK = rgb(C["text"]["primary"])
INK_SOFT = rgb(C["text"]["secondary"])
MUTED = rgb(C["neutral"]["500"])
LINE = rgb(C["neutral"]["100"])
SURFACE = rgb(C["neutral"]["50"])
WHITE = rgb("#FFFFFF")
DARK = rgb(C["brand"].get("secondary", C["text"]["primary"]))
SERIES = [ACCENT, rgb(C["neutral"]["700"]), rgb(C["neutral"]["300"]), rgb(C["neutral"]["500"])]
FONT = tok["font"]["family"]["heading"].split(",")[0].strip().strip('"')   # tokens.json의 첫 번째 폰트

W, H = Inches(13.333), Inches(7.5)
M = Inches(0.6)                     # 좌우 여백
CW = W - 2 * M                      # 본문 폭
TOP = Inches(2.35)                  # 본문 시작
BOTTOM = Inches(6.75)               # 본문 끝


# ---------- 데이터 ----------
def read_csv(rel):
    with open(IR / rel, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def resolve(ref):
    """'data/kpi.csv#mau' → 행 dict"""
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


# ---------- 텍스트 도우미 ----------
def text(slide, x, y, w, h, s, size=16, bold=False, color=INK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    lines = s if isinstance(s, list) else [s]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run()
        r.text = line
        f = r.font
        f.name, f.size, f.bold, f.color.rgb = FONT, Pt(size), bold, color
        _ea_font(r)
    return tb


def _ea_font(run):
    """한글(동아시아) 폰트도 Pretendard로 지정."""
    rPr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        el = rPr.find("{http://schemas.openxmlformats.org/drawingml/2006/main}" + tag.split(":")[1])
        if el is None:
            el = rPr.makeelement("{http://schemas.openxmlformats.org/drawingml/2006/main}" + tag.split(":")[1], {})
            rPr.append(el)
        el.set("typeface", FONT)


def rect(slide, x, y, w, h, fill):
    from pptx.enum.shapes import MSO_SHAPE
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    s.line.fill.background()
    s.shadow.inherit = False
    return s


def header(slide, d):
    text(slide, M, Inches(0.55), CW, Inches(0.9), d["title"], size=30, bold=True)
    if d.get("message"):
        text(slide, M, Inches(1.45), CW, Inches(0.7), d["message"], size=17, color=INK_SOFT)


def footer(slide, idx, source=None):
    if source:
        text(slide, M, Inches(7.0), Inches(10), Inches(0.3), f"출처: {source}", size=10, color=MUTED)
    text(slide, W - M - Inches(1), Inches(7.0), Inches(1), Inches(0.3), str(idx), size=10, color=MUTED, align=PP_ALIGN.RIGHT)


# ---------- 슬라이드 타입 ----------
def s_cover(slide, d, idx):
    rect(slide, 0, 0, Inches(0.25), H, ACCENT)
    text(slide, Inches(1.1), Inches(2.4), Inches(11), Inches(1.6), d["title"], size=44, bold=True)
    if d.get("subtitle"):
        text(slide, Inches(1.1), Inches(4.05), Inches(10), Inches(0.8), d["subtitle"], size=20, color=INK_SOFT)
    if d.get("meta"):
        text(slide, Inches(1.1), Inches(6.4), Inches(10), Inches(0.4), d["meta"], size=12, color=MUTED)


def s_statement(slide, d, idx):
    header(slide, d)
    pts = d.get("points", [])[:3]
    if not pts:
        return
    gap = Inches(0.4)
    cw = (CW - gap * (len(pts) - 1)) / len(pts)
    for i, p in enumerate(pts):
        x = M + i * (cw + gap)
        rect(slide, x, TOP, cw, Emu(Inches(0.06)), ACCENT if i == 0 else LINE)
        text(slide, x, TOP + Inches(0.3), cw, Inches(0.6), p["head"], size=20, bold=True)
        text(slide, x, TOP + Inches(1.0), cw, Inches(2.8), p.get("body", ""), size=16, color=INK_SOFT)
    footer(slide, idx, d.get("source"))


def s_chart(slide, d, idx):
    header(slide, d)
    c = d["chart"]
    rows = read_csv(c["data"])
    cd = CategoryChartData()
    cd.categories = [r[c["x"]] for r in rows]
    for ycol in c["y"]:
        cd.add_series(c.get("labels", {}).get(ycol, ycol), [num(r[ycol]) for r in rows])
    kind = {"bar": XL_CHART_TYPE.COLUMN_CLUSTERED, "stacked": XL_CHART_TYPE.COLUMN_STACKED,
            "line": XL_CHART_TYPE.LINE_MARKERS, "hbar": XL_CHART_TYPE.BAR_CLUSTERED}[c.get("kind", "bar")]
    gf = slide.shapes.add_chart(kind, M, TOP, CW, BOTTOM - TOP, cd)
    ch = gf.chart
    ch.font.name, ch.font.size, ch.font.color.rgb = FONT, Pt(14), INK_SOFT
    ch.has_title = False                      # 슬라이드 제목이 결론을 말하므로 차트 제목은 생략
    ch.has_legend = len(c["y"]) > 1
    if ch.has_legend:
        ch.legend.position, ch.legend.include_in_layout = XL_LEGEND_POSITION.TOP, False
    va = ch.value_axis
    va.has_major_gridlines = False
    va.visible = False
    ca = ch.category_axis
    ca.format.line.color.rgb = LINE
    ca.has_major_gridlines = False
    if kind == XL_CHART_TYPE.BAR_CLUSTERED:
        ca.reverse_order = True               # 가로 막대는 CSV 순서대로 위에서 아래로
    plot = ch.plots[0]
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.number_format, dl.number_format_is_linked = '#,##0', False
    dl.font.size, dl.font.bold, dl.font.color.rgb = Pt(14), True, INK
    if kind != XL_CHART_TYPE.LINE_MARKERS:
        dl.position = XL_LABEL_POSITION.OUTSIDE_END if kind != XL_CHART_TYPE.COLUMN_STACKED else XL_LABEL_POSITION.CENTER
        plot.gap_width = 60
    hi = c.get("highlight")
    for si, series in enumerate(plot.series):
        base = SERIES[si % len(SERIES)] if len(c["y"]) > 1 else (rgb(C["neutral"]["300"]) if hi else ACCENT)
        if kind == XL_CHART_TYPE.LINE_MARKERS:
            series.format.line.color.rgb = base if len(c["y"]) > 1 else ACCENT
            series.format.line.width = Pt(3)
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
        text(slide, M, TOP - Inches(0.35), Inches(4), Inches(0.3), f"단위: {c['unit']}", size=11, color=MUTED)
    src = d.get("source") or "; ".join(sorted({r.get("source", "") for r in rows if r.get("source")}))
    footer(slide, idx, src or None)


def s_metrics(slide, d, idx):
    header(slide, d)
    items = [resolve(i["value_ref"]) | {"label_override": i.get("label")} for i in d["items"]][:4]
    gap = Inches(0.35)
    cw = (CW - gap * (len(items) - 1)) / len(items)
    srcs = set()
    for i, r in enumerate(items):
        x = M + i * (cw + gap)
        rect(slide, x, TOP, cw, Inches(3.4), SURFACE)
        text(slide, x + Inches(0.35), TOP + Inches(0.5), cw - Inches(0.7), Inches(1.2),
             [f"{fmt(r['value'])}{r.get('unit', '')}"], size=44, bold=True, color=ACCENT if i == 0 else INK)
        text(slide, x + Inches(0.35), TOP + Inches(1.8), cw - Inches(0.7), Inches(1.2),
             r["label_override"] or r.get("label", r["key"]), size=16, color=INK_SOFT)
        if r.get("as_of"):
            text(slide, x + Inches(0.35), TOP + Inches(2.85), cw - Inches(0.7), Inches(0.3), f"기준 {r['as_of']}", size=11, color=MUTED)
        if r.get("source"):
            srcs.add(r["source"])
    footer(slide, idx, d.get("source") or "; ".join(sorted(srcs)) or None)


def s_table(slide, d, idx):
    header(slide, d)
    rows = read_csv(d["table"]["data"])
    cols = d["table"].get("columns") or [k for k in rows[0] if k != "source"]
    hi = d["table"].get("highlight_row")
    n_r, n_c = len(rows) + 1, len(cols)
    tbl = slide.shapes.add_table(n_r, n_c, M, TOP, CW, Inches(0.55) * n_r).table
    for j, col in enumerate(cols):
        cell = tbl.cell(0, j)
        cell.text = d["table"].get("labels", {}).get(col, col)
        cell.fill.solid()
        cell.fill.fore_color.rgb = DARK
    for i, r in enumerate(rows, 1):
        for j, col in enumerate(cols):
            cell = tbl.cell(i, j)
            cell.text = r[col]
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb("#FDF1EC") if hi and r[cols[0]] == hi else WHITE
    for i in range(n_r):
        for j in range(n_c):
            for p in tbl.cell(i, j).text_frame.paragraphs:
                for run in p.runs:
                    run.font.name, run.font.size = FONT, Pt(14)
                    run.font.bold = i == 0 or (hi and j == 0 and tbl.cell(i, 0).text == hi)
                    run.font.color.rgb = WHITE if i == 0 else INK
                    _ea_font(run)
    srcs = sorted({r.get("source", "") for r in rows if r.get("source")})
    footer(slide, idx, d.get("source") or "; ".join(srcs) or None)


def s_team(slide, d, idx):
    header(slide, d)
    people = d["people"][:4]
    gap = Inches(0.35)
    cw = (CW - gap * (len(people) - 1)) / len(people)
    for i, p in enumerate(people):
        x = M + i * (cw + gap)
        rect(slide, x, TOP, Inches(1.3), Inches(1.3), LINE)   # 사진 자리
        text(slide, x, TOP, Inches(1.3), Inches(1.3), "사진", size=12, color=MUTED,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        text(slide, x, TOP + Inches(1.55), cw, Inches(0.5), p["name"], size=20, bold=True)
        text(slide, x, TOP + Inches(2.05), cw, Inches(0.4), p["role"], size=15, color=ACCENT)
        text(slide, x, TOP + Inches(2.55), cw, Inches(1.8), p.get("bio", ""), size=14, color=INK_SOFT)
    footer(slide, idx)


def s_ask(slide, d, idx):
    rect(slide, 0, 0, W, H, DARK)
    r = resolve(d["amount_ref"])
    text(slide, M, Inches(0.8), CW, Inches(0.8), d["title"], size=30, bold=True, color=WHITE)
    text(slide, M, Inches(1.9), CW, Inches(1.4), f"{fmt(r['value'])}{r.get('unit', '')}", size=72, bold=True, color=WHITE)
    if d.get("message"):
        text(slide, M, Inches(3.4), Inches(7), Inches(0.8), d["message"], size=18, color=rgb(C["neutral"]["300"]))
    if d.get("use_of_funds"):
        rows = read_csv(d["use_of_funds"])
        y = Inches(4.5)
        for row in rows:
            text(slide, M, y, Inches(5), Inches(0.45), row["label"], size=16, color=WHITE)
            text(slide, M + Inches(5), y, Inches(1.5), Inches(0.45), f"{fmt(row['value'])}{row.get('unit', '%')}", size=16, bold=True, color=WHITE, align=PP_ALIGN.RIGHT)
            y += Inches(0.5)
    text(slide, W - M - Inches(1), Inches(7.0), Inches(1), Inches(0.3), str(idx), size=10, color=rgb(C["neutral"]["500"]), align=PP_ALIGN.RIGHT)


def s_closing(slide, d, idx):
    text(slide, M, Inches(2.6), CW, Inches(1.2), d["title"], size=40, bold=True)
    if d.get("message"):
        text(slide, M, Inches(3.9), CW, Inches(1.0), d["message"], size=18, color=INK_SOFT)
    if d.get("contact"):
        text(slide, M, Inches(6.2), CW, Inches(0.4), d["contact"], size=14, color=MUTED)


BUILDERS = {"cover": s_cover, "statement": s_statement, "chart": s_chart, "metrics": s_metrics,
            "table": s_table, "team": s_team, "ask": s_ask, "closing": s_closing}


def main():
    spec_path = Path(sys.argv[1] if len(sys.argv) > 1 else IR / "deck.json")
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    tpl = spec.get("template")
    prs = Presentation(str(ROOT / tpl)) if tpl else Presentation()
    if not tpl:
        prs.slide_width, prs.slide_height = W, H
    blank = prs.slide_layouts[6] if len(prs.slide_layouts) > 6 else prs.slide_layouts[-1]
    for i, d in enumerate(spec["slides"], 1):
        slide = prs.slides.add_slide(blank)
        BUILDERS[d["type"]](slide, d, i)
        if d.get("notes"):
            slide.notes_slide.notes_text_frame.text = d["notes"]
    out_dir = ROOT / "output" / f"ir-{spec['name']}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "deck.pptx"
    prs.save(out)
    print(f"생성: {out.relative_to(ROOT)} ({len(spec['slides'])}장, 색: {TOKENS_PATH.relative_to(ROOT)})")


if __name__ == "__main__":
    main()
