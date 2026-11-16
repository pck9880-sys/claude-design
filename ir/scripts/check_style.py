"""PPTX 서식 규칙 검사: 최소 글자 크기, 허용 폰트, 선 굵기.

사용: python ir/scripts/check_style.py <deck.pptx> [--style output/ir-x/style.json]
- 최소 글자 크기: 선택한 typography 의 min_pt (출처·페이지 번호 등은 caption 최소값 허용)
- 폰트: assets/fonts 카탈로그(README) 폰트만. 맑은 고딕 등 시스템 폰트는 실패
- 선 굵기: styles.json fixed.line_pt (0.5 / 0.8 / 1.6pt)만
어떤 방법으로 만든 PPT든 쓸 수 있다.
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")
import argparse
import json
import re
from pathlib import Path

from pptx import Presentation
from pptx.util import Pt

ROOT = Path(__file__).resolve().parents[2]
BANNED = re.compile(r"(맑은 고딕|Malgun|굴림|Gulim|돋움|Dotum|바탕|Batang|궁서|Gungsuh|^HY|HCR|함초롬|Arial|Calibri|Times New Roman|Segoe)", re.I)


def allowed_fonts():
    txt = (ROOT / "assets/fonts/README.md").read_text(encoding="utf-8")
    names = set(re.findall(r"(Pretendard|Freesentation|Noto Serif KR|Noto Sans KR|Kkakdugi Drafting|Mulmaru|DOSIyagiBoldface|DOSPilgi|Montserrat|Plus Jakarta Sans|Orbitron|Audiowide|Outward|Black Ops One|Rubik Glitch|Chewy|Special Elite)", txt))
    return names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx")
    ap.add_argument("--style")
    a = ap.parse_args()
    cat = json.loads((ROOT / "design-kit/ir-styles/styles.json").read_text(encoding="utf-8"))
    ch = {c["id"]: c for c in cat["chapters"]}
    sty = {**cat["defaults"], **(json.loads((ROOT / a.style).read_text(encoding="utf-8")) if a.style else {})}
    mins = ch["typography"]["options"][sty["typography"]]["min_pt"]
    lines_ok = {round(v, 2) for v in cat["fixed"]["line_pt"].values()}
    fonts_ok = allowed_fonts()
    fails = []
    prs = Presentation(a.pptx)
    for i, slide in enumerate(prs.slides, 1):
        for shp in slide.shapes:
            xml = shp._element.xml
            for m in re.finditer(r'sz="(\d+)"', xml):
                sz = int(m.group(1)) / 100
                if sz < mins["caption"] - 0.01 or (sz < mins["body"] - 0.01 and not _is_caption(shp)):
                    fails.append(f"슬라이드 {i}: 글자 {sz}pt < 최소 {mins['body']}pt ('{_label(shp)}')")
                    break
            for face in set(re.findall(r'typeface="([^"+][^"]*)"', xml)):
                base = re.sub(r" (Thin|ExtraLight|Light|Regular|Medium|SemiBold|Bold|ExtraBold|Black)$", "", face)
                if BANNED.search(face) or base not in fonts_ok:
                    fails.append(f"슬라이드 {i}: 허용되지 않은 폰트 '{face}' ('{_label(shp)}')")
            for m in re.finditer(r'<a:ln\b[^>]*\bw="(\d+)"', xml):
                pt = round(int(m.group(1)) / 12700, 2)
                if pt and pt not in lines_ok:
                    fails.append(f"슬라이드 {i}: 선 굵기 {pt}pt (허용 {sorted(lines_ok)}) ('{_label(shp)}')")
    for f in dict.fromkeys(fails):
        print("FAIL", f)
    print("서식 검사 통과 (최소 글자·폰트·선 굵기)" if not fails else f"서식 검사 실패 {len(set(fails))}건")
    _sys.exit(1 if fails else 0)


def _is_caption(shp):
    t = shp.text_frame.text if getattr(shp, "has_text_frame", False) and shp.has_text_frame else ""
    return t.startswith("출처") or t.startswith("기준") or t.isdigit() or "이미지 자리" in t or len(t) <= 25


def _label(shp):
    t = shp.text_frame.text if getattr(shp, "has_text_frame", False) and shp.has_text_frame else ""
    return (t or shp.name)[:20]


if __name__ == "__main__":
    main()
