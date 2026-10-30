"""Frozen V2-P2 evidence construction and verdict precedence."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .fixtures import registered_cells
from .trajectory import TimedBondEvent
from .types import P2Arm, P2Cell, P2Config, P2Purpose, Verdict


@dataclass(frozen=True)
class CellOutcome:
    cell: P2Cell
    bond_time: float
    max_absolute_energy_drift: float
    finite: bool
    events: tuple[TimedBondEvent, ...]


@dataclass(frozen=True)
class P2Evidence:
    artifact_valid: bool
    all_values_finite: bool
    primary_contrast: float
    convergence_contrast: float
    convergence_relative_error: float | None
    scientific_contrast_holds: bool
    negative_control_holds: bool
    convergence_holds: bool
    reproduction_holds: bool
    energy_holds: bool


def _invalid_evidence() -> P2Evidence:
    return P2Evidence(
        artifact_valid=False,
        all_values_finite=False,
        primary_contrast=0.0,
        convergence_contrast=0.0,
        convergence_relative_error=None,
        scientific_contrast_holds=False,
        negative_control_holds=False,
        convergence_holds=False,
        reproduction_holds=False,
        energy_holds=False,
    )


def _same_sign(left: float, right: float) -> bool:
    return (left == 0.0 and right == 0.0) or (left > 0 and right > 0) or (left < 0 and right < 0)


def build_evidence(
    outcomes: tuple[CellOutcome, ...], config: P2Config
) -> P2Evidence:
    """Evaluate only the registered matrix and thresholds."""
    expected = registered_cells(config)
    if len(outcomes) != len(expected):
        return _invalid_evidence()
    by_slug = {outcome.cell.slug: outcome for outcome in outcomes}
    if len(by_slug) != len(expected) or set(by_slug) != {cell.slug for cell in expected}:
        return _invalid_evidence()
    ordered = tuple(by_slug[cell.slug] for cell in expected)
    numeric_finite = all(
        outcome.finite
        and math.isfinite(outcome.bond_time)
        and math.isfinite(outcome.max_absolute_energy_drift)
        for outcome in ordered
    )

    def get(purpose: P2Purpose, arm: P2Arm, source: tuple[int, int]) -> CellOutcome:
        return next(
            outcome for outcome in ordered
            if outcome.cell.purpose is purpose
            and outcome.cell.arm is arm
            and outcome.cell.source_centre == source
        )

    primary = sum(
        get(P2Purpose.PRIMARY, P2Arm.FULL, source).bond_time
        - get(P2Purpose.PRIMARY, P2Arm.NO_FIELD_FEEDBACK, source).bond_time
        for source in config.source_centres
    )
    convergence = sum(
        get(P2Purpose.CONVERGENCE, P2Arm.FULL, source).bond_time
        - get(P2Purpose.CONVERGENCE, P2Arm.NO_FIELD_FEEDBACK, source).bond_time
        for source in config.source_centres
    )
    if primary == 0.0:
        relative_error = 0.0 if convergence == 0.0 else None
    else:
        relative_error = abs(convergence - primary) / abs(primary)
    convergence_holds = (
        relative_error is not None
        and relative_error <= 0.20
        and _same_sign(primary, convergence)
    )
    reproduction_holds = all(
        abs(
            get(P2Purpose.PRIMARY, P2Arm.FULL, source).bond_time
            - get(P2Purpose.REPRODUCTION, P2Arm.FULL, source).bond_time
        ) <= 1e-12
        and get(P2Purpose.PRIMARY, P2Arm.FULL, source).events
        == get(P2Purpose.REPRODUCTION, P2Arm.FULL, source).events
        for source in config.source_centres
    )
    return P2Evidence(
        artifact_valid=True,
        all_values_finite=numeric_finite,
        primary_contrast=float(primary),
        convergence_contrast=float(convergence),
        convergence_relative_error=relative_error,
        scientific_contrast_holds=primary >= 3.0 * config.bond_lifetime,
        negative_control_holds=all(
            get(P2Purpose.PRIMARY, P2Arm.NO_CAPTURE, source).bond_time == 0.0
            for source in config.source_centres
        ),
        convergence_holds=convergence_holds,
        reproduction_holds=reproduction_holds,
        energy_holds=all(
            outcome.max_absolute_energy_drift <= config.energy_tolerance
            for outcome in ordered
        ),
    )


def decide_verdict(evidence: P2Evidence) -> Verdict:
    if not evidence.artifact_valid:
        return Verdict.FAIL
    numerical = (
        evidence.all_values_finite
        and evidence.convergence_holds
        and evidence.reproduction_holds
        and evidence.energy_holds
    )
    if not numerical:
        return Verdict.INCONCLUSIVE
    if evidence.scientific_contrast_holds and evidence.negative_control_holds:
        return Verdict.PASS
    return Verdict.NULL

