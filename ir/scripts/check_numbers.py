"""덱 명세(deck.json)에 직접 적힌 숫자가 data 파일에 근거가 있는지 대조.

사용: python ir/scripts/check_numbers.py ir/deck.json
- FAIL: data 어디에도 없는 숫자 (지어낸 수치 가능성)
- OK  : data 값과 일치, 또는 slide.derived 에 계산 근거를 적은 숫자
연도(19xx/20xx)와 슬라이드 번호 같은 1자리 수는 검사에서 뺀다.
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IR = ROOT / "ir"
NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")


def norm(s):
    return s.replace(",", "").rstrip("0").rstrip(".") if "." in s else s.replace(",", "")


def data_numbers():
    found = set()
    for f in (IR / "data").glob("*.csv"):
        with open(f, encoding="utf-8-sig") as fh:
            for row in csv.DictReader(fh):
                for v in row.values():
                    for m in NUM.findall(str(v)):
                        found.add(norm(m))
    return found


SKIP_KEYS = {"type", "data", "value_ref", "amount_ref", "use_of_funds", "image", "icon", "photo", "section",
             "derived", "notes", "source", "highlight", "highlight_row", "x", "y", "unit", "kind", "labels",
             "columns", "current", "label"}


def texts(node, key=None):
    """슬라이드 안의 사람이 읽는 문장을 모두 모은다 (데이터 경로·아이콘 이름 등은 제외)."""
    out = []
    if isinstance(node, dict):
        for k, v in node.items():
            if k not in SKIP_KEYS:
                out += texts(v, k)
    elif isinstance(node, list):
        for v in node:
            out += texts(v, key)
    elif isinstance(node, str) and node.strip():
        out.append(node)
    return out


def main():
    spec = json.loads(Path(sys.argv[1] if len(sys.argv) > 1 else IR / "deck.json").read_text(encoding="utf-8"))
    known = data_numbers()
    fails = 0
    for i, s in enumerate(spec["slides"], 1):
        derived = {norm(k) for k in s.get("derived", {})}
        for t in texts(s):
            for m in NUM.findall(t):
                n = norm(m)
                if re.fullmatch(r"(19|20)\d\d", n) or len(n) == 1:
                    continue
                if n in known or n in derived:
                    continue
                fails += 1
                print(f"FAIL 슬라이드 {i}: '{m}' — data에 없음 (문장: {t[:40]}…). data에 추가하거나 slide.derived에 계산 근거를 적을 것")
    print("숫자 대조 통과" if not fails else f"숫자 대조 실패 {fails}건")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
