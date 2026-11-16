import sys
sys.stdout.reconfigure(encoding="utf-8")
from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Cm, Pt
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
W9 = r"C:\Users\admin\클로드\output\ir-project-moment\v4\work9"
prs = Presentation(sys.argv[1])
s = prs.slides[14]
for sh in list(s.shapes):
    if sh.name in ("기부 문구",) or "목업" in sh.name or sh.name == "기부 사진":
        sh._element.getparent().remove(sh._element)
don = min([x for x in s.shapes if x.name.startswith("직사각형")], key=lambda x: x.left)
bx, by, bw, bh = (v / 360000 for v in (don.left, don.top, don.width, don.height))

def rounded(pic, r=0.3):
    pic.auto_shape_type = MSO_SHAPE.ROUNDED_RECTANGLE
    g = pic._element.spPr.find(f"{{{A}}}prstGeom")
    av = g.find(f"{{{A}}}avLst")
    if av is None: av = etree.SubElement(g, f"{{{A}}}avLst")
    av.clear(); gd = etree.SubElement(av, f"{{{A}}}gd"); gd.set("name", "adj")
    gd.set("fmla", f"val {int(r * 360000 / min(pic.width, pic.height) * 100000)}")

tiles = [("s15_52.png", "기부 영상"), ("s15_57.png", "기부 후기 피드"), ("s15_49.png", "기부 사진")]
ar = [Image.open(f"{W9}\{f}").width / Image.open(f"{W9}\{f}").height for f, _ in tiles]
GAP = 0.2
top = by + 1.4
qh = 1.35
H = (by + bh - 0.5 - qh - 0.35) - top
W = sum(a * H for a in ar) + GAP * 2
if W > bw - 1.14:
    H = (bw - 1.14 - GAP * 2) / sum(ar); W = bw - 1.14
x = bx + (bw - W) / 2
for (f, nm), a in zip(tiles, ar):
    p = s.shapes.add_picture(f"{W9}\{f}", Cm(x), Cm(top), Cm(a * H), Cm(H)); p.name = nm
    rounded(p)
    if "피드" in nm:
        p.line.color.rgb = RGBColor(0xE8, 0xEB, 0xEF); p.line.width = Pt(0.75)
    x += a * H + GAP
# 문구: 피드 아래 캡션처럼 가운데
tb = s.shapes.add_textbox(Cm(bx + 0.57), Cm(top + H + 0.35), Cm(bw - 1.14), Cm(qh)); tb.name = "기부 문구"
tf = tb.text_frame
tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.TOP
for i, t in enumerate(["“사랑으로 성장하고 현재에 감사하며 어제보다 행복한 내일을 꿈꾸는", "건강하고 아름다운 사회를 소망합니다.”"]):
    pp = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    pp.alignment = PP_ALIGN.CENTER; pp.line_spacing = 1.2
    r = pp.add_run(); r.text = t
    r.font.name = "Pretendard SemiBold"; r.font.size = Pt(14); r.font.color.rgb = RGBColor(0x45, 0x4C, 0x56)
    rpr = r._r.get_or_add_rPr()
    for tag in ("ea", "cs"):
        el = etree.SubElement(rpr, f"{{{A}}}{tag}"); el.set("typeface", "Pretendard SemiBold")
prs.save(sys.argv[2]); print("ok", round(H, 2))
