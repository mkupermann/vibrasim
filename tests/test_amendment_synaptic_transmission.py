"""Tests for synaptic transmission (BS6, BS7)."""
import numpy as np
from world.config import WorldConfig
from world.state import World
from world.physics import synaptic_transmission


def _world_with_one_oriented_bridge():
    cfg = WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=16, n_nodes_max=16,
        box_size=(100.0, 100.0, 100.0),
        stdp_enabled=True,
        r_bridge=5.0,
        synaptic_transmission_strength=0.5,
        synaptic_transmission_threshold=5.0,
    )
    w = World(cfg)
    # Pre-synaptic atom (placeholder; not used in this test)
    w.k_pos[0] = [55.0, 50.0, 50.0]
    w.k_level[0] = 4
    w.k_alive[0] = True
    # Bridge molecule at (60, 50, 50), strength 20, orientation (1,0,0)
    w.k_pos[1] = [60.0, 50.0, 50.0]
    w.k_level[1] = 5
    w.k_alive[1] = True
    w.k_strength[1] = 20.0
    w.k_orientation[1] = [1.0, 0.0, 0.0]
    # Post-synaptic atom at (65, 50, 50), zero charge initially
    w.k_pos[2] = [65.0, 50.0, 50.0]
    w.k_level[2] = 4
    w.k_alive[2] = True
    w.k_charge[2] = 0.0
    w.k_count = 3
    return w


def test_BS6_aligned_vibration_charges_postsynaptic_atom():
    """A vibration moving in the orientation direction near a strong bridge
    deposits charge into the post-synaptic atom."""
    w = _world_with_one_oriented_bridge()
    # Vibration at the bridge position with velocity (15, 0, 0) — aligned with orientation
    w.s_pos[0] = [60.0, 50.0, 50.0]
    w.s_vel[0] = [15.0, 0.0, 0.0]
    w.s_freq[0] = 1000.0
    w.s_alive[0] = True
    w.n_alive = 1

    initial_charge = float(w.k_charge[2])
    synaptic_transmission(w, dt=1.0 / 60.0)
    final_charge = float(w.k_charge[2])
    # Expected charge gain: alignment(=1.0) * w_synaptic(0.5) * dt(1/60) ≈ 0.00833
    expected_gain = 1.0 * 0.5 * (1.0 / 60.0)
    assert abs((final_charge - initial_charge) - expected_gain) < 0.001, (
        f"BS6: charge gain {final_charge - initial_charge:.5f} != expected {expected_gain:.5f}"
    )


def test_BS7_misaligned_vibration_does_not_charge():
    """A vibration moving against the orientation direction does NOT
    deposit charge into the post-synaptic atom."""
    w = _world_with_one_oriented_bridge()
    w.s_pos[0] = [60.0, 50.0, 50.0]
    w.s_vel[0] = [-15.0, 0.0, 0.0]  # opposite direction
    w.s_freq[0] = 1000.0
    w.s_alive[0] = True
    w.n_alive = 1

    initial_charge = float(w.k_charge[2])
    synaptic_transmission(w, dt=1.0 / 60.0)
    final_charge = float(w.k_charge[2])
    assert final_charge == initial_charge


def test_BS7b_weak_bridge_does_not_transmit():
    """Bridge with strength below threshold does not transmit even if aligned."""
    w = _world_with_one_oriented_bridge()
    w.k_strength[1] = 2.0  # below threshold of 5.0
    w.s_pos[0] = [60.0, 50.0, 50.0]
    w.s_vel[0] = [15.0, 0.0, 0.0]
    w.s_freq[0] = 1000.0
    w.s_alive[0] = True
    w.n_alive = 1

    synaptic_transmission(w, dt=1.0 / 60.0)
    assert w.k_charge[2] == 0.0


def test_BS7c_unoriented_bridge_does_not_transmit():
    """Bridge with zero orientation does not transmit."""
    w = _world_with_one_oriented_bridge()
    w.k_orientation[1] = [0.0, 0.0, 0.0]  # no orientation
    w.s_pos[0] = [60.0, 50.0, 50.0]
    w.s_vel[0] = [15.0, 0.0, 0.0]
    w.s_freq[0] = 1000.0
    w.s_alive[0] = True
    w.n_alive = 1

    synaptic_transmission(w, dt=1.0 / 60.0)
    assert w.k_charge[2] == 0.0
