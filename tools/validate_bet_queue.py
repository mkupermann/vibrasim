#!/usr/bin/env python3
"""Validate the bet queue at ``~/.eqmod/bet/queue.yaml``.

Symmetric to ``tools/validate_queue.py`` but for the parallel bet
pipeline. Reuses ``tools/queue_semantics.DEPENDENCY_RE`` so the
explicit-vs-narrative blocker distinction is identical between the
short-queue, long-run queue, and bet queue. The dispatcher branch
matching pattern is shared too.

Fails the call if:

    1. The queue file is unparseable.
    2. An item has explicit dependency on a terminal-non-passed item
       (the same ``X must reach status...`` regex as the autopilot
       preflight).
    3. An item's ``pytest_target`` is empty or points at a non-existent
       file beneath the repo (so the dispatcher cannot silently NULL
       every iteration with "no such test").
    4. ``max_runtime_seconds`` is set above the 12-month-bet ceiling
       (1h hard cap, per LOGBOOK 2026-05-22 entry).

Warns (does not fail) on:

    a. Narrative mentions of other items by ID in blocker text.
    b. Items in non-terminal ``running`` state when no current.pid is
       present (suggests a dispatcher crash; operator should ``/requeue``).

Usage::

    .venv/bin/python tools/validate_bet_queue.py
    .venv/bin/python tools/validate_bet_queue.py --queue /tmp/q.yaml

Exit code 0 on OK, 1 on fail.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
from queue_semantics import (  # noqa: E402
    DEPENDENCY_RE,
    TERMINAL_NON_PASSED,
    extract_explicit_dependencies,
    narrative_id_mentions,
)

DEFAULT_QUEUE = Path.home() / ".eqmod/bet/queue.yaml"
DEFAULT_PIDFILE = Path.home() / ".eqmod/bet/current.pid"
BET_HARD_CAP_SECONDS = 3600  # 1h per LOGBOOK 2026-05-22 pre-registration


def _normalise_status(raw) -> str:
    """YAML null → '', literal 'None'/'null' → 'null'."""
    if raw is None:
        return ""
    s = str(raw)
    if s in ("None", "null"):
        return "null"
    return s


def validate(queue_path: Path, pidfile: Path | None = None) -> tuple[int, list[str], list[str]]:
    """Returns (exit_code, errors, warnings)."""
    if not queue_path.exists():
        return 1, [f"validate_bet_queue: no queue at {queue_path}"], []
    try:
        q = yaml.safe_load(queue_path.read_text()) or {}
    except yaml.YAMLError as exc:
        return 1, [f"validate_bet_queue: YAML parse error: {exc}"], []

    items = q.get("items") or []
    idx = {(i.get("id") or ""): _normalise_status(i.get("status")) for i in items}

    errors: list[str] = []
    warnings: list[str] = []

    for item in items:
        item_id = item.get("id") or "<no-id>"
        status = _normalise_status(item.get("status"))

        # Rule 2 — explicit dependency on terminal-non-passed item.
        # Only enforced for items that could still fire (queued).
        if status == "queued":
            for dep_id in extract_explicit_dependencies(item.get("blockers") or []):
                if dep_id == item_id:
                    continue
                st = idx.get(dep_id, "<not-in-queue>")
                if st in TERMINAL_NON_PASSED:
                    errors.append(
                        f"  {item_id} has explicit dependency on {dep_id} "
                        f"(status={st!r}, TERMINAL — will never reach passed)"
                    )

            # Warnings — narrative mentions
            for other_id in narrative_id_mentions(
                item.get("blockers") or [], item_id, idx.keys()
            ):
                st = idx.get(other_id)
                if st != "passed":
                    warnings.append(
                        f"  {item_id} narratively mentions {other_id} "
                        f"(status={st!r}); narrative mentions are documentation only "
                        f"under the shared queue_semantics.DEPENDENCY_RE."
                    )

        # Rule 3 — pytest_target must exist (skip terminal items;
        # historical entries may reference removed tests)
        if status in ("queued", "running"):
            target = (item.get("pytest_target") or "").split()
            if not target:
                errors.append(
                    f"  {item_id} has empty pytest_target — dispatcher cannot "
                    f"evaluate a verdict without one"
                )
            else:
                for t in target:
                    # Pytest target can be "tests/foo.py" or "tests/foo.py::test_x"
                    file_part = t.split("::", 1)[0]
                    candidate = (REPO / file_part) if not Path(file_part).is_absolute() else Path(file_part)
                    if not candidate.exists():
                        errors.append(
                            f"  {item_id} pytest_target points at non-existent "
                            f"file: {file_part!r} (resolved: {candidate})"
                        )

        # Rule 4 — max_runtime_seconds ceiling
        mrt = item.get("max_runtime_seconds")
        if mrt is not None:
            try:
                mrt_i = int(mrt)
                if mrt_i > BET_HARD_CAP_SECONDS:
                    errors.append(
                        f"  {item_id} max_runtime_seconds={mrt_i} exceeds the "
                        f"bet's 1h ({BET_HARD_CAP_SECONDS}s) iteration cap "
                        f"(LOGBOOK 2026-05-22)"
                    )
                if mrt_i <= 0:
                    errors.append(
                        f"  {item_id} max_runtime_seconds={mrt_i} must be > 0"
                    )
            except (TypeError, ValueError):
                errors.append(
                    f"  {item_id} max_runtime_seconds is not an integer: {mrt!r}"
                )

        # Warning — running but no pidfile suggests crash
        if status == "running" and pidfile is not None and not pidfile.exists():
            warnings.append(
                f"  {item_id} status=running but no pidfile at {pidfile}; "
                f"dispatcher may have crashed — consider /requeue"
            )

    if errors:
        return 1, errors, warnings
    return 0, [], warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate bet queue.yaml")
    parser.add_argument(
        "--queue", type=str, default=str(DEFAULT_QUEUE),
        help="path to bet queue (default %(default)s)",
    )
    parser.add_argument(
        "--pidfile", type=str, default=str(DEFAULT_PIDFILE),
        help="path to dispatcher pidfile (default %(default)s)",
    )
    args = parser.parse_args(argv)

    queue_path = Path(args.queue)
    pidfile = Path(args.pidfile) if args.pidfile else None

    code, errors, warnings = validate(queue_path, pidfile)

    if errors:
        print(
            f"validate_bet_queue: FAIL — bet queue at {queue_path} has unsatisfiable items:",
            file=sys.stderr,
        )
        for e in errors:
            print(e, file=sys.stderr)
        if warnings:
            print("\n(also warnings, not blocking):", file=sys.stderr)
            for w in warnings:
                print(w, file=sys.stderr)
        return code

    if warnings:
        print("validate_bet_queue: WARN", file=sys.stderr)
        for w in warnings:
            print(w, file=sys.stderr)

    try:
        items = (yaml.safe_load(queue_path.read_text()) or {}).get("items") or []
    except Exception:
        items = []
    queued = sum(1 for i in items if _normalise_status(i.get("status")) == "queued")
    print(
        f"validate_bet_queue: OK — {len(items)} items total, {queued} queued, "
        f"queue at {queue_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
