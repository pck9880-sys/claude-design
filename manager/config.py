from __future__ import annotations

import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


class Config(dict):
    """dict + 점 접근 (cfg.claude.binary)."""

    def __getattr__(self, key):
        try:
            v = self[key]
        except KeyError as e:
            raise AttributeError(key) from e
        return Config(v) if isinstance(v, dict) else v


def load(path: Path | None = None) -> Config:
    path = path or Path(os.environ.get("AI_MANAGER_CONFIG", ROOT / "config.yaml"))
    with open(path, encoding="utf-8") as f:
        cfg = Config(yaml.safe_load(f))
    ws = Path(os.path.expanduser(cfg["workspace"]))
    cfg["workspace"] = str(ws)
    for sub in ("drafts", "references", "fonts", "guidelines", "reports", ".context/screens", ".state", "logs"):
        (ws / sub).mkdir(parents=True, exist_ok=True)
    return cfg


def workspace(cfg: Config) -> Path:
    return Path(cfg["workspace"])
