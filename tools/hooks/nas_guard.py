"""PreToolUse 훅: NAS 파일 삭제·이동·덮어쓰기를 무조건 차단한다.

NAS 경로는 tools/nas.json 의 "roots" 목록 (예: "\\\\NAS01\\work", "Z:\\", "//nas01/work").
- Edit / Write / MultiEdit / NotebookEdit 가 NAS 경로를 대상으로 하면 차단
- Bash / PowerShell 명령에 NAS 경로와 삭제·이동·덮어쓰기 동작이 함께 있으면 차단
  (rm, rmdir, rd, del, erase, unlink, mv, move, ren, Remove-Item, Move-Item, Rename-Item, Clear-Content,
   Set-Content, Out-File, >, >>, robocopy /MIR /MOVE /PURGE, xcopy, shutil.rmtree, os.remove, git clean ...)
- NAS 에서 다른 곳으로 '복사'와 '읽기'는 허용 (읽기는 settings.json 의 ask 규칙으로 매번 허가를 받음)
차단되면 exit 2 → Claude Code 가 도구 실행을 막는다.
"""
import sys as _sys
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = ROOT / "tools" / "nas.json"

DANGER = re.compile(
    r"(\brm\b|\brmdir\b|\brd\b|\bdel\b|\berase\b|\bunlink\b|\bmv\b|\bmove\b|\bren(ame)?\b|"
    r"Remove-Item|Move-Item|Rename-Item|Clear-Content|Clear-Item|Set-Content|Add-Content|Out-File|"
    r"New-Item\b[^|;]*-Force|Copy-Item\b[^|;]*-Force|robocopy|xcopy|\bformat\b|"
    r"rmtree|os\.remove|os\.unlink|os\.rename|os\.replace|Path\([^)]*\)\.(unlink|rmdir|rename|replace|write_)|"
    r"shutil\.(move|rmtree)|git\s+clean|git\s+rm|\btruncate\b|\bshred\b|>{1,2})",
    re.I,
)


def norm(p):
    return p.replace("/", "\\").rstrip("\\").lower()


def roots():
    try:
        cfg = json.loads(CFG.read_text(encoding="utf-8"))
        return [norm(r) for r in cfg.get("roots", []) if r.strip()]
    except Exception:  # noqa: BLE001
        return []


def hits_nas(text, rs):
    t = norm(text)
    return any(r and r in t for r in rs)


def main():
    _sys.stderr.reconfigure(encoding="utf-8")
    rs = roots()
    if not rs:
        return 0
    try:
        ev = json.loads(_sys.stdin.buffer.read().decode("utf-8", "replace") or "{}")
    except json.JSONDecodeError:
        return 0
    tool, inp = ev.get("tool_name", ""), ev.get("tool_input", {}) or {}
    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        fp = inp.get("file_path") or inp.get("notebook_path") or ""
        if hits_nas(fp, rs):
            print(f"[NAS 보호] NAS 파일은 수정·덮어쓰기 금지: {fp}\n→ 필요하면 프로젝트 안으로 복사해서 작업할 것.", file=_sys.stderr)
            return 2
    elif tool in ("Bash", "PowerShell"):
        cmd = inp.get("command", "")
        # NAS 쪽으로 복사(덮어쓰기 위험): 복사 명령의 마지막 인자가 NAS 경로면 차단
        for part in re.split(r"[;&|\n]+", cmd):
            toks = part.strip().split()
            if toks and re.match(r"(cp|copy|Copy-Item|scp|rsync)$", toks[0], re.I) and len(toks) > 2 and hits_nas(toks[-1], rs):
                print("[NAS 보호] NAS로 복사(덮어쓰기)는 금지. NAS → 프로젝트 방향만 허용.", file=_sys.stderr)
                return 2
        if hits_nas(cmd, rs) and DANGER.search(cmd):
            print("[NAS 보호] NAS 경로에 삭제·이동·덮어쓰기가 포함된 명령은 실행할 수 없음.\n"
                  "→ NAS는 읽기와 '프로젝트로 복사'만 허용. 명령을 나눠서 NAS에는 읽기만 할 것.", file=_sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    _sys.exit(main())
