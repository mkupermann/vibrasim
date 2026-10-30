from dataclasses import replace

import numpy as np

from vibrasim2.p0.energy import (
    EnergyRecord,
    a_b,
    coupling_identity_residual,
    energy_record,
    max_material_energy_ratio,
    max_relative_energy_drift,
    run_trajectory,
)
from vibrasim2.p0.fixtures import initial_state
from vibrasim2.p0.types import (
    ChannelMode,
    P0Config,
    P0State,
    RunCell,
    RunPurpose,
    Topology,
)


SOURCE = (4, 16)


def cell(
    topology: Topology = Topology.CYCLE,
    mode: ChannelMode = ChannelMode.FULL,
    *,
    steps: int = 20,
) -> RunCell:
    return RunCell(topology, mode, RunPurpose.PRIMARY, SOURCE, 0.05, steps)


def test_decoupled_matter_energy_stays_zero():
    config = P0Config.registered()
    trajectory = run_trajectory(
        cell(mode=ChannelMode.DECOUPLED),
        config,
        initial_state(config, SOURCE),
    )

    assert all(record.h_matter == 0.0 for record in trajectory.records)


def test_cycle_and_branch_initial_totals_are_one():
    config = P0Config.registered()
    state = initial_state(config, SOURCE)

    for topology in (Topology.CYCLE, Topology.BRANCH):
        record = energy_record(state, cell(topology), config, tick=0)
        assert record.h_total is not None
        assert abs(record.h_total - 1.0) <= 1e-12


def test_record_and_snapshot_ticks_are_exact():
    config = replace(P0Config.registered(), steps=20)
    trajectory = run_trajectory(cell(steps=20), config, initial_state(config, SOURCE))

    assert tuple(record.tick for record in trajectory.records) == tuple(range(21))
    assert tuple(snapshot.tick for snapshot in trajectory.snapshots) == (0, 10, 20)
    assert tuple(record.simulation_time for record in trajectory.records) == tuple(
        tick * 0.05 for tick in range(21)
    )


def test_coupling_integral_uses_trapezoidal_endpoints():
    config = P0Config.registered()
    trajectory = run_trajectory(
        cell(steps=1), config, initial_state(config, SOURCE)
    )
    first, second = trajectory.records
    assert first.p_field_from_coupling is not None
    assert second.p_field_from_coupling is not None
    assert first.p_matter_from_coupling is not None
    assert second.p_matter_from_coupling is not None

    assert second.integral_field_power == 0.5 * 0.05 * (
        first.p_field_from_coupling + second.p_field_from_coupling
    )
    assert second.integral_matter_power == 0.5 * 0.05 * (
        first.p_matter_from_coupling + second.p_matter_from_coupling
    )


def test_nonfinite_state_records_failure_and_stops_trajectory():
    config = P0Config.registered()
    initial = initial_state(config, SOURCE)
    u = initial.u.copy()
    u[0, 0] = np.nan
    nonfinite = P0State(u, initial.p, initial.q, initial.r)

    trajectory = run_trajectory(cell(), config, nonfinite)

    assert len(trajectory.records) == 1
    assert trajectory.records[0].tick == 0
    assert not trajectory.records[0].finite
    assert trajectory.records[0].h_total is None
    assert tuple(snapshot.tick for snapshot in trajectory.snapshots) == (0,)
    assert np.isnan(trajectory.snapshots[0].state.u[0, 0])


def test_registered_trace_metrics_use_unrounded_values_and_exclude_tick_zero():
    records = (
        EnergyRecord(0, 0.0, 0.7, 0.2, 0.1, 1.0, 0.0, 0.0, 0.0, 0.0, True),
        EnergyRecord(1, 0.05, 0.6, 0.3, 0.1004, 1.0004, -0.2, 0.1, -0.005, 0.0025, True),
        EnergyRecord(2, 0.10, 0.5, 0.4, 0.1002, 1.0002, -0.1, 0.0, -0.012, 0.005, True),
    )

    np.testing.assert_allclose(max_relative_energy_drift(records), 0.0004, rtol=0.0, atol=1e-15)
    np.testing.assert_allclose(coupling_identity_residual(records), 0.0068, rtol=0.0, atol=1e-15)
    assert max_material_energy_ratio(records) == 0.4
    assert a_b(records) == 0.4


def test_a_b_does_not_allow_tick_zero_to_supply_the_peak():
    records = (
        EnergyRecord(0, 0.0, 0.0, 0.9, 0.1, 1.0, 0.0, 0.0, 0.0, 0.0, True),
        EnergyRecord(1, 0.05, 0.7, 0.2, 0.1, 1.0, 0.0, 0.0, 0.0, 0.0, True),
    )

    assert a_b(records) == 0.2
