"""Fixture for AUTO-1 silent-pass auditor — CLEAN.

This file is not collected by pytest (filename begins with ``_``).
It exists so the auditor can prove it does NOT flag a precondition
that is handled correctly via ``pytest.fail()``.
"""
import pytest


def fake_test_F3b_clean():
    persistence_fractions = []
    n_strong_before = 0  # synthetic precondition

    # ── correct handling: a zero precondition is a hard fail, ──
    # ── not a silent 100% success. Auditor MUST NOT flag this. ──
    if n_strong_before == 0:
        pytest.fail("precondition failed: no strong structures formed")

    for fraction in [0.9, 0.8, 0.7]:
        persistence_fractions.append(fraction)

    avg = sum(persistence_fractions) / len(persistence_fractions)
    assert avg >= 0.5
