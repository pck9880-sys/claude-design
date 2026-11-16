import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\admin\클로드\output\ir-project-moment\v4\work17")
import design17 as d
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Cm, Pt
BUR = RGBColor(0x8E, 0x24, 0x30); G1 = RGBColor(0x5B, 0x62, 0x70)
prs = Presentation(sys.argv[1]); s = prs.slides[7]
cm = d.cm
for sh in list(s.shapes):
    if sh.name == "화살표": d.remove(sh)
g = [x for x in s.shapes if x.name == "그룹 2"][0]
k = 0.86
bot = cm(g.top) + cm(g.height)
w, h = cm(g.width) * k, cm(g.height) * k
g.width, g.height = Cm(w), Cm(h); g.top = Cm(bot - h)
for x in s.shapes:
    if x.name == "Online 본문": x.width = Cm(w)
cx, cy, D = (1.53 + w + 21.73) / 2, 11.35, 3.2
ring = s.shapes.add_shape(MSO_SHAPE.OVAL, Cm(cx - D/2), Cm(cy - D/2), Cm(D), Cm(D))
ring.fill.background(); ring.line.color.rgb = BUR; ring.line.width = Pt(1.6); ring.name = "순환 링"
inner = s.shapes.add_shape(MSO_SHAPE.OVAL, Cm(cx - 1.05), Cm(cy - 1.05), Cm(2.1), Cm(2.1))
inner.fill.solid(); inner.fill.fore_color.rgb = BUR; inner.line.fill.background(); inner.name = "순환 중심"
tf = inner.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
for i, t in enumerate(("FLYING", "WHEEL")):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.alignment = PP_ALIGN.CENTER; p.line_spacing = 1.0
    r = p.add_run(); r.text = t; d.setfont(r, "Pretendard ExtraBold", 9, RGBColor(255, 255, 255))
for y, rot in ((cy - D/2, 90), (cy + D/2, 270)):
    a = s.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, Cm(cx - 0.22), Cm(y - 0.2), Cm(0.44), Cm(0.4))
    a.rotation = rot; a.fill.solid(); a.fill.fore_color.rgb = BUR; a.line.fill.background(); a.name = "순환 화살촉"
for y, t in ((cy - D/2 - 1.0, "인지도 · 초기 수요"), (cy + D/2 + 0.4, "경험 · 브랜드 충성도")):
    d.text(s, cx - 2.3, y, 4.6, 0.55, [[(t, "Pretendard SemiBold", 9.5, G1)]], PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, "순환 라벨", wrap=False)
d.drop_slides(prs, {8})
prs.save(sys.argv[2]); print("ok", round(cx, 2))
