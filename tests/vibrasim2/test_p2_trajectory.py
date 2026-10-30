from dataclasses import replace

import numpy as np

from vibrasim2.p2.dynamics import accounted_energy, initial_state
from vibrasim2.p2.trajectory import run_trajectory
from vibrasim2.p2.types import P2Arm, P2Cell, P2Config, P2Purpose


SOURCE = (4, 16)


def short_cell(arm=P2Arm.FULL, *, steps=12, dt=0.025):
    return P2Cell(arm, P2Purpose.PRIMARY, SOURCE, dt, steps)


def test_trajectory_records_every_tick_and_registered_frame_cadence():
    config = replace(P2Config.registered(), frame_stride=5)
    initial = initial_state(config, SOURCE)

    trajectory = run_trajectory(short_cell(steps=12), config, initial)

    assert [record.tick for record in trajectory.records] == list(range(13))
    assert [snapshot.tick for snapshot in trajectory.snapshots] == [0, 5, 10, 12]
    assert trajectory.records[0].accounted_energy == accounted_energy(
        initial, P2Arm.FULL, config
    )
    assert all(record.finite for record in trajectory.records)


def test_trajectory_timestamps_events_and_integrates_bond_time():
    config = replace(
        P2Config.registered(), formation_cost=0.0, bond_lifetime=0.05,
        frame_stride=1,
    )
    initial = initial_state(config, SOURCE)

    trajectory = run_trajectory(short_cell(steps=4, dt=0.025), config, initial)

    assert [(event.tick, event.kind) for event in trajectory.events] == [
        *( (1, "formed") for _ in range(6) ),
        *( (3, "expired") for _ in range(6) ),
        *( (3, "formed") for _ in range(6) ),
    ]
    assert trajectory.records[-1].bond_time == 6 * 0.025 * 3


def test_identical_short_runs_have_identical_discrete_events_and_metrics():
    config = replace(P2Config.registered(), frame_stride=5)
    cell = short_cell(steps=20)

    first = run_trajectory(cell, config, initial_state(config, SOURCE))
    second = run_trajectory(cell, config, initial_state(config, SOURCE))

    assert first.events == second.events
    assert first.records == second.records


def test_nonfinite_state_stops_with_invalid_record_instead_of_continuing():
    config = replace(P2Config.registered(), frame_stride=1)
    initial = initial_state(config, SOURCE)
    unsafe_u = initial.u.copy()
    unsafe_u[0, 0] = 1e308
    initial = object.__new__(type(initial))
    for name, value in {
        "u": unsafe_u, "p": np.zeros(config.grid_shape),
        "q": np.zeros(6), "r": np.zeros(6), "reservoirs": np.zeros(6),
        "bonds": (), "formation_sink": 0.0, "bond_time": 0.0,
    }.items():
        object.__setattr__(initial, name, value)

    trajectory = run_trajectory(short_cell(steps=3), config, initial)

    assert len(trajectory.records) == 1
    assert trajectory.records[0].finite is False
