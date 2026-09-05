"""Deterministic in-memory P2 trajectory and scientific trace values."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .dynamics import accounted_energy, registered_step
from .types import P2Cell, P2Config, P2State


@dataclass(frozen=True)
class P2EnergyRecord:
    tick: int
    simulation_time: float
    accounted_energy: float | None
    absolute_energy_drift: float | None
    reservoir_energy: float | None
    formation_sink: float | None
    live_bond_count: int
    bond_time: float | None
    finite: bool


@dataclass(frozen=True)
class P2Snapshot:
    tick: int
    simulation_time: float
    state: P2State


@dataclass(frozen=True)
class TimedBondEvent:
    tick: int
    simulation_time: float
    kind: str
    left: int
    right: int


@dataclass(frozen=True)
class P2Trajectory:
    cell: P2Cell
    records: tuple[P2EnergyRecord, ...]
    snapshots: tuple[P2Snapshot, ...]
    events: tuple[TimedBondEvent, ...]


def _finite(value: float) -> float | None:
    value = float(value)
    return value if math.isfinite(value) else None


def _record(
    state: P2State,
    cell: P2Cell,
    config: P2Config,
    tick: int,
    initial_energy: float | None,
) -> P2EnergyRecord:
    total = _finite(accounted_energy(state, cell.arm, config))
    reservoir = _finite(np.asarray(state.reservoirs, dtype=np.float64).sum())
    sink = _finite(state.formation_sink)
    bond_time = _finite(state.bond_time)
    drift = (
        _finite(abs(total - initial_energy))
        if total is not None and initial_energy is not None
        else None
    )
    finite = all(value is not None for value in (total, drift, reservoir, sink, bond_time))
    return P2EnergyRecord(
        tick=tick,
        simulation_time=tick * cell.dt,
        accounted_energy=total,
        absolute_energy_drift=drift,
        reservoir_energy=reservoir,
        formation_sink=sink,
        live_bond_count=len(state.bonds),
        bond_time=bond_time,
        finite=finite,
    )


def run_trajectory(
    cell: P2Cell, config: P2Config, initial: P2State
) -> P2Trajectory:
    """Run one cell while retaining every ledger tick and registered frame."""
    initial_total = _finite(accounted_energy(initial, cell.arm, config))
    records = [_record(initial, cell, config, 0, initial_total)]
    snapshots = [P2Snapshot(0, 0.0, initial)]
    events: list[TimedBondEvent] = []
    if not records[0].finite:
        return P2Trajectory(cell, tuple(records), tuple(snapshots), ())

    state = initial
    for tick in range(1, cell.steps + 1):
        state, step_events = registered_step(state, cell.arm, config, dt=cell.dt)
        for event in step_events:
            events.append(
                TimedBondEvent(
                    tick=tick,
                    simulation_time=tick * cell.dt,
                    kind=event.kind,
                    left=event.left,
                    right=event.right,
                )
            )
        record = _record(state, cell, config, tick, initial_total)
        records.append(record)
        if tick % config.frame_stride == 0 or tick == cell.steps or not record.finite:
            snapshots.append(P2Snapshot(tick, tick * cell.dt, state))
        if not record.finite:
            break
    return P2Trajectory(cell, tuple(records), tuple(snapshots), tuple(events))

