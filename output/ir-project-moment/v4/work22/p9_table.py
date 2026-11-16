import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\admin\클로드\output\ir-project-moment\v4\work17")
import design17 as d
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.util import Cm, Pt
GEN = r"C:\Users\admin\클로드\assets\generated"
prs = Presentation(sys.argv[1]); s = prs.slides[0]; cm = d.cm
L, R, TOP, BOT = 1.53, 32.34, 5.77, 17.52
C1, C2, C3, C4 = (L, 5.4), (7.25, 5.3), (13.05, 5.6), (19.0, R - 19.0)
rh = (BOT - TOP) / 4
for sh in list(s.shapes):
    if sh.name in ("화살표", "구분선"): d.remove(sh)
def col(name):
    return sorted([x for x in s.shapes if x.name == name and x.shape_type == 17], key=lambda x: x.top)
for i, (m, a, t) in enumerate(zip(col("성장 모멘텀"), col("As-Is"), col("To-Be"))):
    y = TOP + i * rh
    for sh, (x, w), pad in ((m, C1, 0), (a, C3, 0), (t, (C4[0] + 0.45, C4[1] - 0.6), 0)):
        sh.left, sh.top, sh.width, sh.height = Cm(x), Cm(y), Cm(w), Cm(rh)
        tf = sh.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_top = tf.margin_bottom = 0
    for p in t.text_frame.paragraphs:
        p.line_spacing = 1.0
        for r in p.runs: r.font.size = Pt(10)
    pic = s.shapes.add_picture(f"{GEN}/pm-ir-v19-p9-{['channel','marketing','global','product'][i]}.png",
                               Cm(C2[0]), Cm(y + 0.25), Cm(C2[1]), Cm(rh - 0.5))
    pic.name = "모멘텀 사진"
    ar = (C2[1]) / (rh - 0.5); iw, ih = 1536, 1024
    if iw / ih > ar:
        c = (1 - ar * ih / iw) / 2; pic.crop_left = pic.crop_right = c
    else:
        c = (1 - iw / ar / ih) / 2; pic.crop_top = pic.crop_bottom = c
for k in range(5):
    y = TOP + k * rh
    ln = d.line(s, L, y, R, y, RGBColor(0x1A, 0x1A, 0x1A) if k in (0, 4) else RGBColor(0xC8, 0xCB, 0xD0), 0.5, name="구분선")
    ln.line.dash_style = MSO_LINE_DASH_STYLE.SOLID
bg = [x for x in s.shapes if x.name == "To-Be 배경"][0]
bg.left, bg.top, bg.width, bg.height = Cm(C4[0]), Cm(TOP), Cm(C4[1]), Cm(BOT - TOP)
for x in s.shapes:
    if x.name == "태그":
        t = x.text_frame.text.strip()
        x.left = Cm({"성장 모멘텀": C1[0], "As-Is": C3[0], "To-Be": C4[0] + 0.45}[t])
prs.save(sys.argv[2]); print("ok")
