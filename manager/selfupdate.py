"""매니저 자기 업그레이드. 보호 대상 — AI가 수정할 수 없음.

흐름: git worktree에서 Claude가 수정 → 보호 경로/크기 검사 → 테스트 → 통과 시 main에 반영
→ 종료 코드 42로 재시작 요청 → supervisor가 재시작, 일정 시간 내 죽으면 자동 롤백.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from . import claude_runner
from .config import ROOT
from .prompts import render
from .safety import touches_protected

RESTART_CODE = 42
STATE = ROOT / ".selfupdate"
PENDING = STATE / "pending_verify.json"


def git(*args, cwd=ROOT, check=True) -> str:
    p = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, encoding="utf-8")
    if check and p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.strip()}")
    return p.stdout.strip()


def _tail(path: Path, n=60) -> str:
    if not path.exists():
        return "(없음)"
    return "\n".join(path.read_text(encoding="utf-8", errors="ignore").splitlines()[-n:])


def attempt(cfg, ws: Path, log) -> str:
    """반환: 'applied' | 'nochange' | 'rejected:<사유>' | 'limited' | 'skipped:<사유>'"""
    su = cfg["self_update"]
    if not su["enabled"]:
        return "skipped:disabled"
    if git("status", "--porcelain"):
        return "skipped:dirty-tree"  # 사람이 직접 고치는 중이면 손대지 않음

    STATE.mkdir(exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    branch, wt = f"selfupdate/{ts}", STATE / f"wt-{ts}"
    base = git("rev-parse", "HEAD")
    git("worktree", "add", "-b", branch, str(wt), "HEAD")
    try:
        prompt = render("selfupdate",
                        errors=_tail(ws / "logs" / "errors.log"),
                        feedback=_tail(ws / "FEEDBACK.md", 40),
                        backlog=_tail(ROOT / "docs" / "BACKLOG.md", 80),
                        protected=", ".join(su["protected_paths"]))
        res = claude_runner.run(prompt, cwd=wt, cfg=cfg, tools=["Read", "Edit", "Write", "Glob", "Grep"])
        if res.limited:
            return "limited"
        if not res.ok:
            return f"rejected:claude-error {res.text[:200]}"

        git("add", "-A", cwd=wt)
        changed = [f for f in git("diff", "--cached", "--name-only", cwd=wt).splitlines() if f]
        if not changed:
            return "nochange"
        bad = touches_protected(changed, su["protected_paths"])
        if bad:
            return f"rejected:protected {bad}"
        stat = git("diff", "--cached", "--numstat", cwd=wt).splitlines()
        lines = sum(int(a) + int(d) for a, d, _ in (s.split("\t") for s in stat) if a.isdigit() and d.isdigit())
        if lines > su["max_diff_lines"]:
            return f"rejected:too-large ({lines} lines)"

        if su["require_tests"]:
            t = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x"], cwd=str(wt),
                               capture_output=True, text=True, timeout=600)
            if t.returncode != 0:
                log(f"self-update tests failed:\n{t.stdout[-1500:]}")
                return "rejected:tests-failed"

        summary = next((l[8:].strip() for l in reversed(res.text.splitlines()) if l.startswith("SUMMARY:")),
                       "self-update")
        git("-c", "user.name=AI Manager", "-c", "user.email=ai-manager@localhost",
            "commit", "-m", f"self-update: {summary}", cwd=wt)
        git("tag", f"good-{ts}", base)          # 롤백 지점
        git("merge", "--ff-only", branch)      # main 작업트리에 반영
        PENDING.write_text(json.dumps({"previous": base, "applied_at": time.time(), "summary": summary}),
                           encoding="utf-8")
        log(f"self-update applied: {summary}")
        return "applied"
    finally:
        git("worktree", "remove", "--force", str(wt), check=False)
        shutil.rmtree(wt, ignore_errors=True)
        git("branch", "-D", branch, check=False)


def confirm_if_healthy(cfg, started_at: float, log) -> None:
    """업데이트 후 healthy_after_minutes 동안 살아 있으면 확정."""
    if PENDING.exists() and time.time() - started_at > cfg["self_update"]["healthy_after_minutes"] * 60:
        PENDING.unlink(missing_ok=True)
        log("self-update confirmed healthy")
