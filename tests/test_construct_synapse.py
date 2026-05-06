"""Tests for tools/construct_synapse.py."""
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.snapshot import save_snapshot, load_snapshot

from tools.construct_synapse import construct_synapse
from tools.detect_neurons import detect_neurons


def _empty_world():
    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(200.0, 200.0, 200.0),
        n_vibrations_max=128,
        n_nodes_max=256,
        rng_seed=42,
    )
    return World(cfg)


def test_construct_basic():
    w = _empty_world()
    info = construct_synapse(
        w,
        pre_centre=np.array([80.0, 100.0, 100.0]),
        post_centre=np.array([120.0, 100.0, 100.0]),
        neuron_radius=6.0,
        n_atoms_per_neuron=8,
        n_molecules_per_neuron=6,
        n_cleft_molecules=4,
        n_presynaptic_store=6,
        n_postsynaptic_receivers=6,
    )
    assert len(info["pre_neuron"]["atom_indices"]) == 8
    assert len(info["pre_neuron"]["molecule_indices"]) == 6
    assert len(info["post_neuron"]["atom_indices"]) == 8
    assert len(info["post_neuron"]["molecule_indices"]) == 6
    assert len(info["cleft_node_indices"]) == 4
    assert len(info["presynaptic_store_indices"]) == 6
    assert len(info["postsynaptic_receiver_indices"]) == 6
    assert info["distance"] == pytest.approx(40.0)


def test_axes_face_each_other():
    """The pre's outlet should face toward the post (and vice versa)."""
    w = _empty_world()
    info = construct_synapse(
        w,
        pre_centre=np.array([50.0, 100.0, 100.0]),
        post_centre=np.array([100.0, 100.0, 100.0]),
        neuron_radius=6.0,
    )
    pre_outlet = np.array(info["pre_neuron"]["outlet_centre"])
    post_inlet = np.array(info["post_neuron"]["inlet_centre"])
    pre_centre = np.array(info["pre_neuron"]["centre"])
    post_centre = np.array(info["post_neuron"]["centre"])
    # Pre's outlet should be on the post side of pre_centre.
    direction = post_centre - pre_centre
    direction /= np.linalg.norm(direction)
    rel = pre_outlet - pre_centre
    rel /= np.linalg.norm(rel)
    assert np.dot(rel, direction) > 0.9


def test_construct_zero_distance_rejected():
    w = _empty_world()
    with pytest.raises(ValueError):
        construct_synapse(
            w,
            pre_centre=np.array([50.0, 50.0, 50.0]),
            post_centre=np.array([50.0, 50.0, 50.0]),
        )


def test_construct_cleft_population_inside_cylinder():
    """The cleft molecules should be inside the cleft cylinder geometry."""
    w = _empty_world()
    info = construct_synapse(
        w,
        pre_centre=np.array([80.0, 100.0, 100.0]),
        post_centre=np.array([120.0, 100.0, 100.0]),
        neuron_radius=6.0,
        n_cleft_molecules=4,
    )
    pre_centre = np.array(info["pre_neuron"]["centre"])
    post_centre = np.array(info["post_neuron"]["centre"])
    direction = post_centre - pre_centre
    direction_norm = direction / np.linalg.norm(direction)
    cleft_radius = info["cleft_radius"]
    for idx in info["cleft_node_indices"]:
        pos = w.k_pos[idx]
        # Project onto the pre→post line
        proj = np.dot(pos - pre_centre, direction_norm)
        # Should be between the two outlets
        assert proj > 0
        assert proj < float(np.linalg.norm(direction))
        perp = (pos - pre_centre) - proj * direction_norm
        assert float(np.linalg.norm(perp)) <= cleft_radius * 0.6


def test_construct_then_detect_at_least_one_neuron(tmp_path):
    """After construction the cleft bridges the two neurons in connectivity-based
    detection; detect_neurons may merge them. We assert *at least one* neuron
    candidate is found (whether merged or separated). True separation requires
    density-based clustering — a future detection-tool improvement (not in this
    spec's scope; see docs/superpowers/specs/2026-05-06-phase-5-synapses.md §5).
    """
    w = _empty_world()
    construct_synapse(
        w,
        pre_centre=np.array([80.0, 100.0, 100.0]),
        post_centre=np.array([120.0, 100.0, 100.0]),
        neuron_radius=6.0,
    )
    save_snapshot(w, tmp_path / "syn.npz")
    w2 = load_snapshot(tmp_path / "syn.npz")
    # Use a generous r_compact since the merged cluster spans both neurons + cleft.
    candidates = detect_neurons(w2, r_compact=30.0)
    accepted = [c for c in candidates if c["is_neuron_candidate"]]
    assert len(accepted) >= 1
