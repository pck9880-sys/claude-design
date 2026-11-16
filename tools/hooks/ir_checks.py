"""Claude Code PostToolUse 훅: IR 덱 자동 검수.

- deck*.json 을 편집/작성하면 → check_numbers.py (근거 없는 숫자 차단)
- build_deck.py 를 실행하면 → check_margins.py (여백 1.5cm 침범 차단)
실패하면 exit 2 + stderr 로 Claude에게 알려 바로 고치게 한다. 성공하면 조용히 넘어간다.
"""
import sys as _sys
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(args):
    import os
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([_sys.executable, *args], cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


def main():
    _sys.stderr.reconfigure(encoding="utf-8")
    try:   # Windows 기본 인코딩(cp949) 대신 UTF-8로 읽어야 한글 경로가 깨지지 않는다
        ev = json.loads(_sys.stdin.buffer.read().decode("utf-8", "replace") or "{}")
    except json.JSONDecodeError:
        return 0
    tool, inp = ev.get("tool_name", ""), ev.get("tool_input", {}) or {}
    problems = []

    if tool in ("Edit", "Write", "MultiEdit"):
        fp = inp.get("file_path", "")
        if re.search(r"[\\/]ir[\\/]deck[^\\/]*\.json$", fp):
            code, out = run(["ir/scripts/check_numbers.py", fp])
            if code:
                problems.append(f"[숫자 대조 실패] {fp}\n{out}")

    elif tool == "Bash":
        cmd = inp.get("command", "")
        m = re.search(r"python[^\n;&|]*build_deck\.py\s+([^\s;&|<>]+\.json)", cmd)
        spec_path = ROOT / m.group(1).strip("'\"") if m else None
        if spec_path and spec_path.is_file():
            try:
                spec = json.loads(spec_path.read_text(encoding="utf-8"))
                pptx = ROOT / "output" / f"ir-{spec['name']}" / "deck.pptx"
                pptx = pptx.with_name(spec.get("out_file") or "deck.pptx")
                if pptx.exists():
                    code, out = run(["ir/scripts/check_margins.py", str(pptx), "--tokens", spec.get("tokens") or "tokens.json"])
                    if code:
                        problems.append(f"[여백 검사 실패] {pptx.relative_to(ROOT)}\n{out}")
                    sty = spec.get("style")
                    args = ["ir/scripts/check_style.py", str(pptx)] + (["--style", sty] if isinstance(sty, str) else [])
                    code, out = run(args)
                    if code:
                        problems.append(f"[서식 검사 실패: 최소 글자·폰트·선 굵기] {pptx.relative_to(ROOT)}\n{out}")
            except Exception as e:  # noqa: BLE001
                problems.append(f"[훅 오류] {e}")

    if problems:
        print("\n\n".join(problems) + "\n→ 위 문제를 고친 뒤 다시 생성할 것.", file=_sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    _sys.exit(main())
