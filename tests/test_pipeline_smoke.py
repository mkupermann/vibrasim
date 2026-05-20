"""Pipeline smoke test — R-19 third defence layer against silent autopilot failures.

Covers four pipeline machinery layers that, if any of them silently
breaks, cost the autopilot hours of vacation budget without an alert:

  1. preflight item-picking (autopilot_preflight.select_next_item)
  2. preflight rejection enumeration (...enumerate_rejection_reasons)
  3. queue validator (tools/validate_queue.py)
  4. supervisor stagnation detector (autopilot_supervisor.check_stagnation_and_alert)
  5. pre-commit hook (.eqmod/autopilot/hooks/pre-commit)

Every test in this file is intentionally cheap and runs in the
default fast slice (no @pytest.mark.slow). Failures here are flagged
on every CI run and every postflight regression check.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
TOOLS = REPO / "tools"
VENV_PY = REPO / ".venv/bin/python"
sys.path.insert(0, str(TOOLS))


# ---------------------------------------------------------------------------
# Layer 1+2 — preflight picking and rejection enumeration
# ---------------------------------------------------------------------------

def _item(item_id: str, status: str, blockers: list[str] | None = None) -> dict:
    """Minimal queue-item dict for picking-logic tests."""
    return {
        "id": item_id,
        "status": status,
        "blockers": blockers or [],
        "brief": "LOGBOOK.md",
        "preregistered_acceptance": ["dummy"],
    }


def test_preflight_picks_only_unblocked_items():
    """Mock queue with three queued items, each blocked-by a different
    upstream status: passed (satisfied), null (terminal), queued
    (chain-prerequisite forward dep). The first queued item with a
    satisfied explicit dependency must be picked; the terminal-dep item
    must never be picked even if listed earlier; the queued-dep item
    must be flagged as currently blocked by the validator surface used
    in tests 3 / 4 below.
    """
    from autopilot_preflight import select_next_item, blockers_satisfied, status_by_id

    items = [
        _item("R-DONE", "passed"),
        _item("R-DEAD", "null"),
        _item("R-WAIT", "queued"),  # chain-prerequisite (no own blockers)
        _item("R-BLOCKED-TERMINAL", "queued",
              ["R-DEAD must reach status=passed first"]),
        _item("R-BLOCKED-CHAIN", "queued",
              ["R-WAIT must reach status=passed first"]),
        _item("R-READY", "queued",
              ["R-DONE must reach status=passed first"]),
    ]
    idx = status_by_id(items)

    pick = select_next_item(items)
    # R-WAIT is the first queued item AND has no blockers, so it fires.
    # It is the chain prerequisite that unblocks R-BLOCKED-CHAIN later.
    assert pick is not None
    assert pick["id"] == "R-WAIT", (
        f"preflight should pick the chain-prerequisite (R-WAIT) "
        f"first; got {pick['id']!r}"
    )

    # Per-item satisfaction matches the documented semantics:
    assert blockers_satisfied(items[3], idx) is False, "terminal-dep must block"
    assert blockers_satisfied(items[4], idx) is False, "queued-dep must block"
    assert blockers_satisfied(items[5], idx) is True, "passed-dep must satisfy"


def test_preflight_rejection_message_enumerates_blocked_items():
    """When every queued item is blocked, the enumeration the 0e2c0f6
    commit added must name each blocker source with its current status.
    Silent 'queue exhausted' cost 14 h on 2026-05-20; this test pins the
    format so it cannot regress to a silent rejection.
    """
    from autopilot_preflight import enumerate_rejection_reasons

    items = [
        _item("R-A", "null"),
        _item("R-B", "failed"),
        _item("R-X", "queued", ["R-A must reach status=passed first"]),
        _item("R-Y", "queued", ["R-B must reach status=passed first"]),
    ]
    reasons = enumerate_rejection_reasons(items)
    joined = "\n".join(reasons)
    # Both queued items appear with their specific blocker source
    # and that source's status string.
    assert "R-X blocked by:" in joined, joined
    assert "R-Y blocked by:" in joined, joined
    assert "R-A(status='null')" in joined, joined
    assert "R-B(status='failed')" in joined, joined


# ---------------------------------------------------------------------------
# Layer 3 — queue validator
# ---------------------------------------------------------------------------

def _write_queue(tmp_path: Path, items: list[dict]) -> Path:
    """Serialise an items list to a QUEUE.yaml at tmp_path."""
    out = tmp_path / "QUEUE.yaml"
    out.write_text(yaml.safe_dump({"items": items}, sort_keys=False))
    return out


def _run_validate(queue_path: Path) -> subprocess.CompletedProcess:
    """Run tools/validate_queue.py against a synthetic QUEUE.yaml by
    monkey-patching the QUEUE module-level constant via a tiny wrapper
    script. Avoids depending on the live repo queue.
    """
    wrapper = textwrap.dedent(
        f"""
        import sys
        from pathlib import Path
        sys.path.insert(0, {str(TOOLS)!r})
        import validate_queue
        validate_queue.QUEUE = Path({str(queue_path)!r})
        sys.exit(validate_queue.main())
        """
    )
    return subprocess.run(
        [str(VENV_PY), "-c", wrapper],
        capture_output=True, text=True, timeout=30,
    )


def test_validate_queue_blocks_terminal_blocker_mention(tmp_path):
    """A queued item with an explicit dependency on a null item is
    permanently unsatisfiable. The validator MUST exit 1 and name the
    offender. Catches the 2026-05-20 R-17 class of bug at commit time
    rather than at the 14-hour silent-rejection ceiling.
    """
    items = [
        _item("R-DEAD", "null"),
        _item("R-VICTIM", "queued", ["R-DEAD must reach status=passed first"]),
    ]
    queue_path = _write_queue(tmp_path, items)
    r = _run_validate(queue_path)
    assert r.returncode == 1, (r.stdout, r.stderr)
    assert "R-VICTIM" in r.stderr, r.stderr
    assert "R-DEAD" in r.stderr, r.stderr


def test_validate_queue_allows_queued_chain(tmp_path):
    """A legitimate forward chain — R-A queued, R-B blocking on
    'R-A must reach status=passed first' — is allowed. The validator
    MUST exit 0; the dependency is not terminal, it's pending.
    """
    items = [
        _item("R-A", "queued"),
        _item("R-B", "queued", ["R-A must reach status=passed first"]),
    ]
    queue_path = _write_queue(tmp_path, items)
    r = _run_validate(queue_path)
    assert r.returncode == 0, (r.stdout, r.stderr)


# ---------------------------------------------------------------------------
# Layer 4 — supervisor stagnation detector
# ---------------------------------------------------------------------------

@pytest.fixture
def isolated_supervisor(tmp_path, monkeypatch):
    """Redirect supervisor module-level paths into tmp_path so the test
    cannot read or mutate real ~/.eqmod/autopilot/ state. Also stub
    send_mail and queue_summary so the alert path has no side effects
    outside tmp_path.
    """
    import autopilot_supervisor as sup

    stagnation_state = tmp_path / "stagnation_state.json"
    stop_path = tmp_path / "STOP"
    supervisor_log = tmp_path / "supervisor.log"
    lockdir = tmp_path / "wrapper.lock.d"  # absent → no live wrapper

    monkeypatch.setattr(sup, "REPO", tmp_path, raising=True)
    monkeypatch.setattr(sup, "STAGNATION_STATE", stagnation_state, raising=True)
    monkeypatch.setattr(sup, "STOP_PATH", stop_path, raising=True)
    monkeypatch.setattr(sup, "SUPERVISOR_LOG", supervisor_log, raising=True)
    monkeypatch.setattr(sup, "LOCKDIR", lockdir, raising=True)
    monkeypatch.setattr(sup, "LOCK_PID", lockdir / "pid", raising=True)
    monkeypatch.setattr(sup, "send_mail", lambda subj, body: True, raising=True)
    monkeypatch.setattr(sup, "queue_summary", lambda: "total=0", raising=True)
    return sup, stagnation_state, stop_path


def test_stagnation_detector_sets_stop_after_threshold(isolated_supervisor, monkeypatch):
    """Constant progress signal across N invocations: first call seeds
    the baseline, subsequent unchanged calls increment the counter; at
    threshold the detector sets STOP, appends to LOGBOOK, and flips the
    alerted flag in stagnation_state.json. Threshold defaults to 3
    (STAGNATION_TICKS_THRESHOLD in supervisor); call 4 is the first
    that crosses it.
    """
    sup, state_path, stop_path = isolated_supervisor

    monkeypatch.setattr(
        sup, "measure_progress_signal",
        lambda: {"sha": "deadbeef", "terminal_count": 7},
        raising=True,
    )

    # Call 1 — seed. Counter = 0, STOP not set.
    sup.check_stagnation_and_alert()
    s = json.loads(state_path.read_text())
    assert s["consecutive_stagnant_ticks"] == 0
    assert not stop_path.exists()

    # Calls 2 + 3 — stagnant accumulating below threshold.
    sup.check_stagnation_and_alert()
    sup.check_stagnation_and_alert()
    s = json.loads(state_path.read_text())
    assert s["consecutive_stagnant_ticks"] == 2
    assert not stop_path.exists()

    # Call 4 — crosses threshold. STOP set, alerted True, LOGBOOK appended.
    sup.check_stagnation_and_alert()
    s = json.loads(state_path.read_text())
    assert s["consecutive_stagnant_ticks"] == sup.STAGNATION_TICKS_THRESHOLD
    assert stop_path.exists(), "STOP marker should be set on threshold cross"
    assert s["alerted"] is True
    logbook = sup.REPO / "LOGBOOK.md"
    assert logbook.exists(), "LOGBOOK.md should have been appended"
    assert "stagnation auto-STOP" in logbook.read_text()


def test_stagnation_detector_resets_on_progress(isolated_supervisor, monkeypatch):
    """Two stagnant ticks then a changed signal: the counter resets to
    0, STOP stays unset, alerted stays False. The detector must never
    fire on a moving pipeline.
    """
    sup, state_path, stop_path = isolated_supervisor

    signal = {"sha": "11111111", "terminal_count": 1}

    def current():
        return dict(signal)

    monkeypatch.setattr(sup, "measure_progress_signal", current, raising=True)

    # Tick 1 — seed.
    sup.check_stagnation_and_alert()
    # Tick 2 — stagnant.
    sup.check_stagnation_and_alert()
    s = json.loads(state_path.read_text())
    assert s["consecutive_stagnant_ticks"] == 1

    # Signal changes — pipeline moved.
    signal["terminal_count"] = 2
    sup.check_stagnation_and_alert()

    s = json.loads(state_path.read_text())
    assert s["consecutive_stagnant_ticks"] == 0, "must reset on observed progress"
    assert not stop_path.exists(), "STOP must not be set"
    assert s["alerted"] is False


# ---------------------------------------------------------------------------
# Layer 5 — pre-commit hook
# ---------------------------------------------------------------------------

def test_pre_commit_hook_rejects_self_blocking_queue_edit(tmp_path):
    """Stage a synthetic QUEUE.yaml where a queued item explicitly
    depends on a null item, then run the actual pre-commit hook
    against it. The hook must exit 1.

    Builds a self-contained git repo in tmp_path with only the files
    the hook touches: validate_queue.py, queue_semantics.py, the hook
    script, the synthetic queue, and a .venv symlink for the python.
    """
    # 1. init a fresh repo.
    def git(*args):
        return subprocess.run(
            ["git", *args], cwd=tmp_path, capture_output=True, text=True, check=True,
        )
    git("init", "-q", "-b", "autopilot/test")
    git("config", "user.email", "test@example.invalid")
    git("config", "user.name", "test")
    git("config", "commit.gpgsign", "false")

    # 2. lay out the minimal repo skeleton the hook expects.
    (tmp_path / "tools").mkdir()
    for name in ("validate_queue.py", "queue_semantics.py"):
        (tmp_path / "tools" / name).write_text((TOOLS / name).read_text())
    hooks_dir = tmp_path / ".eqmod/autopilot/hooks"
    hooks_dir.mkdir(parents=True)
    hook_src = (REPO / ".eqmod/autopilot/hooks/pre-commit").read_text()
    hook_dst = hooks_dir / "pre-commit"
    hook_dst.write_text(hook_src)
    hook_dst.chmod(0o755)
    # Symlink .venv so the hook's $repo_root/.venv/bin/python resolves.
    (tmp_path / ".venv").symlink_to(REPO / ".venv")

    # 3. commit a baseline (empty queue) so the hook has a HEAD.
    baseline = {"items": [_item("R-SEED", "passed")]}
    queue_path = tmp_path / ".eqmod/autopilot/QUEUE.yaml"
    queue_path.write_text(yaml.safe_dump(baseline, sort_keys=False))
    git("add", "-A")
    git("commit", "-q", "-m", "baseline")

    # 4. Now write the self-blocking edit and stage it.
    bad = {
        "items": [
            _item("R-SEED", "passed"),
            _item("R-DEAD", "null"),
            _item("R-X", "queued", ["R-DEAD must reach status=passed first"]),
        ],
    }
    queue_path.write_text(yaml.safe_dump(bad, sort_keys=False))
    git("add", str(queue_path))

    # 5. Run the hook (subprocess, NOT through `git commit` — we only
    # want the hook's exit code, and the EQMOD_AUTOPILOT env is not
    # required because the QUEUE.yaml validator section runs for ALL
    # commits, not just autopilot ones).
    r = subprocess.run(
        ["/bin/bash", str(hook_dst)],
        cwd=tmp_path, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 1, (r.stdout, r.stderr, "hook should reject self-blocking edit")
    assert "R-X" in r.stderr or "R-X" in r.stdout, (r.stdout, r.stderr)
