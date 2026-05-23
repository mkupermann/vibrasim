"""Tests for ``tools.bet_dispatcher.BetDispatcher``.

Pre-registration: these tests are the R-23 acceptance gates (see
``.eqmod/autopilot/QUEUE.yaml``). They run a real dispatcher against
a temp state dir + synthetic queue + synthetic mock-item subprocess.
No substrate code is exercised.

The four required tests:
    test_dispatcher_launches_queued_item
    test_dispatcher_hard_cap_kills_overrun
    test_dispatcher_evaluates_passed_item
    test_dispatcher_evaluates_null_item

Total wallclock target: < 30 s for the whole module (no ``slow`` marker).
The hard-cap test pays ~3 s for the SIGTERM grace window + a 2 s
``max_runtime_seconds``; everything else is sub-second.
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from bet_dispatcher import BetDispatcher, DEFAULT_MAX_RUNTIME_SECONDS  # noqa: E402
from validate_bet_queue import validate as validate_bet_queue  # noqa: E402


# ---- helpers ------------------------------------------------------------
def _write_queue(state_dir: Path, items: list[dict]) -> None:
    queue_path = state_dir / "queue.yaml"
    state_dir.mkdir(parents=True, exist_ok=True)
    queue_path.write_text(yaml.safe_dump({"items": items}, sort_keys=False))


def _read_queue(state_dir: Path) -> dict:
    return yaml.safe_load((state_dir / "queue.yaml").read_text())


def _make_mock_pytest(
    pytest_dir: Path,
    *,
    name: str,
    sleep_seconds: float = 0.0,
    result_verdict: str | None = None,
    fail: bool = False,
) -> Path:
    """Write a self-contained pytest file the dispatcher can launch.

    The mock test runs in the same venv as the dispatcher. It optionally
    sleeps (to test the hard cap), writes a result.json with the chosen
    verdict (to test result-driven evaluation), and either passes or
    fails depending on ``fail``.
    """
    pytest_dir.mkdir(parents=True, exist_ok=True)
    (pytest_dir / "__init__.py").touch()
    body = f'''"""Mock pytest target for bet_dispatcher tests — {name}."""
import json
import os
import time
from pathlib import Path


def test_{name}():
    sleep_s = {sleep_seconds!r}
    if sleep_s > 0:
        time.sleep(sleep_s)
    verdict = {result_verdict!r}
    if verdict is not None:
        out_dir = Path(os.environ.get("EQMOD_BET_OUT_DIR", "."))
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "result.json").write_text(
            json.dumps(
                {{"verdict": verdict, "mock": True, "name": "{name}"}},
                indent=2,
            )
        )
    assert not {fail!r}, "mock failure as requested"
'''
    path = pytest_dir / f"test_{name}.py"
    path.write_text(body)
    return path


def _wait_for_process_death(pid: int, timeout: float = 5.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        time.sleep(0.05)
    return False


def _wait_for_process_completion(pid: int, timeout: float = 30.0) -> bool:
    """Reap zombie children of this process and wait for ``pid`` to die.

    ``subprocess.Popen`` was used inside the dispatcher so the parent of
    the launched pytest is the test process. We poll ``os.kill(pid, 0)``
    until it raises ``ProcessLookupError``, reaping any waitable zombies
    so the OS lets the PID actually disappear (otherwise on macOS a
    finished child can stay as a zombie keeping the PID alive).
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        try:
            done_pid, _ = os.waitpid(pid, os.WNOHANG)
            if done_pid != 0:
                return True
        except ChildProcessError:
            return True
        except OSError:
            pass
        time.sleep(0.05)
    return False


@pytest.fixture()
def state_dir(tmp_path: Path) -> Path:
    sd = tmp_path / "bet"
    sd.mkdir(parents=True, exist_ok=True)
    return sd


@pytest.fixture()
def pytest_dir(tmp_path: Path) -> Path:
    """A tmp dir for mock pytest files; added to sys.path so pytest finds them."""
    pd = tmp_path / "mock_pytests"
    pd.mkdir(parents=True, exist_ok=True)
    return pd


# ---- the four required tests --------------------------------------------
def test_dispatcher_launches_queued_item(state_dir: Path, pytest_dir: Path):
    """One queued item → tick() launches it, writes pidfile, marks running."""
    mock_test = _make_mock_pytest(
        pytest_dir, name="launch_smoke", sleep_seconds=2.0, result_verdict="null",
    )
    _write_queue(state_dir, [
        {
            "id": "BET-LAUNCH",
            "hypothesis": "launch path is exercised by tick()",
            "references": ["test_bet_dispatcher.py"],
            "pytest_target": str(mock_test),
            "status": "queued",
            "attempts": 0,
            "max_runtime_seconds": 60,
            "created_at": "2026-05-22T00:00:00",
            "finished_at": None,
        },
    ])

    dispatcher = BetDispatcher(state_dir=state_dir, repo=REPO)
    result = dispatcher.tick()

    try:
        assert result["action"] == "launched", result
        assert result["item"] == "BET-LAUNCH"
        assert dispatcher.pid_path.exists()
        pid = int(dispatcher.pid_path.read_text().strip())
        assert pid > 0
        assert dispatcher.current_item_path.read_text().strip() == "BET-LAUNCH"

        queue_after = _read_queue(state_dir)
        item = next(i for i in queue_after["items"] if i["id"] == "BET-LAUNCH")
        assert item["status"] == "running"
    finally:
        # Tear down any process the test launched
        if dispatcher.pid_path.exists():
            try:
                pid = int(dispatcher.pid_path.read_text().strip())
                dispatcher._kill_process_group(pid)
                _wait_for_process_completion(pid, timeout=5.0)
            except (ValueError, OSError):
                pass


def test_dispatcher_hard_cap_kills_overrun(state_dir: Path, pytest_dir: Path):
    """Mock item with max_runtime_seconds=2 sleeps 5s; dispatcher SIGKILLs."""
    mock_test = _make_mock_pytest(
        pytest_dir, name="hard_cap_sleep", sleep_seconds=5.0, result_verdict="passed",
    )
    _write_queue(state_dir, [
        {
            "id": "BET-CAP",
            "hypothesis": "hard cap kills runaway iterations",
            "references": ["R-LR-3 incident, LOGBOOK 2026-05-20"],
            "pytest_target": str(mock_test),
            "status": "queued",
            "attempts": 0,
            "max_runtime_seconds": 2,
            "created_at": "2026-05-22T00:00:00",
            "finished_at": None,
        },
    ])

    dispatcher = BetDispatcher(state_dir=state_dir, repo=REPO, term_grace_seconds=1.0)
    launch_result = dispatcher.tick()
    assert launch_result["action"] == "launched"
    pid = launch_result["pid"]

    # Wait past the 2s cap so the next tick triggers the kill branch
    time.sleep(2.5)
    kill_result = dispatcher.tick()

    assert kill_result["action"] == "killed", kill_result
    assert kill_result["item"] == "BET-CAP"
    assert kill_result["max_runtime_seconds"] == 2
    assert kill_result["elapsed"] > 2.0

    # Process must be dead
    assert _wait_for_process_completion(pid, timeout=5.0), (
        f"pid {pid} still alive after hard-cap kill"
    )

    queue_after = _read_queue(state_dir)
    item = next(i for i in queue_after["items"] if i["id"] == "BET-CAP")
    assert item["status"] == "failed", item
    assert item.get("attempts") == 1
    assert item.get("finished_at"), item
    blockers = item.get("blockers") or []
    assert any("hard-cap" in str(b) for b in blockers), blockers

    # Pidfile must be cleared so the next tick can pick a new item
    assert not dispatcher.pid_path.exists()
    assert not dispatcher.current_item_path.exists()


def test_dispatcher_evaluates_passed_item(state_dir: Path, pytest_dir: Path):
    """Process is gone, result.json says passed, pytest cross-check exits 0 → passed."""
    item_id = "BET-PASS"
    out_dir = state_dir / item_id
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "result.json").write_text(json.dumps({"verdict": "passed", "mock": True}))

    mock_test = _make_mock_pytest(
        pytest_dir, name="passed_eval", result_verdict="passed",
    )
    _write_queue(state_dir, [
        {
            "id": item_id,
            "hypothesis": "result.json verdict=passed survives cross-check",
            "references": [],
            "pytest_target": str(mock_test),
            "status": "running",
            "attempts": 0,
            "max_runtime_seconds": 60,
            "created_at": "2026-05-22T00:00:00",
            "finished_at": None,
        },
    ])

    # Simulate a finished process by writing a pidfile pointing at PID 1
    # — guaranteed alive, so we first need a *dead* pid. Spawn and reap.
    dummy = subprocess.Popen([sys.executable, "-c", "pass"])
    dummy.wait()
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "current.pid").write_text(str(dummy.pid))
    (state_dir / "current_item.txt").write_text(item_id)

    dispatcher = BetDispatcher(state_dir=state_dir, repo=REPO)
    result = dispatcher.tick()

    assert result["action"] == "evaluated", result
    assert result["item"] == item_id
    assert result["verdict"] == "passed", result
    assert result["attempts"] == 1

    queue_after = _read_queue(state_dir)
    item = next(i for i in queue_after["items"] if i["id"] == item_id)
    assert item["status"] == "passed", item
    assert item["finished_at"], item

    # LOGBOOK entry should exist
    logbook = (state_dir / "LOGBOOK.md").read_text()
    assert item_id in logbook
    assert "PASSED" in logbook

    # result.json should have been re-written by the dispatcher
    written = json.loads((state_dir / item_id / "result.json").read_text())
    assert written["verdict"] == "passed"
    assert written["attempts"] == 1


def test_dispatcher_evaluates_null_item(state_dir: Path, pytest_dir: Path):
    """Process is gone, result.json says null, pytest exits 0 → null."""
    item_id = "BET-NULL"
    out_dir = state_dir / item_id
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "result.json").write_text(json.dumps({"verdict": "null", "mock": True}))

    mock_test = _make_mock_pytest(
        pytest_dir, name="null_eval", result_verdict="null",
    )
    _write_queue(state_dir, [
        {
            "id": item_id,
            "hypothesis": "result.json verdict=null is the >95% expected mode",
            "references": ["LOGBOOK 2026-05-22 bet pre-reg"],
            "pytest_target": str(mock_test),
            "status": "running",
            "attempts": 0,
            "max_runtime_seconds": 60,
            "created_at": "2026-05-22T00:00:00",
            "finished_at": None,
        },
    ])

    dummy = subprocess.Popen([sys.executable, "-c", "pass"])
    dummy.wait()
    (state_dir / "current.pid").write_text(str(dummy.pid))
    (state_dir / "current_item.txt").write_text(item_id)

    dispatcher = BetDispatcher(state_dir=state_dir, repo=REPO)
    result = dispatcher.tick()

    assert result["action"] == "evaluated", result
    assert result["verdict"] == "null", result

    queue_after = _read_queue(state_dir)
    item = next(i for i in queue_after["items"] if i["id"] == item_id)
    # YAML serialises `status: null` as a bare null, which round-trips to
    # Python None. The rest of the codebase treats None/"null"/"None" as
    # the null verdict (queue_semantics.TERMINAL_NON_PASSED).
    assert item["status"] in (None, "null", "None"), item
    assert item["finished_at"], item

    logbook = (state_dir / "LOGBOOK.md").read_text()
    assert item_id in logbook
    assert "NULL" in logbook

    written = json.loads((state_dir / item_id / "result.json").read_text())
    assert written["verdict"] == "null"


# ---- validate_bet_queue smoke tests -------------------------------------
def test_validate_bet_queue_accepts_valid_queue(state_dir: Path, pytest_dir: Path):
    """A queue with a queued item pointing at a real test passes validation."""
    mock_test = _make_mock_pytest(pytest_dir, name="valid", result_verdict="null")
    queue_path = state_dir / "queue.yaml"
    queue_path.write_text(yaml.safe_dump({"items": [
        {
            "id": "BET-001",
            "hypothesis": "synthesis hypothesis text",
            "references": ["ref"],
            "pytest_target": str(mock_test),
            "status": "queued",
            "attempts": 0,
            "max_runtime_seconds": 1800,
            "created_at": "2026-05-22T00:00:00",
            "finished_at": None,
        },
    ]}, sort_keys=False))
    code, errors, _ = validate_bet_queue(queue_path)
    assert code == 0, errors


def test_validate_bet_queue_rejects_missing_pytest_target(state_dir: Path):
    """Pytest target pointing at a non-existent file is a hard error."""
    queue_path = state_dir / "queue.yaml"
    queue_path.write_text(yaml.safe_dump({"items": [
        {
            "id": "BET-MISSING",
            "hypothesis": "",
            "references": [],
            "pytest_target": "tests/bet/does_not_exist.py",
            "status": "queued",
            "attempts": 0,
            "max_runtime_seconds": 3600,
            "created_at": "2026-05-22T00:00:00",
        },
    ]}, sort_keys=False))
    code, errors, _ = validate_bet_queue(queue_path)
    assert code == 1
    assert any("does_not_exist.py" in e for e in errors), errors


def test_validate_bet_queue_rejects_explicit_terminal_dep(state_dir: Path, pytest_dir: Path):
    """Reusing queue_semantics.DEPENDENCY_RE — same semantics as autopilot.

    queue_semantics.DEPENDENCY_RE matches IDs of the form ``R-...``. A bet
    item whose blocker text says "R-X must reach status=passed first" where
    R-X is in the queue with a terminal non-passed status must FAIL the
    validator. This mirrors validate_queue.py's behavior — the regex is
    the single source of truth.
    """
    mock_test = _make_mock_pytest(pytest_dir, name="dep", result_verdict="null")
    queue_path = state_dir / "queue.yaml"
    queue_path.write_text(yaml.safe_dump({"items": [
        {
            "id": "R-PREREQ",
            "hypothesis": "",
            "references": [],
            "pytest_target": str(mock_test),
            "status": "failed",
            "attempts": 1,
            "max_runtime_seconds": 3600,
        },
        {
            "id": "BET-DEPENDENT",
            "hypothesis": "",
            "references": [],
            "pytest_target": str(mock_test),
            "status": "queued",
            "attempts": 0,
            "max_runtime_seconds": 3600,
            "blockers": ["R-PREREQ must reach status=passed first"],
        },
    ]}, sort_keys=False))
    code, errors, _ = validate_bet_queue(queue_path)
    assert code == 1
    assert any("R-PREREQ" in e for e in errors), errors


def test_validate_bet_queue_rejects_over_cap_runtime(state_dir: Path, pytest_dir: Path):
    """max_runtime_seconds > 3600 violates the 1h bet ceiling."""
    mock_test = _make_mock_pytest(pytest_dir, name="cap", result_verdict="null")
    queue_path = state_dir / "queue.yaml"
    queue_path.write_text(yaml.safe_dump({"items": [
        {
            "id": "BET-CAP-EXCEED",
            "hypothesis": "",
            "references": [],
            "pytest_target": str(mock_test),
            "status": "queued",
            "attempts": 0,
            "max_runtime_seconds": 7200,  # 2h — over the 1h cap
        },
    ]}, sort_keys=False))
    code, errors, _ = validate_bet_queue(queue_path)
    assert code == 1
    assert any("max_runtime_seconds" in e for e in errors), errors


# ---- /bet Telegram command smoke ----------------------------------------
def test_cmd_bet_summary_counters_and_progress(monkeypatch, tmp_path: Path):
    """The Telegram /bet handler reads queue.yaml + result.json files.

    Smoke-test by pointing the receiver's path constants at a tmp fixture
    queue + per-item result.json files, then calling cmd_bet directly.
    """
    bet_dir = tmp_path / "bet"
    bet_dir.mkdir()
    queue_path = bet_dir / "queue.yaml"

    # 2 queued, 1 running, 1 passed, 2 null, 1 failed
    items = [
        {"id": "BET-Q1", "status": "queued", "attempts": 0,
         "pytest_target": "x", "max_runtime_seconds": 3600},
        {"id": "BET-Q2", "status": "queued", "attempts": 0,
         "pytest_target": "x", "max_runtime_seconds": 3600},
        {"id": "BET-RUN", "status": "running", "attempts": 0,
         "pytest_target": "x", "max_runtime_seconds": 3600},
        {"id": "BET-PASS", "status": "passed", "attempts": 1,
         "finished_at": "2026-05-23T11:00:00",
         "pytest_target": "x", "max_runtime_seconds": 3600},
        {"id": "BET-N1", "status": None, "attempts": 1,
         "finished_at": "2026-05-23T10:00:00",
         "pytest_target": "x", "max_runtime_seconds": 3600},
        {"id": "BET-N2", "status": None, "attempts": 1,
         "finished_at": "2026-05-23T09:00:00",
         "pytest_target": "x", "max_runtime_seconds": 3600},
        {"id": "BET-FAIL", "status": "failed", "attempts": 1,
         "finished_at": "2026-05-23T08:00:00",
         "pytest_target": "x", "max_runtime_seconds": 3600},
    ]
    queue_path.write_text(yaml.safe_dump({"items": items}, sort_keys=False))

    # BET-N1 result.json declares 3/5 tests passed (best so far)
    (bet_dir / "BET-N1").mkdir()
    (bet_dir / "BET-N1" / "result.json").write_text(json.dumps(
        {"verdict": "null", "tests_passed": ["T1", "T2", "T4"]}
    ))
    (bet_dir / "BET-N2").mkdir()
    (bet_dir / "BET-N2" / "result.json").write_text(json.dumps(
        {"verdict": "null", "tests_passed": ["T1"]}
    ))

    import notify_telegram_receiver as receiver
    monkeypatch.setattr(receiver, "BET_DIR", bet_dir)
    monkeypatch.setattr(receiver, "QUEUE_BET", queue_path)
    monkeypatch.setattr(receiver, "BET_PID", bet_dir / "current.pid")
    monkeypatch.setattr(receiver, "BET_CURRENT_ITEM", bet_dir / "current_item.txt")

    reply = receiver.cmd_bet("")

    assert "2 queued" in reply, reply
    assert "1 running" in reply, reply
    assert "1 passed" in reply, reply
    assert "2 null" in reply, reply
    assert "1 failed" in reply, reply
    # Last 3 completed (sorted by finished_at desc): BET-PASS, BET-N1, BET-N2
    assert "BET-PASS" in reply
    assert "BET-N1" in reply
    # Win-condition progress: best is BET-N1 at 3/5
    assert "3 / 5" in reply, reply
    assert "BET-N1" in reply
