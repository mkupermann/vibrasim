"""Energy ledger, trajectories, and registered trace metrics for P0."""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from typing import Iterable

import numpy as np

from .dynamics import velocity_verlet_step
from .fixtures import coupling_sites, edges_for
from .types import ChannelMode, P0Config, P0State, P0StateSnapshot, RunCell


@dataclass(frozen=True)
class EnergyRecord:
    tick: int
    simulation_time: float
    h_field: float | None
    h_matter: float | None
    h_coupling: float | None
    h_total: float | None
    p_field_from_coupling: float | None
    p_matter_from_coupling: float | None
    integral_field_power: float | None
    integral_matter_power: float | None
    finite: bool


@dataclass(frozen=True)
class Trajectory:
    cell: RunCell
    records: tuple[EnergyRecord, ...]
    snapshots: tuple[P0StateSnapshot, ...]


def _finite_or_none(value: float) -> float | None:
    result = float(value)
    return result if math.isfinite(result) else None


def energy_record(
    state: P0State,
    cell: RunCell,
    config: P0Config,
    tick: int,
    integral_field_power: float = 0.0,
    integral_matter_power: float = 0.0,
) -> EnergyRecord:
    """Evaluate all persisted energy and coupling-power scalars for one tick."""

    if tick < 0:
        raise ValueError("energy-record tick must be non-negative")

    sites = coupling_sites()
    field_kinetic = 0.5 * np.square(state.p).sum()
    field_gradient = 0.5 * config.c**2 * (
        np.square(np.roll(state.u, -1, axis=0) - state.u).sum()
        + np.square(np.roll(state.u, -1, axis=1) - state.u).sum()
    )
    h_field = _finite_or_none(field_kinetic + field_gradient)

    matter_spring = 0.0
    if cell.mode is not ChannelMode.NO_BONDS:
        edges = edges_for(cell.topology)
        differences = state.q[edges[:, 0]] - state.q[edges[:, 1]]
        matter_spring = 0.5 * config.k_b * np.square(differences).sum()
    h_matter = _finite_or_none(0.5 * np.square(state.r).sum() + matter_spring)

    coupling_g = 0.0 if cell.mode is ChannelMode.DECOUPLED else config.g
    mismatch = state.u[sites[:, 0], sites[:, 1]] - state.q
    h_coupling = _finite_or_none(0.5 * coupling_g * np.square(mismatch).sum())

    if h_field is None or h_matter is None or h_coupling is None:
        h_total = None
    else:
        h_total = _finite_or_none(h_field + h_matter + h_coupling)

    matter_coupling_force = coupling_g * mismatch
    field_coupling_force = (
        np.zeros_like(mismatch)
        if cell.mode is ChannelMode.BROKEN_PAIR
        else -coupling_g * mismatch
    )
    p_field = _finite_or_none(
        np.dot(state.p[sites[:, 0], sites[:, 1]], field_coupling_force)
    )
    p_matter = _finite_or_none(np.dot(state.r, matter_coupling_force))
    integral_field = _finite_or_none(integral_field_power)
    integral_matter = _finite_or_none(integral_matter_power)

    values = (
        h_field,
        h_matter,
        h_coupling,
        h_total,
        p_field,
        p_matter,
        integral_field,
        integral_matter,
    )
    finite = all(value is not None for value in values)
    return EnergyRecord(
        tick=tick,
        simulation_time=tick * cell.dt,
        h_field=h_field,
        h_matter=h_matter,
        h_coupling=h_coupling,
        h_total=h_total,
        p_field_from_coupling=p_field,
        p_matter_from_coupling=p_matter,
        integral_field_power=integral_field,
        integral_matter_power=integral_matter,
        finite=finite,
    )


def run_trajectory(
    cell: RunCell,
    config: P0Config,
    initial: P0State,
) -> Trajectory:
    """Run one deterministic cell, retaining every ledger tick and registered frame."""

    records: list[EnergyRecord] = []
    snapshots: list[P0StateSnapshot] = []
    state = initial
    field_integral = 0.0
    matter_integral = 0.0

    current = energy_record(state, cell, config, tick=0)
    records.append(current)
    snapshots.append(P0StateSnapshot(0, 0.0, state))
    if not current.finite:
        return Trajectory(cell, tuple(records), tuple(snapshots))

    for tick in range(1, cell.steps + 1):
        state = velocity_verlet_step(state, cell, config)
        measured = energy_record(state, cell, config, tick=tick)
        if (
            measured.p_field_from_coupling is not None
            and measured.p_matter_from_coupling is not None
            and current.p_field_from_coupling is not None
            and current.p_matter_from_coupling is not None
        ):
            field_integral += 0.5 * cell.dt * (
                current.p_field_from_coupling + measured.p_field_from_coupling
            )
            matter_integral += 0.5 * cell.dt * (
                current.p_matter_from_coupling + measured.p_matter_from_coupling
            )
            measured = replace(
                measured,
                integral_field_power=field_integral,
                integral_matter_power=matter_integral,
            )
        else:
            measured = replace(
                measured,
                integral_field_power=None,
                integral_matter_power=None,
                finite=False,
            )

        records.append(measured)
        if tick % config.frame_stride == 0 or not measured.finite:
            snapshots.append(P0StateSnapshot(tick, tick * cell.dt, state))
        if not measured.finite:
            break
        current = measured

    return Trajectory(cell, tuple(records), tuple(snapshots))


def _records_tuple(records: Iterable[EnergyRecord]) -> tuple[EnergyRecord, ...]:
    result = tuple(records)
    if not result or result[0].h_total is None or result[0].h_total <= 0:
        raise ValueError("trace requires a positive finite initial total energy")
    if any(not record.finite for record in result):
        raise ValueError("trace metrics require finite energy records")
    return result


def max_relative_energy_drift(records: Iterable[EnergyRecord]) -> float:
    trace = _records_tuple(records)
    initial = trace[0].h_total
    assert initial is not None
    totals = (record.h_total for record in trace)
    return max(abs(total - initial) / initial for total in totals if total is not None)


def coupling_identity_residual(records: Iterable[EnergyRecord]) -> float:
    trace = _records_tuple(records)
    initial_total = trace[0].h_total
    initial_coupling = trace[0].h_coupling
    assert initial_total is not None and initial_coupling is not None
    residuals = []
    for record in trace:
        assert record.h_coupling is not None
        assert record.integral_field_power is not None
        assert record.integral_matter_power is not None
        residuals.append(
            abs(
                record.h_coupling
                - initial_coupling
                + record.integral_field_power
                + record.integral_matter_power
            )
            / initial_total
        )
    return max(residuals)


def max_material_energy_ratio(records: Iterable[EnergyRecord]) -> float:
    trace = _records_tuple(records)
    initial = trace[0].h_total
    assert initial is not None
    return max(
        record.h_matter / initial
        for record in trace
        if record.h_matter is not None
    )


def a_b(records: Iterable[EnergyRecord]) -> float:
    trace = _records_tuple(records)
    initial = trace[0].h_total
    assert initial is not None
    post_initial = [record for record in trace if record.tick > 0]
    if not post_initial:
        raise ValueError("A_B requires at least one post-initial record")
    return max(
        record.h_matter / initial
        for record in post_initial
        if record.h_matter is not None
    )
