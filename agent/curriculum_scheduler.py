"""Curriculum scheduler — drive a single substrate through the four stages.

The trained substrate advances on perplexity plateau (gated by a per-stage
``expected_min_cycles`` floor so a noisy early plateau cannot promote it
prematurely). Control substrates advance on a wall-clock schedule matched to
the trained substrate, so all four enter babble mode at comparable training
durations regardless of whether their input ever caused the substrate to
"learn" anything (white noise, time-reversed German, French).

See spec: docs/superpowers/specs/2026-05-10-predictive-babble-design.md, §3, §5.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from agent.convergence import ConvergenceDetector


@dataclass
class CurriculumStage:
    """One curriculum stage on one substrate."""

    name: str
    train_data_path: Path
    expected_min_cycles: int = 50


class CurriculumScheduler:
    """Drive a single substrate through the configured stages.

    Parameters
    ----------
    stages
        Ordered list of ``CurriculumStage``. Typically four (audiobook →
        single-speaker conversation → multi-speaker conversation → live).
    is_trained
        True for the trained substrate (advances on convergence). False for
        controls (advances on wall-clock schedule).
    wall_clock_per_stage
        Seconds per stage for control substrates. Length must equal
        ``len(stages)``. Ignored when ``is_trained`` is True.
    convergence
        Required when ``is_trained`` is True. Ignored otherwise.
    """

    def __init__(
        self,
        stages: list[CurriculumStage],
        is_trained: bool,
        wall_clock_per_stage: list[float],
        convergence: Optional[ConvergenceDetector] = None,
    ) -> None:
        if not stages:
            raise ValueError("CurriculumScheduler requires at least one stage")
        if len(wall_clock_per_stage) != len(stages):
            raise ValueError(
                "wall_clock_per_stage length must match stages "
                f"({len(wall_clock_per_stage)} vs {len(stages)})"
            )
        if is_trained and convergence is None:
            raise ValueError(
                "Trained substrate requires a ConvergenceDetector"
            )

        self._stages = list(stages)
        self._is_trained = bool(is_trained)
        self._wall_clock_per_stage = list(wall_clock_per_stage)
        self._convergence = convergence
        self._stage_index = 0
        # Cycle counter scoped to the current stage (resets on advance).
        self._cycles_in_current_stage = 0

        # Cumulative wall-clock thresholds for control schedule:
        # advance to stage i+1 when elapsed >= cumulative[i].
        cumulative: list[float] = []
        running = 0.0
        for d in self._wall_clock_per_stage:
            running += float(d)
            cumulative.append(running)
        self._cumulative_wall_clock = cumulative

    # ------------------------------------------------------------------ props

    @property
    def current_stage_index(self) -> int:
        """Index into ``stages``; equals ``len(stages)`` once done."""
        return self._stage_index

    @property
    def current_stage(self) -> CurriculumStage:
        if self.is_done():
            raise IndexError(
                "CurriculumScheduler is done; no current stage"
            )
        return self._stages[self._stage_index]

    def is_done(self) -> bool:
        """True once we have advanced past the final stage."""
        return self._stage_index >= len(self._stages)

    # ------------------------------------------------------------------ step

    def step(self, perplexity: float, elapsed_seconds: float) -> bool:
        """Advance one evaluation cycle. Return True iff a stage advance fired.

        For the trained substrate, ``perplexity`` is fed to the convergence
        detector and ``elapsed_seconds`` is ignored. For control substrates,
        ``perplexity`` is ignored and ``elapsed_seconds`` is compared against
        the cumulative wall-clock schedule.
        """
        if self.is_done():
            return False

        if self._is_trained:
            return self._step_trained(perplexity)
        return self._step_control(elapsed_seconds)

    # ----------------------------------------------------------- trained path

    def _step_trained(self, perplexity: float) -> bool:
        assert self._convergence is not None  # guarded in __init__
        self._convergence.observe(perplexity)
        self._cycles_in_current_stage += 1

        stage = self._stages[self._stage_index]
        if self._cycles_in_current_stage < stage.expected_min_cycles:
            return False
        if not self._convergence.has_plateaued():
            return False

        # Advance.
        self._stage_index += 1
        self._cycles_in_current_stage = 0
        # Reset detector so the next stage's plateau is judged on its own
        # perplexity series, not contaminated by the previous stage's tail.
        if not self.is_done():
            self._convergence.reset()
        return True

    # ----------------------------------------------------------- control path

    def _step_control(self, elapsed_seconds: float) -> bool:
        # Advance through any stages whose cumulative threshold has been met.
        # Most ticks advance zero stages; on threshold-crossing ticks we
        # advance exactly one. We loop only to handle the (possible) case of
        # a sparse caller jumping past multiple thresholds in one step.
        advanced = False
        while (
            not self.is_done()
            and elapsed_seconds
            >= self._cumulative_wall_clock[self._stage_index]
        ):
            self._stage_index += 1
            advanced = True
        return advanced
