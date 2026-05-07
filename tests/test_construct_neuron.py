"""Tests for tools/construct_neuron.py."""
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.snapshot import save_snapshot, load_snapshot

from tools.construct_neuron import construct_neuron
from tools.detect_neurons import detect_neurons


def _empty_world():
    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(200.0, 200.0, 200.0),
        n_vibrations_max=64,
        n_nodes_max=128,
        rng_seed=42,
        repulsion_cell_size=200.0,
    )
    return World(cfg)


def test_construct_basic():
    w = _empty_world()
    info = construct_neuron(
        w,
        centre=np.array([100.0, 100.0, 100.0]),
        radius=6.0,
        axis=np.array([1.0, 0.0, 0.0]),
        n_atoms=8,
        n_molecules=6,
    )
    assert len(info["atom_indices"]) == 8
    assert len(info["molecule_indices"]) == 6
    assert info["radius"] == 6.0
    # All placed nodes alive at level 4 or 5
    assert int(((w.k_level == 4) & w.k_alive).sum()) == 8
    assert int(((w.k_level == 5) & w.k_alive).sum()) == 6


def test_construct_axis_normalised():
    w = _empty_world()
    info = construct_neuron(
        w,
        centre=np.array([100.0, 100.0, 100.0]),
        radius=6.0,
        axis=np.array([2.0, 0.0, 0.0]),
        n_atoms=8,
        n_molecules=6,
    )
    # The axis stored in info should be unit-length
    axis = np.array(info["axis"])
    assert np.allclose(np.linalg.norm(axis), 1.0, atol=1e-6)


def test_construct_zero_axis_rejected():
    w = _empty_world()
    with pytest.raises(ValueError):
        construct_neuron(
            w,
            centre=np.array([100.0, 100.0, 100.0]),
            radius=6.0,
            axis=np.array([0.0, 0.0, 0.0]),
            n_atoms=8,
            n_molecules=6,
        )


def test_construct_nodes_inside_radius():
    w = _empty_world()
    centre = np.array([100.0, 100.0, 100.0])
    radius = 6.0
    info = construct_neuron(
        w, centre=centre, radius=radius,
        axis=np.array([1.0, 0.0, 0.0]),
        n_atoms=8, n_molecules=6,
    )
    for idx in info["atom_indices"] + info["molecule_indices"]:
        d = np.linalg.norm(w.k_pos[idx] - centre)
        # Tolerance margin on top of the 0.7-of-radius rejection sample
        assert d <= radius * 0.71


def test_construct_then_detect_round_trip(tmp_path):
    w = _empty_world()
    construct_neuron(
        w,
        centre=np.array([100.0, 100.0, 100.0]),
        radius=6.0,
        axis=np.array([1.0, 0.0, 0.0]),
        n_atoms=8,
        n_molecules=6,
    )
    save_snapshot(w, tmp_path / "neuron.npz")
    w2 = load_snapshot(tmp_path / "neuron.npz")
    candidates = detect_neurons(w2, r_compact=10.0)
    assert len(candidates) >= 1
    assert any(c["is_neuron_candidate"] for c in candidates)
