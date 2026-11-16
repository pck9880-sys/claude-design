"""작업(고객)별 색 파일 만들기. 기본 tokens.json 구조를 복사하고 브랜드 색만 바꾼다.

색 출처 (하나 이상):
  --primary "#1E5BFF" [--secondary "#0B1F3A"]      고객이 준 색 코드
  --from-image ir/inbox/logo.png                   로고·이미지에서 주요 색 추출
  --from-pptx  ir/templates/회사.pptx               PPT 템플릿의 테마 색(accent1, dk2)
사용:
  python tools/make_tokens.py --from-image ir/inbox/logo.png --out output/ir-abc/tokens.json
결과: 흰 글씨 대비 4.5:1 이상이 되도록 버튼·강조용 진한 색(primaryHover)을 자동 계산하고,
      색 출처와 대비 값을 _meta 에 기록한다.
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")
import argparse
import colorsys
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def hex2rgb(h):
    h = h.strip().lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb2hex(c):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(v))) for v in c)


def lum(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def darken_until(c, target=4.5, against=(255, 255, 255)):
    h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in c))
    while contrast(tuple(v * 255 for v in colorsys.hls_to_rgb(h, l, s)), against) < target and l > 0.05:
        l -= 0.01
    return tuple(v * 255 for v in colorsys.hls_to_rgb(h, l, s))


def from_image(path, k=6):
    from PIL import Image
    im = Image.open(path).convert("RGBA")
    im.thumbnail((300, 300))
    data = im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata()
    px = [p[:3] for p in data if p[3] > 200]
    flat = Image.new("RGB", (len(px), 1))
    flat.putdata(px)
    q = flat.quantize(colors=k)
    pal = q.getpalette()[:k * 3]
    counts = sorted(q.getcolors(), reverse=True)
    out = []
    for n, idx in counts:
        c = tuple(pal[idx * 3:idx * 3 + 3])
        _, l, s = colorsys.rgb_to_hls(*(v / 255 for v in c))
        if l > 0.92 or l < 0.06 or s < 0.15:      # 흰색·검정·회색(배경) 제외
            continue
        out.append(c)
    return out


def from_pptx(path):
    with zipfile.ZipFile(path) as z:
        names = sorted(n for n in z.namelist() if re.match(r"ppt/theme/theme\d+\.xml", n))
        xml = z.read(names[0]).decode("utf-8", "ignore")
    cols = []
    for key in ("accent1", "accent2", "dk2"):
        m = re.search(rf"<a:{key}>.*?srgbClr val=\"([0-9A-Fa-f]{{6}})\"", xml, re.S)
        if m:
            cols.append(hex2rgb(m.group(1)))
    return cols


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--primary")
    ap.add_argument("--secondary")
    ap.add_argument("--from-image")
    ap.add_argument("--from-pptx")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    cands, source = [], []
    if a.primary:
        cands.append(hex2rgb(a.primary)); source.append("사용자 지정 색 코드")
    if a.secondary:
        cands.append(hex2rgb(a.secondary))
    if a.from_pptx:
        cands += from_pptx(a.from_pptx); source.append(f"템플릿 테마 색: {Path(a.from_pptx).name}")
    if a.from_image:
        cands += from_image(a.from_image); source.append(f"이미지 추출: {Path(a.from_image).name}")
    if not cands:
        _sys.exit("색 출처가 없음: --primary / --from-image / --from-pptx 중 하나 필요")

    primary = cands[0]
    secondary = cands[1] if len(cands) > 1 else darken_until(primary, 12)
    strong = darken_until(primary, 4.5)

    tok = json.loads((ROOT / "tokens.json").read_text(encoding="utf-8"))
    tok.pop("_note", None)
    tok["color"]["brand"] = {"primary": rgb2hex(primary), "primaryHover": rgb2hex(strong), "secondary": rgb2hex(secondary)}
    tok["_meta"] = {
        "source": source,
        "candidates": [rgb2hex(c) for c in cands],
        "contrast_white_on_primary": round(contrast((255, 255, 255), primary), 2),
        "contrast_white_on_primaryHover": round(contrast((255, 255, 255), strong), 2),
        "note": "primaryHover = 흰 글씨를 올릴 버튼·강조 배경용 (대비 4.5 이상). primary는 넓은 면·장식용.",
    }
    out = ROOT / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(tok, ensure_ascii=False, indent=2), encoding="utf-8")
    m = tok["_meta"]
    print(f"저장: {a.out}\n  primary {rgb2hex(primary)} (흰 글씨 대비 {m['contrast_white_on_primary']})"
          f"\n  primaryHover {rgb2hex(strong)} (대비 {m['contrast_white_on_primaryHover']})"
          f"\n  secondary {rgb2hex(secondary)}\n  후보: {', '.join(m['candidates'])}")


if __name__ == "__main__":
    main()
