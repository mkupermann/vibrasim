"""Registered P1 measurement orchestration and ordered diagnosis."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .input import load_registered_pairs
from .metrics import MetricError, measure_pair
from .types import PairMetrics


class AuditOutcome(str, Enum):
    INVALID = "INVALID"
    TIME_STRUCTURE_CANDIDATE = "TIME_STRUCTURE_CANDIDATE"
    WEAK_CHANNEL = "WEAK_CHANNEL"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class SourceAudit:
    source_centre: tuple[int, int]
    coarse: PairMetrics
    convergence: PairMetrics

    @property
    def integrity_holds(self) -> bool:
        return (
            abs(
                self.coarse.max_abs_contrast
                - self.convergence.max_abs_contrast
            )
            < 0.002
            and self.coarse.max_abs_sign == self.convergence.max_abs_sign
        )

    @property
    def is_time_structure_candidate(self) -> bool:
        lag_evidence = (
            abs(self.convergence.best_lag) >= 0.10
            and self.convergence.best_lag_correlation
            - self.convergence.zero_lag_correlation
            >= 0.05
        )
        return (
            self.integrity_holds
            and self.convergence.max_abs_contrast > 0.02
            and (lag_evidence or self.convergence.rms_contrast > 0.01)
        )


@dataclass(frozen=True)
class AuditResult:
    outcome: AuditOutcome
    sources: tuple[SourceAudit, ...]
    reasons: tuple[str, ...] = ()


def classify_audit(sources: tuple[SourceAudit, ...]) -> AuditResult:
    if len(sources) != 3 or len({item.source_centre for item in sources}) != 3:
        return AuditResult(AuditOutcome.INVALID, sources, ("source_matrix",))
    convergence_failures = tuple(
        "max_abs_contrast_convergence"
        for item in sources
        if abs(item.coarse.max_abs_contrast - item.convergence.max_abs_contrast)
        >= 0.002
    )
    sign_failures = tuple(
        "max_abs_contrast_sign"
        for item in sources
        if item.coarse.max_abs_sign != item.convergence.max_abs_sign
    )
    reasons = convergence_failures + sign_failures
    if reasons:
        return AuditResult(AuditOutcome.INVALID, sources, tuple(dict.fromkeys(reasons)))
    if sum(item.is_time_structure_candidate for item in sources) >= 2:
        return AuditResult(AuditOutcome.TIME_STRUCTURE_CANDIDATE, sources)
    if all(item.convergence.max_abs_contrast < 0.01 for item in sources):
        return AuditResult(AuditOutcome.WEAK_CHANNEL, sources)
    return AuditResult(AuditOutcome.UNRESOLVED, sources)


def audit_registered_run(p0_root: str | Path) -> AuditResult:
    try:
        pairs = load_registered_pairs(p0_root)
        sources = tuple(
            SourceAudit(
                item.source_centre,
                measure_pair(item.coarse.cycle, item.coarse.branch, 10.0),
                measure_pair(
                    item.convergence.cycle, item.convergence.branch, 10.0
                ),
            )
            for item in pairs
        )
    except MetricError as error:
        return AuditResult(AuditOutcome.INVALID, (), (str(error),))
    return classify_audit(sources)
