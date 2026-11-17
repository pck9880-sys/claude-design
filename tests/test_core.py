import json

from manager import claude_runner, planner, safety, workers
from manager.config import load
from manager.prompts import render
from manager.taskqueue import TaskQueue

CFG = {"capture": {"exclude_apps": ["1Password", "카카오톡"], "exclude_title_keywords": ["은행", "password"]}}


def test_privacy_filter():
    assert safety.is_private("1Password 8", "", CFG)
    assert safety.is_private("Safari", "KB국민은행 로그인", CFG)
    assert not safety.is_private("Adobe InDesign 2025", "poster.indd @ 50%", CFG)


def test_protected_paths():
    prot = ["config.yaml", "manager/safety.py", "install/"]
    assert safety.touches_protected(["manager/main.py"], prot) == []
    assert safety.touches_protected(["config.yaml", "install/x.sh", "manager\\safety.py"], prot) == \
        ["config.yaml", "install/x.sh", "manager/safety.py"]


def test_stop_and_pause(tmp_path):
    assert not safety.is_paused(tmp_path)
    (tmp_path / "PAUSE").touch()
    assert safety.is_paused(tmp_path) and not safety.is_stopped(tmp_path)
    (tmp_path / "STOP").touch()
    assert safety.is_stopped(tmp_path)


def test_queue_dedup_priority_heavy(tmp_path):
    q = TaskQueue(tmp_path / "t.db")
    assert q.add("fonts", "A", priority=5)
    assert not q.add("fonts", "A")                     # 중복
    assert q.add("draft", "B", priority=1, heavy=True)
    assert q.next(allow_heavy=False)["title"] == "A"   # heavy는 자리 비움일 때만
    assert q.next(allow_heavy=False) is None
    t = q.next(allow_heavy=True)
    assert t["title"] == "B"
    q.finish(t["id"], True, "/out")
    assert q.started_since(60) == 2 and q.pending_count() == 0


def test_queue_recovers_running(tmp_path):
    q = TaskQueue(tmp_path / "t.db")
    q.add("fonts", "A")
    q.next(True)
    q2 = TaskQueue(tmp_path / "t.db")
    assert q2.pending_count() == 1


def test_parse_tasks_filters_and_clamps():
    text = 'blah\n[{"kind":"fonts","title":"헤드라인","priority":0},{"kind":"hack","title":"x"},' \
           '{"kind":"draft","title":"카피"}]'
    tasks = planner.parse_tasks(text)
    assert [t["kind"] for t in tasks] == ["fonts", "draft"]
    assert tasks[0]["priority"] == 1 and tasks[1]["heavy"] is True
    assert planner.parse_tasks("할 일 없음") == []


def test_parse_claude_output_limit():
    ok = claude_runner.parse_output(0, json.dumps({"result": "done", "is_error": False}), "")
    assert ok.ok and ok.text == "done" and not ok.limited
    lim = claude_runner.parse_output(1, "", "Claude usage limit reached. Resets at 5pm")
    assert not lim.ok and lim.limited


def test_prompts_render():
    for k in ("reference", "fonts", "draft", "guideline"):
        s = render(k, title="T", detail="D", context="{}", rules="R")
        assert "T" in s and "R" in s and "{title}" not in s
    p = render("planner", context="C", recent="-", feedback="-")
    assert '"kind": "fonts"' in p
    s = render("selfupdate", errors="", feedback="", backlog="", protected="config.yaml")
    assert "config.yaml" in s


def test_slug():
    assert workers.slug("포스터 / 헤드라인: 폰트!") == "포스터-헤드라인-폰트"


def test_config_creates_workspace(tmp_path, monkeypatch):
    cfg_file = tmp_path / "c.yaml"
    cfg_file.write_text(f"workspace: {tmp_path / 'ws'}\n", encoding="utf-8")
    cfg = load(cfg_file)
    assert (tmp_path / "ws" / "fonts").is_dir() and cfg.workspace.endswith("ws")


def test_partial_config_uses_defaults(tmp_path):
    f = tmp_path / "c.yaml"
    f.write_text(f"workspace: {tmp_path / 'ws'}\nclaude: {{max_tasks_per_hour: 1}}\n", encoding="utf-8")
    cfg = load(f)
    assert cfg["intervals"]["dispatch_minutes"] == 10
    assert cfg["claude"]["max_tasks_per_hour"] == 1 and cfg["claude"]["binary"] == "claude"
