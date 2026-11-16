"""PPTX의 모든 요소가 고정 여백(안전 영역) 안에 있는지 검사.

사용: python ir/scripts/check_margins.py <deck.pptx> [--tokens output/ir-x/tokens.json]
- 여백 값: tokens.json 의 slide.margin_cm (기본 상하좌우 1.5cm)
- 예외: 이름이 "bleed:" 로 시작하는 도형(꽉 찬 배경·장식), 슬라이드 면적 90% 이상을 덮는 배경, 템플릿 마스터 요소
- 이 도구는 build_deck.py 뿐 아니라 pptx 스킬·Codex 등 어떤 방식으로 만든 PPT에도 쓴다.
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")
import argparse
import json
from pathlib import Path

from pptx import Presentation
from pptx.util import Cm, Emu

ROOT = Path(__file__).resolve().parents[2]
TOL = Cm(0.05)   # 허용 오차 0.5mm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx")
    ap.add_argument("--tokens", default="tokens.json")
    a = ap.parse_args()
    tok = json.loads((ROOT / a.tokens).read_text(encoding="utf-8"))
    mg = tok.get("slide", {}).get("margin_cm", {"top": 1.5, "right": 1.5, "bottom": 1.5, "left": 1.5})
    prs = Presentation(a.pptx)
    W, H = prs.slide_width, prs.slide_height
    x0, y0 = Cm(mg["left"]), Cm(mg["top"])
    x1, y1 = W - Cm(mg["right"]), H - Cm(mg["bottom"])
    fails = 0
    for i, slide in enumerate(prs.slides, 1):
        for shp in slide.shapes:
            if shp.left is None or shp.width is None:
                continue
            if (shp.name or "").startswith("bleed:"):
                continue
            if shp.width * shp.height >= 0.9 * W * H:
                continue
            l, t, r, b = shp.left, shp.top, shp.left + shp.width, shp.top + shp.height
            out = []
            if l < x0 - TOL: out.append(f"왼쪽 {Emu(x0 - l).cm:.2f}cm")
            if t < y0 - TOL: out.append(f"위 {Emu(y0 - t).cm:.2f}cm")
            if r > x1 + TOL: out.append(f"오른쪽 {Emu(r - x1).cm:.2f}cm")
            if b > y1 + TOL: out.append(f"아래 {Emu(b - y1).cm:.2f}cm")
            if out:
                fails += 1
                label = (shp.text_frame.text[:20] if shp.has_text_frame and shp.text_frame.text else shp.name)
                print(f"FAIL 슬라이드 {i}: '{label}' 여백 침범 ({', '.join(out)})")
    print(f"여백 검사 통과 (상{mg['top']} 우{mg['right']} 하{mg['bottom']} 좌{mg['left']}cm)" if not fails
          else f"여백 검사 실패 {fails}건 — 요소를 안전 영역 안으로 옮기거나, 꽉 찬 배경이면 이름을 'bleed:'로 시작")
    _sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
