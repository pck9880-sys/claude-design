"""v18: 전체 배치 재구성. 점선 금지, 실선 0.3pt, 필요한 곳만 옅은 면 박스, 여백 통일(좌우 1.53 / 본문 5.0~17.52).
python layout18.py <사용자 v17.pptx> <출력.pptx>
"""
import io
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Cm, Pt, Emu

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "work17"))
import design17 as d  # noqa: E402

SRC, OUT = sys.argv[1], sys.argv[2]
prs = Presentation(SRC)
SL = list(prs.slides)
L, R, T, B = 1.53, 32.34, 5.0, 17.52
PANEL = RGBColor(0xF4, 0xF6, 0xF8)
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
cm = d.cm


def by_name(s, name):
    return [x for x in s.shapes if x.name == name]


def by_text(s, start):
    return [x for x in s.shapes if x.has_text_frame and x.text_frame.text.strip().startswith(start)]


def move(sh, dx=0, dy=0):
    sh.left = sh.left + Cm(dx); sh.top = sh.top + Cm(dy)


def place(sh, x=None, y=None, w=None, h=None):
    if x is not None: sh.left = Cm(x)
    if y is not None: sh.top = Cm(y)
    if w is not None: sh.width = Cm(w)
    if h is not None: sh.height = Cm(h)


def cover(p, x, y, w, h, ay=0.5):
    """비율 유지 채우기(기존 자르기 무시, 흰 여백 자동 제거)."""
    import numpy as np
    im = Image.open(io.BytesIO(p.image.blob)).convert("RGB")
    a = np.asarray(im).astype(int)
    rows = np.where((a.min(axis=2) < 235).mean(axis=1) > 0.5)[0]
    cols = np.where((a.min(axis=2) < 235).mean(axis=0) > 0.5)[0]
    l0, t0 = (cols.min(), rows.min()) if len(rows) and len(cols) else (0, 0)
    r0, b0 = (cols.max() + 1, rows.max() + 1) if len(rows) and len(cols) else im.size
    W0, H0 = im.size
    iw, ih = r0 - l0, b0 - t0
    if iw / ih > w / h:
        nw = ih * w / h; l = l0 + (iw - nw) / 2; r = l + nw; t = t0; b = b0
    else:
        nh = iw * h / w; t = t0 + (ih - nh) * ay; b = t + nh; l = l0; r = r0
    p.crop_left, p.crop_right = l / W0, 1 - r / W0
    p.crop_top, p.crop_bottom = t / H0, 1 - b / H0
    place(p, x, y, w, h)


def panel(s, x, y, w, h, color=PANEL, name="면 박스"):
    sh = d.rect(s, x, y, w, h, color, name)
    # 맨 뒤로
    s.shapes._spTree.remove(sh._element); s.shapes._spTree.insert(2, sh._element)
    return sh


def font_size(sh, pt):
    for p in sh.text_frame.paragraphs:
        for r in p.runs:
            r.font.size = Pt(pt)


# ---------------- 공통: 점선 제거, 선 0.3pt ----------------
KEEP_THICK = ("추세선",)
for s in SL:
    for sh in s.shapes:
        try:
            ln = sh.line
        except Exception:
            continue
        try:
            visible = ln.fill.type is not None and ln.fill.type != 5  # 5 = background(없음)
        except Exception:
            visible = False
        if sh.shape_type == 9 or sh.name in ("구분선", "선"):
            if sh.name.startswith(KEEP_THICK):
                ln.dash_style = MSO_LINE_DASH_STYLE.SOLID
                continue
            ln.dash_style = MSO_LINE_DASH_STYLE.SOLID
            ln.width = Pt(0.3)
            if sh.name in ("낙하선", "연도 축"):
                ln.color.rgb = d.RULE
        elif visible and sh.shape_type == 1:
            try:
                if ln.dash_style not in (None, MSO_LINE_DASH_STYLE.SOLID):
                    ln.dash_style = MSO_LINE_DASH_STYLE.SOLID
                if ln.width and ln.width > Pt(0.3) and sh.name not in ("말풍선",):
                    ln.width = Pt(0.3)
            except Exception:
                pass

# ---------------- 1p 표지 ----------------
s = SL[0]
hl = by_name(s, "헤드라인")[0]
bar = by_name(s, "표지 포인트 막대")
sub = by_text(s, "오우이")
pm = by_name(s, "PROJECT MOMENT")
logo = by_name(s, "owooii 로고")
if logo: place(logo[0], x=L, y=1.2)
place(hl, x=L, y=6.6)
if bar: place(bar[0], x=L, y=6.05, w=0.9, h=0.08)
if sub:
    sb = sub[0]
    sb.fill.background(); sb.line.fill.background()
    tf = sb.text_frame; tf.margin_left = 0
    for p in tf.paragraphs:
        p.alignment = PP_ALIGN.LEFT
        for r in p.runs:
            d.setfont(r, "Pretendard Medium", 13, d.G1, 20)
    place(sb, x=L, y=10.35, w=14, h=0.7)
if pm:
    p0 = pm[0]
    place(p0, x=L - 0.2, y=B - cm(p0.height))

# ---------------- 2p ----------------
s = SL[1]
for lab, q, y in ((by_text(s, "Case. 01")[0], by_text(s, "“머리카락 말리는 것")[0], T),
                  (by_text(s, "Case. 02")[0], by_text(s, "“머리카락 말리는 데만")[0], T + 0.9)):
    place(lab, x=L, y=y); place(q, x=L + 3.0, y=y + 0.02)
imgs = sorted([x for x in s.shapes if x.shape_type == 13 and x.name.startswith("그림 2")], key=lambda x: x.left)
caps = sorted([x for x in s.shapes if x.name.startswith("TextBox") and cm(x.top) > 15], key=lambda x: x.left)
IY = 7.15
PW = 22.1 - L
iw = (PW - 3 * 0.25) / 4
for i, (im, cp) in enumerate(zip(imgs, caps)):
    x = L + i * (iw + 0.25)
    cover(im, x, IY, iw, B - IY)
    place(cp, x=x + 0.4, y=B - 1.45, w=iw - 0.6)
# 오른쪽 통계 면
px = 22.6
panel(s, px, IY, R - px, B - IY)
stats = [x for x in s.shapes if cm(x.left) > 23 and cm(x.top) > 8 and x.name != "면 박스"]
dy = (IY + 0.9) - 8.53
for x in stats:
    move(x, dx=(px + 0.75) - 23.25, dy=dy)

# ---------------- 3p ----------------
s = SL[2]
for x in s.shapes:
    if x.name in ("owooii 로고", "헤드라인", "본문"):
        move(x, dx=L - 2.54)

# ---------------- 4p ----------------
s = SL[3]
for x in list(s.shapes):
    if x.name.startswith("사각형: 둥근 모서리") and not x.text_frame.text.strip():
        d.remove(x)
cols = [1.53, 9.31, 17.09, 24.88]
cw = (R - L - 3 * 0.25) / 4
cx = [L + i * (cw + 0.25) for i in range(4)]
for x in s.shapes:
    if x.shape_type == 17 and 4.5 < cm(x.top) < 8.2:
        ci = min(range(4), key=lambda k: abs(cols[k] - cm(x.left)))
        place(x, x=cx[ci], w=cw)
        if x.text_frame.text.strip() in ("NURTURE", "FILIAL PIETY", "CARE", "BOND"):
            for p in x.text_frame.paragraphs:
                p.alignment = PP_ALIGN.LEFT
                for r in p.runs:
                    d.setfont(r, "Pretendard Bold", 10, d.NAVY, 60)
            place(x, y=T)
pics = [x for x in s.shapes if x.shape_type == 13 and cm(x.top) > 8]
ih = (B - 8.45 - 0.25) / 2
for p in pics:
    ci = min(range(4), key=lambda k: abs(cols[k] - cm(p.left)))
    row = 0 if cm(p.top) < 12 else 1
    cover(p, cx[ci], 8.45 + row * (ih + 0.25), cw, ih)

# ---------------- 5p ----------------
s = SL[4]
grid = [L, L + (R - L + 0.8) / 3, L + 2 * (R - L + 0.8) / 3]
starts = [2.21, 12.83, 23.45]
for x in s.shapes:
    if x.name in ("그래픽 1",) or cm(x.top) < 4.5:
        continue
    ci = min(range(3), key=lambda k: abs(starts[k] - cm(x.left)) if cm(x.left) >= starts[k] - 0.5 else 99)
    move(x, dx=grid[ci] - starts[ci], dy=-0.28)

# ---------------- 6p ----------------
s = SL[5]
for x in s.shapes:
    if x.name == "카드":
        try:
            if str(x.fill.fore_color.rgb) == "F6F7F9":
                x.fill.background()
        except Exception:
            pass
    if 7.5 < cm(x.top) < 17.3:
        move(x, dy=-0.45)
for x in s.shapes:
    if x.name.startswith("출처"):
        place(x, y=B - 0.4)

# ---------------- 7p: 선만 정리 (공통에서 처리) ----------------

# ---------------- 8p ----------------
s = SL[7]
for x in s.shapes:
    if cm(x.top) < 4.5:
        continue
    if cm(x.left) < 18:
        move(x, dx=L - 2.12, dy=T - 5.26)
    elif cm(x.left) > 19.5:
        move(x, dx=0, dy=T - 5.71)

# ---------------- 9p: 표 전치 (행 머리 → 왼쪽 열) ----------------
s = SL[8]
mom = sorted(by_name(s, "성장 모멘텀"), key=lambda x: x.top)
asis = sorted(by_name(s, "As-Is"), key=lambda x: x.top)
tobe = sorted(by_name(s, "To-Be"), key=lambda x: x.top)
icons = sorted([x for x in s.shapes if x.name.startswith("아이콘 ")], key=lambda x: x.top)
arrows = [x for x in s.shapes if x.name == "화살표"]
for x in list(s.shapes):
    if x.name in ("구분선", "To-Be 배경"):
        d.remove(x)
tags = {x.text_frame.text.strip(): x for x in s.shapes if x.name == "태그"}
LW = 3.4
gx = L + LW + 0.3
cw = (R - gx - 3 * 0.35) / 4
cxs = [gx + i * (cw + 0.35) for i in range(4)]
R1, R2, R3 = T, T + 1.9, T + 3.55      # 성장 모멘텀 / As-Is / To-Be 행 시작
panel(s, L, R3 - 0.25, R - L, B - R3 + 0.25, d.NAVY_L, "To-Be 배경")
for k, (lab, y) in enumerate((("성장 모멘텀", R1), ("As-Is", R2), ("To-Be", R3))):
    t = tags.get(lab)
    if t:
        place(t, x=L + (0.3 if lab == "To-Be" else 0), y=y + 0.05, w=LW)
for y in (R2 - 0.3, R3 - 0.25):
    d.line(s, L, y, R, y, d.RULE, 0.3, name="구분선")
d.line(s, L, T - 0.25, R, T - 0.25, d.INK, 0.3, name="구분선")
d.line(s, L, B, R, B, d.INK, 0.3, name="구분선")
for i in range(4):
    x = cxs[i]
    ic = icons[i]
    place(ic, x=x, y=R1 + 0.05, w=0.6, h=0.6)
    m = mom[i]
    place(m, x=x + 0.85, y=R1, w=cw - 0.85, h=2.2)
    m.text_frame.vertical_anchor = MSO_ANCHOR.TOP
    a = asis[i]
    place(a, x=x, y=R2, w=cw, h=2.5)
    a.text_frame.vertical_anchor = MSO_ANCHOR.TOP
    tb = tobe[i]
    place(tb, x=x, y=R3 + 0.1, w=cw - 0.2, h=B - R3 - 0.4)
    tb.text_frame.vertical_anchor = MSO_ANCHOR.TOP
    tb.text_frame.word_wrap = True
    font_size(tb, 12)
    for p in tb.text_frame.paragraphs: p.line_spacing = 1.45
    for p in tb.text_frame.paragraphs:
        p.alignment = PP_ALIGN.LEFT
    for p in a.text_frame.paragraphs + m.text_frame.paragraphs:
        p.alignment = PP_ALIGN.LEFT
for k, ar in enumerate(arrows):
    if k < 4:
        ar.rotation = 90
        place(ar, x=cxs[k] + cw - 0.6, y=R3 - 0.85)
    else:
        d.remove(ar)

# ---------------- 10p: 위 타임라인 시작선 맞춤 ----------------
s = SL[9]
dy = T - 4.72
for x in s.shapes:
    if 4.5 < cm(x.top) < 8.9:
        move(x, dy=dy)
for x in s.shapes:
    if x.name in ("태그",) and cm(x.top) > 9:
        pass

# ---------------- 11p ----------------
s = SL[10]
for x in s.shapes:
    if cm(x.top) > 4.5:
        move(x, dx=L - 2.12, dy=T - 5.38)

# ---------------- 12p ----------------
s = SL[11]
for x in s.shapes:
    if cm(x.top) < 4.5:
        continue
    if cm(x.left) < 17:
        move(x, dx=L - 2.12, dy=T - 5.25)
    else:
        move(x, dy=T - 5.25)

# ---------------- 14p: 리더 면 박스 ----------------
s = SL[13]
panel(s, L, T, 15.2, 6.35)
panel(s, L + 15.61, T, R - L - 15.61, 6.35)
bw = (R - L - 2 * 0.4) / 3
for i in range(3):
    panel(s, L + i * (bw + 0.4), T + 6.75, bw, B - T - 6.75)
for x in s.shapes:
    if x.name == "면 박스":
        continue
    if cm(x.top) < 11.5 and cm(x.top) > 4.5:
        move(x, dy=0.35)
    elif cm(x.top) >= 11.5:
        move(x, dy=0.0)
# 아래 3명 가로 위치를 면 박스에 맞춤
xs_old = [2.05, 12.56, 23.07]
for x in s.shapes:
    if cm(x.top) >= 11.9 and x.name != "면 박스":
        ci = min(range(3), key=lambda k: abs(xs_old[k] - cm(x.left)) if cm(x.left) >= xs_old[k] - 0.3 else 99)
        move(x, dx=(L + ci * (bw + 0.4) + 0.5) - xs_old[ci])

# ---------------- 15p ----------------
s = SL[14]
thumbs = [by_name(s, n)[0] for n in ("기부 영상 썸네일", "기부 후기 썸네일", "기부 사진 썸네일")]
quote = by_name(s, "기부 문구")[0]
acct = by_name(s, "썸네일 계정")[0]
tags = {x.text_frame.text.strip(): x for x in s.shapes if x.name == "태그"}
place(tags["Donation"], x=L, y=T)
place(quote, x=L, y=T + 0.7, w=17.6, h=1.4)
for p in quote.text_frame.paragraphs:
    p.alignment = PP_ALIGN.LEFT
TY = T + 2.55
H = B - TY
W = H * 0.5625
for i, t in enumerate(thumbs):
    place(t, x=L + i * (W + 0.22), y=TY, w=W, h=H)
place(acct, x=L + 0.35, y=B - 0.95)
sx = L + 3 * W + 2 * 0.22 + 0.8
panel(s, sx, T, R - sx, B - T)
place(tags["Support"], x=sx + 0.6, y=T + 0.5)
tiles = sorted(by_name(s, "로고 타일"), key=lambda x: (round(cm(x.top), 1), x.left))
_lg = [x for x in s.shapes if x.shape_type == 13 and x.name.startswith("Picture")]
def _inside(t):
    cx, cy = t.left + t.width // 2, t.top + t.height // 2
    return min(_lg, key=lambda g: abs(g.left + g.width // 2 - cx) + abs(g.top + g.height // 2 - cy))
logos = [_inside(t) for t in tiles]
tw = (R - sx - 1.2 - 0.3) / 2
ty0 = T + 1.45
th = (B - 0.6 - ty0 - 4 * 0.25) / 5
for k, (t, lg) in enumerate(zip(tiles, logos)):
    x = sx + 0.6 + (k % 2) * (tw + 0.3)
    y = ty0 + (k // 2) * (th + 0.25)
    ox, oy = cm(lg.left) - cm(t.left), cm(lg.top) - cm(t.top)
    lw, lh = cm(lg.width), cm(lg.height)
    place(t, x, y, tw, th)
    t.fill.solid(); t.fill.fore_color.rgb = RGBColor(255, 255, 255)
    sc = min((tw - 0.8) / lw, (th - 0.6) / lh, 1.2)
    place(lg, x + (tw - lw * sc) / 2, y + (th - lh * sc) / 2, lw * sc, lh * sc)

prs.save(OUT)
print("저장", OUT)
