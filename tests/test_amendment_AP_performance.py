"""Plan A.5 performance acceptance tests (AP12, AP13)."""
import time
import numpy as np
import pytest
from dataclasses import replace
from world.config import WorldConfig
from world.state import World
from world.physics import tick


def _growth_config(rng_seed: int = 42) -> WorldConfig:
    """Standard growth-amendment config — mirrors the one in
    tests/test_substrate_growth_e2e.py."""
    return WorldConfig(
        n_initial_vibrations=80,
        n_vibrations_max=200,
        n_nodes_max=32768,
        box_size=(60.0, 60.0, 60.0),
        r_1=3.0, r_2=20.0,
        freq_ratio=0.08,
        freq_tolerance=0.025,
        pair_decay_time=5.0,
        triad_decay_time=30.0,
        lambda_gen=0.001,
        lambda_dec=0.0005,
        rng_seed=rng_seed,
        # PHASE4 dynamics
        neuron_dynamics_enabled=True,
        theta_fire=4.0, n_emit=8, r_integrate=5.0,
        t_refractory=0.05, tau_membrane=0.3, emit_speed=15.0,
        # Plan A amendments
        lambda_dec_mol=0.001,
        r_strengthen=10.0,
        emit_band_ratios=(0.08, 1.0, 12.5),
        mol_fusion_enabled=True,
        # Plan A.5 perf flags (default True; explicit for clarity)
        slot_recycling_enabled=True,
        numba_jit_enabled=True,
    )


def _inject_burst(world, position, n=5, freq=10000.0):
    free_idx = np.where(~world.s_alive)[0][:n]
    for i in free_idx:
        world.s_pos[i] = np.asarray(position) + world.rng.uniform(-0.5, 0.5, 3)
        world.s_vel[i] = 0
        world.s_freq[i] = freq + world.rng.uniform(-100, 100)
        world.s_pol[i] = bool(world.rng.random() < 0.5)
        world.s_alive[i] = True
    if len(free_idx):
        world.n_alive = max(world.n_alive, int(free_idx.max()) + 1)


@pytest.mark.slow
def test_AP12_per_tick_wall_cost_bounded():
    """5-min sim with growth-amendment config; wall-clock per simulated
    second stays within 5x of the minimum across the run.

    Pre-A.5: ratio was >100x as k_count grew. Post-A.5 with slot recycling
    and JIT, the ratio should be ~2-5x.
    """
    w = World(_growth_config())
    burst_pos = np.array([30.0, 30.0, 30.0])
    dt = w.config.dt

    # Warm up the JIT: trigger compilation of every hot path before timing.
    # Numba caches compiled code in __pycache__/, but the first call still
    # hits the dispatch + signature-check overhead. One warmup tick puts
    # all five JIT'd functions through their first call.
    tick(w, dt)

    burst_step = max(1, int(0.5 / dt))
    n_seconds = 5 * 60  # 5 sim-min
    wall_per_sim_sec = []
    ticks_per_sec = int(1.0 / dt)
    for sim_sec in range(n_seconds):
        t_start = time.time()
        for k in range(ticks_per_sec):
            if (k + 1) % burst_step == 0:
                _inject_burst(w, burst_pos)
            tick(w, dt)
        wall_per_sim_sec.append(time.time() - t_start)

    min_wall = min(wall_per_sim_sec)
    max_wall = max(wall_per_sim_sec)
    median_wall = float(np.median(wall_per_sim_sec))
    print(f"AP12: wall-clock per sim-sec — min={min_wall:.3f}s, "
          f"median={median_wall:.3f}s, max={max_wall:.3f}s, "
          f"max/min ratio={max_wall / max(min_wall, 1e-6):.2f}x")
    assert max_wall <= 5.0 * min_wall, (
        f"AP12: wall ratio {max_wall / max(min_wall, 1e-6):.2f}x exceeds bound 5x"
    )
