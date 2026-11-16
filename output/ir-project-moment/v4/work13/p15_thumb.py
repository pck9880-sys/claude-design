import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Cm, Pt
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
W9 = "C:/Users/admin/클로드/output/ir-project-moment/v4/work9/"
OUTD = "C:/Users/admin/클로드/output/ir-project-moment/v4/work13/"
R = 9 / 16

def thumb(src, out, ax=0.5, ay=0.5, grad=True):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    if w / h > R:
        nw = int(h * R); l = int((w - nw) * ax); im = im.crop((l, 0, l + nw, h))
    else:
        nh = int(w / R); t = int((h - nh) * ay); im = im.crop((0, t, w, t + nh))
    im = im.resize((540, 960), Image.LANCZOS)
    a = np.asarray(im).astype(float)
    g = np.zeros(960); s0 = int(960 * 0.62)
    g[s0:] = np.linspace(0, 0.72, 960 - s0) ** 1.2
    if grad:
        a = a * (1 - g[:, None, None])
    Image.fromarray(a.astype("uint8")).save(out, quality=93)
    return out

prs = Presentation(sys.argv[1])
s = prs.slides[14]
old = {x.name: x for x in s.shapes if x.name in ("기부 영상", "기부 후기 피드", "기부 사진")}
H, top = 9.05, 6.25
don = min([x for x in s.shapes if x.name.startswith("직사각형")], key=lambda x: x.left)
bx, bw = don.left / 360000, don.width / 360000
for x in old.values():
    x._element.getparent().remove(x._element)
items = [("s15_52.png", "기부 영상", 0.5, 0.35, "@via_flower"),
         ("s15_57.png", "기부 후기", 0.5, 0.0, ""),
         ("s15_49.png", "기부 사진", 0.22, 0.5, "")]
W = H * R
GAP = 0.35
x = bx + (bw - (W * 3 + GAP * 2)) / 2
for f, nm, ax, ay, handle in items:
    p_img = thumb(W9 + f, OUTD + f"thumb_{f[:-4]}.jpg", ax, ay, grad=("후기" not in nm))
    p = s.shapes.add_picture(p_img, Cm(x), Cm(top), Cm(W), Cm(H)); p.name = f"{nm} 썸네일"
    p.auto_shape_type = MSO_SHAPE.ROUNDED_RECTANGLE
    gm = p._element.spPr.find(f"{{{A}}}prstGeom")
    av = gm.find(f"{{{A}}}avLst")
    if av is None: av = etree.SubElement(gm, f"{{{A}}}avLst")
    av.clear(); gd = etree.SubElement(av, f"{{{A}}}gd"); gd.set("name", "adj"); gd.set("fmla", f"val {int(0.35 / W * 100000)}")
    if "후기" in nm:
        p.line.color.rgb = RGBColor(0xE8, 0xEB, 0xEF); p.line.width = Pt(0.75)
    if handle:
        tb = s.shapes.add_textbox(Cm(x + 0.35), Cm(top + H - 0.95), Cm(W - 0.7), Cm(0.55)); tb.name = "썸네일 계정"
        tf = tb.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.BOTTOM
        r = tf.paragraphs[0].add_run(); r.text = handle
        r.font.name = "Pretendard SemiBold"; r.font.size = Pt(11); r.font.color.rgb = RGBColor(255, 255, 255)
        rpr = r._r.get_or_add_rPr()
        for tag in ("ea", "cs"):
            etree.SubElement(rpr, f"{{{A}}}{tag}").set("typeface", "Pretendard SemiBold")
    x += W + GAP
prs.save(sys.argv[2]); print("ok", round(W, 2), round(H, 2))
