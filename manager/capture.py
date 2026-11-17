"""화면 캡처 + 변화 감지. macOS는 '화면 기록' 권한 필요."""
from __future__ import annotations

import time
from pathlib import Path

from PIL import Image


def grab(out_dir: Path, width: int) -> Path | None:
    try:
        import mss
    except ImportError:
        return None
    try:
        with mss.mss() as sct:
            mon = sct.monitors[1]  # 주 모니터
            shot = sct.grab(mon)
            img = Image.frombytes("RGB", shot.size, shot.rgb)
    except Exception:  # 권한 없음/디스플레이 없음
        return None
    if img.width > width:
        img = img.resize((width, int(img.height * width / img.width)))
    path = out_dir / f"screen-{time.strftime('%Y%m%d-%H%M%S')}.png"
    img.save(path, optimize=True)
    return path


def ahash(path: Path) -> int:
    """8x8 평균 해시 — 화면이 바뀌었는지 대략 판단."""
    img = Image.open(path).convert("L").resize((8, 8))
    px = list(img.getdata())
    avg = sum(px) / len(px)
    return sum(1 << i for i, p in enumerate(px) if p >= avg)


def distance(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


def prune(out_dir: Path, keep: int) -> None:
    files = sorted(out_dir.glob("screen-*.png"))
    for f in files[:-keep]:
        f.unlink(missing_ok=True)
