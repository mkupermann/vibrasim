"""Tests for STDP orientation update convergence (BS5)."""
import numpy as np
from world.config import WorldConfig
from world.state import World
from world.physics import apply_stdp


def test_BS5_orientation_converges_after_many_pairs():
    """50 paired A→B firings should converge k_orientation to within 5° of
    the unit vector (1, 0, 0) and norm in [0.95, 1.05]."""
    cfg = WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=16, n_nodes_max=16,
        box_size=(100.0, 100.0, 100.0),
        stdp_enabled=True,
        tau_LTP=0.020, tau_LTD=0.020,
        delta_LTP=1.0, delta_LTD=0.5,
        r_bridge=5.0,
    )
    w = World(cfg)
    w.k_pos[0] = [50.0, 50.0, 50.0]
    w.k_level[0] = 4
    w.k_alive[0] = True
    w.k_pos[1] = [70.0, 50.0, 50.0]
    w.k_level[1] = 4
    w.k_alive[1] = True
    w.k_pos[2] = [60.0, 50.0, 50.0]
    w.k_level[2] = 5
    w.k_alive[2] = True
    w.k_strength[2] = 1.0
    w.k_count = 3

    for k in range(50):
        w.firing_events = [(0.000, 0), (0.010, 1)]
        w.t = 0.020
        apply_stdp(w)

    o = w.k_orientation[2]
    norm = float(np.linalg.norm(o))
    assert 0.95 <= norm <= 1.05, f"orientation norm {norm:.3f} not in [0.95, 1.05]"
    target = np.array([1.0, 0.0, 0.0])
    cos_angle = float(np.dot(o, target) / norm)
    angle_deg = float(np.degrees(np.arccos(np.clip(cos_angle, -1, 1))))
    assert angle_deg < 5.0, f"orientation deviates by {angle_deg:.1f}° from A→B"
