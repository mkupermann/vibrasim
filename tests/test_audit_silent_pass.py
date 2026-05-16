"""AUTO-1: silent-pass test-pattern auditor.

Detects the F3b-style silent-pass bug recorded in CLAUDE.md and
``docs/maintenance/AUTO-1.md``::

    if n_strong_before == 0:
        persistence_fractions.append(1.0)   # ← silently records success

The pattern is narrow on purpose: a precondition that compares to zero
(or an emptiness check) whose body is a single ``<list>.append(<success
literal>)``. False negatives are expected and acceptable — this auditor
catches the one specific trap that already burned the project once.

Scope is intentionally limited to *static analysis over source text*.
The auditor uses ``ast`` (never regex on Python source) and is read-only.

Acceptance (pre-registered, see docs/maintenance/AUTO-1.md):

* ``test_auditor_finds_silent_pass_in_fixture`` — bad fixture is flagged.
* ``test_auditor_clears_clean_fixture``        — clean fixture is not flagged.
* ``test_auditor_scans_real_test_suite``       — real ``tests/test_*.py``
  produce zero matches that are not whitelist-suppressed, and the
  whitelist contains no stale entries.
"""
from __future__ import annotations

import ast
from pathlib import Path

TESTS_DIR = Path(__file__).parent
REPO_ROOT = TESTS_DIR.parent
FIXTURES_DIR = TESTS_DIR / "fixtures" / "silent_pass"
WHITELIST_PATH = TESTS_DIR / "silent_pass_whitelist.txt"


# ---------------------------------------------------------------------------
# AST predicates
# ---------------------------------------------------------------------------


def _is_zero_literal(node: ast.AST) -> bool:
    """Return True if ``node`` is the integer/float literal 0 (not ``False``)."""
    if not isinstance(node, ast.Constant):
        return False
    value = node.value
    if isinstance(value, bool):
        return False
    return isinstance(value, (int, float)) and value == 0


def _is_len_call(node: ast.AST) -> bool:
    """Return True if ``node`` is a call of the form ``len(<expr>)``."""
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "len"
        and len(node.args) == 1
    )


def _is_listlike_ref(node: ast.AST) -> bool:
    """A reference shape that *could* be a list/array (``x``, ``self.x``, ``x[i]``).

    Conservative on purpose: only Name / Attribute / Subscript are accepted
    so that ``if not some_bool:`` does not get flagged. Full type inference
    is out of scope.
    """
    return isinstance(node, (ast.Name, ast.Attribute, ast.Subscript))


def _is_zero_predicate(test: ast.AST) -> bool:
    """Match the precondition shapes called out in the AUTO-1 brief.

    Matches:
    * ``<expr> == 0`` or ``0 == <expr>``
    * ``len(<expr>) == 0`` or ``0 == len(<expr>)``  (subset of the above)
    * ``not <name|attr|subscript>``                  (emptiness check on a
      list/array-shaped reference)
    """
    if isinstance(test, ast.Compare):
        if len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq):
            left = test.left
            right = test.comparators[0]
            if _is_zero_literal(left) and not _is_zero_literal(right):
                return True
            if _is_zero_literal(right) and not _is_zero_literal(left):
                return True
        return False
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        operand = test.operand
        if _is_listlike_ref(operand) or _is_len_call(operand):
            return True
    return False


def _is_success_literal(node: ast.AST) -> bool:
    """Match the four success-literal shapes called out in the brief: 1, 1.0, True, ``"pass"``.

    ``False`` and other constants must NOT match. Because ``True == 1`` in
    Python, we narrow with ``isinstance`` + ``is`` checks.
    """
    if not isinstance(node, ast.Constant):
        return False
    value = node.value
    if value is True:
        return True
    if isinstance(value, bool):  # captures False
        return False
    if isinstance(value, int) and value == 1:
        return True
    if isinstance(value, float) and value == 1.0:
        return True
    if isinstance(value, str) and value == "pass":
        return True
    return False


def _silent_pass_append_line(body: list[ast.stmt]) -> int | None:
    """If ``body`` is exactly one ``<list>.append(<success literal>)`` call,
    return its line number; otherwise ``None``.
    """
    if len(body) != 1:
        return None
    stmt = body[0]
    if not isinstance(stmt, ast.Expr):
        return None
    call = stmt.value
    if not isinstance(call, ast.Call):
        return None
    if not isinstance(call.func, ast.Attribute):
        return None
    if call.func.attr != "append":
        return None
    if len(call.args) != 1 or call.keywords:
        return None
    if not _is_success_literal(call.args[0]):
        return None
    return stmt.lineno


# ---------------------------------------------------------------------------
# Auditor
# ---------------------------------------------------------------------------


def audit_file(path: Path) -> list[tuple[Path, int, str]]:
    """Audit one Python source file. Return a list of (path, lineno, detail).

    Read-only. Does not import the target. Pure AST.
    """
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    matches: list[tuple[Path, int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        if not _is_zero_predicate(node.test):
            continue
        line = _silent_pass_append_line(node.body)
        if line is None:
            continue
        matches.append(
            (path, line, "silent-pass: zero-precondition appends success literal")
        )
    return matches


def _format_key(path: Path, line: int) -> str:
    """``tests/foo.py:42``-style key, repo-root-relative."""
    try:
        rel = path.relative_to(REPO_ROOT)
    except ValueError:
        rel = path
    return f"{rel}:{line}"


def _load_whitelist() -> set[str]:
    """Read ``tests/silent_pass_whitelist.txt`` if present.

    Format: one ``path:line`` entry per line. Blank lines and ``#``-comment
    lines are ignored. Every non-comment entry MUST have a 1-line
    ``# justified: <reason>`` comment on the immediately preceding line.
    """
    if not WHITELIST_PATH.exists():
        return set()
    entries: set[str] = set()
    lines = WHITELIST_PATH.read_text(encoding="utf-8").splitlines()
    for idx, raw in enumerate(lines):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # Justification comment must be on the immediately preceding line.
        prev = lines[idx - 1].strip() if idx > 0 else ""
        if not prev.startswith("# justified:"):
            raise AssertionError(
                f"{WHITELIST_PATH.name}:{idx + 1}: whitelist entry "
                f"{stripped!r} lacks a '# justified: <reason>' comment "
                f"on the preceding line"
            )
        entries.add(stripped)
    return entries


# ---------------------------------------------------------------------------
# Pre-registered tests
# ---------------------------------------------------------------------------


def test_auditor_finds_silent_pass_in_fixture():
    """Acceptance #1: the auditor flags the deliberate fixture."""
    bad = FIXTURES_DIR / "_bad_example.py"
    assert bad.exists(), f"fixture missing: {bad}"
    matches = audit_file(bad)
    assert matches, (
        f"auditor failed to flag deliberate silent-pass fixture at {bad}; "
        f"this is the negative control — auditor is a state detector, not a finding"
    )
    # The line that matched should be the .append(1.0) line, not the if-test line.
    source_lines = bad.read_text().splitlines()
    matched_line = matches[0][1]
    assert "append(1.0)" in source_lines[matched_line - 1], (
        f"auditor matched {bad}:{matched_line} but that line is "
        f"{source_lines[matched_line - 1]!r}; expected the .append(1.0) line"
    )


def test_auditor_clears_clean_fixture():
    """Acceptance #2: the auditor does NOT flag the clean fixture."""
    clean = FIXTURES_DIR / "_clean_example.py"
    assert clean.exists(), f"fixture missing: {clean}"
    matches = audit_file(clean)
    assert not matches, (
        f"auditor false-positive on clean fixture {clean}: {matches}"
    )


def test_auditor_scans_real_test_suite():
    """Acceptance #3: real test suite is clean modulo whitelist; no stale entries."""
    whitelist = _load_whitelist()

    all_matches: list[tuple[Path, int, str]] = []
    for path in sorted(TESTS_DIR.glob("test_*.py")):
        if path.name == "test_audit_silent_pass.py":
            continue
        all_matches.extend(audit_file(path))

    current_keys = {_format_key(p, line) for (p, line, _) in all_matches}

    stale = whitelist - current_keys
    assert not stale, (
        f"stale whitelist entries (no longer match): {sorted(stale)}; "
        f"remove them from {WHITELIST_PATH.name}"
    )

    unsuppressed = sorted(current_keys - whitelist)
    assert not unsuppressed, (
        "silent-pass patterns detected in test suite:\n  "
        + "\n  ".join(unsuppressed)
        + f"\n\nFix the test (use pytest.fail() on the unreachable branch) "
        f"or, if truly justified, add to {WHITELIST_PATH.name} with a "
        f"'# justified: <reason>' comment on the preceding line."
    )
