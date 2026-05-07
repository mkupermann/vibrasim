"""Tests for tools/detect_neurons.py."""
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World

from tools.detect_neurons import detect_neurons


def _empty_world(n_max_nodes=256):
    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(200.0, 200.0, 200.0),
        n_vibrations_max=64,
        n_nodes_max=n_max_nodes,
        rng_seed=42,
        repulsion_cell_size=200.0,
    )
    return World(cfg)


def _add_node(w, idx, pos, level):
    w.k_pos[idx] = pos
    w.k_freq[idx] = 30000.0 + idx * 100.0
    w.k_pol[idx] = bool(idx % 2)
    w.k_level[idx] = level
    w.k_alive[idx] = True
    w.k_birth[idx] = w.t
    w.k_comp_kind[idx] = 1
    w.k_comp_offset[idx] = w.k_comp_used
    w.k_comp_offset[idx + 1] = w.k_comp_used
    w.k_comp_end[idx] = w.k_comp_used
    if idx >= w.k_count:
        w.k_count = idx + 1


def test_empty_world_no_candidates():
    w = _empty_world()
    candidates = detect_neurons(w)
    assert candidates == []


def test_sparse_atoms_not_a_neuron():
    """5 atoms scattered far apart → no connected component large enough."""
    w = _empty_world()
    positions = [
        [10.0, 10.0, 10.0],
        [80.0, 10.0, 10.0],
        [150.0, 10.0, 10.0],
        [10.0, 80.0, 10.0],
        [80.0, 80.0, 10.0],
    ]
    for i, p in enumerate(positions):
        _add_node(w, i, p, level=4)
    candidates = detect_neurons(w, r_neuron=20.0)  # narrow connectivity
    # Either no candidate clusters, or none meet the size threshold.
    assert all(not c.get("is_neuron_candidate", False) for c in candidates)


def test_compact_dense_cluster_is_candidate():
    """Atoms + molecules in a small sphere → candidate accepted."""
    w = _empty_world()
    centre = np.array([100.0, 100.0, 100.0])
    rng = np.random.default_rng(42)
    # 8 atoms within 4 units of centre
    for i in range(8):
        offset = rng.uniform(-3, 3, 3)
        _add_node(w, i, (centre + offset).tolist(), level=4)
    # 6 molecules within 4 units of centre
    for i in range(6):
        offset = rng.uniform(-3, 3, 3)
        _add_node(w, 8 + i, (centre + offset).tolist(), level=5)
    candidates = detect_neurons(w, r_compact=10.0)
    assert len(candidates) >= 1
    assert any(c["is_neuron_candidate"] for c in candidates)
    accepted = [c for c in candidates if c["is_neuron_candidate"]][0]
    assert accepted["n_atoms"] >= 6
    assert accepted["n_molecules"] >= 4


def test_atoms_only_no_molecules_fails_mass():
    """10 atoms but 0 molecules → fails the molecule mass threshold."""
    w = _empty_world()
    centre = np.array([100.0, 100.0, 100.0])
    rng = np.random.default_rng(42)
    for i in range(10):
        offset = rng.uniform(-3, 3, 3)
        _add_node(w, i, (centre + offset).tolist(), level=4)
    candidates = detect_neurons(w, r_compact=10.0)
    if candidates:
        assert all(not c["is_neuron_candidate"] for c in candidates)


def test_too_loose_cluster_fails_compactness():
    """Same atoms + molecules but spread out → fails compactness."""
    w = _empty_world()
    centre = np.array([100.0, 100.0, 100.0])
    rng = np.random.default_rng(42)
    # Spread within 25 units
    for i in range(8):
        offset = rng.uniform(-25, 25, 3)
        _add_node(w, i, (centre + offset).tolist(), level=4)
    for i in range(6):
        offset = rng.uniform(-25, 25, 3)
        _add_node(w, 8 + i, (centre + offset).tolist(), level=5)
    candidates = detect_neurons(w, r_compact=8.0)
    # Cluster might exist but not be 'compact'
    if candidates:
        assert all((not c["is_compact"]) or (not c["is_neuron_candidate"])
                    for c in candidates)
