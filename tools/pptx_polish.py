"""기존 PPTX 부분 디벨롭 도구 모음 (원본 스타일 유지).

  logos   <in> <out> --slide 8 --names "그림 36,그림 37,..." [--tile F4F4F5]
          로고 배경을 투명하게 따고(누끼), 같은 크기의 옅은 타일 위에 가운데 정렬
  bullets <in> <out> [--from "+"] [--to "•"]
          문단 앞의 '+' 표시를 원형 글머리로 (색은 그대로)
  padding <in> <out> --pdf <렌더 PDF> [--pad-cm 0.6]
          두꺼운 테두리 상자마다 안쪽 아래 여백을 위 여백 기준으로 통일 (같은 줄 상자는 높이 맞춤)
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")
import argparse
import io

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Cm, Emu


def knockout(blob, tol=28):
    """가장자리에서 이어진 배경색(흰색·회색)을 투명하게."""
    from PIL import Image
    im = Image.open(io.BytesIO(blob)).convert("RGBA")
    w, h = im.size
    px = im.load()
    corners = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
    bg = tuple(sorted(c[i] for c in corners)[1] for i in range(3))
    seen = set()
    stack = [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
    near = lambda c: abs(c[0] - bg[0]) + abs(c[1] - bg[1]) + abs(c[2] - bg[2]) <= tol * 3 and c[3] > 0
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or not (0 <= x < w and 0 <= y < h):
            continue
        seen.add((x, y))
        if near(px[x, y]):
            px[x, y] = (255, 255, 255, 0)
            stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    out = io.BytesIO()
    im.save(out, "PNG")
    return out.getvalue(), im.size


def cmd_logos(a):
    prs = Presentation(a.inp)
    s = prs.slides[a.slide - 1]
    names = [n.strip() for n in a.names.split(",")]
    pics = [sh for sh in s.shapes if sh.name in names]
    if not pics:
        _sys.exit("로고를 못 찾음")
    xs = sorted({round(Emu(p.left).cm, 0) for p in pics})
    left = min(p.left for p in pics)
    right = max(p.left + p.width for p in pics)
    top = min(p.top for p in pics)
    bottom = max(p.top + p.height for p in pics)
    rows = sorted({round(Emu(p.top).cm, 0) for p in pics})
    ncol = max(len([p for p in pics if round(Emu(p.top).cm, 0) == r]) for r in rows)
    nrow = len(rows)
    gap = Cm(0.25)
    tile_w = int((right - left - gap * (ncol - 1)) / ncol)
    tile_h = int(min(Cm(1.15), (bottom - top + Cm(0.3) - gap * (nrow - 1)) / nrow))
    order = sorted(pics, key=lambda p: (round(Emu(p.top).cm, 0), p.left))
    col = RGBColor.from_string(a.tile)
    for i, p in enumerate(order):
        r, c = divmod(i, ncol)
        tx, ty = int(left + c * (tile_w + gap)), int(top - Cm(0.15) + r * (tile_h + gap))
        tile = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, tx, ty, tile_w, tile_h)
        tile.adjustments[0] = 0.12
        tile.fill.solid(); tile.fill.fore_color.rgb = col
        tile.line.fill.background(); tile.shadow.inherit = False
        st = tile._element.find("{http://schemas.openxmlformats.org/presentationml/2006/main}style")
        if st is not None:
            tile._element.remove(st)
        blob, (iw, ih) = knockout(p.image.blob)
        maxw, maxh = tile_w * 0.78, tile_h * 0.55
        k = min(maxw / iw, maxh / ih)
        w, h = int(iw * k), int(ih * k)
        newp = s.shapes.add_picture(io.BytesIO(blob), tx + (tile_w - w) // 2, ty + (tile_h - h) // 2, w, h)
        newp.name = p.name + " (누끼)"
        p._element.getparent().remove(p._element)
    prs.save(a.out)
    print(f"로고 {len(order)}개 누끼 + 타일({ncol}×{nrow}) 정렬")


def cmd_bullets(a):
    from pptx.oxml.ns import qn
    prs = Presentation(a.inp)
    n = 0
    for s in prs.slides:
        for sh in s.shapes:
            if not sh.has_text_frame:
                continue
            for p in sh.text_frame.paragraphs:
                runs = p.runs
                if not runs:
                    continue
                first = runs[0]
                t = first.text
                import re as _re
                if _re.match(r"^\s*" + _re.escape(a.frm) + r"(?!\s*\d)", t):     # +197% 같은 숫자는 제외
                    first.text = t.replace(a.frm, a.to, 1)
                    n += 1
    prs.save(a.out)
    print(f"'{a.frm}' → '{a.to}' {n}곳")


def cmd_padding(a):
    import pymupdf
    prs = Presentation(a.inp)
    W, H = prs.slide_width, prs.slide_height
    doc = pymupdf.open(a.pdf)
    pad_min = Cm(a.pad_cm)
    changed = 0
    for si, s in enumerate(prs.slides):
        page = doc[si]
        sx, sy = page.rect.width / W, page.rect.height / H
        boxes = [sh for sh in s.shapes if sh.shape_type == 1 and sh.line.fill.type is not None
                 and sh.line.width and sh.line.width >= Emu(12700 * 1.2) and sh.width > W * 0.15 and sh.height > H * 0.15]
        if not boxes:
            continue
        items = [b[:4] for b in page.get_text("blocks")]
        for img in page.get_image_info():
            items.append(tuple(img["bbox"]))
        for dr in page.get_drawings():
            r = dr["rect"]
            if r.width < page.rect.width * 0.9:
                items.append((r.x0, r.y0, r.x1, r.y1))
        res = []
        for b in boxes:
            x0, y0, x1, y1 = b.left * sx, b.top * sy, (b.left + b.width) * sx, (b.top + b.height) * sy
            inside = [it for it in items if it[0] >= x0 + 2 and it[2] <= x1 - 2 and it[1] >= y0 + 2 and it[3] <= y1 - 2]
            if not inside:
                continue
            top_pad = (min(it[1] for it in inside) - y0) / sy
            content_bottom = max(it[3] for it in inside) / sy
            res.append((b, top_pad, content_bottom))
        rows = {}
        for b, tp, cb in res:
            rows.setdefault(round(Emu(b.top).cm, 0), []).append((b, tp, cb))
        for _, grp in rows.items():
            pad = max(pad_min, min(tp for _, tp, _ in grp))
            new_bottom = max(cb for _, _, cb in grp) + pad
            for b, _, _ in grp:
                nh = int(new_bottom - b.top)
                if abs(nh - b.height) > Cm(0.1) and b.top + nh <= H - Cm(0.5):
                    b.height = nh
                    changed += 1
    prs.save(a.out)
    print(f"상자 {changed}개 높이 조정 (아래 여백 = 위 여백 기준, 최소 {a.pad_cm}cm, 같은 줄은 같은 높이)")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    l = sp.add_parser("logos"); l.add_argument("inp"); l.add_argument("out"); l.add_argument("--slide", type=int, required=True)
    l.add_argument("--names", required=True); l.add_argument("--tile", default="F4F4F5"); l.set_defaults(fn=cmd_logos)
    b = sp.add_parser("bullets"); b.add_argument("inp"); b.add_argument("out"); b.add_argument("--from", dest="frm", default="+")
    b.add_argument("--to", default="•"); b.set_defaults(fn=cmd_bullets)
    p = sp.add_parser("padding"); p.add_argument("inp"); p.add_argument("out"); p.add_argument("--pdf", required=True)
    p.add_argument("--pad-cm", type=float, default=0.6); p.set_defaults(fn=cmd_padding)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
