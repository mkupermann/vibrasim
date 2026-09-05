import numpy as np
import pytest

from vibrasim2.p1.metrics import MetricError, measure_pair
from vibrasim2.p1.types import Trace


def trace(values, dt=1.0):
    array = np.asarray(values, dtype=np.float64)
    return Trace(np.arange(len(array), dtype=np.float64) * dt, array)


def test_measure_pair_reports_hand_calculated_contrasts():
    measured = measure_pair(trace([0, 3, 0]), trace([0, 1, 0]), 1.0)
    assert measured.signed_peak_contrast == 2.0
    assert measured.max_abs_contrast == 2.0
    assert measured.rms_contrast == pytest.approx(np.sqrt(4.0 / 3.0))
    assert measured.max_abs_time == 1.0
    assert measured.max_abs_sign == 1
    assert measured.cycle_peak_time == 1.0
    assert measured.branch_peak_time == 1.0


def test_maximum_ties_choose_earliest_time():
    measured = measure_pair(trace([0, 2, -2, 0]), trace([0, 0.1, -0.1, 0]), 1.0)
    assert measured.max_abs_time == 1.0
    assert measured.max_abs_sign == 1


def test_cross_correlation_tie_prefers_small_absolute_then_negative_lag():
    measured = measure_pair(
        trace([1, -1, 1, -1]), trace([-1, 1, -1, 1]), 2.0
    )
    assert measured.best_lag == -1.0
    assert measured.best_lag_correlation == pytest.approx(1.0)


def test_zero_variance_trace_is_invalid():
    flat = trace([1, 1, 1])
    with pytest.raises(MetricError, match="zero variance"):
        measure_pair(flat, flat, 1.0)


def test_mismatched_timestamps_are_invalid():
    with pytest.raises(MetricError, match="timestamps"):
        measure_pair(trace([0, 1, 0]), trace([0, 1, 0], dt=0.5), 1.0)
