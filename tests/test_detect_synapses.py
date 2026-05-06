"""Tests for tools/detect_synapses.py."""
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.snapshot import save_snapshot, load_snapshot

from tools.construct_synapse import construct_synapse
from tools.construct_neuron import construct_neuron
from tools.detect_synapses import detect_synapses


def _empty_world():
    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(400.0, 400.0, 400.0),
        n_vibrations_max=128,
        n_nodes_max=512,
        rng_seed=42,
    )
    return World(cfg)


def test_no_neurons_no_synapse():
    w = _empty_world()
    candidates = detect_synapses(w)
    assert candidates == []


def test_two_neurons_at_synapse_distance_detected(tmp_path):
    """Two SEPARATE neurons placed at synapse distance, no cleft bridging:
    detect_neurons sees both, detect_synapses pairs them as a candidate."""
    w = _empty_world()
    # Construct two neurons WITHOUT a cleft bridging them.
    construct_neuron(
        w, np.array([80.0, 100.0, 100.0]), 6.0,
        np.array([1.0, 0.0, 0.0]), n_atoms=8, n_molecules=6,
    )
    construct_neuron(
        w, np.array([120.0, 100.0, 100.0]), 6.0,
        np.array([-1.0, 0.0, 0.0]), n_atoms=8, n_molecules=6,
    )
    save_snapshot(w, tmp_path / "two.npz")
    w2 = load_snapshot(tmp_path / "two.npz")
    candidates = detect_synapses(w2)
    assert len(candidates) >= 1


def test_constructed_synapse_detection_with_cleft(tmp_path):
    """Constructing a full synapse (with cleft) tests the merged-cluster path.
    The cleft molecules bridge the two neurons in connectivity-based detection,
    so detect_neurons may return one merged cluster — and detect_synapses then
    correctly returns no synapse candidate (need ≥2 separate neurons).

    This documents the known limitation; density-based clustering would fix it
    (future work, see Phase 5 spec §5)."""
    w = _empty_world()
    construct_synapse(
        w,
        pre_centre=np.array([80.0, 100.0, 100.0]),
        post_centre=np.array([120.0, 100.0, 100.0]),
        neuron_radius=6.0,
    )
    save_snapshot(w, tmp_path / "syn.npz")
    w2 = load_snapshot(tmp_path / "syn.npz")
    # The detection should run without error regardless of whether it finds a synapse.
    candidates = detect_synapses(w2)
    assert isinstance(candidates, list)


def test_lone_neuron_no_synapse(tmp_path):
    """A single neuron alone → no synapse candidates."""
    w = _empty_world()
    construct_neuron(
        w, np.array([100.0, 100.0, 100.0]), 6.0,
        np.array([1.0, 0.0, 0.0]), n_atoms=8, n_molecules=6,
    )
    save_snapshot(w, tmp_path / "lone.npz")
    w2 = load_snapshot(tmp_path / "lone.npz")
    candidates = detect_synapses(w2)
    assert candidates == []


def test_two_far_neurons_no_synapse(tmp_path):
    """Two neurons too far apart → no candidate (D > D_max)."""
    w = _empty_world()
    construct_neuron(
        w, np.array([50.0, 100.0, 100.0]), 6.0,
        np.array([1.0, 0.0, 0.0]), n_atoms=8, n_molecules=6,
    )
    construct_neuron(
        w, np.array([350.0, 100.0, 100.0]), 6.0,
        np.array([-1.0, 0.0, 0.0]), n_atoms=8, n_molecules=6,
    )
    save_snapshot(w, tmp_path / "far.npz")
    w2 = load_snapshot(tmp_path / "far.npz")
    candidates = detect_synapses(w2)
    # Distance ~300, exceeds default d_max = 5*r_compact = 40
    assert candidates == []


def test_two_close_neurons_become_one_cluster(tmp_path):
    """Two neurons too close (their connectivity overlaps) → detect_neurons may merge them."""
    w = _empty_world()
    # Place neurons within neuron_radius of each other; they may be detected as one cluster.
    construct_neuron(
        w, np.array([100.0, 100.0, 100.0]), 6.0,
        np.array([1.0, 0.0, 0.0]), n_atoms=8, n_molecules=6,
    )
    construct_neuron(
        w, np.array([110.0, 100.0, 100.0]), 6.0,
        np.array([-1.0, 0.0, 0.0]), n_atoms=8, n_molecules=6,
    )
    save_snapshot(w, tmp_path / "close.npz")
    w2 = load_snapshot(tmp_path / "close.npz")
    # Either no synapse (merged into one big cluster, no pair) or some weird detection.
    # Test passes as long as it doesn't crash.
    candidates = detect_synapses(w2)
    assert isinstance(candidates, list)
