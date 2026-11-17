"""큐에서 꺼낸 작업을 Claude 에이전트로 실행하고 결과를 워크스페이스에 저장."""
from __future__ import annotations

import re
import time
from pathlib import Path

from . import claude_runner
from .config import ROOT
from .prompts import render

FOLDER = {"reference": "references", "fonts": "fonts", "draft": "drafts", "guideline": "guidelines"}
TOOLS = {
    "reference": ["Read", "Write", "Edit", "WebSearch", "WebFetch"],
    "fonts": ["Read", "Write", "Edit", "WebSearch", "WebFetch"],
    "draft": ["Read", "Write", "Edit", "Glob"],
    "guideline": ["Read", "Write", "Edit", "Glob"],
}


def slug(text: str) -> str:
    s = re.sub(r"[^\w가-힣-]+", "-", text).strip("-")
    return s[:50] or "task"


def run_task(task, cfg, ws: Path) -> tuple[claude_runner.RunResult, Path]:
    out = ws / FOLDER[task["kind"]] / f"{time.strftime('%Y%m%d-%H%M')}-{slug(task['title'])}"
    out.mkdir(parents=True, exist_ok=True)
    rules = (ROOT / "prompts" / "common_rules.md").read_text(encoding="utf-8")
    prompt = render(task["kind"], title=task["title"], detail=task["detail"],
                    context=task["context_json"] or "(없음)", rules=rules)
    extra = [ws / "guidelines"] if task["kind"] == "guideline" else []
    res = claude_runner.run(prompt, cwd=out, cfg=cfg, tools=TOOLS[task["kind"]], extra_dirs=extra)
    return res, out
