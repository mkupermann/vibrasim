from dataclasses import replace

import numpy as np

from vibrasim2.p0.fixtures import (
    coupling_sites,
    edges_for,
    initial_state,
    omega_upper,
    reproduction_cells,
    registered_stage_a_cells,
)
from vibrasim2.p0.types import ChannelMode, P0Config, RunCell, RunPurpose, Topology


def test_registered_sites_and_edges_are_exact():
    np.testing.assert_array_equal(
        coupling_sites(),
        np.array(((13, 16), (14, 13), (18, 13), (19, 16), (18, 19), (14, 19))),
    )
    np.testing.assert_array_equal(
        edges_for(Topology.CYCLE),
        np.array(((0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0))),
    )
    np.testing.assert_array_equal(
        edges_for(Topology.BRANCH),
        np.array(((0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5))),
    )


def test_stage_a_matrix_contains_only_registered_cells():
    config = P0Config.registered()
    cells = registered_stage_a_cells(config)
    expected = []
    for source in config.source_centres:
        expected.extend(
            (
                RunCell(Topology.CYCLE, ChannelMode.FULL, RunPurpose.PRIMARY, source, 0.05, 2000),
                RunCell(Topology.BRANCH, ChannelMode.FULL, RunPurpose.PRIMARY, source, 0.05, 2000),
                RunCell(Topology.CYCLE, ChannelMode.NO_BONDS, RunPurpose.PRIMARY, source, 0.05, 2000),
                RunCell(Topology.CYCLE, ChannelMode.DECOUPLED, RunPurpose.PRIMARY, source, 0.05, 2000),
                RunCell(Topology.CYCLE, ChannelMode.BROKEN_PAIR, RunPurpose.SENSITIVITY, source, 0.05, 2000),
                RunCell(Topology.BRANCH, ChannelMode.BROKEN_PAIR, RunPurpose.SENSITIVITY, source, 0.05, 2000),
                RunCell(Topology.CYCLE, ChannelMode.FULL, RunPurpose.CONVERGENCE, source, 0.025, 4000),
                RunCell(Topology.BRANCH, ChannelMode.FULL, RunPurpose.CONVERGENCE, source, 0.025, 4000),
            )
        )
    assert cells == tuple(expected)


def test_reproduction_matrix_is_exact():
    config = P0Config.registered()
    assert reproduction_cells(config) == tuple(
        RunCell(topology, ChannelMode.FULL, RunPurpose.REPRODUCTION, source, 0.05, 2000)
        for source in config.source_centres
        for topology in (Topology.CYCLE, Topology.BRANCH)
    )


def test_initial_state_is_deterministic_mean_zero_and_read_only():
    config = P0Config.registered()
    first = initial_state(config, (4, 16))
    second = initial_state(config, (4, 16))
    np.testing.assert_array_equal(first.u, second.u)
    assert abs(float(first.u.mean())) < 1e-15
    assert first.u.dtype == np.float64
    assert not first.u.flags.writeable
    assert not first.p.flags.writeable
    assert not first.q.flags.writeable
    assert not first.r.flags.writeable
    with np.testing.assert_raises(ValueError):
        first.u[0, 0] = 3.0


def test_initial_cycle_energy_is_one_by_direct_scaling():
    config = P0Config.registered()
    state = initial_state(config, (4, 16))
    gradient = 0.5 * config.c**2 * (
        np.square(np.roll(state.u, -1, axis=0) - state.u).sum()
        + np.square(np.roll(state.u, -1, axis=1) - state.u).sum()
    )
    sites = coupling_sites()
    coupling = 0.5 * config.g * np.square(state.u[sites[:, 0], sites[:, 1]]).sum()

    assert abs(float(gradient + coupling) - 1.0) <= 1e-12


def test_registered_stability_bound_holds_and_invalid_config_is_rejected():
    config = P0Config.registered()
    assert config.dt * omega_upper(config, Topology.BRANCH) < 0.25
    with np.testing.assert_raises_regex(ValueError, "registered P0 configuration"):
        replace(config, g=1.1).assert_registered()
