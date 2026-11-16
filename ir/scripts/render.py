"""PPTX → PDF → 슬라이드 PNG (검수용).

사용: python ir/scripts/render.py output/ir-<name>/deck.pptx
출력: 같은 폴더의 deck.pdf, preview/slide-01.png ...
LibreOffice(soffice)가 필요하다.
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")
import shutil
import subprocess
import sys
from pathlib import Path

CANDIDATES = [
    shutil.which("soffice"),
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    "/usr/bin/soffice",
]


def main():
    pptx = Path(sys.argv[1]).resolve()
    soffice = next((c for c in CANDIDATES if c and Path(c).exists()), None)
    if not soffice:
        print("LibreOffice가 없어 렌더를 건너뜀. PPTX는 그대로 사용 가능.")
        sys.exit(2)
    out = pptx.parent
    subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(out), str(pptx)],
                   check=True, capture_output=True, timeout=300)
    pdf = out / (pptx.stem + ".pdf")
    import pymupdf
    prev = out / "preview"
    prev.mkdir(exist_ok=True)
    for old in prev.glob("slide-*.png"):
        old.unlink()
    doc = pymupdf.open(pdf)
    for i, page in enumerate(doc, 1):
        page.get_pixmap(dpi=110).save(prev / f"slide-{i:02d}.png")
    print(f"PDF: {pdf.name}, 미리보기 {len(doc)}장 → {prev}")


if __name__ == "__main__":
    main()
