"""v20: 로커스코리아 IR 스타일 적용 (상단바 제외).
- 연회색 배경 + 흰 둥근 카드, 카드 왼쪽 위 버건디 삼각 포인트
- 제목: 큰 페이지 번호 + 세로선 + 아이브로 한 줄, 아래 헤드라인(강조어 버건디)
- 본문 전체를 카드 안쪽 여백만큼 균일 축소
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Cm, Pt, Emu

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "work17"))
import design17 as d  # noqa: E402

SRC, OUT = sys.argv[1], sys.argv[2]
prs = Presentation(SRC)
BG = RGBColor(0xF2, 0xF2, 0xF3)
BUR = RGBColor(0x8E, 0x24, 0x30)
GRAYNUM = RGBColor(0xB4, 0xB8, 0xBF)
WHITE = RGBColor(255, 255, 255)
L, R, T, B = 1.53, 32.34, 5.0, 17.52
CT, CB = 4.75, 17.52          # 카드 영역 위·아래
PADX, PADY = 0.6, 0.35
cm = d.cm
HEADER = ("메뉴", "상단선", "활성 표시", "상단 구분", "페이지 번호", "그래픽 1", "그래픽 2", "아이브로", "타이틀")

# 원래 좌표계(본문 1.53~32.34, 5.0~17.52) → 카드 안쪽
sx = (R - L - 2 * PADX) / (R - L)
sy = (CB - CT - 2 * PADY - 0.0) / (B - T)
S = min(sx, sy)
X0 = L + ((R - L) - (R - L) * S) / 2
Y0 = CT + PADY


def tx(x): return X0 + (x - L) * S
def ty(y): return Y0 + (y - T) * S


# 페이지별 카드 영역(원래 좌표): (x0, x1, y0, y1) 안에 중심이 있는 요소들의 테두리로 카드 생성
REGIONS = {
    2: [(1.4, 22.3, 4.8, 18), (22.4, 33, 4.8, 18)],
    4: [(1.4, 9.2, 4.8, 18), (9.2, 17.0, 4.8, 18), (17.0, 24.8, 4.8, 18), (24.8, 33, 4.8, 18)],
    5: [(1.4, 11.5, 4.8, 18), (11.5, 22.3, 4.8, 18), (22.3, 33, 4.8, 18)],
    6: [(1.4, 7.6, 7.5, 17.2), (7.6, 13.9, 7.5, 17.2), (13.9, 20.1, 7.5, 17.2), (20.1, 26.4, 7.5, 17.2),
        (26.4, 33, 7.5, 17.2)],
    7: [(1.4, 11.8, 4.8, 18), (11.8, 33, 4.8, 18)],
    8: [(1.4, 20.3, 4.8, 18), (21.0, 33, 4.8, 18)],
    }
MIDS = {15: [21.0], 8: [20.6]}
REGIONS.update({
    9: [(1.4, 33, 4.6, 18)],
    10: [(1.4, 33, 4.6, 8.9), (1.4, 20.0, 8.9, 18.1), (20.0, 33, 8.9, 18.1)],
    11: [(1.4, 33, 4.8, 18)],
    12: [(1.4, 16.8, 4.8, 18), (16.8, 33, 4.8, 18)],
    13: [(1.4, 33, 4.6, 8.9), (1.4, 16.2, 8.9, 18.1), (16.2, 33, 8.9, 18.1)],
    14: [(1.4, 16.9, 4.8, 11.6), (16.9, 33, 4.8, 11.6), (1.4, 11.9, 11.6, 18.1), (11.9, 22.4, 11.6, 18.1),
         (22.4, 33, 11.6, 18.1)],
    15: [(1.4, 21.5, 4.8, 18), (21.5, 33, 4.8, 18)],
})


def setfont(r, font, size, color):
    d.setfont(r, font, size, color)


def card(s, x, y, w, h):
    c = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Cm(x), Cm(y), Cm(w), Cm(h))
    c.adjustments[0] = min(0.35 / min(w, h), 0.5)
    c.fill.solid(); c.fill.fore_color.rgb = WHITE; c.line.fill.background(); c.name = "카드"
    tri = s.shapes.add_shape(MSO_SHAPE.RIGHT_TRIANGLE, Cm(x), Cm(y), Cm(0.6), Cm(0.6))
    tri.fill.solid(); tri.fill.fore_color.rgb = BUR; tri.line.fill.background(); tri.name = "카드 포인트"
    tri._element.spPr.find(f"{{{d.A}}}xfrm").set("flipV", "1")
    tree = s.shapes._spTree
    for el in (tri._element, c._element):
        tree.remove(el); tree.insert(2, el)


for idx, s in enumerate(prs.slides, 1):
    if idx in (1, 3):
        continue
    s.background.fill.solid(); s.background.fill.fore_color.rgb = BG
    content = [sh for sh in s.shapes if sh.name not in HEADER and sh.top is not None and cm(sh.top) > 4.4]
    # 기존 회색 면 박스·카드 제거
    for sh in list(content):
        if sh.name in ("면 박스", "카드", "To-Be 배경") or sh.name.startswith("제품 타일"):
            if sh.name == "To-Be 배경":
                sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor(0xF8, 0xF0, 0xF1)
                continue
            if sh.name.startswith("제품 타일"):
                sh.fill.solid(); sh.fill.fore_color.rgb = BG
                continue
            d.remove(sh); content.remove(sh)
    # 카드 영역: 행별로 같은 높이, 열 경계는 이웃 내용 사이 가운데
    regs = REGIONS.get(idx, [])
    groups = []
    for (x0, x1, y0, y1) in regs:
        mem = [sh for sh in content if x0 <= cm(sh.left) + cm(sh.width) / 2 < x1 and
               y0 <= cm(sh.top) + cm(sh.height) / 2 < y1]
        if mem:
            groups.append(((y0, y1), mem))
    # 본문 축소 이동
    for sh in content:
        x, y, w, h = cm(sh.left), cm(sh.top), cm(sh.width), cm(sh.height)
        sh.left, sh.top = Cm(tx(x)), Cm(ty(y))
        sh.width, sh.height = Cm(w * S), Cm(h * S)
    rows = sorted({g[0] for g in groups})
    GAP = 0.3
    prev_bottom = None
    for ri, rk in enumerate(rows):
        gs = [g for g in groups if g[0] == rk]
        ext = []
        for _, mem in gs:
            ext.append((min(cm(m.left) for m in mem), max(cm(m.left) + cm(m.width) for m in mem),
                        min(cm(m.top) for m in mem), max(cm(m.top) + cm(m.height) for m in mem)))
        ext.sort()
        ry0 = CT if ri == 0 else prev_bottom + GAP
        if ri == len(rows) - 1:
            ry1 = CB
        else:
            nxt = [g for g in groups if g[0] == rows[ri + 1]]
            ntop = min(cm(m.top) for _, mem in nxt for m in mem)
            ry1 = min(max(e[3] for e in ext) + PADY, ntop - PADY - GAP)
        bounds = [L]
        mids = [tx(m) for m in MIDS.get(idx, [])] or [(a[1] + b[0]) / 2 for a, b in zip(ext, ext[1:])]
        for mid in mids[:len(ext) - 1]:
            bounds += [mid - GAP / 2, mid + GAP / 2]
        bounds.append(R)
        for k in range(len(ext)):
            card(s, bounds[2 * k], ry0, bounds[2 * k + 1] - bounds[2 * k], ry1 - ry0)
        prev_bottom = ry1
    # 카드 아래로 넘친 사진은 카드 끝에서 자름
    for sh in s.shapes:
        if sh.shape_type == 13 and sh.name.startswith("bleed:"):
            bot = cm(sh.top) + cm(sh.height)
            if bot > CB:
                keep = (CB - cm(sh.top)) / cm(sh.height)
                sh.crop_bottom = sh.crop_bottom + (1 - sh.crop_bottom - sh.crop_top) * (1 - keep)
                sh.height = Cm(CB - cm(sh.top))
    # ---- 제목 영역 ----
    eb = [sh for sh in s.shapes if sh.name == "아이브로"]
    tt = [sh for sh in s.shapes if sh.name == "타이틀"]
    num = d.text(s, L, 2.05, 2.2, 1.05, [[(f"{idx:02d}", "Pretendard Medium", 26, GRAYNUM)]],
                 anchor=MSO_ANCHOR.MIDDLE, name="섹션 번호", wrap=False)
    d.line(s, L + 1.95, 2.25, L + 1.95, 2.95, RGBColor(0x1A, 0x1A, 0x1A), 0.75, name="섹션 세로선")
    if eb:
        e = eb[0]
        e.left, e.top, e.width = Cm(L + 2.25), Cm(2.3), Cm(R - L - 2.25)
        for p in e.text_frame.paragraphs:
            for r in p.runs:
                setfont(r, "Pretendard Bold", 11.5, RGBColor(0x1A, 0x1A, 0x1A))
    if tt:
        t = tt[0]
        t.left, t.top = Cm(L), Cm(3.3)
        for p in t.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(22)
                try:
                    if str(r.font.color.rgb) not in ("000000", "1A1A1A", "171A1F", "262626", "121212"):
                        r.font.color.rgb = BUR
                except Exception:
                    pass
        # 앞에 버건디 두 점
        dd = d.text(s, L, 3.3, 0.7, cm(t.height), [[("··", "Pretendard ExtraBold", 22, BUR)]],
                    anchor=MSO_ANCHOR.MIDDLE, name="제목 점", wrap=False)
        t.left = Cm(L + 0.62)

prs.save(OUT)
print("저장", OUT, "배율", round(S, 3))
