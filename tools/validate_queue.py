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

    # A blocker mention is BAD only if the mentioned item is in a TERMINAL
    # non-passed state. Items in {queued, in_progress, blocked} may yet
    # reach 'passed' through the normal pipeline — those are legitimate
    # forward-looking prerequisites (e.g. R-18 blocking on R-17 while
    # R-17 is queued). Items in {null, failed} will never become passed
    # without manual intervention; mentioning them in a blocker silently
    # freezes the candidate. That is the bug class we are catching.
    TERMINAL_NON_PASSED = {"null", "failed", "None"}

    errors: list[str] = []
    for item in items:
        if item.get("status") != "queued":
            continue
        item_id = item.get("id") or "<no-id>"
        for line in item.get("blockers") or []:
            if not isinstance(line, str):
                continue
            for other_id, st in idx.items():
                if not other_id or other_id == item_id:
                    continue
                if re.search(rf"\b{re.escape(other_id)}\b", line) and st in TERMINAL_NON_PASSED:
                    errors.append(
                        f"  {item_id} blocked by mention of {other_id} "
                        f"(status={st!r}, TERMINAL — will never reach passed without manual action)."
                    )
                    errors.append(
                        f"    offending blocker text: {line[:140]}..."
                    )

    if errors:
        print(
            "validate_queue: FAIL — queued items have self-blocking blocker references:",
            file=sys.stderr,
        )
        for e in errors:
            print(e, file=sys.stderr)
        print(
            "\nFix: rephrase the blocker so it mentions ONLY item IDs whose"
            " passing is a real prerequisite. For narrative context to non-passed"
            " items, drop the bare ID and use a phrase + LOGBOOK pointer instead"
            " (e.g. 'the prior diagnostic item, see LOGBOOK 2026-05-20').",
            file=sys.stderr,
        )
        return 1

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
