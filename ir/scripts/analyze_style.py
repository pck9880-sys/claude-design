"""내가 만든 PPTX들에서 서식 습관을 통계로 뽑는다 (XML만 읽어 빠름, 원본 수정 없음).

사용: python ir/scripts/analyze_style.py "<PPTX 폴더>" --out design-kit/ir-styles/analysis.json
뽑는 것: 글자 크기, 자간(spc), 행간(lnSpc), 선 굵기, 점선 종류, 도형 종류, 둥근 모서리 비율,
        화살표(선 끝 모양·화살표 도형), 글머리 기호, 이미지 수·둥근 이미지, 상단바(위쪽 가로 도형), 폰트
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")
import argparse
import json
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

EMU_CM = 360000


def r1(v):
    return round(v, 1)


def analyze_pdfs(folder):
    """PDF 레퍼런스(샘플): 글꼴·글자 크기(33.87cm 폭 기준 환산)·선 굵기·채움 색을 뽑는다."""
    import pymupdf
    P = defaultdict(Counter)
    files = sorted(Path(folder).glob("*.pdf"))
    pages = 0
    for f in files:
        doc = pymupdf.open(f)
        for page in list(doc)[:40]:
            pages += 1
            k = 33.867 / (page.rect.width / 72 * 2.54)        # 폭을 33.87cm로 맞춘 배율
            for b in page.get_text("dict")["blocks"]:
                for line in b.get("lines", []):
                    for sp in line["spans"]:
                        if sp["text"].strip():
                            P["font_pt"][round(sp["size"] * k * 2) / 2] += 1
                            P["font_face"][re.sub(r"^[A-Z]{6}\+", "", sp["font"])] += 1
            for dr in page.get_drawings():
                if dr.get("width"):
                    P["line_pt"][round(dr["width"] * k, 1)] += 1
                if dr.get("dashes") and dr["dashes"] not in ("[] 0", "[] 0.0"):
                    P["dash"]["dashed"] += 1
                if dr.get("fill"):
                    P["fill_rgb"]["#%02X%02X%02X" % tuple(int(c * 255) for c in dr["fill"][:3])] += 1
    out = {"decks": len(files), "pages_sampled": pages,
           "stats": {k: [[str(v), n] for v, n in c.most_common(15)] for k, c in P.items()}}
    fp = sorted(P["font_pt"].elements())
    if fp:
        out["font_pt_percentile"] = {p: fp[int(len(fp) * p / 100)] for p in (5, 10, 25, 50, 75, 90)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", help="PPTX(경량본) 폴더")
    ap.add_argument("--pdf", help="PDF 레퍼런스 폴더 (선택)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    files = sorted(Path(a.folder).glob("*.pptx"))
    S = defaultdict(Counter)
    per_deck = {}
    for f in files:
        try:
            z = zipfile.ZipFile(f)
        except Exception as e:  # noqa: BLE001
            print("건너뜀", f.name, e)
            continue
        pres = z.read("ppt/presentation.xml").decode("utf8", "ignore")
        m = re.search(r'<p:sldSz cx="(\d+)" cy="(\d+)"', pres)
        W, H = (int(m.group(1)), int(m.group(2))) if m else (12192000, 6858000)
        S["slide_size_cm"][f"{W / EMU_CM:.2f}x{H / EMU_CM:.2f}"] += 1
        slides = sorted((n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)),
                        key=lambda n: int(re.findall(r"\d+", n)[0]))
        d = Counter()
        for si, n in enumerate(slides):
            x = z.read(n).decode("utf8", "ignore")
            for v in re.findall(r'<a:(?:rPr|defRPr|endParaRPr)[^>]*\bsz="(\d+)"', x):
                S["font_pt"][int(v) / 100] += 1
            for v in re.findall(r'<a:(?:rPr|defRPr)[^>]*\bspc="(-?\d+)"', x):
                S["tracking_pt"][int(v) / 100] += 1          # 자간 (pt 단위, 음수=좁게)
            for v in re.findall(r"<a:lnSpc><a:spcPct val=\"(\d+)\"", x):
                S["leading_pct"][int(v) / 1000] += 1         # 행간 %
            for v in re.findall(r"<a:spcBef><a:spcPts val=\"(\d+)\"", x):
                S["para_space_before_pt"][int(v) / 100] += 1
            for v in re.findall(r'<a:ln\b[^>]*\bw="(\d+)"', x):
                S["line_pt"][r1(int(v) / 12700)] += 1
            for v in re.findall(r'<a:prstDash val="(\w+)"', x):
                S["dash"][v] += 1
            for v in re.findall(r'<a:prstGeom prst="(\w+)"', x):
                S["shape"][v] += 1
            for adj in re.findall(r'<a:prstGeom prst="roundRect">\s*<a:avLst>\s*<a:gd name="adj" fmla="val (\d+)"', x):
                S["roundrect_adj_pct"][round(int(adj) / 1000)] += 1   # 짧은 변 대비 둥글기 %
            for t in re.findall(r'<a:(?:tailEnd|headEnd) type="(\w+)"', x):
                if t != "none":
                    S["line_end"][t] += 1
            for c in re.findall(r'<a:buChar char="([^"]+)"', x):
                S["bullet_char"][c] += 1
            if "<a:buAutoNum" in x:
                S["bullet_char"]["(자동 번호)"] += 1
            pics = re.findall(r"<p:pic>.*?</p:pic>", x, re.S)
            S["pictures_per_slide"][min(len(pics), 6)] += 1
            for p in pics:
                g = re.search(r'<a:prstGeom prst="(\w+)"', p)
                S["picture_geom"][g.group(1) if g else "rect"] += 1
            for tf in re.findall(r'<a:latin typeface="([^"]+)"', x) + re.findall(r'<a:ea typeface="([^"]+)"', x):
                if not tf.startswith("+"):
                    S["font_face"][tf] += 1
            # 위쪽 가로 띠(상단바): 위 15% 안, 폭 40% 이상, 높이 12% 이하인 도형
            for sp in re.findall(r"<p:sp>.*?</p:sp>", x, re.S):
                off = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"/><a:ext cx="(\d+)" cy="(\d+)"', sp)
                if not off:
                    continue
                ox, oy, cx, cy = map(int, off.groups())
                if si > 0 and oy < H * 0.15 and cx > W * 0.4 and cy < H * 0.12:
                    kind = "텍스트 있음" if "<a:t>" in sp else "도형만"
                    geom = (re.search(r'prst="(\w+)"', sp) or [None, "custom"])[1]
                    S["topbar"][f"{geom}/{kind}/h{round(cy / EMU_CM, 1)}cm"] += 1
                # 여백: 슬라이드 가장자리에서 가장 가까운 텍스트 상자 거리
                if "<a:t>" in sp and cx < W * 0.9:
                    S["text_left_cm"][r1(ox / EMU_CM)] += 1
                    S["text_top_cm"][r1(oy / EMU_CM)] += 1
            d["slides"] += 1
        per_deck[f.stem] = d["slides"]

    def top(c, k=12):
        return [[str(v), n] for v, n in c.most_common(k)]

    out = {"decks": len(per_deck), "slides": sum(per_deck.values()),
           "stats": {k: top(v, 20 if k in ("font_pt", "line_pt", "shape") else 12) for k, v in S.items()}}
    fp = sorted(S["font_pt"].elements())
    if fp:
        out["font_pt_percentile"] = {p: fp[int(len(fp) * p / 100)] for p in (5, 10, 25, 50, 75, 90)}
    out = {"portfolio_pptx": out}
    if a.pdf:
        out["samples_pdf"] = analyze_pdfs(a.pdf)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=0)[:6000])


if __name__ == "__main__":
    main()
