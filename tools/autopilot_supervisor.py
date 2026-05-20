"""EQMOD autopilot supervisor.

Runs every 30 minutes via launchd. Single responsibility: ensure the
autopilot wrapper keeps moving forward through the queue without
human intervention.

Decision tree per run:
    1. Is `~/.eqmod/autopilot/STOP` present?
       → exit clean. User has paused the autopilot.
    2. Is the wrapper lock (~/.eqmod/autopilot/wrapper.lock.d/) held by
       an alive PID?
       2a. If alive AND held for >5h → kill it (likely stuck postflight
           or pytest), log, fall through to step 3.
       2b. If alive AND held for <5h → exit clean. Wrapper is healthy.
    3. Are there any items with status=queued in QUEUE.yaml?
       → fire the wrapper (nohup, background).
    4. No queued items → exit clean. Queue exhausted; nothing to do.

Logs to ~/.eqmod/autopilot/supervisor.log (append).
"""
from __future__ import annotations

import datetime as _dt
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
QUEUE_PATH = REPO / ".eqmod/autopilot/QUEUE.yaml"
WRAPPER_PATH = REPO / ".eqmod/autopilot/run_autopilot.sh"
STATE_DIR = Path.home() / ".eqmod/autopilot"
STOP_PATH = STATE_DIR / "STOP"
LOCKDIR = STATE_DIR / "wrapper.lock.d"
LOCK_PID = LOCKDIR / "pid"
SUPERVISOR_LOG = STATE_DIR / "supervisor.log"
STAGNATION_STATE = STATE_DIR / "stagnation_state.json"
STUCK_THRESHOLD_SECONDS = 5 * 3600  # 5 h

# Liveness contract: how many consecutive supervisor ticks may pass without
# observable pipeline progress (new autopilot commit on origin/main, or
# queued-item transitioning to a terminal status) before we declare
# stagnation, set STOP, and mail. 3 ticks * 30 min = 1.5 h.
# Set deliberately tight: the 2026-05-20 incidents lost 14 h precisely
# because the system tolerated arbitrary idle time without complaint.
STAGNATION_TICKS_THRESHOLD = 3

# Try to import mail support; degrade gracefully if not on the path.
sys.path.insert(0, str(REPO / "tools"))
try:
    from autopilot_mail import send_mail  # type: ignore  # noqa: E402
except Exception:
    def send_mail(subject: str, body: str) -> bool:  # type: ignore
        log(f"send_mail unavailable — would have sent: {subject!r}")
        return False


def log(msg: str) -> None:
    line = f"[{_dt.datetime.now().isoformat()}] {msg}\n"
    SUPERVISOR_LOG.parent.mkdir(parents=True, exist_ok=True)
    with SUPERVISOR_LOG.open("a") as f:
        f.write(line)


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False
    except Exception:
        return False


def kill_pid_tree(pid: int) -> None:
    """SIGTERM the wrapper and any python/claude/pytest children."""
    try:
        # Find children via pgrep -P
        r = subprocess.run(
            ["/usr/bin/pgrep", "-P", str(pid)],
            capture_output=True, text=True, timeout=5,
        )
        children = [int(p) for p in r.stdout.split() if p.strip().isdigit()]
        for cpid in children:
            kill_pid_tree(cpid)
    except Exception as exc:
        log(f"  child enumeration for pid {pid} failed: {exc!r}")
    try:
        os.kill(pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        pass
    # Give it a moment
    time.sleep(2)
    if pid_alive(pid):
        try:
            os.kill(pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass


def measure_progress_signal() -> dict:
    """Return a snapshot of pipeline-progress indicators.

    Two signals, both polled cheaply on each supervisor tick:
      - latest_autopilot_commit_sha — head of origin/main if the latest commit
        looks like autopilot work (subject starts with 'autopilot:' or contains
        ' status to main'); else the latest non-autopilot commit. Used to detect
        whether the pipeline has merged any verdict in the recent window.
      - terminal_status_count — number of items currently in a terminal
        non-queued state (passed / null / failed). Increases monotonically as
        the pipeline finishes items. A stagnant pipeline keeps this constant.

    The pair (sha, count) is the liveness signal. If both stay unchanged
    across N consecutive supervisor ticks, the pipeline has produced no
    observable work.
    """
    # SHA: ask git for origin/main HEAD (no network, just the cached ref).
    try:
        r = subprocess.run(
            ["git", "-C", str(REPO), "rev-parse", "origin/main"],
            capture_output=True, text=True, timeout=5,
        )
        latest_sha = r.stdout.strip() if r.returncode == 0 else "unknown"
    except Exception as exc:
        log(f"  measure_progress: git rev-parse failed: {exc!r}")
        latest_sha = "unknown"

    # Terminal-status count from current QUEUE.yaml.
    terminal_count = 0
    if QUEUE_PATH.exists():
        try:
            q = yaml.safe_load(QUEUE_PATH.read_text())
            items = q.get("items") or []
            terminal_count = sum(
                1 for i in items
                if i.get("status") in ("passed", "null", "failed", "None")
                or i.get("status") is None and i.get("attempts", 0) >= 1
            )
        except Exception as exc:
            log(f"  measure_progress: QUEUE parse failed: {exc!r}")

    return {"sha": latest_sha, "terminal_count": terminal_count}


def load_stagnation_state() -> dict:
    """Read the persisted stagnation ledger. Returns dict with keys:
      - last_progress_signal: dict (sha, terminal_count) at the moment we
        last observed progress
      - last_progress_at: ISO timestamp
      - consecutive_stagnant_ticks: int
      - alerted: bool — whether we already mailed about the current stagnation
    """
    if not STAGNATION_STATE.exists():
        return {
            "last_progress_signal": None,
            "last_progress_at": None,
            "consecutive_stagnant_ticks": 0,
            "alerted": False,
        }
    try:
        import json
        return json.loads(STAGNATION_STATE.read_text())
    except Exception as exc:
        log(f"  stagnation state corrupt — resetting: {exc!r}")
        return {
            "last_progress_signal": None,
            "last_progress_at": None,
            "consecutive_stagnant_ticks": 0,
            "alerted": False,
        }


def save_stagnation_state(state: dict) -> None:
    import json
    STAGNATION_STATE.parent.mkdir(parents=True, exist_ok=True)
    STAGNATION_STATE.write_text(json.dumps(state, indent=2))


def check_stagnation_and_alert() -> bool:
    """Liveness contract enforcement. Returns True if we set STOP this tick.

    Algorithm:
      - Measure current progress signal.
      - Compare to last recorded.
      - If unchanged: increment consecutive_stagnant_ticks. If threshold
        crossed and we haven't already alerted in this stagnation event:
        set STOP marker, mail, append to LOGBOOK, set alerted=True.
      - If changed: reset consecutive_stagnant_ticks, alerted=False, update
        last_progress_signal.
    """
    current = measure_progress_signal()
    state = load_stagnation_state()
    last = state.get("last_progress_signal")
    now = _dt.datetime.now()

    if last is None or last != current:
        # Progress observed (or first-ever tick). Reset and persist.
        state["last_progress_signal"] = current
        state["last_progress_at"] = now.isoformat()
        state["consecutive_stagnant_ticks"] = 0
        state["alerted"] = False
        save_stagnation_state(state)
        log(
            f"  liveness: progress observed (sha={current['sha'][:8]} "
            f"terminal_count={current['terminal_count']})"
        )
        return False

    # Signal unchanged this tick — stagnation accumulating.
    state["consecutive_stagnant_ticks"] += 1
    n = state["consecutive_stagnant_ticks"]
    save_stagnation_state(state)

    if n < STAGNATION_TICKS_THRESHOLD:
        log(
            f"  liveness: stagnant tick {n}/{STAGNATION_TICKS_THRESHOLD} "
            f"(sha={current['sha'][:8]} terminal_count={current['terminal_count']})"
        )
        return False

    # Threshold crossed. If already alerted, stay quiet but keep STOP set.
    if state.get("alerted"):
        log(
            f"  liveness: stagnation persists (tick {n}); already alerted, "
            f"STOP marker present"
        )
        if not STOP_PATH.exists():
            STOP_PATH.write_text(
                f"Set by supervisor due to stagnation at "
                f"{state['last_progress_at']} (re-asserted)\n"
            )
        return True

    # First time crossing the threshold: full alert.
    log(f"!! STAGNATION DETECTED: {n} consecutive ticks without progress")

    # Set STOP so the next launchd autopilot fire exits clean without
    # burning a Claude session against a broken pipeline.
    STOP_PATH.write_text(
        f"# Pipeline stagnation auto-STOP\n"
        f"# Set by supervisor 2026-05-20+ liveness check.\n"
        f"# Last observed progress: {state['last_progress_at']}\n"
        f"# Consecutive stagnant ticks: {n}\n"
        f"# Signal at last progress: {state['last_progress_signal']!r}\n"
        f"# Investigate and remove this file to resume.\n"
    )

    # Mail.
    subject = "EQMOD PIPELINE STAGNATION — autopilot paused"
    idle_hours = 0.0
    try:
        last_at = _dt.datetime.fromisoformat(state["last_progress_at"])
        idle_hours = (now - last_at).total_seconds() / 3600
    except Exception:
        pass
    body = (
        f"The EQMOD autopilot pipeline has produced no observable progress\n"
        f"for {n} consecutive supervisor ticks ({idle_hours:.1f} h since the\n"
        f"last observed change). The supervisor set\n"
        f"~/.eqmod/autopilot/STOP so the next launchd fire exits clean.\n\n"
        f"Last observed signal:\n"
        f"  origin/main HEAD: {current['sha']}\n"
        f"  terminal items count: {current['terminal_count']}\n"
        f"  last progress at: {state['last_progress_at']}\n\n"
        f"Current queue summary: {queue_summary()}\n\n"
        f"What to investigate first:\n"
        f"  - tail ~/.eqmod/autopilot/session.log — what does the preflight say?\n"
        f"  - .venv/bin/python tools/validate_queue.py — any self-blocking blockers?\n"
        f"  - git log --oneline origin/main -5 — has anything autopilot-committed?\n"
        f"  - ls ~/.eqmod/autopilot/wrapper.lock.d 2>/dev/null — is something stuck?\n\n"
        f"Resume the pipeline by deleting ~/.eqmod/autopilot/STOP after fixing\n"
        f"the root cause.\n\n"
        f"This alert fires exactly once per stagnation event. Subsequent ticks\n"
        f"reassert STOP silently. Mail repeats only after observable progress\n"
        f"is detected and stagnation re-accumulates.\n"
    )
    send_mail(subject, body)

    # LOGBOOK entry — durable record so the next session sees it without
    # having to read the supervisor log.
    try:
        logbook = REPO / "LOGBOOK.md"
        entry = (
            f"\n\n## {now.date().isoformat()} — Pipeline stagnation auto-STOP "
            f"(supervisor liveness check)\n\n"
            f"- **Trigger**: {n} consecutive supervisor ticks "
            f"({idle_hours:.1f} h) without observable progress.\n"
            f"- **Last signal**: origin/main HEAD {current['sha'][:12]}, "
            f"terminal items {current['terminal_count']}.\n"
            f"- **STOP marker set**: ~/.eqmod/autopilot/STOP — autopilot will not\n"
            f"  fire until this file is removed.\n"
            f"- **Mail sent**: {subject}\n"
        )
        with logbook.open("a") as f:
            f.write(entry)
    except Exception as exc:
        log(f"  logbook append failed: {exc!r}")

    state["alerted"] = True
    save_stagnation_state(state)
    return True


def queue_has_queued_items() -> bool:
    if not QUEUE_PATH.exists():
        return False
    q = yaml.safe_load(QUEUE_PATH.read_text())
    items = q.get("items") or []
    return any(i.get("status") == "queued" for i in items)


def queue_summary() -> str:
    if not QUEUE_PATH.exists():
        return "(no QUEUE.yaml)"
    q = yaml.safe_load(QUEUE_PATH.read_text())
    items = q.get("items") or []
    from collections import Counter
    c = Counter((i.get("status") or "?") for i in items)
    return f"total={len(items)} " + " ".join(f"{k}={v}" for k, v in sorted(c.items()))


def fire_wrapper() -> int:
    """Launch run_autopilot.sh detached. Returns wrapper PID."""
    # Truncate logs so we can tell the new session apart from old
    (STATE_DIR / "session.log").touch()
    proc = subprocess.Popen(
        ["/bin/bash", str(WRAPPER_PATH)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )
    return proc.pid


def main() -> int:
    log(f"--- supervisor tick; queue: {queue_summary()}")

    # Liveness check runs FIRST, before STOP check, so that progress-resumed
    # state gets recorded correctly even after a manual STOP is in place.
    # check_stagnation_and_alert returns True if it just set STOP — fall
    # through to STOP-handling below in that case.
    check_stagnation_and_alert()

    if STOP_PATH.exists():
        log("STOP marker present — exiting clean")
        return 0

    if LOCKDIR.exists():
        try:
            pid_text = LOCK_PID.read_text().strip()
            pid = int(pid_text)
        except (FileNotFoundError, ValueError):
            pid = None
        if pid and pid_alive(pid):
            lock_age = time.time() - LOCK_PID.stat().st_mtime
            if lock_age < STUCK_THRESHOLD_SECONDS:
                log(f"wrapper alive pid={pid} age={lock_age:.0f}s — healthy, exit")
                return 0
            log(f"wrapper STUCK pid={pid} age={lock_age:.0f}s (>{STUCK_THRESHOLD_SECONDS}s) — killing tree")
            kill_pid_tree(pid)
            # Wait a moment for the trap to release lock
            time.sleep(5)
            # If lock is still there (trap didn't run), force-clean
            if LOCKDIR.exists():
                try:
                    LOCK_PID.unlink(missing_ok=True)
                    LOCKDIR.rmdir()
                    log("  force-removed stale lockdir")
                except Exception as exc:
                    log(f"  lockdir cleanup failed: {exc!r}")
        else:
            # Lock dir present but pid dead — stale, clean
            log("stale lockdir (pid dead) — force-cleaning")
            try:
                LOCK_PID.unlink(missing_ok=True)
                LOCKDIR.rmdir()
            except Exception as exc:
                log(f"  cleanup failed: {exc!r}")

    # At this point no wrapper is running
    if not queue_has_queued_items():
        log("queue exhausted (no queued items) — exit clean")
        return 0

    new_pid = fire_wrapper()
    log(f"fired new wrapper pid={new_pid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
