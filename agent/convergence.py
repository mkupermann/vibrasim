"""Windowed-perplexity plateau detector for the predictive-babble curriculum.

Pure-Python, no project dependencies. Used by `curriculum_scheduler.py` to
decide when the trained substrate has stopped improving on the dev split and
the next stage may be entered.

See spec: docs/superpowers/specs/2026-05-10-predictive-babble-design.md, §3.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ConvergenceDetector:
    """Track perplexity history; report whether it has plateaued.

    A plateau is declared when:
      1. We have observed at least ``min_history_for_decision`` perplexities
         (so noisy early cycles cannot trigger an advance), AND
      2. The relative improvement between the previous ``window_size`` cycles
         and the most recent ``window_size`` cycles is below
         ``min_relative_improvement``.

    Relative improvement is defined as
        (mean(prev_window) - mean(last_window)) / max(mean(prev_window), 1e-9)
    so a value < threshold means perplexity has stopped dropping appreciably.
    Negative values (perplexity rising) also count as "not improving" and
    therefore plateaued.
    """

    window_size: int = 10
    min_relative_improvement: float = 0.01
    min_history_for_decision: int = 20
    _history: list[float] = field(default_factory=list, repr=False)

    def observe(self, perplexity: float) -> None:
        """Record one perplexity sample."""
        self._history.append(float(perplexity))

    def has_plateaued(self) -> bool:
        """Return True iff we have enough history AND the slope is flat."""
        n = len(self._history)
        if n < self.min_history_for_decision:
            return False
        # Need at least 2 * window_size points to form prev/last windows.
        if n < 2 * self.window_size:
            return False
        last = self._history[-self.window_size :]
        prev = self._history[-2 * self.window_size : -self.window_size]
        mean_last = sum(last) / len(last)
        mean_prev = sum(prev) / len(prev)
        rel_improvement = (mean_prev - mean_last) / max(mean_prev, 1e-9)
        return rel_improvement < self.min_relative_improvement

    def reset(self) -> None:
        """Drop all observed history. After reset, plateau is False until
        ``min_history_for_decision`` new observations accumulate."""
        self._history.clear()

    def history(self) -> list[float]:
        """Return a *copy* of the observed perplexity series."""
        return list(self._history)
