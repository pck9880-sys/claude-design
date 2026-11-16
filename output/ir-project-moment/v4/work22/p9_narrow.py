import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\admin\클로드\output\ir-project-moment\v4\work17")
import design17 as d
from pptx import Presentation
from pptx.util import Cm
prs = Presentation(sys.argv[1]); s = prs.slides[8]
d.ungroup(s)
cm = d.cm
X_OLD0, X_OLD1 = 1.55, 1.55 + 30.9
X_NEW0, X_NEW1 = 8.25, 32.34
k = (X_NEW1 - X_NEW0) / (X_OLD1 - X_OLD0)
for sh in s.shapes:
    if sh.top is None or cm(sh.top) < 4.5:
        continue
    x, w = cm(sh.left), cm(sh.width)
    sh.left = Cm(X_NEW0 + (x - X_OLD0) * k)
    if sh.shape_type == 13 or sh.name in ("화살표",) or sh.shape_type == 5:
        sh.left = Cm(X_NEW0 + (x + w / 2 - X_OLD0) * k - w / 2)   # 그림·화살표는 비율 유지
    else:
        sh.width = Cm(w * k)
from pptx.util import Pt
for sh in s.shapes:
    if sh.has_text_frame and sh.top is not None and cm(sh.left) >= 20.0 and cm(sh.top) > 5.5:
        sh.width = Cm(32.34 - cm(sh.left) - 0.1)
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                if r.font.size: r.font.size = Pt(r.font.size.pt - 1)
d.drop_slides(prs, {9})
prs.save(sys.argv[2]); print("ok k=", round(k, 3))
