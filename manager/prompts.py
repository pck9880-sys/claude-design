from __future__ import annotations

from .config import ROOT


class _Safe(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def render(name: str, **kw) -> str:
    text = (ROOT / "prompts" / f"{name}.md").read_text(encoding="utf-8")
    return text.format_map(_Safe(kw))
