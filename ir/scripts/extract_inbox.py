"""ir/inbox/ 의 문서를 텍스트(마크다운)로 추출해 ir/inbox/_extracted/ 에 저장.

지원: .docx .pdf .xlsx .xlsm .csv .pptx .txt .md
사용: python ir/scripts/extract_inbox.py [inbox 경로]
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INBOX = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "ir" / "inbox"
OUT = INBOX / "_extracted"


def from_docx(p):
    import docx
    d = docx.Document(p)
    lines = [para.text for para in d.paragraphs if para.text.strip()]
    for ti, table in enumerate(d.tables, 1):
        lines.append(f"\n[표 {ti}]")
        for row in table.rows:
            lines.append("| " + " | ".join(c.text.strip() for c in row.cells) + " |")
    return "\n".join(lines)


def from_pdf(p):
    import pdfplumber
    out = []
    with pdfplumber.open(p) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            out.append(f"\n## p.{i}\n{page.extract_text() or '(텍스트 없음: 이미지 페이지일 수 있음)'}")
    return "\n".join(out)


def from_xlsx(p):
    import openpyxl
    wb = openpyxl.load_workbook(p, data_only=True, read_only=True)
    out = []
    for ws in wb.worksheets:
        out.append(f"\n## 시트: {ws.title}")
        for row in ws.iter_rows(values_only=True):
            if any(v is not None for v in row):
                out.append("| " + " | ".join("" if v is None else str(v) for v in row) + " |")
    return "\n".join(out)


def from_pptx(p):
    from pptx import Presentation
    prs = Presentation(p)
    out = []
    for i, slide in enumerate(prs.slides, 1):
        out.append(f"\n## 슬라이드 {i}")
        for shp in slide.shapes:
            if shp.has_text_frame and shp.text_frame.text.strip():
                out.append(shp.text_frame.text.strip())
            if getattr(shp, "has_table", False) and shp.has_table:
                for row in shp.table.rows:
                    out.append("| " + " | ".join(c.text.strip() for c in row.cells) + " |")
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame.text.strip():
            out.append(f"(노트) {slide.notes_slide.notes_text_frame.text.strip()}")
    return "\n".join(out)


def from_text(p):
    for enc in ("utf-8", "cp949"):
        try:
            return p.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return p.read_text(encoding="utf-8", errors="replace")


HANDLERS = {".docx": from_docx, ".pdf": from_pdf, ".xlsx": from_xlsx, ".xlsm": from_xlsx,
            ".pptx": from_pptx, ".csv": from_text, ".txt": from_text, ".md": from_text}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files = [f for f in INBOX.rglob("*") if f.is_file() and "_extracted" not in f.parts]
    if not files:
        print(f"inbox가 비어 있음: {INBOX}")
        return
    for f in sorted(files):
        h = HANDLERS.get(f.suffix.lower())
        if not h:
            print(f"건너뜀 (지원 안 함, PDF로 변환해 넣을 것): {f.name}")
            continue
        try:
            text = h(f)
        except Exception as e:  # noqa: BLE001
            print(f"실패: {f.name} — {e}")
            continue
        out = OUT / (f.stem + f.suffix.replace(".", "_") + ".md")
        out.write_text(f"# 원본: {f.name}\n\n{text}\n", encoding="utf-8")
        shown = out.relative_to(ROOT) if out.is_relative_to(ROOT) else out
        print(f"추출: {f.name} → {shown} ({len(text)}자)")


if __name__ == "__main__":
    main()
