"""Tests for tools/detect_membranes.py — sphere fit, gap detection, threshold logic."""
import math
import numpy as np
import pytest

from tools.detect_membranes import fit_sphere, count_gaps, connected_components
from tools.construct_membrane import fibonacci_sphere


def test_sphere_fit_recovers_synthetic():
    centre = np.array([50.0, 60.0, 70.0])
    radius = 25.0
    pts = fibonacci_sphere(200, radius, centre)
    fitted_centre, fitted_radius, sigma_r = fit_sphere(pts)
    assert np.allclose(fitted_centre, centre, atol=0.5)
    assert abs(fitted_radius - radius) < 0.5
    assert sigma_r < 0.1


def test_sphere_fit_with_noise():
    centre = np.array([0.0, 0.0, 0.0])
    radius = 30.0
    rng = np.random.default_rng(42)
    pts = fibonacci_sphere(300, radius, centre)
    pts += rng.normal(0, 0.1 * radius, pts.shape)
    fitted_centre, fitted_radius, sigma_r = fit_sphere(pts)
    assert abs(fitted_radius - radius) / radius < 0.05
    assert np.linalg.norm(fitted_centre - centre) < 0.05 * radius


def test_connected_components_isolated_clusters():
    """Two well-separated clusters → two components."""
    cluster1 = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float64)
    cluster2 = np.array([[100, 100, 100], [101, 100, 100]], dtype=np.float64)
    pts = np.vstack([cluster1, cluster2])
    components = connected_components(pts, r_neighbour=2.0)
    assert len(components) == 2
    assert sum(len(c) for c in components) == 5


def test_connected_components_one_cluster():
    pts = np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0]], dtype=np.float64)
    components = connected_components(pts, r_neighbour=2.0)
    assert len(components) == 1
    assert len(components[0]) == 4


def test_gap_detection_full_shell_dense():
    """A dense Fibonacci shell has no gaps with default coarse binning."""
    centre = np.array([0.0, 0.0, 0.0])
    pts = fibonacci_sphere(400, 30.0, centre)
    n_gaps = count_gaps(pts, centre)
    assert n_gaps == 0


def test_gap_detection_one_missing_cap():
    """A dense shell with the +Z cap removed → at least 1 detected gap."""
    centre = np.array([0.0, 0.0, 0.0])
    pts = fibonacci_sphere(400, 30.0, centre)
    # Remove points whose direction is in the +Z cap (z/R > 0.7 — generous cap)
    directions = (pts - centre) / 30.0
    mask = directions[:, 2] < 0.7
    pts_with_gap = pts[mask]
    n_gaps = count_gaps(pts_with_gap, centre)
    assert n_gaps >= 1
    # Loose upper bound — sparse-binning artifacts may fragment, but it's clearly a gap
    assert n_gaps <= 4


def test_detect_constructed_shell_is_closed(tmp_path):
    """Construct a shell, run detection on the resulting snapshot."""
    from world.config import WorldConfig
    from world.state import World
    from world.snapshot import save_snapshot, load_snapshot
    from tools.construct_membrane import construct_shell
    from tools.detect_membranes import detect_membranes

    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(200.0, 200.0, 200.0),
        n_vibrations_max=64,
        n_nodes_max=256,
        r_2=15.0,
        rng_seed=42,
    )
    w = World(cfg)
    centre = np.array([100.0, 100.0, 100.0])
    # 80 molecules on a 40-radius shell → mean nearest-neighbour ~17, comfortably under r_membrane=30
    construct_shell(w, centre, radius=40.0, n_molecules=80, level=5)
    save_snapshot(w, tmp_path / "shell.npz")

    w2 = load_snapshot(tmp_path / "shell.npz")
    candidates = detect_membranes(w2, min_molecules=12, r_membrane=30.0)
    assert len(candidates) >= 1
    closed = [c for c in candidates if c["closed"]]
    assert len(closed) >= 1
    c = closed[0]
    assert abs(c["radius"] - 40.0) < 5.0
    assert c["n_molecules"] >= 12


def test_detect_filled_ball_is_not_closed(tmp_path):
    """A solid filled ball of 100 nodes should NOT be classified as a closed membrane."""
    from world.config import WorldConfig
    from world.state import World
    from world.snapshot import save_snapshot, load_snapshot
    from tools.detect_membranes import detect_membranes

    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(200.0, 200.0, 200.0),
        n_vibrations_max=64,
        n_nodes_max=512,
        r_2=20.0,
        rng_seed=42,
    )
    w = World(cfg)
    rng = np.random.default_rng(42)
    centre = np.array([100.0, 100.0, 100.0])
    n = 100
    # Fill a ball of radius 30 with random points
    radii = rng.uniform(0, 30.0, n) ** (1/3) * 30.0  # cubic-root for volume-uniform
    z = rng.uniform(-1, 1, n)
    phi = rng.uniform(0, 2 * np.pi, n)
    sqz = np.sqrt(1 - z * z)
    for i in range(n):
        idx = w.k_count
        w.k_pos[idx] = centre + radii[i] * np.array([sqz[i] * np.cos(phi[i]),
                                                      sqz[i] * np.sin(phi[i]),
                                                      z[i]])
        w.k_freq[idx] = 30000.0
        w.k_pol[idx] = bool(i % 2)
        w.k_level[idx] = 5
        w.k_alive[idx] = True
        w.k_count += 1
    save_snapshot(w, tmp_path / "ball.npz")

    w2 = load_snapshot(tmp_path / "ball.npz")
    candidates = detect_membranes(w2, min_molecules=12)
    closed = [c for c in candidates if c["closed"]]
    # A solid ball has interior_count > 0, so should NOT be closed
    assert len(closed) == 0
