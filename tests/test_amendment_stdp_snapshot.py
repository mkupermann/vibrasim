"""Tests for k_orientation snapshot round-trip (BS8)."""
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.snapshot import save_snapshot, load_snapshot


def test_BS8_orientation_round_trips_through_snapshot(tmp_path):
    """k_orientation must round-trip through save/load with float64 precision."""
    cfg = WorldConfig(n_initial_vibrations=0, n_nodes_max=16)
    w = World(cfg)
    w.k_orientation[3] = [0.7, 0.3, 0.0]
    w.k_orientation[5] = [-0.5, 0.5, 0.7]
    p = tmp_path / "snapshot_t000000.00.npz"
    save_snapshot(w, p)
    w2 = load_snapshot(p)
    assert np.allclose(w2.k_orientation[3], [0.7, 0.3, 0.0])
    assert np.allclose(w2.k_orientation[5], [-0.5, 0.5, 0.7])
    # Untouched slots stay zero
    assert np.allclose(w2.k_orientation[0], [0.0, 0.0, 0.0])
