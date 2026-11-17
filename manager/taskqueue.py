"""SQLite 작업 큐 — 중복 방지, 우선순위, 시간당 실행 수 집계."""
from __future__ import annotations

import sqlite3
import threading
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kind TEXT NOT NULL,           -- reference | fonts | draft | guideline | selfupdate
  title TEXT NOT NULL,
  detail TEXT DEFAULT '',
  dedup_key TEXT UNIQUE,
  priority INTEGER DEFAULT 5,   -- 1 높음 ~ 9 낮음
  heavy INTEGER DEFAULT 0,      -- 1이면 자리 비움일 때만 실행
  status TEXT DEFAULT 'queued', -- queued | running | done | failed | skipped
  context_json TEXT DEFAULT '',
  output_dir TEXT DEFAULT '',
  error TEXT DEFAULT '',
  created REAL, started REAL, finished REAL
);
CREATE INDEX IF NOT EXISTS idx_status ON tasks(status, priority, created);
"""


class TaskQueue:
    def __init__(self, path: Path):
        self.db = sqlite3.connect(str(path), check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.lock = threading.Lock()
        with self.lock:
            self.db.executescript(SCHEMA)
            # 비정상 종료로 running에 걸린 작업 복구
            self.db.execute("UPDATE tasks SET status='queued' WHERE status='running'")
            self.db.commit()

    def add(self, kind, title, detail="", dedup_key=None, priority=5, heavy=False, context_json="") -> bool:
        key = dedup_key or f"{kind}:{title}".lower()
        with self.lock:
            try:
                self.db.execute(
                    "INSERT INTO tasks(kind,title,detail,dedup_key,priority,heavy,context_json,created)"
                    " VALUES (?,?,?,?,?,?,?,?)",
                    (kind, title, detail, key, int(priority), int(bool(heavy)), context_json, time.time()))
                self.db.commit()
                return True
            except sqlite3.IntegrityError:
                return False  # 이미 했거나 대기 중인 작업

    def next(self, allow_heavy: bool):
        with self.lock:
            row = self.db.execute(
                "SELECT * FROM tasks WHERE status='queued' AND (heavy=0 OR ?)"
                " ORDER BY priority, created LIMIT 1", (int(allow_heavy),)).fetchone()
            if row:
                self.db.execute("UPDATE tasks SET status='running', started=? WHERE id=?",
                                (time.time(), row["id"]))
                self.db.commit()
            return row

    def finish(self, task_id, ok: bool, output_dir="", error=""):
        with self.lock:
            self.db.execute("UPDATE tasks SET status=?, finished=?, output_dir=?, error=? WHERE id=?",
                            ("done" if ok else "failed", time.time(), output_dir, error[:2000], task_id))
            self.db.commit()

    def requeue(self, task_id):
        with self.lock:
            self.db.execute("UPDATE tasks SET status='queued', started=NULL WHERE id=?", (task_id,))
            self.db.commit()

    def pending_count(self) -> int:
        with self.lock:
            return self.db.execute("SELECT COUNT(*) FROM tasks WHERE status='queued'").fetchone()[0]

    def started_since(self, seconds: float) -> int:
        with self.lock:
            return self.db.execute("SELECT COUNT(*) FROM tasks WHERE started > ?",
                                   (time.time() - seconds,)).fetchone()[0]

    def recent(self, limit=15):
        with self.lock:
            return self.db.execute(
                "SELECT kind,title,status FROM tasks ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
