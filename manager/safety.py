"""안전장치. self-update 보호 대상 — AI가 수정할 수 없음."""
from __future__ import annotations

from pathlib import Path


def is_stopped(ws: Path) -> bool:
    """워크스페이스에 STOP 파일이 있으면 매니저 전체 정지(긴급 정지)."""
    return (ws / "STOP").exists()


def is_paused(ws: Path) -> bool:
    """PAUSE 파일이 있으면 새 작업 배분/업데이트를 멈춤(진행 중 작업은 마무리)."""
    return (ws / "PAUSE").exists() or is_stopped(ws)


def is_private(app: str, title: str, cfg) -> bool:
    """민감한 앱/창이면 True → 캡처하지 않음."""
    a, t = (app or "").lower(), (title or "").lower()
    if any(x.lower() in a for x in cfg["capture"]["exclude_apps"]):
        return True
    if any(x.lower() in t for x in cfg["capture"]["exclude_title_keywords"]):
        return True
    return False


def touches_protected(changed_files: list[str], protected: list[str]) -> list[str]:
    """변경 파일 중 보호 경로에 해당하는 것 반환."""
    bad = []
    for f in changed_files:
        f = f.replace("\\", "/")
        for p in protected:
            if f == p or (p.endswith("/") and f.startswith(p)):
                bad.append(f)
                break
    return bad
