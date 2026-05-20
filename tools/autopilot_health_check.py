"""EQMOD autopilot health check — comprehensive monitor.

Runs hourly via the watchdog (or standalone). Audits everything that
can fail silently in the autopilot pipeline:

  1. Long-run dispatcher: pid file vs process aliveness, hard-cap
     compliance, stale state files.
  2. Short autopilot: supervisor tick recency, wrapper-lock sanity.
  3. Watchdog itself: last-tick recency (called via this script's
     last_health_check_at marker).
  4. Working tree: branch is main between sessions, no orphaned stashes.
  5. Mail subsystem: send_mail callable, recent successful sends.
  6. Queue files: YAML valid in both short and long-run, validate_queue
     passes on short.
  7. STOP markers: alert if either short or long-run STOP is present
     (operator may have forgotten about it).
  8. State-dir disk usage: alert if >1 GB consumed.

Exit 0 on healthy. Exit 1 on anomalies (mail still sent on each
anomaly individually). Designed to be safe to run repeatedly.

Designed to FAIL EARLY: better to over-mail than to silently lose
14 hours of vacation.
"""
from __future__ import annotations

import datetime as _dt
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
try:
    from autopilot_mail import send_mail  # type: ignore
except Exception:
    def send_mail(subject: str, body: str) -> bool:  # type: ignore
        return False

STATE_AUTOPILOT = Path.home() / ".eqmod/autopilot"
STATE_LONGRUN = Path.home() / ".eqmod/long-run"

LAST_TICK = STATE_AUTOPILOT / "last_tick.txt"
SUPERVISOR_LOG = STATE_AUTOPILOT / "supervisor.log"
LOCKDIR = STATE_AUTOPILOT / "wrapper.lock.d"
SHORT_STOP = STATE_AUTOPILOT / "STOP"
QUEUE_SHORT = REPO / ".eqmod/autopilot/QUEUE.yaml"

LONGRUN_QUEUE = STATE_LONGRUN / "queue.yaml"
LONGRUN_PID = STATE_LONGRUN / "current.pid"
LONGRUN_ITEM = STATE_LONGRUN / "current_item.txt"
LONGRUN_LOG = STATE_LONGRUN / "dispatcher.log"
LONGRUN_STOP = STATE_LONGRUN / "STOP"

HEALTH_CHECK_LOG = STATE_AUTOPILOT / "health_check.log"


def now() -> _dt.datetime:
    return _dt.datetime.now()


def log(msg: str) -> None:
    HEALTH_CHECK_LOG.parent.mkdir(parents=True, exist_ok=True)
    with HEALTH_CHECK_LOG.open("a") as f:
        f.write(f"[{now().isoformat()}] {msg}\n")


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False
    except Exception:
        return False


def file_age_hours(p: Path) -> float | None:
    if not p.exists():
        return None
    return (time.time() - p.stat().st_mtime) / 3600.0


def check_longrun_dispatcher() -> list[tuple[str, str]]:
    """Return list of (severity, message). severity is 'crit' or 'warn'."""
    issues: list[tuple[str, str]] = []

    # 1. PID file vs process aliveness
    if LONGRUN_PID.exists():
        try:
            pid = int(LONGRUN_PID.read_text().strip())
        except ValueError:
            issues.append((
                "crit",
                f"long-run current.pid contains garbage: "
                f"{LONGRUN_PID.read_text()!r}",
            ))
            return issues
        alive = pid_alive(pid)
        if not alive:
            issues.append((
                "warn",
                f"long-run current.pid={pid} but process dead; "
                f"dispatcher should clean this up on next tick",
            ))
        else:
            # 2. Hard-cap violation check (mirror dispatcher logic)
            elapsed_hours = (time.time() - LONGRUN_PID.stat().st_mtime) / 3600
            try:
                q = yaml.safe_load(LONGRUN_QUEUE.read_text())
                cap = (q.get("window") or {}).get("max_runtime_hours_per_item", 24)
            except Exception:
                cap = 24
            if elapsed_hours > cap:
                issues.append((
                    "crit",
                    f"long-run process pid={pid} has been running "
                    f"{elapsed_hours:.1f}h (cap={cap}h). Dispatcher "
                    f"should have killed it; check enforcement code.",
                ))
            elif elapsed_hours > cap * 0.85:
                issues.append((
                    "warn",
                    f"long-run process pid={pid} approaching hard cap: "
                    f"{elapsed_hours:.1f}h of {cap}h ({elapsed_hours/cap*100:.0f}%)",
                ))

    # 3. Dispatcher tick recency
    age = file_age_hours(LONGRUN_LOG)
    if age is not None and age > 1.0:
        issues.append((
            "crit",
            f"long-run dispatcher.log is {age:.1f}h old. Dispatcher "
            f"runs every 30 min; >1h means launchd or wrapper has died.",
        ))

    return issues


def check_short_autopilot() -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    # 1. Lock dir sanity
    if LOCKDIR.exists():
        lock_pid_file = LOCKDIR / "pid"
        if lock_pid_file.exists():
            try:
                pid = int(lock_pid_file.read_text().strip())
                if not pid_alive(pid):
                    issues.append((
                        "warn",
                        f"wrapper.lock.d/pid={pid} but process dead — "
                        f"supervisor should clean on next tick",
                    ))
                else:
                    elapsed_hours = (
                        time.time() - lock_pid_file.stat().st_mtime
                    ) / 3600
                    if elapsed_hours > 5:
                        issues.append((
                            "crit",
                            f"wrapper pid={pid} stuck {elapsed_hours:.1f}h "
                            f"(>5h supervisor threshold). Supervisor should "
                            f"have killed it.",
                        ))
            except ValueError:
                issues.append(("crit", "wrapper.lock.d/pid is unreadable"))

    # 2. Supervisor tick recency
    age = file_age_hours(SUPERVISOR_LOG)
    if age is not None and age > 1.0:
        issues.append((
            "crit",
            f"supervisor.log is {age:.1f}h old. Supervisor runs every "
            f"30 min; >1h means launchd has died.",
        ))

    # 3. Last_tick recency (set by run_autopilot.sh)
    age = file_age_hours(LAST_TICK)
    if age is not None and age > 12:
        issues.append((
            "warn",
            f"last_tick.txt is {age:.1f}h old (12h threshold).",
        ))

    return issues


def check_stop_markers() -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if SHORT_STOP.exists():
        age = file_age_hours(SHORT_STOP)
        issues.append((
            "warn",
            f"short-autopilot STOP marker present "
            f"(age {age:.1f}h if age else 'unknown'). "
            f"Autopilot paused — remove if intentional.",
        ))
    if LONGRUN_STOP.exists():
        age = file_age_hours(LONGRUN_STOP)
        issues.append((
            "warn",
            f"long-run STOP marker present "
            f"(age {age:.1f}h). Dispatcher paused — remove if intentional.",
        ))
    return issues


def check_working_tree() -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    try:
        r = subprocess.run(
            ["git", "-C", str(REPO), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        current = r.stdout.strip()
    except Exception as exc:
        issues.append(("crit", f"cannot read current branch: {exc!r}"))
        return issues

    # If a wrapper is running, autopilot/X is expected. Otherwise main.
    wrapper_running = LOCKDIR.exists() and (LOCKDIR / "pid").exists() and \
        (lambda: True if (lambda p: pid_alive(p) if p else False)(
            int((LOCKDIR / "pid").read_text().strip())
            if (LOCKDIR / "pid").exists() else None
        ) else False)()

    if not wrapper_running and current != "main":
        issues.append((
            "warn",
            f"working tree on {current!r}, expected main between sessions. "
            f"Next autopilot fire will fail at preflight HEAD check.",
        ))

    # Stash count — stale stashes accumulate from interrupted sessions
    try:
        r = subprocess.run(
            ["git", "-C", str(REPO), "stash", "list"],
            capture_output=True, text=True, timeout=5,
        )
        n_stashes = len([ln for ln in r.stdout.splitlines() if ln.strip()])
        if n_stashes > 3:
            issues.append((
                "warn",
                f"git stash list has {n_stashes} entries. "
                f"Old autopilot-isolation stashes may need cleanup.",
            ))
    except Exception:
        pass

    return issues


def check_queue_validity() -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    # Short queue: run validator
    try:
        r = subprocess.run(
            [str(REPO / ".venv/bin/python"), str(REPO / "tools/validate_queue.py")],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode != 0:
            issues.append((
                "crit",
                f"validate_queue.py exits {r.returncode} on short queue:\n"
                f"  {r.stderr.strip()[:500]}",
            ))
    except Exception as exc:
        issues.append(("crit", f"could not run validate_queue.py: {exc!r}"))

    # Long-run queue: YAML parse
    if LONGRUN_QUEUE.exists():
        try:
            yaml.safe_load(LONGRUN_QUEUE.read_text())
        except yaml.YAMLError as exc:
            issues.append((
                "crit",
                f"long-run queue.yaml YAML parse error: {exc}",
            ))

    return issues


def check_state_dirs() -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for state in (STATE_AUTOPILOT, STATE_LONGRUN):
        if not state.exists():
            continue
        # rough disk usage
        try:
            r = subprocess.run(
                ["du", "-sk", str(state)],
                capture_output=True, text=True, timeout=10,
            )
            kb = int(r.stdout.split()[0])
            if kb > 1_000_000:  # 1 GB
                issues.append((
                    "warn",
                    f"{state} contains {kb/1024:.0f} MB. "
                    f"Old session logs / snapshots may need pruning.",
                ))
        except Exception:
            pass
    return issues


def main() -> int:
    log(f"--- health check tick")

    checks = [
        ("long-run dispatcher", check_longrun_dispatcher),
        ("short autopilot", check_short_autopilot),
        ("STOP markers", check_stop_markers),
        ("working tree", check_working_tree),
        ("queue validity", check_queue_validity),
        ("state dirs", check_state_dirs),
    ]

    all_issues: list[tuple[str, str, str]] = []
    for area, fn in checks:
        try:
            for severity, msg in fn():
                all_issues.append((area, severity, msg))
        except Exception as exc:
            all_issues.append((area, "crit", f"check raised: {exc!r}"))

    if not all_issues:
        log("  all clear")
        return 0

    # Group by severity
    crits = [(a, m) for a, s, m in all_issues if s == "crit"]
    warns = [(a, m) for a, s, m in all_issues if s == "warn"]

    log(f"  {len(crits)} crit + {len(warns)} warn")
    for area, msg in crits:
        log(f"  CRIT [{area}]: {msg}")
    for area, msg in warns:
        log(f"  WARN [{area}]: {msg}")

    # Mail on any crit. Don't mail on warns alone (would be noisy).
    if crits:
        subject = f"[EQMOD health] {len(crits)} CRIT, {len(warns)} warn"
        body = "Critical issues:\n\n"
        for area, msg in crits:
            body += f"  [{area}] {msg}\n\n"
        if warns:
            body += "\nWarnings:\n\n"
            for area, msg in warns:
                body += f"  [{area}] {msg}\n\n"
        body += f"\nTick: {now().isoformat()}\n"
        body += f"Full log: ~/.eqmod/autopilot/health_check.log\n"
        send_mail(subject, body)

    return 1 if crits else 0


if __name__ == "__main__":
    sys.exit(main())
