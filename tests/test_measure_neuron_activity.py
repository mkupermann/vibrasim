"""Tests for tools/measure_neuron_activity.py."""
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.snapshot import save_snapshot

from tools.measure_neuron_activity import measure_activity


def _save_snapshot_with_vibrations(path, t, vibration_positions):
    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(200.0, 200.0, 200.0),
        n_vibrations_max=128,
        n_nodes_max=64,
        rng_seed=42,
        repulsion_cell_size=200.0,
    )
    w = World(cfg)
    w.t = t
    for i, pos in enumerate(vibration_positions):
        if i >= w.s_pos.shape[0]:
            break
        w.s_pos[i] = pos
        w.s_vel[i] = [0.0, 0.0, 0.0]
        w.s_freq[i] = 1000.0 + i
        w.s_pol[i] = bool(i % 2)
        w.s_alive[i] = True
    w.n_alive = min(len(vibration_positions), w.s_pos.shape[0])
    save_snapshot(w, path)


def test_no_input_no_output_zeros(tmp_path):
    centre = np.array([100.0, 100.0, 100.0])
    axis = np.array([1.0, 0.0, 0.0])
    radius = 6.0
    # Three snapshots with NO vibrations near the cluster
    paths = []
    for i in range(3):
        p = tmp_path / f"snapshot_t{i:09.2f}.npz"
        # Place vibrations far from the cluster (at world origin)
        far_positions = [[10.0 + 5.0 * j, 10.0, 10.0] for j in range(5)]
        _save_snapshot_with_vibrations(p, t=float(i), vibration_positions=far_positions)
        paths.append(p)
    result = measure_activity(paths, centre, axis, radius)
    assert all(c == 0 for c in result["input_count_per_step"])
    assert all(c == 0 for c in result["output_count_per_step"])
    assert result["firing_events"] == []


def test_input_only_no_firing(tmp_path):
    centre = np.array([100.0, 100.0, 100.0])
    axis = np.array([1.0, 0.0, 0.0])
    radius = 6.0
    inlet_centre = centre + 6.0 * 0.6 * axis  # at (103.6, 100, 100)
    paths = []
    for i in range(5):
        p = tmp_path / f"snapshot_t{i:09.2f}.npz"
        positions = [inlet_centre.tolist() for _ in range(3)]  # 3 vibrations at inlet
        _save_snapshot_with_vibrations(p, t=float(i), vibration_positions=positions)
        paths.append(p)
    result = measure_activity(paths, centre, axis, radius)
    assert sum(result["input_count_per_step"]) > 0
    assert sum(result["output_count_per_step"]) == 0
    assert result["firing_events"] == []


def test_output_spike_detected_as_firing(tmp_path):
    centre = np.array([100.0, 100.0, 100.0])
    axis = np.array([1.0, 0.0, 0.0])
    radius = 6.0
    outlet_centre = centre - 6.0 * 0.6 * axis  # at (96.4, 100, 100)
    paths = []
    # Two quiet snapshots, one big spike, two more quiet
    for i in range(5):
        p = tmp_path / f"snapshot_t{i:09.2f}.npz"
        if i == 2:
            positions = [outlet_centre.tolist() for _ in range(20)]  # big spike
        else:
            positions = [[10.0, 10.0, 10.0]]  # far away, count 0
        _save_snapshot_with_vibrations(p, t=float(i), vibration_positions=positions)
        paths.append(p)
    result = measure_activity(paths, centre, axis, radius)
    assert len(result["firing_events"]) >= 1
    # Firing event should peak at i=2 (t=2.0)
    fe = result["firing_events"][0]
    assert abs(fe["peak_t"] - 2.0) < 0.1


def test_single_transient_at_zero_baseline_not_a_firing(tmp_path):
    """Regression test for C3: when output baseline is zero, a single
    transient (count=1) at the outlet must NOT register as a firing event.
    Previously the threshold floor was 1.0, so any single mobile node
    drifting through registered as a firing."""
    centre = np.array([100.0, 100.0, 100.0])
    axis = np.array([1.0, 0.0, 0.0])
    radius = 6.0
    outlet_centre = centre - 6.0 * 0.6 * axis
    paths = []
    # 5 quiet snapshots, one with a single drift, 5 more quiet
    for i in range(11):
        p = tmp_path / f"snapshot_t{i:09.2f}.npz"
        if i == 5:
            positions = [outlet_centre.tolist()]  # single transient
        else:
            positions = [[10.0, 10.0, 10.0]]  # far away
        _save_snapshot_with_vibrations(p, t=float(i), vibration_positions=positions)
        paths.append(p)
    result = measure_activity(paths, centre, axis, radius)
    # Single transient should NOT be a firing event with the new floor.
    assert result["firing_events"] == []


def test_single_snapshot_returns_empty_lists(tmp_path):
    """One snapshot is not enough to detect activity."""
    centre = np.array([100.0, 100.0, 100.0])
    axis = np.array([1.0, 0.0, 0.0])
    radius = 6.0
    p = tmp_path / "snapshot_t000000.00.npz"
    _save_snapshot_with_vibrations(p, t=0.0, vibration_positions=[[100, 100, 100]])
    result = measure_activity([p], centre, axis, radius)
    assert result["firing_events"] == []
    assert result["integration_lag_ms"] is None
    assert result["refractory_ms"] is None
