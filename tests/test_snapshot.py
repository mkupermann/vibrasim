import numpy as np
import pytest
from pathlib import Path
from world.config import WorldConfig
from world.state import World
from world.snapshot import save_snapshot, load_snapshot, snapshot_filename


def test_filename_format():
    p = snapshot_filename(123.45)
    assert p.endswith("snapshot_t000123.45.npz")


def test_filename_chronological_sort():
    files = sorted([snapshot_filename(t) for t in (10.0, 1.0, 100.0)])
    # Lexicographic sort should match numerical order
    times = [float(f.split('_t')[1].split('.npz')[0]) for f in files]
    assert times == sorted(times)


def test_round_trip(tmp_path):
    cfg = WorldConfig(rng_seed=42)
    w = World(cfg)
    # Run a few ticks to make state non-trivial
    from world.physics import tick
    for _ in range(10):
        tick(w, cfg.dt)
    path = tmp_path / "snap.npz"
    save_snapshot(w, path)
    w2 = load_snapshot(path)
    np.testing.assert_array_equal(w.s_pos, w2.s_pos)
    np.testing.assert_array_equal(w.k_pos, w2.k_pos)
    assert w.t == w2.t
    assert w.n_alive == w2.n_alive
    assert w.k_count == w2.k_count


def test_resumed_world_can_tick(tmp_path):
    cfg = WorldConfig(rng_seed=42)
    w = World(cfg)
    from world.physics import tick
    for _ in range(10):
        tick(w, cfg.dt)
    path = tmp_path / "snap.npz"
    save_snapshot(w, path)
    w2 = load_snapshot(path)
    tick(w2, cfg.dt)  # should not crash


def test_snapshot_preserves_k_strength(tmp_path):
    """k_strength must round-trip through save/load."""
    cfg = WorldConfig(n_initial_vibrations=0, n_nodes_max=8)
    w = World(cfg)
    # Set distinctive strengths on a few nodes
    w.k_strength[0] = 17.5
    w.k_strength[3] = 99.9
    p = tmp_path / "snapshot_t000000.00.npz"
    save_snapshot(w, p)
    w2 = load_snapshot(p)
    assert w2.k_strength[0] == 17.5
    assert w2.k_strength[3] == 99.9
    # Untouched slots round-trip too
    assert w2.k_strength[1] == 1.0


def test_AP_snapshot_preserves_k_ref_count(tmp_path):
    """k_ref_count round-trips through save/load."""
    cfg = WorldConfig(n_initial_vibrations=0, n_nodes_max=8)
    w = World(cfg)
    w.k_ref_count[2] = 7
    w.k_ref_count[5] = 3
    p = tmp_path / "snapshot_t000000.00.npz"
    save_snapshot(w, p)
    w2 = load_snapshot(p)
    assert w2.k_ref_count[2] == 7
    assert w2.k_ref_count[5] == 3
    assert w2.k_ref_count[0] == 0
