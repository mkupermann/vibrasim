"""Shared queue semantics — single source of truth for preflight + validator.

Both ``autopilot_preflight.py`` and ``validate_queue.py`` must agree on
what counts as a real dependency in a queue item's blocker text. Until
2026-05-20T21:00 the two layers used different word-boundary regexes;
the mismatch caused the cascading-failures incident at 20:33 + 21:03.

Convention: a queue item's blocker line declares an item-level
prerequisite by writing the prerequisite's ID followed by
``must reach status...``. All other ID mentions in blocker text are
narrative documentation and do not gate the item.

This module is intentionally minimal — just the regex and a small
helper. Both layers import it. Edits here propagate atomically.
"""
from __future__ import annotations

import re
from typing import Iterable

# YAML representations of "non-passed terminal" statuses.
# YAML `null` → Python None → coerced to "".
# YAML literal "None" (unquoted, capitalised) → Python str "None".
# YAML "null" as quoted string → "null".
TERMINAL_NON_PASSED = frozenset({"", "null", "None", "failed"})

# Explicit-dependency regex. Both preflight and validator extract real
# prerequisites only from this pattern. The capture group returns the
# referenced item ID.
DEPENDENCY_RE = re.compile(
    r"\b(R-[A-Z0-9][A-Za-z0-9-]*)\s+must\s+reach\s+status",
    re.IGNORECASE,
)


def extract_explicit_dependencies(blocker_lines: Iterable[str]) -> set[str]:
    """Return the set of item IDs this blocker text explicitly depends on.

    Narrative mentions of item IDs (not in the "X must reach status..."
    form) are ignored. The result is the set the preflight uses to
    decide whether the candidate can fire.
    """
    deps: set[str] = set()
    for line in blocker_lines or []:
        if not isinstance(line, str):
            continue
        for m in DEPENDENCY_RE.finditer(line):
            deps.add(m.group(1))
    return deps


def narrative_id_mentions(
    blocker_lines: Iterable[str],
    own_id: str,
    known_ids: Iterable[str],
) -> set[str]:
    """Return item IDs mentioned narratively (NOT as explicit dependencies).

    These are documentation, not gating. The validator surfaces them as
    warnings so the author can confirm intent.
    """
    explicit = extract_explicit_dependencies(blocker_lines)
    seen: set[str] = set()
    known = set(known_ids)
    for line in blocker_lines or []:
        if not isinstance(line, str):
            continue
        for other_id in known:
            if not other_id or other_id == own_id or other_id in explicit:
                continue
            if re.search(rf"\b{re.escape(other_id)}\b", line):
                seen.add(other_id)
    return seen
