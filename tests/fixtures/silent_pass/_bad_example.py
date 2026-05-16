"""Fixture for AUTO-1 silent-pass auditor — DELIBERATELY broken.

This file is not collected by pytest (filename begins with ``_``).
It exists so the auditor can prove it flags a known-bad pattern.

The bug shape mirrors the F3b silent-pass bug recorded in CLAUDE.md:
when the precondition ``n_strong_before == 0`` is met, the test silently
records a 100% success instead of failing fast.
"""


def fake_test_F3b_silent_pass():
    persistence_fractions = []
    n_strong_before = 0  # synthetic precondition

    # ── deliberate silent-pass pattern; auditor MUST flag this line ──
    if n_strong_before == 0:
        persistence_fractions.append(1.0)
    else:
        persistence_fractions.append(0.5)

    avg = sum(persistence_fractions) / len(persistence_fractions)
    assert avg >= 0.5
