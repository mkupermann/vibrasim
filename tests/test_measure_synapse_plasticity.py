"""Tests for tools/measure_synapse_plasticity.py."""
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.snapshot import save_snapshot

from tools.measure_synapse_plasticity import (
    measure_plasticity, _co_active_windows, _inactive_intervals, _slope_in_window
)


def test_co_active_windows_overlap():
    pre = [(0.0, 1.0), (5.0, 6.0)]
    post = [(0.5, 1.5), (10.0, 11.0)]
    co = _co_active_windows(pre, post, max_lag=1.0)
    # Pre[0] and Post[0] overlap → merged window
    assert any(s <= 0.5 and e >= 1.5 for s, e in co)


def test_co_active_windows_no_overlap_no_lag():
    pre = [(0.0, 1.0)]
    post = [(10.0, 11.0)]
    co = _co_active_windows(pre, post, max_lag=0.5)
    assert co == []


def test_inactive_intervals_basic():
    inactive = _inactive_intervals([(2.0, 4.0), (6.0, 8.0)], 0.0, 10.0)
    assert (0.0, 2.0) in inactive
    assert (4.0, 6.0) in inactive
    assert (8.0, 10.0) in inactive


def test_slope_in_window_positive():
    times = [0.0, 1.0, 2.0, 3.0, 4.0]
    values = [10, 11, 12, 13, 14]
    slope = _slope_in_window(times, values, 0.0, 4.0)
    assert slope == pytest.approx(1.0, abs=0.01)


def test_slope_in_window_too_few_samples():
    times = [0.0]
    values = [10]
    slope = _slope_in_window(times, values, 0.0, 4.0)
    assert slope is None


def _save_synthetic_snapshot(path, t: float, store_count: int, recv_count: int,
                              pre_outlet, post_inlet):
    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(200.0, 200.0, 200.0),
        n_vibrations_max=64,
        n_nodes_max=64,
        rng_seed=42,
    )
    w = World(cfg)
    w.t = t
    rng = np.random.default_rng(42 + int(t * 1000))
    for i in range(store_count):
        idx = w.k_count
        offset = rng.uniform(-0.5, 0.5, 3)
        w.k_pos[idx] = pre_outlet + offset
        w.k_freq[idx] = 60000.0
        w.k_pol[idx] = bool(idx % 2)
        w.k_level[idx] = 5
        w.k_alive[idx] = True
        w.k_count += 1
    for i in range(recv_count):
        idx = w.k_count
        offset = rng.uniform(-0.5, 0.5, 3)
        w.k_pos[idx] = post_inlet + offset
        w.k_freq[idx] = 60000.0
        w.k_pol[idx] = bool(idx % 2)
        w.k_level[idx] = 5
        w.k_alive[idx] = True
        w.k_count += 1
    save_snapshot(w, path)


def test_no_activity_returns_none_signal(tmp_path):
    pre_centre = np.array([80.0, 100.0, 100.0])
    post_centre = np.array([120.0, 100.0, 100.0])
    direction = (post_centre - pre_centre) / 40.0
    pre_outlet = pre_centre + 6.0 * 0.6 * direction
    post_inlet = post_centre - 6.0 * 0.6 * direction
    paths = []
    for i in range(3):
        p = tmp_path / f"snapshot_t{i:09.2f}.npz"
        _save_synthetic_snapshot(p, t=float(i), store_count=2, recv_count=2,
                                   pre_outlet=pre_outlet, post_inlet=post_inlet)
        paths.append(p)
    result = measure_plasticity(paths, pre_centre, post_centre, neuron_radius=6.0)
    assert result["hebbian_signal"] is None  # no activity → can't compute signal
    assert len(result["pre_active_intervals"]) == 0


def test_synthetic_growth_during_co_activity(tmp_path):
    """Hand-crafted: store + receiver counts grow linearly through entire run.
    Without activity windows the slope is computable globally; we verify
    the per-step counts are extracted correctly."""
    pre_centre = np.array([80.0, 100.0, 100.0])
    post_centre = np.array([120.0, 100.0, 100.0])
    direction = (post_centre - pre_centre) / 40.0
    pre_outlet = pre_centre + 6.0 * 0.6 * direction
    post_inlet = post_centre - 6.0 * 0.6 * direction
    paths = []
    for i in range(5):
        p = tmp_path / f"snapshot_t{i:09.2f}.npz"
        # Counts grow over time
        _save_synthetic_snapshot(p, t=float(i), store_count=2 + i, recv_count=2 + i,
                                   pre_outlet=pre_outlet, post_inlet=post_inlet)
        paths.append(p)
    result = measure_plasticity(paths, pre_centre, post_centre, neuron_radius=6.0)
    # Counts should reflect the growth
    assert result["presynaptic_store_per_step"] == [2, 3, 4, 5, 6]
    assert result["postsynaptic_receivers_per_step"] == [2, 3, 4, 5, 6]


def test_pre_post_centres_zero_distance_rejected(tmp_path):
    p = tmp_path / "snapshot_t000000.00.npz"
    _save_synthetic_snapshot(p, 0.0, 0, 0,
                               np.array([100, 100, 100]),
                               np.array([100, 100, 100]))
    with pytest.raises(ValueError):
        measure_plasticity([p], np.array([100., 100., 100.]),
                              np.array([100., 100., 100.]))
