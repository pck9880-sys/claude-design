import sys, io
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
from PIL import Image
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Cm
prs = Presentation("프로젝트모먼트_IR_1차시안_v9.pptx")
s = prs.slides[6]
g = next(sh for sh in s.shapes if sh.shape_type == 6)
pics = {c.shape_id: c for c in g.shapes if c.shape_type == 13}
GAP = 0.27
X0, X1, Y0, Y1 = 15.45, 31.85, 9.40, 16.58

from lxml import etree
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
def round_(p, r_cm=0.25):
    p.auto_shape_type = MSO_SHAPE.ROUNDED_RECTANGLE
    geom = p._element.spPr.find(f"{{{A}}}prstGeom")
    av = geom.find(f"{{{A}}}avLst")
    if av is None:
        av = etree.SubElement(geom, f"{{{A}}}avLst")
    av.clear()
    gd = etree.SubElement(av, f"{{{A}}}gd"); gd.set("name", "adj")
    gd.set("fmla", f"val {int(r_cm * 360000 / min(p.width, p.height) * 100000)}")

def place(p, x, y, w, h, trim=False, ax=0.5):
    im = Image.open(io.BytesIO(p.image.blob)).convert("RGB")
    a = np.asarray(im).astype(int)
    l, t, r, b = 0, 0, im.width, im.height
    if trim:  # 사진 바깥 회색 여백 잘라내기
        bg = a[2, 2]
        diff = np.abs(a - bg).sum(axis=2) > 30
        ys, xs = np.where(diff)
        l, t, r, b = xs.min() + 2, ys.min() + 2, xs.max() - 2, ys.max() - 2
    cw, ch = r - l, b - t
    tgt = w / h
    if cw / ch > tgt:
        nw = ch * tgt; l += (cw - nw) * ax; r = l + nw
    else:
        nh = cw / tgt; t += (ch - nh) / 2; b = t + nh
    p.crop_left, p.crop_right = l / im.width, 1 - r / im.width
    p.crop_top, p.crop_bottom = t / im.height, 1 - b / im.height
    p.left, p.top, p.width, p.height = Cm(x), Cm(y), Cm(w), Cm(h)
    round_(p)

H = Y1 - Y0
side_w = 4.6
main_w = (X1 - X0) - side_w - GAP
place(pics[24], X0, Y0, main_w, H, trim=True, ax=1.0)
sx = X0 + main_w + GAP
top_h = side_w / 2.07
place(pics[25], sx, Y0, side_w, top_h)
bw = (side_w - GAP) / 2
bh = H - top_h - GAP
place(pics[26], sx, Y0 + top_h + GAP, bw, bh, trim=True)
place(pics[27], sx + bw + GAP, Y0 + top_h + GAP, bw, bh)
# 왼쪽 이미지도 같은 라운드로 통일
for sid in (17, 18, 19, 20, 21, 22, 23):
    p = pics[sid]
    round_(p)
prs.save("프로젝트모먼트_IR_1차시안_v10.pptx")
print("ok")

# 로고 타일: 잘리지 않게 검은 바탕 위 가운데 배치한 새 이미지로 교체
p = pics[26]
im = Image.open(io.BytesIO(p.image.blob)).convert("RGB")
a = np.asarray(im).astype(int)
ys, xs = np.where(np.abs(a - a[2, 2]).sum(axis=2) > 30)
tile = im.crop((xs.min() + 6, ys.min() + 6, xs.max() - 6, ys.max() - 6))
bx, by, bw_, bh_ = p.left, p.top, p.width, p.height
PX = 400
canvas = Image.new("RGB", (PX, int(PX * bh_ / bw_)), tuple(int(v) for v in np.asarray(tile)[5, 5]))
TW = int(PX * 0.8); t = tile.resize((TW, int(tile.height * TW / tile.width)), Image.LANCZOS)
canvas.paste(t, ((PX - TW) // 2, (canvas.height - t.height) // 2))
canvas.save("work9/p7_logo_tile.png")
p._element.getparent().remove(p._element)
np_ = s.shapes.add_picture("work9/p7_logo_tile.png", bx, by, bw_, bh_)
np_.name = "owooii 로고 타일"
round_(np_)
prs.save("프로젝트모먼트_IR_1차시안_v10.pptx")
print("logo ok")
