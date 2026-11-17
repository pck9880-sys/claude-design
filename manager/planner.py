"""현재 작업 상황(스크린샷 + Adobe 문서 정보)을 보고 미리 할 일을 뽑는다."""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import claude_runner
from .prompts import render

KINDS = {"reference", "fonts", "draft", "guideline"}


def plan(context: dict, recent: list, feedback: str, cfg, ws: Path) -> tuple[list[dict], claude_runner.RunResult]:
    prompt = render("planner", context=json.dumps(context, ensure_ascii=False, indent=2),
                    recent="\n".join(f"- [{r['status']}] {r['kind']}: {r['title']}" for r in recent) or "(없음)",
                    feedback=feedback or "(없음)")
    res = claude_runner.run(prompt, cwd=ws, cfg=cfg, tools=["Read"])
    return (parse_tasks(res.text) if res.ok else []), res


def parse_tasks(text: str) -> list[dict]:
    m = re.search(r"\[.*\]", text or "", re.S)
    if not m:
        return []
    try:
        items = json.loads(m.group(0))
    except json.JSONDecodeError:
        return []
    out = []
    for it in items if isinstance(items, list) else []:
        if not isinstance(it, dict) or it.get("kind") not in KINDS or not it.get("title"):
            continue
        out.append({
            "kind": it["kind"],
            "title": str(it["title"])[:200],
            "detail": str(it.get("detail", ""))[:2000],
            "dedup_key": str(it.get("dedup_key") or f"{it['kind']}:{it['title']}")[:200].lower(),
            "priority": max(1, min(9, int(it.get("priority", 5)))),
            "heavy": bool(it.get("heavy", it["kind"] == "draft")),
        })
    return out[:5]
