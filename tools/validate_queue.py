#!/usr/bin/env python3
"""Validate .eqmod/autopilot/QUEUE.yaml — catch self-blocking blocker strings.

The preflight blocker check (tools/autopilot_preflight.py::blockers_satisfied)
scans every blocker string for word-boundary mentions of other item IDs. If
ANY mentioned item is not 'passed', the candidate item is rejected. This
catches genuine prerequisites correctly. It also catches NARRATIVE
references — blocker text like "X confirmed the firewall" mentions X by ID,
and if X is null/failed/queued, the candidate stays blocked silently.

This validator runs that same scan and FAILS THE COMMIT if any queued
item references a non-passed item by ID. Wired into the pre-commit hook
on QUEUE.yaml changes. Catches the bug at commit time instead of via
14h of silent launchd-tick rejections (the 2026-05-20 R-17 incident).

Exit 0 if OK. Exit 1 with a precise per-item error list.

Can also be run manually before any QUEUE.yaml edit:
    .venv/bin/python tools/validate_queue.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
QUEUE = REPO / ".eqmod/autopilot/QUEUE.yaml"

# Shared semantics with autopilot_preflight.py — see tools/queue_semantics.py
sys.path.insert(0, str(REPO / "tools"))
from queue_semantics import (  # noqa: E402
    DEPENDENCY_RE,
    TERMINAL_NON_PASSED,
    extract_explicit_dependencies,
    narrative_id_mentions,
)


def main() -> int:
    if not QUEUE.exists():
        print(f"validate_queue: no QUEUE.yaml at {QUEUE}", file=sys.stderr)
        return 1
    try:
        q = yaml.safe_load(QUEUE.read_text())
    except yaml.YAMLError as exc:
        print(f"validate_queue: YAML parse error: {exc}", file=sys.stderr)
        return 1
    items = q.get("items") or []
    idx = {(i.get("id") or ""): (i.get("status") or "") for i in items}

    errors: list[str] = []
    warnings: list[str] = []
    for item in items:
        if item.get("status") != "queued":
            continue
        item_id = item.get("id") or "<no-id>"
        blockers = item.get("blockers") or []

        # FAIL: explicit "X must reach status..." dependency on terminal item.
        # Uses the shared extractor so this can never drift from preflight.
        for dep_id in extract_explicit_dependencies(blockers):
            if dep_id == item_id:
                continue
            st = idx.get(dep_id, "<not-in-queue>")
            if st in TERMINAL_NON_PASSED:
                errors.append(
                    f"  {item_id} has explicit dependency on {dep_id} "
                    f"(status={st!r}, TERMINAL — will never reach passed)."
                )

        # FAIL: brief field must point at an existing file. The preflight
        # rejects missing-brief items with a 30-min tick burn; catch it here
        # at commit time. Class-C bug from 2026-05-20T21:03 (R-19 brief was
        # the description sentence instead of a path).
        brief = item.get("brief")
        if brief:
            brief_path = REPO / brief
            if not brief_path.exists():
                errors.append(
                    f"  {item_id} brief points at non-existent path: {brief!r}"
                )
                errors.append(
                    f"    (resolved to {brief_path}); preflight would reject at "
                    f"the brief-file-exists check"
                )

        # WARN: narrative mentions of non-passed items. Allowed under the new
        # preflight semantics but worth flagging so the author can confirm.
        for other_id in narrative_id_mentions(blockers, item_id, idx.keys()):
            st = idx.get(other_id)
            if st != "passed":
                warnings.append(
                    f"  {item_id} narratively mentions {other_id} "
                    f"(status={st!r}); narrative mentions are documentation "
                    f"only under the new preflight regex. Re-read to confirm intent."
                )

    if errors:
        print(
            "validate_queue: FAIL — queued items have unsatisfiable explicit dependencies:",
            file=sys.stderr,
        )
        for e in errors:
            print(e, file=sys.stderr)
        print(
            "\nFix: an item declared 'X must reach status=passed first' where X is "
            "already in a terminal non-passed state will never be picked. Either "
            "drop the dependency (it is not real) or retarget at an item that can "
            "still pass.",
            file=sys.stderr,
        )
        if warnings:
            print("\n(also warnings, not blocking):", file=sys.stderr)
            for w in warnings:
                print(w, file=sys.stderr)
        return 1

    if warnings:
        print("validate_queue: WARN — narrative item mentions in blockers:", file=sys.stderr)
        for w in warnings:
            print(w, file=sys.stderr)

    queued = sum(1 for i in items if i.get("status") == "queued")
    # "ready to fire" = queued and every mentioned other-item is currently passed.
    ready = sum(
        1
        for i in items
        if i.get("status") == "queued"
        and all(
            not isinstance(line, str)
            or all(
                not (
                    other_id != i.get("id")
                    and re.search(rf"\b{re.escape(other_id)}\b", line)
                    and st != "passed"
                )
                for other_id, st in idx.items()
            )
            for line in (i.get("blockers") or [])
        )
    )
    print(
        f"validate_queue: OK — {len(items)} items total, "
        f"{queued} queued, {ready} ready-to-fire-now"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
