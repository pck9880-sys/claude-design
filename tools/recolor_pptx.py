"""PPTX 안의 색을 바꿔치기 (기존 덱의 포인트 색 교체용). 원본은 건드리지 않고 새 파일로 저장.

사용: python tools/recolor_pptx.py <입력.pptx> <출력.pptx> F38153=C73544 DC569C=8E2430 ...
슬라이드·차트·레이아웃·마스터의 srgbClr 값만 바꾼다 (사진은 그대로).
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")
import re
import zipfile

src, dst, *pairs = _sys.argv[1:]
mp = {a.upper(): b.upper() for a, b in (p.split("=") for p in pairs)}
pat = re.compile(r'(srgbClr val=")([0-9A-Fa-f]{6})(")')
count = {k: 0 for k in mp}


def sub(m):
    v = m.group(2).upper()
    if v in mp:
        count[v] += 1
        return m.group(1) + mp[v] + m.group(3)
    return m.group(0)


with zipfile.ZipFile(src) as zi, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
    for it in zi.infolist():
        data = zi.read(it.filename)
        if re.match(r"ppt/(slides/slide\d+|charts/chart\d+|slideLayouts/slideLayout\d+|slideMasters/slideMaster\d+)\.xml$", it.filename):
            data = pat.sub(sub, data.decode("utf-8")).encode("utf-8")
        zo.writestr(it, data)
print("바꾼 횟수:", count)
