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


def _merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in (over or {}).items():
        out[k] = _merge(base[k], v) if isinstance(v, dict) and isinstance(base.get(k), dict) else v
    return out


def load(path: Path | None = None) -> Config:
    """기본값(config.yaml) 위에 사용자 설정 파일을 덮어씀 — 일부 키만 있어도 동작."""
    path = path or Path(os.environ.get("AI_MANAGER_CONFIG", ROOT / "config.yaml"))
    with open(ROOT / "config.yaml", encoding="utf-8") as f:
        base = yaml.safe_load(f)
    with open(path, encoding="utf-8") as f:
        cfg = Config(_merge(base, yaml.safe_load(f)))
    ws = Path(os.path.expanduser(cfg["workspace"]))
    cfg["workspace"] = str(ws)
    for sub in ("drafts", "references", "fonts", "guidelines", "reports", ".context/screens", ".state", "logs"):
        (ws / sub).mkdir(parents=True, exist_ok=True)
    return cfg


def workspace(cfg: Config) -> Path:
    return Path(cfg["workspace"])
