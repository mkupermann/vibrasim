"""Tests for STDP asymmetric LTP/LTD (BS4)."""
import numpy as np
from world.config import WorldConfig
from world.state import World
from world.physics import apply_stdp


def test_BS4_alternating_pairs_net_to_baseline():
    """50 alternating cycles of A→B (LTP) then B→A (LTD): final strength
    should stay within [80%, 130%] of initial 100.0.

    Per cycle (after the first LTP gives the bridge an orientation):
    - LTP gain  = delta_LTP * exp(-Δt/tau_LTP) = 1.0 * exp(-0.5) ≈ 0.6065
    - LTD loss  = delta_LTD * exp(-Δt/tau_LTD) = 0.5 * exp(-0.5) ≈ 0.3033
    - Net per cycle ≈ +0.303
    Over 50 cycles, expected final ≈ 115. Within [80, 130]."""
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
    w.k_strength[2] = 100.0  # start strong so LTD can take effect
    w.k_count = 3

    initial_strength = float(w.k_strength[2])

    for k in range(50):
        # A→B: causal, LTP
        w.firing_events = [(0.000, 0), (0.010, 1)]
        w.t = 0.020
        apply_stdp(w)
        # B→A: anti-causal w.r.t. the bridge's accumulated orientation, LTD
        w.firing_events = [(0.000, 1), (0.010, 0)]
        w.t = 0.020
        apply_stdp(w)

    final_strength = float(w.k_strength[2])
    assert 0.80 * initial_strength <= final_strength <= 1.30 * initial_strength, (
        f"BS4: final strength {final_strength:.2f} not in [80, 130]"
    )
