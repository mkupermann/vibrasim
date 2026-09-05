from dataclasses import replace

import numpy as np

from vibrasim2.p0.fixtures import coupling_sites
from vibrasim2.p2.dynamics import (
    accounted_energy,
    forces,
    initial_state,
    registered_step,
)
from vibrasim2.p2.types import Bond, P2Arm, P2Config


SOURCE = (4, 16)


def test_initial_state_has_exact_normalized_accounted_energy():
    config = P2Config.registered()

    state = initial_state(config, SOURCE)

    np.testing.assert_allclose(
        accounted_energy(state, P2Arm.FULL, config), 1.0, rtol=0, atol=2e-15
    )
    assert state.bonds == ()
    np.testing.assert_array_equal(state.reservoirs, np.zeros(6))


def test_zero_state_is_fixed_without_funded_bonds():
    config = P2Config.registered()
    state = initial_state(config, SOURCE)
    zero = replace(
        state,
        u=np.zeros(config.grid_shape), p=np.zeros(config.grid_shape),
        q=np.zeros(6), r=np.zeros(6),
    )

    stepped, events = registered_step(zero, P2Arm.FULL, config, dt=config.dt)

    np.testing.assert_array_equal(stepped.u, zero.u)
    np.testing.assert_array_equal(stepped.p, zero.p)
    np.testing.assert_array_equal(stepped.q, zero.q)
    np.testing.assert_array_equal(stepped.r, zero.r)
    assert stepped.bonds == ()
    assert events == ()


def test_no_capture_arm_cannot_fund_bonds():
    config = P2Config.registered()
    state = initial_state(config, SOURCE)

    for _ in range(100):
        state, events = registered_step(state, P2Arm.NO_CAPTURE, config, dt=config.dt)
        assert not events

    np.testing.assert_array_equal(state.reservoirs, np.zeros(6))
    assert state.bonds == ()
    assert state.formation_sink == 0.0


def test_live_bond_force_matches_registered_potential_gradient():
    config = P2Config.registered()
    state = initial_state(config, SOURCE)
    sites = coupling_sites()
    bond = Bond(0, 1, age=1.0, matter_rest=0.0, field_rest=0.0)
    state = replace(state, bonds=(bond,))
    epsilon = 1e-7
    plus_q = state.q.copy()
    minus_q = state.q.copy()
    plus_q[0] += epsilon
    minus_q[0] -= epsilon
    numerical = (
        accounted_energy(replace(state, q=plus_q), P2Arm.FULL, config)
        - accounted_energy(replace(state, q=minus_q), P2Arm.FULL, config)
    ) / (2 * epsilon)

    np.testing.assert_allclose(
        forces(state, P2Arm.FULL, config).matter[0], -numerical, rtol=1e-6, atol=1e-8
    )
    assert tuple(sites[0]) != tuple(sites[1])


def test_short_no_capture_trajectory_stays_within_registered_energy_tolerance():
    config = P2Config.registered()
    state = initial_state(config, SOURCE)
    initial = accounted_energy(state, P2Arm.NO_CAPTURE, config)
    maximum = 0.0

    for _ in range(200):
        state, _ = registered_step(state, P2Arm.NO_CAPTURE, config, dt=config.dt)
        maximum = max(maximum, abs(accounted_energy(state, P2Arm.NO_CAPTURE, config) - initial))

    assert maximum <= config.energy_tolerance
