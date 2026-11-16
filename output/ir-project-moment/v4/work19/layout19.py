"""v19: 버건디 포인트, 2·4p 얇은 알약, 5p 검정 아이콘, 7p 잡지형 모자이크, 8p 목업 확대·알약,
9p 생성 이미지, 11p 연결 배치, 12p 면 박스."""
import io
import subprocess
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import numpy as np
from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Cm, Pt, Emu

HERE = Path(__file__).parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / "work17"))
import design17 as d  # noqa: E402

SRC, OUT = sys.argv[1], sys.argv[2]
TMP = HERE / "_recolor.pptx"
subprocess.run([sys.executable, str(ROOT / "tools/recolor_pptx.py"), SRC, str(TMP),
                "1C5470=8E2430", "123A4F=5E1620", "BCD3DD=DDB8BE", "7FA3B3=B97A84",
                "E3EEF2=F6ECEE", "EEF4F6=F8F0F1", "5F8799=B5646F"], check=True)
prs = Presentation(TMP)
SL = list(prs.slides)
BUR = RGBColor(0x8E, 0x24, 0x30)
INK = RGBColor(0x1A, 0x1A, 0x1A)
PANEL = RGBColor(0xF4, 0xF5, 0xF7)
WHITE = RGBColor(255, 255, 255)
L, R, T, B = 1.53, 32.34, 5.0, 17.52
SH = 19.05
GEN = ROOT / "assets/generated"
ICON = HERE / "icons"
cm = d.cm


def place(sh, x=None, y=None, w=None, h=None):
    if x is not None: sh.left = Cm(x)
    if y is not None: sh.top = Cm(y)
    if w is not None: sh.width = Cm(w)
    if h is not None: sh.height = Cm(h)


def move(sh, dx=0, dy=0):
    sh.left = sh.left + Cm(dx); sh.top = sh.top + Cm(dy)


def to_back(s, sh):
    s.shapes._spTree.remove(sh._element); s.shapes._spTree.insert(2, sh._element)


def pill(s, x, y, text, filled=False, size=10, h=0.62):
    w = d.tw(text, size, "Bold") + 0.75
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Cm(x), Cm(y), Cm(w), Cm(h))
    sh.adjustments[0] = 0.5; sh.name = "알약"
    if filled:
        sh.fill.solid(); sh.fill.fore_color.rgb = BUR; sh.line.fill.background()
    else:
        sh.fill.background(); sh.line.color.rgb = BUR; sh.line.width = Pt(0.5)
    tf = sh.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE; tf.word_wrap = False
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = text; d.setfont(r, "Pretendard Bold", size, WHITE if filled else BUR, 20)
    return sh, w


def uncrop(p):
    p.crop_left = p.crop_right = p.crop_top = p.crop_bottom = 0
    p.auto_shape_type = MSO_SHAPE.RECTANGLE


def ratio(p):
    im = Image.open(io.BytesIO(p.image.blob))
    return im.width / im.height


def trim_white(p):
    im = Image.open(io.BytesIO(p.image.blob)).convert("RGB")
    a = np.asarray(im).astype(int)
    m = a.min(axis=2) < 240
    rows = np.where(m.mean(axis=1) > 0.02)[0]; cols = np.where(m.mean(axis=0) > 0.02)[0]
    l, t, r, b = cols.min(), rows.min(), cols.max() + 1, rows.max() + 1
    p.crop_left, p.crop_right = l / im.width, 1 - r / im.width
    p.crop_top, p.crop_bottom = t / im.height, 1 - b / im.height
    p.auto_shape_type = MSO_SHAPE.RECTANGLE
    return (r - l) / (b - t)


def cover(p, x, y, w, h):
    im = Image.open(io.BytesIO(p.image.blob))
    iw, ih = im.size
    if iw / ih > w / h:
        nw = ih * w / h; c = (iw - nw) / 2 / iw
        p.crop_left = p.crop_right = c; p.crop_top = p.crop_bottom = 0
    else:
        nh = iw * h / w; c = (ih - nh) / 2 / ih
        p.crop_top = p.crop_bottom = c; p.crop_left = p.crop_right = 0
    place(p, x, y, w, h)


def swap_pic(s, old, path, name=None):
    pic = s.shapes.add_picture(str(path), old.left, old.top, old.width, old.height)
    pic.name = name or old.name
    old._element.addprevious(pic._element); d.remove(old)
    return pic


# ---------------- 2p: Case 얇은 알약 ----------------
s = SL[1]
for sh in list(s.shapes):
    if sh.has_text_frame and sh.text_frame.text.strip() in ("Case. 01", "Case. 02"):
        y = cm(sh.top); t = sh.text_frame.text.strip()
        d.remove(sh)
        pill(s, L, y + 0.05, t)

# ---------------- 4p: 얇은 알약 ----------------
s = SL[3]
for sh in list(s.shapes):
    if sh.has_text_frame and sh.text_frame.text.strip() in ("NURTURE", "FILIAL PIETY", "CARE", "BOND"):
        x, y, t = cm(sh.left), cm(sh.top), sh.text_frame.text.strip()
        d.remove(sh)
        pill(s, x, y, t)

# ---------------- 5p: Point 삭제, 검정 아이콘 + 타이틀 ----------------
s = SL[4]
for sh in list(s.shapes):
    if sh.has_text_frame and sh.text_frame.text.strip().startswith("Point."):
        d.remove(sh)
icons = {sh.name.split(" ", 1)[1]: sh for sh in s.shapes if sh.name.startswith("아이콘 ")}
titles = sorted([sh for sh in s.shapes if sh.has_text_frame and sh.text_frame.text.strip() in
                 ("BLDC 듀얼 고속 모터", "저소음 및 NTC 스마트 센서", "FUNCTIONALITY")], key=lambda x: x.left)
descs = sorted([sh for sh in s.shapes if sh.name in ("TextBox 24", "TextBox 25", "TextBox 26")], key=lambda x: x.left)
for (ic, tt, ds) in zip(("fan", "volume-x", "sliders-horizontal"), titles, descs):
    x = cm(tt.left)
    old = icons[ic]
    pic = swap_pic(s, old, ICON / f"k-{ic}.png", f"아이콘 {ic}")
    place(pic, x, T + 0.12, 0.62, 0.62)
    place(tt, x=x + 0.85, y=T)
    place(ds, y=T + 1.0)

# ---------------- 7p: 잡지형 모자이크 (자르기·라운드 없음) ----------------
s = SL[6]
pics = {sh.shape_id: sh for sh in s.shapes if sh.shape_type == 13}
copy_ids = [17, 18, 19, 20, 21, 22, 23]
X0, W = 12.2, R - 12.2
G = 0.2
cps = [pics[i] for i in copy_ids]
for p in cps:
    uncrop(p)
ars = [ratio(p) for p in cps]
hc = (W - G * 6) / sum(ars)
x = X0
CY = T + 0.65
for p, a in zip(cps, ars):
    place(p, x, CY, a * hc, hc); x += a * hc + G
main, land, port, logo = pics[6], pics[8], pics[10], pics[94]
am = trim_white(main)
for p in (land, port, logo):
    uncrop(p)
al, ap, alo = ratio(land), ratio(port), ratio(logo)
# 왼쪽 메인 높이 H, 오른쪽 열 = 가로 사진 위 + 세로·로고 아래
k1 = 1 / al + 1 / (ap + alo)
H = (W - G + G / (ap + alo) * 0 + (G - G / (ap + alo)) / k1 * 0)
# 폭 식: am*H + G + w = W,  w/al + G + (w-G)/(ap+alo) = H
w = (W - G - am * (G - G / (ap + alo))) / (1 + am * k1)
H = w / al + G + (w - G) / (ap + alo)
oy = B - H
place(main, X0, oy, am * H, H)
rx = X0 + am * H + G
place(land, rx, oy, w, w / al)
hb = (w - G) / (ap + alo)
place(port, rx, oy + w / al + G, ap * hb, hb)
place(logo, rx + ap * hb + G, oy + w / al + G, alo * hb, hb)
for sh in s.shapes:
    if sh.name == "이미지 라벨" and sh.text_frame.text.strip() == "owooii":
        place(sh, y=oy - 0.65)
    if sh.name == "선" and abs(cm(sh.top) - 9.9) < 0.1:
        place(sh, y=oy - 0.4)
    if sh.name == "이미지 라벨" and "카피캣" in sh.text_frame.text:
        place(sh, y=T)
    if sh.name == "선" and abs(cm(sh.top) - 5.25) < 0.1:
        place(sh, y=T + 0.25)

# ---------------- 8p: 목업 확대(하단 붙임) + 알약 ----------------
s = SL[7]
OW = 18.6
phones = sorted([sh for sh in s.shapes if "목업 phone" in sh.name], key=lambda x: x.left)
browser = [sh for sh in s.shapes if "목업 browser" in sh.name][0]
# 브라우저 목업은 왼쪽(사진) 부분만 보이게 자름
bar_b = ratio(browser)
browser.crop_left, browser.crop_right = 0, 0.42
ab = bar_b * 0.58
ap_ = cm(phones[0].width) / cm(phones[0].height)
GG = 0.3
Hm = (OW - GG * 4) / (ap_ * 4 + ab)
top = SH - Hm
x = L
for p in phones:
    place(p, x, top, ap_ * Hm, Hm); p.name = "bleed:" + p.name; x += ap_ * Hm + GG
place(browser, x, top, ab * Hm, Hm); browser.name = "bleed:" + browser.name
for sh in list(s.shapes):
    if sh.name == "태그":
        t = sh.text_frame.text.strip(); y = cm(sh.top); xx = cm(sh.left)
        d.remove(sh)
        pill(s, xx, y, t, filled=True, size=10.5, h=0.66)
    if sh.name == "구분선" and cm(sh.left) < 5:
        place(sh, w=OW)
    if sh.name == "Online 본문":
        place(sh, w=OW)
# 오프라인 열: 오른쪽으로 좁혀 이동
OX = L + OW + 1.6
old_x0, old_w = 20.04, 11.85
sc = (R - OX) / old_w
for sh in s.shapes:
    if cm(sh.left) >= 20.0 and cm(sh.top) > 4.5:
        nx = OX + (cm(sh.left) - old_x0) * sc
        if sh.shape_type == 13 or sh.name.startswith("Rounded"):
            place(sh, nx, T + (cm(sh.top) - T) * 1.0, cm(sh.width) * sc, cm(sh.height) * sc)
        else:
            place(sh, x=nx, w=cm(sh.width) * sc if sh.name != "알약" else None)
for sh in s.shapes:
    if sh.name == "화살표":
        place(sh, x=L + OW + 0.38)

# ---------------- 9p: 아이콘 삭제, 하단 생성 이미지 ----------------
s = SL[8]
for sh in list(s.shapes):
    if sh.name.startswith("아이콘 "):
        d.remove(sh)
cols = sorted([sh for sh in s.shapes if sh.name == "성장 모멘텀"], key=lambda x: x.left)
tobe = sorted([sh for sh in s.shapes if sh.name == "To-Be"], key=lambda x: x.left)
asis = sorted([sh for sh in s.shapes if sh.name == "As-Is"], key=lambda x: x.left)
xs = [cm(a.left) for a in asis]
cw = cm(asis[0].width) - 0.15
IH = 3.4
for sh, x in zip(cols, xs):
    place(sh, x=x, w=cw)
    for p in sh.text_frame.paragraphs:
        for r in p.runs:
            r.font.size = Pt(15)
for sh in tobe:
    for p in sh.text_frame.paragraphs:
        p.line_spacing = 1.25
        for r in p.runs:
            r.font.size = Pt(10)
    place(sh, h=B - IH - 0.35 - cm(sh.top))
for x, f in zip(xs, ("channel", "marketing", "global", "product")):
    p = s.shapes.add_picture(str(GEN / f"pm-ir-v19-p9-{f}.png"), Cm(x), Cm(B - IH), Cm(cw), Cm(IH))
    p.name = f"생성 이미지 {f}"
    cover(p, x, B - IH - 0.25, cw, IH)

# ---------------- 11p: 두 이미지가 맞닿게, 가운데 & ----------------
s = SL[10]
img_d = [sh for sh in s.shapes if sh.name == "그림 6"][0]
img_c = [sh for sh in s.shapes if sh.name == "그림 7"][0]
amp = [sh for sh in s.shapes if sh.name == "&"][0]
HH = B - T
ad, ac = cm(img_d.width) / cm(img_d.height), cm(img_c.width) / cm(img_c.height)
wd, wc = ad * HH, ac * HH
TW = (R - L - wd - wc - 1.6) / 2
xd = L + TW + 0.8
xc = xd + wd
left_items, right_items = [], []
for sh in s.shapes:
    if sh in (img_d, img_c, amp) or cm(sh.top) < 4.5:
        continue
    (left_items if cm(sh.left) < 17 else right_items).append(sh)
lx0 = min(cm(x.left) for x in left_items)
rx0 = min(cm(x.left) for x in right_items)
for sh in left_items:
    move(sh, dx=L - lx0)
for sh in right_items:
    move(sh, dx=(xc + wc + 0.8) - rx0)
for sh in left_items + right_items:
    if sh.has_text_frame and sh.width > Cm(TW):
        sh.width = Cm(TW)
place(img_d, xd, T, wd, HH); place(img_c, xc, T, wc, HH)
img_d.auto_shape_type = MSO_SHAPE.RECTANGLE; img_c.auto_shape_type = MSO_SHAPE.RECTANGLE
D = 1.5
place(amp, xc - D / 2, T + HH / 2 - D / 2, D, D)
amp.fill.solid(); amp.fill.fore_color.rgb = BUR
amp.line.color.rgb = WHITE; amp.line.width = Pt(2.5)
for p in amp.text_frame.paragraphs:
    for r in p.runs:
        r.font.size = Pt(20); r.font.color.rgb = WHITE
s.shapes._spTree.remove(amp._element); s.shapes._spTree.append(amp._element)
for sh in list(s.shapes):
    if sh.name.startswith("아이콘 "):
        nm = sh.name.split(" ", 1)[1]
        if (ICON / f"b-{nm}.png").exists():
            swap_pic(s, sh, ICON / f"b-{nm}.png")

# ---------------- 12p: 아이콘 삭제, 면 박스로 분리 ----------------
s = SL[11]
for sh in list(s.shapes):
    if sh.name.startswith("아이콘 "):
        d.remove(sh)
PW = (R - L - 0.5) / 2
for i in range(2):
    pn = d.rect(s, L + i * (PW + 0.5), T, PW, B - T, PANEL, "면 박스"); to_back(s, pn)
for sh in s.shapes:
    if sh.name == "면 박스" or cm(sh.top) < 4.5:
        continue
    if cm(sh.left) < 17:
        move(sh, dx=0.6, dy=0.5)
    else:
        move(sh, dx=(L + PW + 0.5 + 0.6) - 17.89, dy=0.5)
for sh in s.shapes:
    if sh.name == "태그":
        sh.left = Cm(L + 0.6) if cm(sh.left) < 17 else Cm(L + PW + 0.5 + 0.6)

prs.save(OUT)
TMP.unlink()
print("저장", OUT)
