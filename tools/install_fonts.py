"""assets/fonts 의 폰트를 이 기기에 설치 (클라우드 세션·다른 PC용).

- Linux(클라우드 세션): ~/.local/share/fonts 에 복사 후 fc-cache
- macOS: ~/Library/Fonts 에 복사
- Windows: 자동 설치하지 않음 → 폴더를 열어 폰트 파일 선택 후 우클릭 > 설치
사용: python tools/install_fonts.py
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")
import platform
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "fonts"
files = [f for f in SRC.rglob("*") if f.suffix.lower() in (".ttf", ".otf")]

system = platform.system()
if system == "Linux":
    dst = Path.home() / ".local" / "share" / "fonts" / "claude-design"
elif system == "Darwin":
    dst = Path.home() / "Library" / "Fonts"
else:
    print(f"Windows: {SRC} 를 열어 폰트 파일을 모두 선택 → 우클릭 → '설치' (이미 설치된 PC면 건너뜀)")
    _sys.exit(0)

dst.mkdir(parents=True, exist_ok=True)
for f in files:
    shutil.copy2(f, dst / f.name)
if system == "Linux" and shutil.which("fc-cache"):
    subprocess.run(["fc-cache", "-f", str(dst)], check=False)
print(f"설치: {len(files)}개 → {dst}")
