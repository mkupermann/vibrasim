from dataclasses import replace

import pytest

from vibrasim2.p1.audit import AuditOutcome, SourceAudit, classify_audit
from vibrasim2.p1.types import PairMetrics


def metrics(*, maximum, rms, lag=0.0, gain=0.0, sign=1):
    return PairMetrics(
        signed_peak_contrast=maximum / 2,
        max_abs_contrast=maximum,
        rms_contrast=rms,
        max_abs_time=1.0,
        max_abs_sign=sign,
        cycle_peak_time=1.0,
        branch_peak_time=1.0 + lag,
        best_lag=lag,
        zero_lag_correlation=0.8 - gain,
        best_lag_correlation=0.8,
    )


def sources(*, maximum, rms, lag=0.0, gain=0.0):
    coarse = metrics(maximum=maximum - 0.001, rms=rms, lag=lag, gain=gain)
    convergence = metrics(maximum=maximum, rms=rms, lag=lag, gain=gain)
    return tuple(SourceAudit(source, coarse, convergence) for source in ((4, 16), (16, 4), (4, 4)))


@pytest.mark.parametrize(
    ("items", "expected"),
    [
        (sources(maximum=0.03, rms=0.02), AuditOutcome.TIME_STRUCTURE_CANDIDATE),
        (sources(maximum=0.03, rms=0.005, lag=0.2, gain=0.1), AuditOutcome.TIME_STRUCTURE_CANDIDATE),
        (sources(maximum=0.005, rms=0.003), AuditOutcome.WEAK_CHANNEL),
        (sources(maximum=0.015, rms=0.005), AuditOutcome.UNRESOLVED),
    ],
)
def test_ordered_diagnostic_outcomes(items, expected):
    assert classify_audit(items).outcome is expected


def test_exact_candidate_boundaries_are_unresolved():
    items = sources(maximum=0.02, rms=0.01, lag=0.10, gain=0.05)
    assert classify_audit(items).outcome is AuditOutcome.UNRESOLVED


def test_convergence_boundary_is_invalid_before_candidate():
    items = list(sources(maximum=0.03, rms=0.02))
    first = items[0]
    items[0] = replace(
        first,
        convergence=replace(
            first.convergence,
            max_abs_contrast=first.coarse.max_abs_contrast + 0.002,
        ),
    )
    result = classify_audit(tuple(items))
    assert result.outcome is AuditOutcome.INVALID
    assert "max_abs_contrast_convergence" in result.reasons


def test_sign_disagreement_is_invalid():
    items = list(sources(maximum=0.03, rms=0.02))
    items[0] = replace(
        items[0], convergence=replace(items[0].convergence, max_abs_sign=-1)
    )
    assert classify_audit(tuple(items)).outcome is AuditOutcome.INVALID
