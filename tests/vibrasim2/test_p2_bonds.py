import numpy as np

from vibrasim2.p0.fixtures import coupling_sites
from vibrasim2.p2.bonds import (
    age_and_expire_bonds,
    bond_forces,
    bond_spring_energy,
    capture_positive_work,
    form_eligible_bonds,
)
from vibrasim2.p2.types import Bond, P2Arm, P2Config, P2State


def state_with(*, r=None, reservoirs=None, bonds=(), q=None, u=None):
    config = P2Config.registered()
    return P2State(
        u=np.zeros(config.grid_shape) if u is None else u,
        p=np.zeros(config.grid_shape),
        q=np.zeros(6) if q is None else q,
        r=np.zeros(6) if r is None else r,
        reservoirs=np.zeros(6) if reservoirs is None else reservoirs,
        bonds=bonds,
        formation_sink=0.0,
        bond_time=0.0,
    )


def test_capture_debits_exact_kinetic_energy_and_ignores_negative_work():
    state = state_with(r=np.array([2.0, -1.0, 0, 0, 0, 0]))
    updated, captured = capture_positive_work(
        state, coupling_force=np.array([1.0, 1.0, 0, 0, 0, 0]),
        dt=0.5, fraction=0.25,
    )

    assert captured == 0.25
    np.testing.assert_allclose(updated.reservoirs, [0.25, 0, 0, 0, 0, 0])
    assert 0.5 * (state.r @ state.r - updated.r @ updated.r) == captured
    assert updated.r[1] == -1.0


def test_capture_is_bounded_by_available_local_kinetic_energy():
    state = state_with(r=np.array([0.1, 0, 0, 0, 0, 0]))
    updated, captured = capture_positive_work(
        state, coupling_force=np.array([100.0, 0, 0, 0, 0, 0]),
        dt=1.0, fraction=1.0,
    )

    assert captured == 0.005000000000000001
    assert updated.r[0] == 0.0
    assert updated.reservoirs[0] == captured


def test_formation_is_paid_local_deterministic_and_zero_spring_energy():
    config = P2Config.registered()
    q = np.arange(6, dtype=float) / 10
    u = np.zeros(config.grid_shape)
    sites = coupling_sites()
    u[sites[:, 0], sites[:, 1]] = np.arange(6, dtype=float) / 20
    state = state_with(q=q, u=u, reservoirs=np.full(6, 0.02))

    updated, events = form_eligible_bonds(state, config)

    assert tuple((b.left, b.right) for b in updated.bonds) == (
        (0, 1), (0, 5), (1, 2), (2, 3), (3, 4), (4, 5)
    )
    np.testing.assert_allclose(updated.reservoirs, np.zeros(6), atol=1e-15)
    assert updated.formation_sink == 0.12
    assert tuple((e.kind, e.left, e.right) for e in events) == tuple(
        ("formed", b.left, b.right) for b in updated.bonds
    )
    assert sum(bond_spring_energy(updated, b, config) for b in updated.bonds) == 0.0


def test_formation_requires_each_endpoint_half_cost_and_respects_valence():
    config = P2Config.registered()
    poor = state_with(reservoirs=np.array([0.02, 0.009, 0.02, 0.02, 0.02, 0.02]))
    updated, _ = form_eligible_bonds(poor, config)
    assert all(1 not in (bond.left, bond.right) for bond in updated.bonds)
    assert max(sum(node in (b.left, b.right) for b in updated.bonds) for node in range(6)) <= 2


def test_expiry_returns_instantaneous_spring_potential_to_endpoints():
    config = P2Config.registered()
    sites = coupling_sites()
    u = np.zeros(config.grid_shape)
    u[tuple(sites[1])] = 2.0
    state = state_with(
        q=np.array([0.0, 1.0, 0, 0, 0, 0]), u=u,
        bonds=(Bond(0, 1, 9.99, matter_rest=0.0, field_rest=0.0),),
    )
    expected = 0.5 * config.k_m * 1.0**2 + 0.5 * config.k_f * 2.0**2

    updated, events = age_and_expire_bonds(state, config, dt=0.02)

    assert updated.bonds == ()
    np.testing.assert_allclose(updated.reservoirs[:2], [expected / 2, expected / 2])
    assert updated.bond_time == 0.02
    assert [(e.kind, e.left, e.right) for e in events] == [("expired", 0, 1)]


def test_bond_forces_are_antisymmetric_and_control_removes_only_field_term():
    config = P2Config.registered()
    sites = coupling_sites()
    u = np.zeros(config.grid_shape)
    u[tuple(sites[1])] = 2.0
    state = state_with(
        q=np.array([0.0, 1.0, 0, 0, 0, 0]), u=u,
        bonds=(Bond(0, 1, 1.0, matter_rest=0.0, field_rest=0.0),),
    )

    full_field, full_matter = bond_forces(state, P2Arm.FULL, config)
    control_field, control_matter = bond_forces(state, P2Arm.NO_FIELD_FEEDBACK, config)

    assert full_matter.sum() == 0.0
    assert full_field.sum() == 0.0
    np.testing.assert_array_equal(control_matter, full_matter)
    np.testing.assert_array_equal(control_field, np.zeros(config.grid_shape))

