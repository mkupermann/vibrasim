"""Pure frozen measurements over pairs of persisted matter-energy traces."""

from __future__ import annotations

import math

import numpy as np

from .types import PairMetrics, Trace


class MetricError(ValueError):
    """Raised when a trace cannot support the registered measurements."""


def _validated_pair(cycle: Trace, branch: Trace) -> float:
    if (
        cycle.times.ndim != 1
        or cycle.values.ndim != 1
        or branch.times.ndim != 1
        or branch.values.ndim != 1
        or len(cycle.times) < 3
        or len(cycle.times) != len(cycle.values)
        or len(branch.times) != len(branch.values)
        or len(cycle.times) != len(branch.times)
    ):
        raise MetricError("traces must be equal one-dimensional arrays")
    if not (
        np.isfinite(cycle.times).all()
        and np.isfinite(cycle.values).all()
        and np.isfinite(branch.times).all()
        and np.isfinite(branch.values).all()
    ):
        raise MetricError("traces must be finite")
    if not np.array_equal(cycle.times, branch.times):
        raise MetricError("trace timestamps must match")
    steps = np.diff(cycle.times)
    if not (steps > 0).all() or not np.allclose(steps, steps[0], rtol=0, atol=1e-12):
        raise MetricError("trace timestamps must be strictly uniform")
    if np.linalg.norm(cycle.values - cycle.values.mean()) == 0 or np.linalg.norm(
        branch.values - branch.values.mean()
    ) == 0:
        raise MetricError("zero variance trace")
    return float(steps[0])


def _correlation(left: np.ndarray, right: np.ndarray) -> float | None:
    left = left - left.mean()
    right = right - right.mean()
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    if denominator == 0:
        return None
    return float(np.dot(left, right) / denominator)


def measure_pair(cycle: Trace, branch: Trace, max_lag_time: float) -> PairMetrics:
    dt = _validated_pair(cycle, branch)
    if not math.isfinite(max_lag_time) or max_lag_time < 0:
        raise MetricError("max lag must be finite and non-negative")
    lag_ratio = max_lag_time / dt
    max_lag_steps = int(round(lag_ratio))
    if not math.isclose(lag_ratio, max_lag_steps, rel_tol=0, abs_tol=1e-10):
        raise MetricError("max lag must be an integer number of timesteps")
    max_lag_steps = min(max_lag_steps, len(cycle.values) - 2)

    candidates: list[tuple[float, int]] = []
    for lag in range(-max_lag_steps, max_lag_steps + 1):
        if lag < 0:
            left, right = cycle.values[-lag:], branch.values[:lag]
        elif lag > 0:
            left, right = cycle.values[:-lag], branch.values[lag:]
        else:
            left, right = cycle.values, branch.values
        correlation = _correlation(left, right)
        if correlation is not None:
            candidates.append((correlation, lag))
    zero = next((corr for corr, lag in candidates if lag == 0), None)
    if zero is None or not candidates:
        raise MetricError("zero variance trace")
    best_correlation, best_lag_steps = min(
        candidates, key=lambda item: (-item[0], abs(item[1]), item[1])
    )

    difference = cycle.values - branch.values
    maximum_index = int(np.argmax(np.abs(difference)))
    maximum_value = float(difference[maximum_index])
    return PairMetrics(
        signed_peak_contrast=float(cycle.values.max() - branch.values.max()),
        max_abs_contrast=abs(maximum_value),
        rms_contrast=float(np.sqrt(np.mean(np.square(difference)))),
        max_abs_time=float(cycle.times[maximum_index]),
        max_abs_sign=1 if maximum_value > 0 else -1 if maximum_value < 0 else 0,
        cycle_peak_time=float(cycle.times[int(np.argmax(cycle.values))]),
        branch_peak_time=float(branch.times[int(np.argmax(branch.values))]),
        best_lag=float(best_lag_steps * dt),
        zero_lag_correlation=zero,
        best_lag_correlation=best_correlation,
    )
