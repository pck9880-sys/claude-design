"""챕터별 스타일 보기 이미지 만들기: 각 선택지를 실제로 렌더해 한 장에 나란히.

사용: python tools/style_preview.py [--tokens output/ir-x/tokens.json] [--out design-kit/ir-styles/previews]
결과: <out>/<챕터>.png  (typography, cover, header, connector, card, image, bullet, divider, summary_bar)
고객 색 파일(--tokens)을 주면 그 고객 색으로 미리보기를 만든다.
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")
import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = json.loads((ROOT / "design-kit/ir-styles/styles.json").read_text(encoding="utf-8"))
CH = {c["id"]: c for c in CAT["chapters"]}

PROC = {"type": "process", "section": "02 솔루션", "title": "예약부터 정산까지 4단계로 끝납니다",
        "message": "공방은 일정만 올리면 나머지는 자동으로 처리됩니다",
        "steps": [{"label": "STEP 01", "head": "일정 등록", "body": "클래스 일정과 정원을 올립니다"},
                  {"label": "STEP 02", "head": "실시간 예약", "body": "빈자리를 보고 바로 예약합니다"},
                  {"label": "STEP 03", "head": "자동 알림", "body": ["수업 전날 안내", "취소 시 대기자 연결"]},
                  {"label": "STEP 04", "head": "자동 정산", "body": "매주 나눠 입금합니다"}]}
STAT = {"type": "statement", "section": "01 문제", "title": "공방 클래스는 찾기도, 예약하기도 어렵습니다",
        "message": "수요는 있지만 예약 경로가 전화와 DM에 묶여 있습니다",
        "points": [{"head": "흩어진 정보", "body": ["인스타그램·블로그에 분산", "가격 비교가 어려움"]},
                   {"head": "수동 정산", "body": ["매달 엑셀로 정산", "오류와 분쟁 발생"]},
                   {"head": "빈 자리", "body": ["취소석 재판매 불가", "매출 손실"]}],
        "summary": "예약·정산·빈자리를 한 번에 푸는 곳이 없습니다"}
COVER = {"type": "cover", "title": "흙과 손", "subtitle": "동네 공방을 예약 가능한 클래스로", "meta": "Investor Relations 2026"}
TEAM = {"type": "team", "section": "05 팀", "title": "공방과 플랫폼을 모두 아는 팀",
        "people": [{"name": "김대표", "role": "CEO", "bio": "도예 공방 운영 7년"},
                   {"name": "이개발", "role": "CTO", "bio": "결제·정산 시스템 리드"},
                   {"name": "박운영", "role": "COO", "bio": "파트너 확장 담당"}]}

JOBS = {   # 챕터: (스타일 키, 보여줄 슬라이드)
    "typography": ("typography", STAT), "cover": ("cover", COVER), "header": ("header", STAT),
    "connector": ("connector", PROC), "card": ("card", STAT), "image": ("image", TEAM),
    "bullet": ("bullet", STAT), "divider": ("divider", TEAM), "summary_bar": ("summary_bar", STAT),
}


def options(chapter):
    if chapter in ("bullet", "divider", "summary_bar"):
        return {k: {"name": v} for k, v in CH["detail"]["options"][chapter].items()}
    return CH[chapter]["options"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokens", default="tokens.json")
    ap.add_argument("--out", default="design-kit/ir-styles/previews")
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp())
    built = []
    for chap, (key, slide) in JOBS.items():
        if a.only and chap not in a.only:
            continue
        for opt in options(chap):
            name = f"_preview-{chap}-{opt}"
            spec = {"name": "_preview", "out_file": f"{name}.pptx", "company": "HEUK&SON", "tokens": a.tokens,
                    "style": {key: opt, **({"card": "C"} if chap == "header" else {})}, "slides": [slide]}
            sp = tmp / f"{name}.json"
            sp.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
            r = subprocess.run([_sys.executable, str(ROOT / "ir/scripts/build_deck.py"), str(sp)], capture_output=True,
                               text=True, encoding="utf-8", errors="replace", cwd=ROOT)
            if r.returncode:
                print("실패", name, r.stderr[-300:])
                continue
            built.append((chap, opt, ROOT / "output/ir-_preview" / f"{name}.pptx"))
    soffice = shutil.which("soffice") or r"C:\Program Files\LibreOffice\program\soffice.exe"
    subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(tmp)] + [str(p) for _, _, p in built],
                   capture_output=True, timeout=900)
    import pymupdf
    from PIL import Image, ImageDraw, ImageFont
    lab = ImageFont.truetype(str(ROOT / "assets/fonts/Pretendard/Pretendard-SemiBold.ttf"), 22)
    by = {}
    for chap, opt, p in built:
        pdf = tmp / (p.stem + ".pdf")
        if not pdf.exists():
            continue
        pix = pymupdf.open(pdf)[0].get_pixmap(dpi=40)
        by.setdefault(chap, []).append((opt, Image.frombytes("RGB", (pix.width, pix.height), pix.samples)))
    for chap, ims in by.items():
        cols = 3 if len(ims) > 4 else len(ims)
        w, h = ims[0][1].size
        rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * (w + 16) + 16, rows * (h + 50) + 16), "#E9ECEF")
        d = ImageDraw.Draw(sheet)
        for i, (opt, im) in enumerate(ims):
            x, y = 16 + (i % cols) * (w + 16), 16 + (i // cols) * (h + 50)
            sheet.paste(im, (x, y + 38))
            d.text((x, y + 6), f"{opt}  {options(chap)[opt]['name']}", font=lab, fill="#171A1F")
        sheet.save(out / f"{chap}.png")
        print(f"저장: {a.out}/{chap}.png ({len(ims)}개)")
    shutil.rmtree(ROOT / "output/ir-_preview", ignore_errors=True)
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
