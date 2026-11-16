"""레퍼런스 자료를 GitHub에 올릴 수 있는 가벼운 사본으로 만든다 (원본은 건드리지 않음).

  python tools/lite_refs.py pdf  "<원본 폴더>" refs/ir/samples            # PDF 이미지 압축
  python tools/lite_refs.py pptx "<원본 폴더>" refs/ir/portfolio/pptx-lite # PPTX 사진을 작은 자리표시로 교체

- PDF: 이미지를 150dpi·JPEG 품질 70으로 다시 저장 (글자·도형은 벡터 그대로)
- PPTX: 도형·글꼴·자간·선·여백 등 서식은 그대로, ppt/media 안의 사진·영상만 작은 회색 이미지로 교체
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")
import io
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def lite_pdf(src, dst):
    import pymupdf
    doc = pymupdf.open(src)
    try:
        doc.rewrite_images(dpi_threshold=160, dpi_target=150, quality=70, lossy=True, lossless=True, bitonal=True, color=True, gray=True)
    except Exception as e:  # noqa: BLE001
        print("  이미지 재압축 실패, 정리만 함:", e)
    doc.save(dst, garbage=4, deflate=True, clean=True)


def placeholder(fmt):
    from PIL import Image
    im = Image.new("RGB", (8, 8), (200, 200, 200))
    b = io.BytesIO()
    im.save(b, format={"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "gif": "GIF", "bmp": "BMP", "tif": "TIFF", "tiff": "TIFF"}.get(fmt, "PNG"))
    return b.getvalue()


def lite_pptx(src, dst):
    import re
    with zipfile.ZipFile(src) as zi, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
        for item in zi.infolist():
            if item.filename.startswith("ppt/fonts/"):
                continue   # 포함된 폰트 제거 (용량 대부분, 유료 폰트 재배포 방지). 폰트 이름은 XML에 남는다
            data = zi.read(item.filename)
            if item.filename == "ppt/presentation.xml":
                data = re.sub(rb"<p:embeddedFontLst>.*?</p:embeddedFontLst>", b"", data, flags=re.S)
            elif item.filename == "ppt/_rels/presentation.xml.rels":
                data = re.sub(rb'<Relationship [^>]*Type="[^"]*/font"[^>]*/>', b"", data)
            elif item.filename == "[Content_Types].xml":
                data = re.sub(rb'<Override PartName="/ppt/fonts/[^"]*"[^>]*/>', b"", data)
            if item.filename.startswith("ppt/media/"):
                ext = item.filename.rsplit(".", 1)[-1].lower()
                if ext in ("png", "jpg", "jpeg", "gif", "bmp", "tif", "tiff"):
                    data = placeholder(ext)
                elif ext in ("mp4", "mov", "avi", "wmv", "m4v", "mp3", "wav", "wdp", "jxr", "emf", "wmf", "svg"):
                    data = b""   # 영상·특수 이미지는 비움 (서식 분석에는 영향 없음)
            zo.writestr(item, data)


def main():
    kind, src_dir, out_dir = _sys.argv[1], Path(_sys.argv[2]), ROOT / _sys.argv[3]
    out_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(src_dir.glob(f"*.{kind}"))
    tot_in = tot_out = 0
    for f in files:
        dst = out_dir / f.name
        (lite_pdf if kind == "pdf" else lite_pptx)(f, dst)
        a, b = f.stat().st_size, dst.stat().st_size
        tot_in, tot_out = tot_in + a, tot_out + b
        print(f"{f.name}: {a / 1048576:.1f}MB → {b / 1048576:.1f}MB")
    print(f"합계 {len(files)}개: {tot_in / 1048576:.0f}MB → {tot_out / 1048576:.0f}MB")


if __name__ == "__main__":
    main()
