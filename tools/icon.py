"""라인 아이콘 도구: 찾기 · 규칙 검사 · 브랜드 색 PNG 만들기.

  python tools/icon.py find 예약 달력 calendar          # Lucide 세트에서 이름으로 찾기 (영문 키워드 권장)
  python tools/icon.py check assets/icons/custom/x.svg   # 라인 아이콘 규칙 검사
  python tools/icon.py render <svg> --color "#2F4A7A" --out assets/generated/icon-x.png [--px 256]
  python tools/icon.py sheet <svg들> --out 모음.png       # 검수용 한 장 모음

라인 아이콘 규칙 (모든 아이콘 공통, GPT 생성 포함):
  24×24 viewBox, fill="none", stroke="currentColor", stroke-width 1.75, 둥근 선 끝·모서리,
  면 채움·그라데이션·글자 없음, 요소 2–6개 이내, 사방 2px 여백, 한 아이콘 = 한 가지 뜻
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LUCIDE = ROOT / "assets/icons/lucide"
STROKE = "1.75"

KO = {  # 자주 쓰는 한국어 → Lucide 영문 키워드
    "예약": "calendar", "달력": "calendar", "일정": "calendar", "정산": "wallet", "결제": "credit-card", "돈": "banknote",
    "매출": "trending-up", "성장": "trending-up", "사용자": "user", "고객": "users", "팀": "users", "알림": "bell",
    "검색": "search", "보안": "shield", "데이터": "database", "분석": "chart", "차트": "chart", "시장": "globe",
    "글로벌": "globe", "공장": "factory", "제조": "factory", "배송": "truck", "물류": "truck", "건물": "building",
    "회사": "building", "문서": "file-text", "계약": "file-signature", "설정": "settings", "자동": "workflow",
    "ai": "brain", "인공지능": "brain", "로봇": "bot", "클라우드": "cloud", "모바일": "smartphone", "앱": "smartphone",
    "웹": "monitor", "연결": "link", "파트너": "handshake", "협업": "handshake", "목표": "target", "아이디어": "lightbulb",
    "시간": "clock", "속도": "zap", "에너지": "zap", "환경": "leaf", "친환경": "leaf", "건강": "heart-pulse",
    "의료": "stethoscope", "교육": "graduation-cap", "학습": "book-open", "쇼핑": "shopping-cart", "상품": "package",
    "위치": "map-pin", "지도": "map", "메시지": "message-circle", "채팅": "message-circle", "체크": "check",
    "완료": "circle-check", "경고": "triangle-alert", "문제": "circle-alert", "특허": "award", "수상": "trophy",
    "투자": "piggy-bank", "비용": "receipt", "절감": "trending-down", "공방": "palette", "도자기": "amphora",
}


def find(words):
    names = sorted(p.stem for p in LUCIDE.glob("*.svg"))
    keys = [KO.get(w.lower(), w.lower()) for w in words]
    hits = []
    for k in keys:
        hits += [n for n in names if n == k] + [n for n in names if k in n and n != k]
    seen = list(dict.fromkeys(hits))
    print("\n".join(seen[:30]) if seen else "없음 → GPT로 생성: python tools/gpt.py icon ...")


def check(svg_path):
    s = Path(svg_path).read_text(encoding="utf-8")
    probs = []
    if 'viewBox="0 0 24 24"' not in s:
        probs.append("viewBox가 0 0 24 24가 아님")
    if re.search(r'fill="(?!none)[^"]+"', s):
        probs.append("면 채움(fill)이 있음 — 라인만 허용")
    if "<text" in s or "<image" in s:
        probs.append("글자나 이미지가 들어 있음")
    if re.search(r"gradient|filter|<style", s, re.I):
        probs.append("그라데이션·필터·스타일 사용")
    n = len(re.findall(r"<(path|circle|rect|line|polyline|polygon|ellipse)\b", s))
    if n > 8:
        probs.append(f"요소가 {n}개로 복잡함 (8개 이하 권장)")
    if 'stroke-linecap="round"' not in s or 'stroke-linejoin="round"' not in s:
        probs.append("선 끝·모서리가 둥글지 않음")
    print("규칙 통과" if not probs else "규칙 위반: " + " / ".join(probs))
    return not probs


def normalize(svg, color):
    s = re.sub(r'stroke-width="[^"]+"', f'stroke-width="{STROKE}"', svg)
    s = s.replace("currentColor", color)
    return s


def render(svg_path, color, out, px=256):
    import pymupdf
    s = normalize(Path(svg_path).read_text(encoding="utf-8"), color)
    s = re.sub(r'width="24"\s+height="24"', f'width="{px}" height="{px}"', s, count=1)
    doc = pymupdf.open(stream=s.encode("utf-8"), filetype="svg")
    pix = doc[0].get_pixmap(alpha=True)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    pix.save(out)
    return out


def sheet(svgs, out, color="#171A1F"):
    from PIL import Image, ImageDraw, ImageFont
    import tempfile
    lab = ImageFont.truetype(str(ROOT / "assets/fonts/Pretendard/Pretendard-Medium.ttf"), 14)
    cell = 140
    cols = min(6, len(svgs))
    rows = (len(svgs) + cols - 1) // cols
    S = Image.new("RGB", (cols * cell, rows * (cell + 20)), "white")
    d = ImageDraw.Draw(S)
    for i, sv in enumerate(svgs):
        tmp = Path(tempfile.gettempdir()) / f"_icon{i}.png"
        render(sv, color, str(tmp), 96)
        im = Image.open(tmp).convert("RGBA")
        x, y = (i % cols) * cell, (i // cols) * (cell + 20)
        S.paste(im, (x + 22, y + 10), im)
        d.text((x + 6, y + cell - 10), Path(sv).stem[:18], font=lab, fill="#666")
    S.save(out)
    print("저장:", out)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    f = sp.add_parser("find"); f.add_argument("words", nargs="+")
    c = sp.add_parser("check"); c.add_argument("svg")
    r = sp.add_parser("render"); r.add_argument("svg"); r.add_argument("--color", default="#171A1F")
    r.add_argument("--out", required=True); r.add_argument("--px", type=int, default=256)
    s = sp.add_parser("sheet"); s.add_argument("svgs", nargs="+"); s.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.cmd == "find":
        find(a.words)
    elif a.cmd == "check":
        _sys.exit(0 if check(a.svg) else 1)
    elif a.cmd == "render":
        print("저장:", render(a.svg, a.color, a.out, a.px))
    else:
        sheet(a.svgs, a.out)


if __name__ == "__main__":
    main()
