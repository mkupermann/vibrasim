"""EQMOD autopilot preflight check.

Run BEFORE every headless Claude session. Decides whether to proceed and which
item to work on. Exits non-zero on any precondition failure — the launchd job
must skip the session in that case.

Outputs (on success):
    - ~/.eqmod/autopilot/current_item.txt   : the item id Claude will work on
    - ~/.eqmod/autopilot/last_tick.txt      : ISO timestamp of this preflight
    - stdout                                : a one-line summary

Preconditions:
    - ~/.eqmod/autopilot/STOP must NOT exist
    - repo working tree must be clean (no uncommitted changes on main)
    - QUEUE.yaml must parse and contain at least one queued or in_progress item
    - the brief file for that item must exist
    - HEAD must be on main (we'll branch from there)
    - fast-slice pytest must pass (sanity baseline)
"""
from __future__ import annotations

import datetime as _dt
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
QUEUE_PATH = REPO / ".eqmod/autopilot/QUEUE.yaml"
STATE_DIR = Path.home() / ".eqmod/autopilot"
STOP_PATH = STATE_DIR / "STOP"
CURRENT_ITEM_PATH = STATE_DIR / "current_item.txt"
CURRENT_BRIEF_PATH = STATE_DIR / "current_brief.txt"
LAST_TICK_PATH = STATE_DIR / "last_tick.txt"


def die(msg: str, code: int = 1) -> None:
    print(f"preflight: FAIL: {msg}", file=sys.stderr)
    sys.exit(code)


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, **kw)


def status_by_id(items: list[dict]) -> dict:
    """Map item id -> status string for every item in the queue."""
    return {(it.get("id") or ""): (it.get("status") or "") for it in items}


def blockers_satisfied(item: dict, idx: dict) -> bool:
    """True iff every explicit dependency of `item` is `passed`.

    Uses the shared dependency extractor from queue_semantics so this can
    never drift from validate_queue. Non-existent dependency targets are
    treated as satisfied (mention of a non-existent item is ignored).
    """
    from queue_semantics import extract_explicit_dependencies  # noqa: E402

    item_id = item.get("id")
    for dep_id in extract_explicit_dependencies(item.get("blockers") or []):
        if dep_id == item_id:
            continue
        dep_status = idx.get(dep_id)
        if dep_status is None:
            continue
        if dep_status != "passed":
            return False
    return True


def select_next_item(items: list[dict]) -> dict | None:
    """Replicates preflight's picking rule: in_progress wins, else first
    queued item whose explicit dependencies are all satisfied. Returns the
    picked item dict, or None if nothing is eligible.
    """
    for it in items:
        if it.get("status") == "in_progress":
            return it
    idx = status_by_id(items)
    for it in items:
        if it.get("status") == "queued" and blockers_satisfied(it, idx):
            return it
    return None


def enumerate_rejection_reasons(items: list[dict]) -> list[str]:
    """For every queued item, return a one-line explanation of why it
    cannot fire right now. Narrative ID mentions of non-passed items are
    surfaced too — this is diagnostic output, broader than the gating
    semantics. Used by main() when no item is pickable; the 0e2c0f6
    commit added this enumeration after the 2026-05-20 R-17 incident
    burned 14 h of silent rejection.
    """
    idx = status_by_id(items)
    reasons: list[str] = []
    for it in items:
        if it.get("status") != "queued":
            continue
        iid = it.get("id") or "<no-id>"
        blocked_by: list[str] = []
        for line in (it.get("blockers") or []):
            if not isinstance(line, str):
                continue
            for other_id, other_status in idx.items():
                if not other_id or other_id == iid:
                    continue
                if re.search(rf"\b{re.escape(other_id)}\b", line):
                    if other_status != "passed":
                        blocked_by.append(f"{other_id}(status={other_status!r})")
        if blocked_by:
            reasons.append(f"  {iid} blocked by: {', '.join(blocked_by)}")
        else:
            reasons.append(f"  {iid} blockers satisfied but not picked — investigate")
    return reasons


def main() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. STOP marker
    if STOP_PATH.exists():
        die(f"STOP marker present at {STOP_PATH} — autopilot disabled by user")

    # 2. Clean tree on main
    r = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    branch = r.stdout.strip()
    if branch != "main":
        die(f"HEAD is on '{branch}', expected main")
    r = run(["git", "status", "--porcelain"])
    if r.stdout.strip():
        die("working tree not clean — uncommitted changes on main:\n" + r.stdout)

    # 3. Queue
    if not QUEUE_PATH.exists():
        die(f"queue file missing: {QUEUE_PATH}")
    queue = yaml.safe_load(QUEUE_PATH.read_text())
    items = queue.get("items") or []
    if not items:
        die("queue is empty — nothing to work on")

    # Pick the next item: in_progress takes priority (resume), else first
    # queued item whose explicit blockers are satisfied. The picking and
    # enumeration logic lives at module level (select_next_item /
    # enumerate_rejection_reasons) so it can be unit-tested without a
    # full git+pytest fixture.
    pick = select_next_item(items)
    if pick is None:
        # Enumerate WHY each queued item was rejected. Silent "queue exhausted"
        # cost the 2026-05-20 R-17 incident 14 hours of vacation budget.
        reasons = enumerate_rejection_reasons(items)
        detail = "\n".join(reasons) if reasons else "  (no queued items at all)"
        die(
            "no items with status in {queued, in_progress} satisfying blockers — "
            "queue exhausted or all queued items are blocked\n" + detail
        )

    # 4. Item-level sanity
    item_id = pick.get("id")
    if not item_id:
        die("picked item has no id")
    if pick.get("attempts", 0) >= 3:
        die(f"item {item_id} has attempts>=3 — should have been marked failed by postflight")
    brief = pick.get("brief")
    if not brief:
        die(f"item {item_id} has no brief: field")
    brief_path = REPO / brief
    if not brief_path.exists():
        die(f"brief file missing for {item_id}: {brief_path}")
    if not pick.get("preregistered_acceptance"):
        die(f"item {item_id} has empty preregistered_acceptance")

    # 5. Fast-slice pytest sanity. We tolerate "no tests collected" but not failures.
    r = run([str(REPO / ".venv/bin/python"), "-m", "pytest", "-m", "not slow", "-x", "--tb=no", "-q"])
    if r.returncode != 0:
        # Print last 20 lines of pytest output for the watchdog mail.
        tail = "\n".join((r.stdout + r.stderr).splitlines()[-20:])
        die(f"baseline pytest fails on main BEFORE autopilot starts:\n{tail}")

    # 6. Switch to autopilot/<item-id> branch (create if absent, reset to main otherwise).
    branch_name = f"autopilot/{item_id}"
    r = run(["git", "rev-parse", "--verify", branch_name])
    if r.returncode == 0:
        # Branch exists — check it out, fast-forward only.
        run(["git", "checkout", branch_name], check=True)
    else:
        run(["git", "checkout", "-b", branch_name], check=True)

    # 7. Persist the pick + timestamp
    CURRENT_ITEM_PATH.write_text(item_id + "\n")
    CURRENT_BRIEF_PATH.write_text(brief + "\n")
    LAST_TICK_PATH.write_text(_dt.datetime.now().isoformat() + "\n")

    print(f"preflight OK — branch={branch_name} item={item_id} attempts={pick.get('attempts', 0)}")


if __name__ == "__main__":
    main()
