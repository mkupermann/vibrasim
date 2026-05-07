"""Tests for k_count plateau under sustained input (AP5)."""
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import tick


@pytest.mark.slow
def test_AP5_k_count_plateaus_under_sustained_growth():
    """20-simulated-second run with the growth-amendment config; k_count
    must plateau at no more than 2× peak alive node count.

    Note: pre-Plan A.5 (Tasks 9-13) Numba JIT, the per-tick cost is
    dominated by pure-Python O(k_count) loops, so durations longer than
    ~20 sim-sec take many wall-minutes. AP12 (Task 14) and AP13 (Task 15)
    cover longer-duration verification once JIT is in place.
    """
    cfg = WorldConfig(
        n_initial_vibrations=80, n_vibrations_max=200, n_nodes_max=4096,
        box_size=(60.0, 60.0, 60.0),
        r_1=3.0, r_2=20.0,
        freq_ratio=0.08, freq_tolerance=0.025,
        pair_decay_time=5.0, triad_decay_time=30.0,
        lambda_gen=0.001, lambda_dec=0.0005,
        rng_seed=42,
        neuron_dynamics_enabled=True,
        theta_fire=4.0, n_emit=8, r_integrate=5.0,
        t_refractory=0.05, tau_membrane=0.3, emit_speed=15.0,
        lambda_dec_mol=0.01,
        r_strengthen=10.0,
        emit_band_ratios=(0.08, 1.0, 12.5),
        mol_fusion_enabled=True,
        slot_recycling_enabled=True,
    )
    w = World(cfg)
    burst_pos = np.array([30.0, 30.0, 30.0])

    def _inject_burst():
        free_idx = np.where(~w.s_alive)[0][:5]
        for i in free_idx:
            w.s_pos[i] = burst_pos + w.rng.uniform(-0.5, 0.5, 3)
            w.s_vel[i] = 0
            w.s_freq[i] = 10000.0 + w.rng.uniform(-100, 100)
            w.s_pol[i] = bool(w.rng.random() < 0.5)
            w.s_alive[i] = True
        if len(free_idx):
            w.n_alive = max(w.n_alive, int(free_idx.max()) + 1)

    dt = cfg.dt
    burst_step = max(1, int(0.5 / dt))
    n_ticks = int(20.0 / dt)  # 20 simulated seconds — ratio is stable by here;
                              # longer-duration plateau verification is in
                              # AP12/AP13 (Tasks 14-15) after JIT lands.
    peak_alive = 0
    for k in range(n_ticks):
        if (k + 1) % burst_step == 0:
            _inject_burst()
        tick(w, dt)
        alive_now = int(w.k_alive[:w.k_count].sum())
        peak_alive = max(peak_alive, alive_now)
    final_k_count = w.k_count

    print(f"AP5: peak alive nodes = {peak_alive}, final k_count = {final_k_count}, "
          f"ratio = {final_k_count / max(peak_alive, 1):.2f}")
    assert final_k_count <= 2 * max(peak_alive, 1), (
        f"AP5: k_count {final_k_count} exceeds 2× peak alive {peak_alive} "
        "— slot recycling not effective"
    )
