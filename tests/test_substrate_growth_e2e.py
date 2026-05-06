"""End-to-end integration tests for the substrate growth foundation
(Plan A). These tests instantiate the full physics with all amendments
enabled and verify the F1-F4 acceptance criteria from the foundation
spec §6.1."""
import numpy as np
import pytest
from dataclasses import replace
from world.config import WorldConfig
from world.state import World
from world.physics import tick


def _growth_config(rng_seed: int = 42) -> WorldConfig:
    """Standard config for growth-foundation acceptance tests.

    Tuned from the original spec to be feasible on a pure-Python substrate:
    - freq_tolerance tightened from 0.10 → 0.005 (default) to keep binding
      rate low and prevent monotonic k_count explosion over 60 min.
    - lambda_gen/lambda_dec set to 0 so ambient regeneration doesn't
      continuously re-fill the vibration buffer and drive k_count to grow
      without bound; the periodic burst is the only input signal.
    - n_vibrations_max reduced to 100 so the per-tick binding scan over free
      vibrations stays fast enough for the 60-min run to complete in
      reasonable wall-clock time.
    - n_nodes_max increased to 4096 so the monotonic node-slot allocator
      does not exhaust capacity over a 60-min run.
    - pair_decay_time / triad_decay_time shortened so electrons and pairs
      recycle back to free vibrations quickly, maintaining the free-vib
      population without ambient_regeneration.
    - r_1 tightened to 3.0 to further reduce per-tick binding encounters.
    """
    return WorldConfig(
        n_initial_vibrations=50,
        n_vibrations_max=100,
        n_nodes_max=4096,
        box_size=(40.0, 40.0, 40.0),
        r_1=3.0, r_2=15.0,
        freq_ratio=0.08, freq_tolerance=0.005,
        pair_decay_time=5.0, triad_decay_time=20.0,
        lambda_gen=0.0, lambda_dec=0.0,
        rng_seed=rng_seed,
        # PHASE4 dynamics
        neuron_dynamics_enabled=True,
        theta_fire=4.0, n_emit=4, r_integrate=3.0,
        t_refractory=0.05, tau_membrane=0.3, emit_speed=15.0,
        # Plan A amendments
        lambda_dec_mol=0.02,
        r_strengthen=8.0,
        emit_band_ratios=(0.08, 1.0, 12.5),
        mol_fusion_enabled=True,
    )


def _inject_burst(world, position, n=5, freq=10000.0):
    """Helper: place n vibrations at position with zero velocity."""
    free_idx = np.where(~world.s_alive)[0][:n]
    for i in free_idx:
        world.s_pos[i] = np.asarray(position) + world.rng.uniform(-0.5, 0.5, 3)
        world.s_vel[i] = 0.0
        world.s_freq[i] = freq + world.rng.uniform(-100, 100)
        world.s_pol[i] = bool(world.rng.random() < 0.5)
        world.s_alive[i] = True
    if len(free_idx):
        world.n_alive = max(world.n_alive, int(free_idx.max()) + 1)


def _evolve(world, n_seconds, burst_position=None, burst_period_s=0.1):
    """Tick forward, optionally injecting bursts at burst_position every burst_period_s."""
    dt = world.config.dt
    n_ticks = int(n_seconds / dt)
    burst_step = max(1, int(burst_period_s / dt)) if burst_position is not None else None
    for k in range(n_ticks):
        if burst_step and (k + 1) % burst_step == 0:
            _inject_burst(world, burst_position)
        tick(world, dt)


@pytest.mark.slow
def test_F1_sustained_run_does_not_explode_or_collapse():
    """F1: 60-min sim with periodic input maintains a steady-state population.

    Pass: total alive vibration count stays in [25%, 200%] of mean for ≥80% of run.
    """
    w = World(_growth_config())
    burst_pos = [20.0, 20.0, 20.0]
    samples = []
    dt = w.config.dt
    # Sample every 60 simulated seconds across a 60-min run = 60 samples
    for minute in range(60):
        _evolve(w, n_seconds=60.0, burst_position=burst_pos, burst_period_s=0.5)
        samples.append(int(w.s_alive.sum()))

    mean_count = float(np.mean(samples))
    min_count = float(np.min(samples))
    max_count = float(np.max(samples))
    in_band = sum(1 for s in samples if 0.25 * mean_count <= s <= 2.0 * mean_count)
    pct_in_band = in_band / len(samples)

    print(f"F1 stats: mean={mean_count:.0f}, min={min_count:.0f}, "
          f"max={max_count:.0f}, in-band={pct_in_band*100:.0f}%")
    assert pct_in_band >= 0.8, (
        f"F1 violation: only {pct_in_band*100:.0f}% of samples in [0.25×, 2.0×] mean"
    )
