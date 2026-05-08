"""Tests for asymmetric STDP at reward boundary (RA1-RA5)."""
import numpy as np
from world.config import WorldConfig
from world.state import World
from world.physics import apply_stdp


def _make_cfg():
    return WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=16, n_nodes_max=16,
        box_size=(100.0, 100.0, 100.0),
        stdp_enabled=True,
        tau_LTP=0.020, tau_LTD=0.020,
        delta_LTP=1.0, delta_LTD=0.5,
        r_bridge=5.0,
    )


def _base_world(cfg):
    """Two atoms + one bridge molecule between them.

    Atom 0 at (50,50,50) — non-reward (k_reward_polarity=0).
    Atom 1 at (70,50,50) — reward port atom (k_reward_polarity set by caller).
    Bridge at (60,50,50) with orientation set by caller.
    """
    w = World(cfg)
    w.k_pos[0] = [50.0, 50.0, 50.0]
    w.k_level[0] = 4
    w.k_alive[0] = True
    # atom_j = 1: reward polarity set by caller
    w.k_pos[1] = [70.0, 50.0, 50.0]
    w.k_level[1] = 4
    w.k_alive[1] = True
    # bridge
    w.k_pos[2] = [60.0, 50.0, 50.0]
    w.k_level[2] = 5
    w.k_alive[2] = True
    w.k_strength[2] = 100.0
    w.k_count = 3
    return w


def test_RA1_positive_reward_aligned_orientation_LTP():
    """Pair: non-reward atom → reward atom with k_reward_polarity=+1.
    Bridge orientation aligned with A→B (alignment ≥ 0). No swap → LTP.
    Strength must increase."""
    cfg = _make_cfg()
    w = _base_world(cfg)
    w.k_reward_polarity[1] = 1
    w.k_orientation[2] = [1.0, 0.0, 0.0]  # aligned with A→B

    initial = float(w.k_strength[2])
    w.firing_events = [(0.000, 0), (0.010, 1)]
    w.t = 0.020
    apply_stdp(w)

    final = float(w.k_strength[2])
    assert final > initial, (
        f"RA1: expected LTP (strength increase), got {initial} → {final}"
    )


def test_RA2_negative_reward_atom_aligned_orientation_flips_to_LTD():
    """Pair: non-reward atom → reward-port atom with k_reward_polarity=-1.
    Existing bridge orientation aligned with A→B (which would normally
    apply LTP). The flip changes it to LTD."""
    cfg = _make_cfg()
    w = _base_world(cfg)
    w.k_reward_polarity[1] = -1
    w.k_orientation[2] = [1.0, 0.0, 0.0]  # aligned with A→B

    initial = float(w.k_strength[2])
    w.firing_events = [(0.000, 0), (0.010, 1)]
    w.t = 0.020
    apply_stdp(w)

    final = float(w.k_strength[2])
    assert final < initial, (
        f"RA2: expected LTD (strength decrease), got {initial} → {final}"
    )


def test_RA3_positive_reward_anti_aligned_orientation_LTD():
    """Pair: non-reward atom → reward atom with k_reward_polarity=+1.
    Bridge orientation anti-aligned with A→B (alignment < 0). No swap → LTD.
    Strength must decrease."""
    cfg = _make_cfg()
    w = _base_world(cfg)
    w.k_reward_polarity[1] = 1
    w.k_orientation[2] = [-1.0, 0.0, 0.0]  # anti-aligned with A→B

    initial = float(w.k_strength[2])
    w.firing_events = [(0.000, 0), (0.010, 1)]
    w.t = 0.020
    apply_stdp(w)

    final = float(w.k_strength[2])
    assert final < initial, (
        f"RA3: expected LTD (strength decrease), got {initial} → {final}"
    )


def test_RA4_negative_reward_anti_aligned_orientation_flips_to_LTP():
    """Pair: non-reward atom → reward atom with k_reward_polarity=-1.
    Bridge orientation anti-aligned with A→B (which would normally apply LTD).
    The flip changes it to LTP: strength must increase."""
    cfg = _make_cfg()
    w = _base_world(cfg)
    w.k_reward_polarity[1] = -1
    w.k_orientation[2] = [-1.0, 0.0, 0.0]  # anti-aligned with A→B

    initial = float(w.k_strength[2])
    w.firing_events = [(0.000, 0), (0.010, 1)]
    w.t = 0.020
    apply_stdp(w)

    final = float(w.k_strength[2])
    assert final > initial, (
        f"RA4: expected LTP (strength increase), got {initial} → {final}"
    )


def test_RA5_ambient_atom_inside_reward_port_position_no_swap():
    """Atom inside reward port BUT k_reward_polarity=0 (ambient origin).
    Aligned bridge → LTP (swap is gated on polarity, not position)."""
    cfg = _make_cfg()
    w = _base_world(cfg)
    # Place atom_j inside the reward port region, but polarity stays 0
    w.k_pos[1] = [70.0, 50.0, 50.0]
    w.k_reward_polarity[1] = 0  # explicit: ambient, no swap
    w.k_orientation[2] = [1.0, 0.0, 0.0]  # aligned

    initial = float(w.k_strength[2])
    w.firing_events = [(0.000, 0), (0.010, 1)]
    w.t = 0.020
    apply_stdp(w)

    final = float(w.k_strength[2])
    assert final > initial, (
        f"RA5: expected LTP (no swap for polarity=0), got {initial} → {final}"
    )
