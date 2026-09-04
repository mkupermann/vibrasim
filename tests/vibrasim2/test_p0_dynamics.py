import numpy as np

from vibrasim2.p0.dynamics import forces, periodic_laplacian, velocity_verlet_step
from vibrasim2.p0.energy import energy_record
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
    purpose: RunPurpose = RunPurpose.PRIMARY,
    *,
    steps: int = 20,
) -> RunCell:
    return RunCell(topology, mode, purpose, SOURCE, 0.05, steps)


def with_coordinate(
    state: P0State,
    component: str,
    index: tuple[int, ...],
    delta: float,
) -> P0State:
    arrays = {
        "u": state.u.copy(),
        "p": state.p.copy(),
        "q": state.q.copy(),
        "r": state.r.copy(),
    }
    arrays[component][index] += delta
    return P0State(arrays["u"], arrays["p"], arrays["q"], arrays["r"])


def potential(record) -> float:
    assert record.h_field is not None
    assert record.h_matter is not None
    assert record.h_coupling is not None
    return record.h_field + record.h_matter + record.h_coupling


def test_periodic_laplacian_wraps_both_axes():
    u = np.zeros((4, 4), dtype=np.float64)
    u[0, 0] = 1.0
    expected = np.zeros((4, 4), dtype=np.float64)
    expected[0, 0] = -4.0
    expected[1, 0] = expected[3, 0] = 1.0
    expected[0, 1] = expected[0, 3] = 1.0

    np.testing.assert_array_equal(periodic_laplacian(u), expected)


def test_zero_state_is_a_fixed_point():
    config = P0Config.registered()
    zero = P0State(
        np.zeros((32, 32)), np.zeros((32, 32)), np.zeros(6), np.zeros(6)
    )

    stepped = velocity_verlet_step(zero, cell(), config)

    np.testing.assert_array_equal(stepped.u, zero.u)
    np.testing.assert_array_equal(stepped.p, zero.p)
    np.testing.assert_array_equal(stepped.q, zero.q)
    np.testing.assert_array_equal(stepped.r, zero.r)


def test_broken_pair_omits_only_the_field_reaction():
    config = P0Config.registered()
    state = initial_state(config, SOURCE)
    full_force = forces(state, cell(), config)
    broken_force = forces(
        state,
        cell(mode=ChannelMode.BROKEN_PAIR, purpose=RunPurpose.SENSITIVITY),
        config,
    )

    np.testing.assert_array_equal(full_force.matter, broken_force.matter)
    assert not np.array_equal(full_force.field, broken_force.field)


def test_field_force_matches_finite_difference_h_f_and_h_c():
    config = P0Config.registered()
    state = initial_state(config, SOURCE)
    epsilon = 1e-7
    coordinate = (13, 16)
    plus = with_coordinate(state, "u", coordinate, epsilon)
    minus = with_coordinate(state, "u", coordinate, -epsilon)
    numerical_gradient = (
        potential(energy_record(plus, cell(), config, tick=0))
        - potential(energy_record(minus, cell(), config, tick=0))
    ) / (2.0 * epsilon)

    np.testing.assert_allclose(
        forces(state, cell(), config).field[coordinate],
        -numerical_gradient,
        rtol=1e-6,
        atol=1e-8,
    )


def test_matter_force_matches_finite_difference_h_m_and_h_c():
    config = P0Config.registered()
    state = initial_state(config, SOURCE)
    epsilon = 1e-7
    plus = with_coordinate(state, "q", (0,), epsilon)
    minus = with_coordinate(state, "q", (0,), -epsilon)
    numerical_gradient = (
        potential(energy_record(plus, cell(), config, tick=0))
        - potential(energy_record(minus, cell(), config, tick=0))
    ) / (2.0 * epsilon)

    np.testing.assert_allclose(
        forces(state, cell(), config).matter[0],
        -numerical_gradient,
        rtol=1e-6,
        atol=1e-8,
    )


def test_velocity_verlet_uses_cell_timestep_without_mutating_input():
    config = P0Config.registered()
    state = initial_state(config, SOURCE)
    before = tuple(array.copy() for array in (state.u, state.p, state.q, state.r))

    stepped = velocity_verlet_step(state, cell(), config)

    for actual, expected in zip((state.u, state.p, state.q, state.r), before, strict=True):
        np.testing.assert_array_equal(actual, expected)
    assert stepped is not state
    assert stepped.u.dtype == np.float64
    assert stepped.q.dtype == np.float64
