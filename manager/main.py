"""매니저 본체: 10분마다 상황 파악·작업 배분, 작업자는 쉬지 않고 큐 소화, 1시간마다 자기 업그레이드."""
from __future__ import annotations

import json
import logging
import sys
import threading
import time
from pathlib import Path

from . import adobe, capture, planner, selfupdate, workers
from .config import load, workspace
from .platform_utils import active_window, idle_seconds, notify
from .safety import is_paused, is_private, is_stopped
from .taskqueue import TaskQueue


class Manager:
    def __init__(self):
        self.cfg = load()
        self.ws = workspace(self.cfg)
        self.q = TaskQueue(self.ws / ".state" / "tasks.db")
        self.state_path = self.ws / ".state" / "manager.json"
        self.state = self._load_state()
        self.started_at = time.time()
        self.worker_busy = threading.Event()
        self.updating = threading.Event()
        self._setup_logging()

    # ---------- 상태/로그 ----------
    def _load_state(self) -> dict:
        try:
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        except Exception:
            return {"last_dispatch": 0, "last_selfupdate": time.time(), "backoff_until": 0, "last_hash": 0,
                    "last_doc": ""}

    def _save_state(self):
        self.state_path.write_text(json.dumps(self.state, ensure_ascii=False), encoding="utf-8")

    def _setup_logging(self):
        logs = self.ws / "logs"
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        self.log = logging.getLogger("ai-manager")
        self.log.setLevel(logging.INFO)
        for path, level in ((logs / "manager.log", logging.INFO), (logs / "errors.log", logging.WARNING)):
            h = logging.FileHandler(path, encoding="utf-8")
            h.setLevel(level)
            h.setFormatter(fmt)
            self.log.addHandler(h)
        self.log.addHandler(logging.StreamHandler(sys.stdout))

    def report(self, line: str):
        path = self.ws / "reports" / f"{time.strftime('%Y-%m-%d')}.md"
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"- {time.strftime('%H:%M')} {line}\n")

    # ---------- 판단 ----------
    def is_idle(self) -> bool:
        return idle_seconds() > self.cfg["idle"]["idle_after_minutes"] * 60

    def limited(self) -> bool:
        return time.time() < self.state.get("backoff_until", 0)

    def backoff(self, why: str):
        self.state["backoff_until"] = time.time() + self.cfg["claude"]["backoff_minutes_on_limit"] * 60
        self._save_state()
        self.log.warning(f"사용량 한도 도달 → {self.cfg['claude']['backoff_minutes_on_limit']}분 휴식 ({why})")

    def budget_ok(self) -> bool:
        c = self.cfg["claude"]
        cap = c["max_tasks_per_hour_idle"] if self.is_idle() else c["max_tasks_per_hour"]
        return self.q.started_since(3600) < cap

    # ---------- 10분: 상황 파악 + 배분 ----------
    def dispatch(self):
        app, title = active_window()
        if is_private(app, title, self.cfg):
            self.log.info("민감한 창 감지 → 캡처/배분 건너뜀")
            return
        ctx = {"app": app, "window_title": title, "user_idle": self.is_idle(),
               "time": time.strftime("%Y-%m-%d %H:%M")}
        doc = adobe.document_info(app)
        if doc:
            ctx["document"] = doc

        changed = False
        if self.cfg["capture"]["enabled"]:
            shots = self.ws / ".context" / "screens"
            shot = capture.grab(shots, self.cfg["capture"]["downscale_width"])
            if shot:
                h = capture.ahash(shot)
                changed = capture.distance(h, self.state.get("last_hash", 0)) >= self.cfg["capture"]["change_threshold"]
                self.state["last_hash"] = h
                ctx["screenshot"] = str(shot)
                capture.prune(shots, self.cfg["capture"]["keep_last"])
        doc_key = json.dumps(doc, sort_keys=True, ensure_ascii=False) if doc else title
        changed = changed or doc_key != self.state.get("last_doc")
        self.state["last_doc"] = doc_key
        self._save_state()

        if not changed and self.q.pending_count() > 0:
            self.log.info("화면 변화 없음 + 대기 작업 있음 → 플래너 생략")
            return
        feedback_path = self.ws / "FEEDBACK.md"
        feedback = feedback_path.read_text(encoding="utf-8")[-3000:] if feedback_path.exists() else ""
        tasks, res = planner.plan(ctx, self.q.recent(), feedback, self.cfg, self.ws)
        if res.limited:
            return self.backoff("planner")
        ctx_json = json.dumps({k: v for k, v in ctx.items() if k != "screenshot"}, ensure_ascii=False)
        added = [t["title"] for t in tasks if self.q.add(context_json=ctx_json, **t)]
        if added:
            self.log.info(f"새 작업 {len(added)}개: {added}")

    # ---------- 작업자: 쉬지 않고 큐 소화 ----------
    def worker_loop(self):
        while not is_stopped(self.ws):
            if is_paused(self.ws) or self.updating.is_set() or self.limited() or not self.budget_ok():
                time.sleep(30)
                continue
            task = self.q.next(allow_heavy=self.is_idle())
            if not task:
                time.sleep(30)
                continue
            self.worker_busy.set()
            try:
                self.log.info(f"작업 시작 #{task['id']} [{task['kind']}] {task['title']}")
                res, out = workers.run_task(task, self.cfg, self.ws)
                if res.limited:
                    self.q.requeue(task["id"])
                    self.backoff(task["title"])
                    continue
                self.q.finish(task["id"], res.ok, str(out), "" if res.ok else res.text)
                if res.ok:
                    self.report(f"✅ [{task['kind']}] {task['title']} → `{out}`")
                    if self.cfg.get("notify"):
                        notify("AI 매니저", f"준비 완료: {task['title']}")
                else:
                    self.log.warning(f"작업 실패 #{task['id']}: {res.text[:500]}")
            except Exception:
                self.log.exception(f"작업 예외 #{task['id']}")
                self.q.finish(task["id"], False, error="exception")
            finally:
                self.worker_busy.clear()

    # ---------- 1시간: 자기 업그레이드 ----------
    def maybe_self_update(self) -> bool:
        iv = self.cfg["intervals"]
        since = time.time() - self.state.get("last_selfupdate", 0)
        all_done = self.q.pending_count() == 0 and not self.worker_busy.is_set()
        due = since >= iv["self_update_minutes"] * 60 or (all_done and since >= iv["idle_self_update_minutes"] * 60)
        if not due or self.limited() or selfupdate.PENDING.exists():
            return False
        self.updating.set()
        applied = False
        try:
            while self.worker_busy.is_set():   # 진행 중인 작업이 끝날 때까지 대기
                time.sleep(10)
            self.state["last_selfupdate"] = time.time()
            self._save_state()
            result = selfupdate.attempt(self.cfg, self.ws, self.log.warning)
            self.log.info(f"self-update: {result}")
            if result == "limited":
                self.backoff("self-update")
            if result == "applied":
                self.report("🔧 매니저 자기 업데이트 적용 (재시작)")
                applied = True
                return True
            return False
        except Exception:
            self.log.exception("self-update 예외")
            return False
        finally:
            if not applied:          # 적용됐으면 재시작까지 새 작업을 잡지 않음
                self.updating.clear()

    def run(self) -> int:
        self.log.info(f"AI 매니저 시작 (workspace={self.ws})")
        threading.Thread(target=self.worker_loop, daemon=True).start()
        iv = self.cfg["intervals"]
        while True:
            if is_stopped(self.ws):
                self.log.info("STOP 파일 감지 → 종료")
                return 0
            selfupdate.confirm_if_healthy(self.cfg, self.started_at, self.log.info)
            if not is_paused(self.ws):
                try:
                    if time.time() - self.state.get("last_dispatch", 0) >= iv["dispatch_minutes"] * 60 \
                            and not self.limited():
                        self.state["last_dispatch"] = time.time()
                        self.dispatch()
                except Exception:
                    self.log.exception("dispatch 예외")
                if self.maybe_self_update():
                    return selfupdate.RESTART_CODE
            time.sleep(iv["tick_seconds"])


if __name__ == "__main__":
    sys.exit(Manager().run())
