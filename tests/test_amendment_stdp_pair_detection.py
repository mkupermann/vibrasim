"""Tests for STDP bridge identification (BS1-BS3 + supporting cases)."""
import numpy as np
from world.config import WorldConfig
from world.state import World
from world.physics import molecules_in_tube


def _make_world():
    cfg = WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=16, n_nodes_max=16,
        box_size=(100.0, 100.0, 100.0),
        r_bridge=5.0,
    )
    return World(cfg)


def test_molecule_in_tube_is_identified():
    w = _make_world()
    # Molecule on the line segment from (50,50,50) to (70,50,50)
    w.k_pos[0] = [60.0, 50.0, 50.0]
    w.k_level[0] = 5
    w.k_alive[0] = True
    w.k_count = 1
    A = np.array([50.0, 50.0, 50.0])
    B = np.array([70.0, 50.0, 50.0])
    indices = molecules_in_tube(w, A, B, 5.0)
    assert list(indices) == [0]


def test_molecule_outside_tube_is_excluded():
    w = _make_world()
    # Molecule perpendicular distance = 15, > r_bridge=5
    w.k_pos[0] = [60.0, 65.0, 50.0]
    w.k_level[0] = 5
    w.k_alive[0] = True
    w.k_count = 1
    A = np.array([50.0, 50.0, 50.0])
    B = np.array([70.0, 50.0, 50.0])
    indices = molecules_in_tube(w, A, B, 5.0)
    assert list(indices) == []


def test_molecule_beyond_segment_endpoints_is_excluded():
    """Projection scalar t must be in [0, 1]; molecules past either endpoint are out."""
    w = _make_world()
    # Molecule at (80,50,50) — beyond B=(70,50,50)
    w.k_pos[0] = [80.0, 50.0, 50.0]
    w.k_level[0] = 5
    w.k_alive[0] = True
    w.k_count = 1
    A = np.array([50.0, 50.0, 50.0])
    B = np.array([70.0, 50.0, 50.0])
    indices = molecules_in_tube(w, A, B, 5.0)
    assert list(indices) == []


def test_only_level_5_plus_molecules_are_candidates():
    """Atoms (level 4), pairs/triads (level 2/3) are not bridge candidates."""
    w = _make_world()
    # Three nodes on the line; only level >=5 should be picked
    for i, (level, pos) in enumerate([(4, [60.0, 50.0, 50.0]),
                                       (5, [62.0, 50.0, 50.0]),
                                       (6, [64.0, 50.0, 50.0])]):
        w.k_pos[i] = pos
        w.k_level[i] = level
        w.k_alive[i] = True
    w.k_count = 3
    A = np.array([50.0, 50.0, 50.0])
    B = np.array([70.0, 50.0, 50.0])
    indices = sorted(molecules_in_tube(w, A, B, 5.0).tolist())
    assert indices == [1, 2]


def test_dead_molecules_are_excluded():
    w = _make_world()
    w.k_pos[0] = [60.0, 50.0, 50.0]
    w.k_level[0] = 5
    w.k_alive[0] = False  # dead
    w.k_count = 1
    A = np.array([50.0, 50.0, 50.0])
    B = np.array([70.0, 50.0, 50.0])
    indices = molecules_in_tube(w, A, B, 5.0)
    assert list(indices) == []
