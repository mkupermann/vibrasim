import numpy as np
import pytest

from vibrasim2.p2.fixtures import candidate_edges, registered_cells
from vibrasim2.p2.types import Bond, P2Arm, P2Config, P2Purpose, P2State


def test_registered_configuration_is_exact():
    config = P2Config.registered()

    assert config.grid_shape == (32, 32)
    assert config.candidate_radius == 4.5
    assert config.c == 1.0
    assert config.g == 1.0
    assert config.k_m == 0.5
    assert config.k_f == 0.25
    assert config.capture_fraction == 0.25
    assert config.formation_cost == 0.02
    assert config.bond_lifetime == 10.0
    assert config.dt == 0.025
    assert config.steps == 4000
    assert config.source_centres == ((4, 16), (16, 4), (4, 4))
    assert config.frame_stride == 10


def test_registered_configuration_rejects_a_changed_value():
    config = P2Config.registered()
    changed = P2Config(**{**config.__dict__, "formation_cost": 0.01})

    with pytest.raises(ValueError, match="registered P2 configuration"):
        changed.assert_registered()


def test_candidates_come_from_radius_and_are_lexicographic():
    assert candidate_edges(P2Config.registered()) == (
        (0, 1), (0, 5), (1, 2), (2, 3), (3, 4), (4, 5)
    )


def test_bond_rejects_invalid_local_state():
    with pytest.raises(ValueError, match="ordered distinct endpoints"):
        Bond(1, 1, age=0.0, matter_rest=0.0, field_rest=0.0)
    with pytest.raises(ValueError, match="non-negative finite age"):
        Bond(0, 1, age=float("nan"), matter_rest=0.0, field_rest=0.0)


def test_state_copies_arrays_and_rejects_duplicate_bonds():
    config = P2Config.registered()
    u = np.zeros(config.grid_shape)
    state = P2State(
        u=u,
        p=np.zeros(config.grid_shape),
        q=np.zeros(6),
        r=np.zeros(6),
        reservoirs=np.zeros(6),
        bonds=(Bond(0, 1, 0.0, 0.0, 0.0),),
        formation_sink=0.0,
        bond_time=0.0,
    )
    u[0, 0] = 1.0

    assert state.u[0, 0] == 0.0
    assert not state.u.flags.writeable
    with pytest.raises(ValueError, match="duplicate bond"):
        P2State(
            u=state.u, p=state.p, q=state.q, r=state.r,
            reservoirs=state.reservoirs,
            bonds=(state.bonds[0], state.bonds[0]),
            formation_sink=0.0, bond_time=0.0,
        )


def test_state_rejects_negative_reservoir_and_nonfinite_accounting():
    config = P2Config.registered()
    base = dict(
        u=np.zeros(config.grid_shape), p=np.zeros(config.grid_shape),
        q=np.zeros(6), r=np.zeros(6), bonds=(), formation_sink=0.0,
        bond_time=0.0,
    )
    with pytest.raises(ValueError, match="reservoirs"):
        P2State(**base, reservoirs=np.array([-1.0, 0, 0, 0, 0, 0]))
    with pytest.raises(ValueError, match="formation_sink"):
        P2State(**{**base, "formation_sink": float("inf")}, reservoirs=np.zeros(6))


def test_arm_names_are_scientific_contract():
    assert tuple(arm.value for arm in P2Arm) == (
        "full", "no_capture", "no_field_feedback"
    )


def test_registered_matrix_has_exact_18_unique_cells():
    config = P2Config.registered()
    cells = registered_cells(config)

    assert len(cells) == 18
    assert len({cell.slug for cell in cells}) == 18
    for source in config.source_centres:
        source_cells = tuple(cell for cell in cells if cell.source_centre == source)
        assert tuple((cell.purpose, cell.arm) for cell in source_cells) == (
            (P2Purpose.PRIMARY, P2Arm.FULL),
            (P2Purpose.PRIMARY, P2Arm.NO_CAPTURE),
            (P2Purpose.PRIMARY, P2Arm.NO_FIELD_FEEDBACK),
            (P2Purpose.CONVERGENCE, P2Arm.FULL),
            (P2Purpose.CONVERGENCE, P2Arm.NO_FIELD_FEEDBACK),
            (P2Purpose.REPRODUCTION, P2Arm.FULL),
        )
        assert source_cells[3].dt == config.dt / 2
        assert source_cells[3].steps == config.steps * 2
