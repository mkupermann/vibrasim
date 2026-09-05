"""Immutable value objects for the P1 trace audit."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Trace:
    times: np.ndarray
    values: np.ndarray

    def __post_init__(self) -> None:
        times = np.asarray(self.times, dtype=np.float64).copy()
        values = np.asarray(self.values, dtype=np.float64).copy()
        times.setflags(write=False)
        values.setflags(write=False)
        object.__setattr__(self, "times", times)
        object.__setattr__(self, "values", values)


@dataclass(frozen=True)
class PairMetrics:
    signed_peak_contrast: float
    max_abs_contrast: float
    rms_contrast: float
    max_abs_time: float
    max_abs_sign: int
    cycle_peak_time: float
    branch_peak_time: float
    best_lag: float
    zero_lag_correlation: float
    best_lag_correlation: float
