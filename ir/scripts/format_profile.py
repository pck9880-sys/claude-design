"""PPT 템플릿에서 서식 규칙을 뽑아 ir/format-profile.md 로 저장.

사용: python ir/scripts/format_profile.py ir/templates/회사템플릿.pptx
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu

ROOT = Path(__file__).resolve().parents[2]


def theme_info(path):
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if re.match(r"ppt/theme/theme\d+\.xml", n)]
        if not names:
            return {}, {}
        xml = z.read(sorted(names)[0]).decode("utf-8", errors="ignore")
    colors = {}
    for key in ("dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6"):
        m = re.search(rf"<a:{key}>.*?(?:srgbClr val=\"([0-9A-Fa-f]{{6}})\"|lastClr=\"([0-9A-Fa-f]{{6}})\")", xml, re.S)
        if m:
            colors[key] = "#" + (m.group(1) or m.group(2)).upper()
    fonts = {}
    for kind in ("majorFont", "minorFont"):
        m = re.search(rf"<a:{kind}>.*?<a:latin typeface=\"([^\"]*)\".*?(?:<a:ea typeface=\"([^\"]*)\")?", xml, re.S)
        h = re.search(rf"<a:{kind}>.*?<a:font script=\"Hang\" typeface=\"([^\"]*)\"", xml, re.S)
        if m:
            fonts[kind] = {"latin": m.group(1), "hangul": h.group(1) if h else (m.group(2) or "")}
    return colors, fonts


def main():
    if len(sys.argv) < 2:
        print("사용: python ir/scripts/format_profile.py <템플릿.pptx>")
        sys.exit(1)
    src = Path(sys.argv[1])
    prs = Presentation(src)
    w, h = Emu(prs.slide_width), Emu(prs.slide_height)
    colors, fonts = theme_info(src)

    used_fonts, used_sizes = Counter(), Counter()
    for slide in prs.slides:
        for shp in slide.shapes:
            if not shp.has_text_frame:
                continue
            for para in shp.text_frame.paragraphs:
                for run in para.runs:
                    if run.font.name:
                        used_fonts[run.font.name] += 1
                    if run.font.size:
                        used_sizes[round(run.font.size.pt)] += 1

    lines = [f"# 서식 프로파일", f"", f"원본: `{src.name}` (자동 추출, 사람이 검토 후 보완)", "",
             "## 슬라이드", f"- 크기: {w.inches:.2f} x {h.inches:.2f} in ({'16:9' if abs(w / h - 16 / 9) < 0.02 else '4:3' if abs(w / h - 4 / 3) < 0.02 else '기타'})",
             f"- 기존 슬라이드 수: {len(prs.slides)}", "", "## 테마 색"]
    lines += [f"- {k}: `{v}`" for k, v in colors.items()] or ["- (추출 실패)"]
    lines += ["", "## 테마 폰트"]
    lines += [f"- {k}: 영문 `{v['latin']}` / 한글 `{v['hangul'] or '-'}`" for k, v in fonts.items()] or ["- (추출 실패)"]
    lines += ["", "## 실제 사용된 폰트 (빈도순)"] + [f"- {f}: {n}회" for f, n in used_fonts.most_common(6)]
    lines += ["", "## 실제 사용된 글자 크기 (pt, 빈도순)"] + [f"- {s}pt: {n}회" for s, n in used_sizes.most_common(8)]
    lines += ["", "## 레이아웃"]
    for i, layout in enumerate(prs.slide_layouts):
        phs = ", ".join(f"{ph.placeholder_format.type}".split(" ")[0] for ph in layout.placeholders)
        lines.append(f"- [{i}] {layout.name} — {phs or '자리표시자 없음'}")
    lines += ["", "## 수동 확인 필요", "- 로고 위치·크기:", "- 페이지 번호·출처 표기 위치:", "- 여백 규칙:", "- 차트 스타일(색 순서, 축 표기):"]

    out = ROOT / "ir" / "format-profile.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"저장: {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
