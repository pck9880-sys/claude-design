"""Claude Code CLI(헤드리스, `claude -p`)로 작업 실행. Max 계정 로그인 상태를 그대로 사용."""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

LIMIT_MARKERS = ("usage limit", "limit reached", "rate limit", "rate_limit", "overloaded",
                 "too many requests", "429")


@dataclass
class RunResult:
    ok: bool
    text: str
    limited: bool = False   # 사용량 한도 → 매니저가 백오프
    cost_usd: float = 0.0


def run(prompt: str, cwd: Path, cfg, tools: list[str], extra_dirs: list[Path] = (),
        system_append: str = "") -> RunResult:
    c = cfg["claude"]
    cmd = [c["binary"], "-p", prompt, "--output-format", "json",
           "--permission-mode", "acceptEdits",
           "--allowedTools", ",".join(tools)]
    if c.get("model"):
        cmd += ["--model", c["model"]]
    for d in extra_dirs:
        cmd += ["--add-dir", str(d)]
    if system_append:
        cmd += ["--append-system-prompt", system_append]
    try:
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                           encoding="utf-8", timeout=c["task_timeout_minutes"] * 60)
    except subprocess.TimeoutExpired:
        return RunResult(False, "timeout")
    except FileNotFoundError:
        return RunResult(False, f"claude CLI를 찾을 수 없음: {c['binary']}")
    return parse_output(p.returncode, p.stdout, p.stderr)


def parse_output(code: int, stdout: str, stderr: str) -> RunResult:
    text, is_error, cost = stdout, code != 0, 0.0
    try:
        data = json.loads(stdout)
        text = data.get("result") or ""
        is_error = is_error or bool(data.get("is_error"))
        cost = float(data.get("total_cost_usd") or 0)
    except (json.JSONDecodeError, TypeError):
        pass
    blob = f"{text}\n{stderr}".lower()
    limited = is_error and any(m in blob for m in LIMIT_MARKERS)
    return RunResult(not is_error, text if text else stderr, limited, cost)
