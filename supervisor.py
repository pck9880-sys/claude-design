"""상주 프로세스. OS 로그인 시 이것만 실행하면 됨 (LaunchAgent / 작업 스케줄러).

- manager.main 을 실행하고, 종료 코드 42(자기 업데이트)면 재시작
- 업데이트 직후 비정상 종료하면 이전 버전으로 자동 롤백
- 짧은 시간에 반복 크래시하면 정지하고 알림
보호 대상 — AI가 수정할 수 없음.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PENDING = ROOT / ".selfupdate" / "pending_verify.json"
RESTART_CODE = 42


def notify(msg: str) -> None:
    try:
        sys.path.insert(0, str(ROOT))
        from manager.platform_utils import notify as n
        n("AI 매니저", msg)
    except Exception:
        pass


def rollback() -> bool:
    try:
        prev = json.loads(PENDING.read_text(encoding="utf-8"))["previous"]
        subprocess.run(["git", "reset", "--hard", prev], cwd=ROOT, check=True)
        PENDING.unlink(missing_ok=True)
        notify("업데이트 후 오류가 발생해 이전 버전으로 되돌렸습니다.")
        return True
    except Exception as e:
        notify(f"롤백 실패: {e}")
        return False


def main() -> None:
    crashes: list[float] = []
    while True:
        start = time.time()
        code = subprocess.call([sys.executable, "-m", "manager.main"], cwd=ROOT)
        if code == 0:
            break                       # STOP 파일 등 정상 종료
        if code == RESTART_CODE:
            continue                    # 업데이트 반영 후 재시작
        if PENDING.exists() and rollback():
            continue
        crashes = [t for t in crashes if time.time() - t < 600] + [time.time()]
        if len(crashes) >= 3:
            notify("10분 내 3회 크래시 — 매니저를 정지했습니다. logs를 확인하세요.")
            break
        time.sleep(min(60, 5 * len(crashes)) if time.time() - start < 60 else 5)


if __name__ == "__main__":
    main()
