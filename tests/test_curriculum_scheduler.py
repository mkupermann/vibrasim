"""Unit tests for ConvergenceDetector + CurriculumScheduler.

The two are tightly coupled (the scheduler embeds a detector), so spec keeps
their tests in one file. All tests are synthetic — no World, no corpus,
no real perplexity series. Total runtime well under 2 s.

Reference: docs/superpowers/specs/2026-05-10-predictive-babble-design.md, §3, §8.
F3b silent-pass guard: every conditional path uses ``pytest.fail`` on
unreachable branches.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agent.convergence import ConvergenceDetector
from agent.curriculum_scheduler import CurriculumScheduler, CurriculumStage


# --------------------------------------------------------------------------- #
# ConvergenceDetector                                                         #
# --------------------------------------------------------------------------- #


def test_no_plateau_before_min_history() -> None:
    """Fewer observations than ``min_history_for_decision`` → never plateau."""
    det = ConvergenceDetector(
        window_size=10,
        min_relative_improvement=0.01,
        min_history_for_decision=20,
    )
    for _ in range(5):
        det.observe(50.0)
    if det.has_plateaued():
        pytest.fail(
            "Plateau triggered with only 5 observations "
            "(min_history_for_decision=20)"
        )
    assert len(det.history()) == 5


def test_monotone_decrease_no_plateau() -> None:
    """Strictly improving series must not be flagged as plateau."""
    det = ConvergenceDetector(
        window_size=10,
        min_relative_improvement=0.01,
        min_history_for_decision=20,
    )
    # Linear 100 → 70 over 30 samples = ~1 unit drop per cycle ≈ 1.4% / cycle
    # over the moving window. Comfortably above the 1% threshold.
    n = 30
    for i in range(n):
        ppl = 100.0 - (30.0 * i / (n - 1))
        det.observe(ppl)
    if det.has_plateaued():
        pytest.fail(
            "Plateau triggered on monotone-decreasing series "
            f"(history tail = {det.history()[-5:]})"
        )


def test_flat_series_plateaus() -> None:
    """Flat (with tiny noise) series past min_history must plateau."""
    det = ConvergenceDetector(
        window_size=10,
        min_relative_improvement=0.01,
        min_history_for_decision=20,
    )
    # Deterministic tiny oscillation around 50.0; no real improvement.
    for i in range(30):
        det.observe(50.0 + (0.001 if i % 2 == 0 else -0.001))
    if not det.has_plateaued():
        pytest.fail(
            "Flat series did not plateau "
            f"(history tail = {det.history()[-5:]})"
        )


def test_post_plateau_recovery_resets() -> None:
    """Flat → sharp drop → flat: plateau returns once the new flat region
    has matured into the rolling window. We verify the three regimes:
      (a) after first flat region: plateaued.
      (b) immediately after a sharp drop: NOT plateaued (window straddles
          the cliff so prev-mean ≫ last-mean → big improvement).
      (c) after the second flat region matures: plateaued again.
    """
    det = ConvergenceDetector(
        window_size=10,
        min_relative_improvement=0.01,
        min_history_for_decision=20,
    )
    # (a) 30 cycles flat at 50.0
    for _ in range(30):
        det.observe(50.0)
    if not det.has_plateaued():
        pytest.fail("First flat region failed to plateau")

    # (b) Sharp drop to 10.0 for the next 10 cycles. The most recent window
    # mean is ~10, the previous window mean is ~50 → 80% improvement →
    # NOT plateaued.
    for _ in range(10):
        det.observe(10.0)
    if det.has_plateaued():
        pytest.fail(
            "Plateau wrongly detected immediately after a sharp improvement"
        )

    # (c) Continue flat at 10.0 for another 20 cycles so both windows lie
    # entirely inside the new flat region.
    for _ in range(20):
        det.observe(10.0)
    if not det.has_plateaued():
        pytest.fail(
            "Second flat region failed to plateau after maturing "
            f"(history tail = {det.history()[-5:]})"
        )


def test_reset_clears_history() -> None:
    """reset() drops history; plateau goes False until min_history rebuilt."""
    det = ConvergenceDetector(
        window_size=10,
        min_relative_improvement=0.01,
        min_history_for_decision=20,
    )
    for _ in range(50):
        det.observe(50.0)
    if not det.has_plateaued():
        pytest.fail("Pre-reset flat series failed to plateau")
    det.reset()
    if det.history():
        pytest.fail("history() not empty after reset()")
    if det.has_plateaued():
        pytest.fail("Plateau still True immediately after reset()")


# --------------------------------------------------------------------------- #
# CurriculumScheduler — shared fixtures                                       #
# --------------------------------------------------------------------------- #


def _make_stages(min_cycles: int = 10) -> list[CurriculumStage]:
    """Four synthetic stages, each requiring ``min_cycles`` minimum."""
    return [
        CurriculumStage(
            name=f"stage{i}",
            train_data_path=Path(f"/tmp/fake_stage_{i}.f32.raw"),
            expected_min_cycles=min_cycles,
        )
        for i in range(1, 5)
    ]


def _trained_scheduler(min_cycles: int = 10) -> CurriculumScheduler:
    return CurriculumScheduler(
        stages=_make_stages(min_cycles=min_cycles),
        is_trained=True,
        wall_clock_per_stage=[0.0, 0.0, 0.0, 0.0],  # ignored
        convergence=ConvergenceDetector(
            window_size=10,
            min_relative_improvement=0.01,
            min_history_for_decision=20,
        ),
    )


# --------------------------------------------------------------------------- #
# CurriculumScheduler                                                         #
# --------------------------------------------------------------------------- #


def test_trained_advances_on_plateau() -> None:
    """Trained substrate fed plateaued perplexity should walk all 4 stages."""
    sched = _trained_scheduler(min_cycles=10)
    advances = 0
    # 100 cycles is far more than 4 stages × (min_cycles + min_history).
    # min_cycles=10, but min_history_for_decision=20 dominates per stage.
    for _ in range(200):
        if sched.step(perplexity=50.0, elapsed_seconds=0.0):
            advances += 1
        if sched.is_done():
            break
    if not sched.is_done():
        pytest.fail(
            f"Scheduler not done after 200 cycles "
            f"(stage_index={sched.current_stage_index}, advances={advances})"
        )
    if advances != 4:
        pytest.fail(f"Expected exactly 4 advances, got {advances}")


def test_trained_does_not_advance_before_min_cycles() -> None:
    """expected_min_cycles is a hard floor even when perplexity plateaus."""
    sched = _trained_scheduler(min_cycles=50)
    for _ in range(5):
        advanced = sched.step(perplexity=50.0, elapsed_seconds=0.0)
        if advanced:
            pytest.fail(
                "Scheduler advanced before expected_min_cycles=50 was reached"
            )
    if sched.current_stage_index != 0:
        pytest.fail(
            f"Stage index drifted to {sched.current_stage_index}; expected 0"
        )


def test_control_advances_on_wall_clock() -> None:
    """Control schedule: cumulative thresholds 10/20/30/40s."""
    sched = CurriculumScheduler(
        stages=_make_stages(min_cycles=10),
        is_trained=False,
        wall_clock_per_stage=[10.0, 10.0, 10.0, 10.0],
        convergence=None,  # ignored
    )
    # Sequence per spec: 0, 5, 15, 25, 35, 45.
    # Cumulative thresholds: 10, 20, 30, 40.
    # So: 0 → no advance, 5 → no, 15 ≥ 10 → advance to stage 1,
    # 25 ≥ 20 → stage 2, 35 ≥ 30 → stage 3, 45 ≥ 40 → done.
    expected = [
        (0.0, False, 0, False),
        (5.0, False, 0, False),
        (15.0, True, 1, False),
        (25.0, True, 2, False),
        (35.0, True, 3, False),
        (45.0, True, 4, True),
    ]
    for elapsed, expect_advance, expect_index, expect_done in expected:
        advanced = sched.step(perplexity=999.0, elapsed_seconds=elapsed)
        if advanced != expect_advance:
            pytest.fail(
                f"At elapsed={elapsed}s: expected advance={expect_advance}, "
                f"got {advanced}"
            )
        if sched.current_stage_index != expect_index:
            pytest.fail(
                f"At elapsed={elapsed}s: expected stage_index="
                f"{expect_index}, got {sched.current_stage_index}"
            )
        if sched.is_done() != expect_done:
            pytest.fail(
                f"At elapsed={elapsed}s: expected is_done={expect_done}, "
                f"got {sched.is_done()}"
            )


def test_control_ignores_perplexity() -> None:
    """Control substrate must never advance when elapsed is held at 0."""
    sched = CurriculumScheduler(
        stages=_make_stages(min_cycles=10),
        is_trained=False,
        wall_clock_per_stage=[10.0, 10.0, 10.0, 10.0],
        convergence=None,
    )
    # Wildly varying perplexities — would trigger plateau-or-not in any
    # convergence detector — but elapsed stays at 0 so nothing advances.
    perplexities = [1.0, 1000.0, 0.5, 50.0, 50.0, 50.0, 50.0, 1e6, 1e-6, 50.0]
    for ppl in perplexities * 10:
        advanced = sched.step(perplexity=ppl, elapsed_seconds=0.0)
        if advanced:
            pytest.fail(
                f"Control substrate advanced on perplexity={ppl} "
                "with elapsed=0 — perplexity must be ignored"
            )
    if sched.current_stage_index != 0:
        pytest.fail(
            f"Stage index drifted to {sched.current_stage_index}; expected 0"
        )


def test_step_returns_true_only_on_advance() -> None:
    """step() returns True exactly on the cycle that advances; False else."""
    sched = _trained_scheduler(min_cycles=10)
    # Track every step's return for the first stage advance.
    advance_cycles: list[int] = []
    for cycle in range(60):
        if sched.step(perplexity=50.0, elapsed_seconds=0.0):
            advance_cycles.append(cycle)
            break
    else:
        pytest.fail(
            "Scheduler did not advance within 60 plateaued cycles"
        )

    # Sanity: only one advance recorded so far, and it happened after both
    # min_history_for_decision (20) and expected_min_cycles (10) were met.
    if len(advance_cycles) != 1:
        pytest.fail(
            f"Expected exactly 1 advance in this loop, got {advance_cycles}"
        )
    if advance_cycles[0] < 19:  # cycle index 19 == 20th observation
        pytest.fail(
            f"Advanced too early: cycle index {advance_cycles[0]} "
            "(need ≥ min_history_for_decision=20 observations)"
        )

    # Now feed a few more cycles on the *next* stage; the very next call
    # must return False (we just reset the detector → not enough history).
    next_returns = [
        sched.step(perplexity=50.0, elapsed_seconds=0.0) for _ in range(5)
    ]
    if any(next_returns):
        pytest.fail(
            f"Scheduler advanced again immediately after a stage transition: "
            f"{next_returns}"
        )
