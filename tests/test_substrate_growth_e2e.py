"""End-to-end integration tests for the substrate growth foundation
(Plan A). These tests instantiate the full physics with all amendments
enabled and verify the F1-F4 acceptance criteria from the foundation
spec §6.1."""
import numpy as np
import pytest
import tomllib
from dataclasses import replace
from pathlib import Path
from world.config import WorldConfig
from world.state import World
from world.physics import tick


def _load_acceptance():
    """Load tests/acceptance.toml — the frozen pre-registration contract.
    F1-F5 read thresholds and held-out seeds from here, never local constants."""
    p = Path(__file__).parent / "acceptance.toml"
    with p.open("rb") as f:
        return tomllib.load(f)


def _growth_config(rng_seed: int = 42) -> WorldConfig:
    """Standard config for growth-foundation acceptance tests.

    Tuned from the original spec for the pure-Python substrate:
    - freq_tolerance=0.025 (between the spec's 0.10 which caused node-buffer
      explosion and 0.005 which produced near-zero binding). Allows binding
      at a sustainable rate so atoms and molecules actually form.
    - n_nodes_max=32768: the node-slot allocator is monotonic (slots never
      recycled); at ~6-7 new nodes/s the spec's 128-slot ceiling is hit in
      under a second. 32768 gives headroom for the full 60-min run.
    - lambda_dec=0.0005 (with lambda_gen=0.001): turns over the vibration
      pool slowly so the periodic burst injector can actually land
      vibrations. With lambda_dec=0 the buffer pinned at n_vibrations_max
      and the F1 test passed trivially with zero atoms or molecules formed.
    - lambda_dec_mol=0.001: Plan A growth-amendment config (≈1-min half-life
      at strength=1; not the legacy-compat default of 0.0; see world/config.py
      annotation).
    """
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
@pytest.mark.skip(
    reason="Blocked on Plan A.5 (substrate performance). F1 at 5 sim-min "
    "currently runs 75+ wall-min due to monotonic allocator + O(k_count) "
    "Python loops; multiple attempts have OOM-killed or hit OS sleep. "
    "After Plan A.5 lands slot recycling + Numba JIT, this test will "
    "complete in <5 wall-min and be re-enabled. Plan A.5's AP13 "
    "independently verifies F1 at full 60 sim-min."
)
def test_F1_sustained_run_does_not_explode_or_collapse():
    """F1: 5-min sim with periodic input maintains a steady-state population.

    Reads acceptance.toml: [F1] thresholds + [seeds] held_out. Bootstrap CI
    lower bound clears in_band_min_pct.
    """
    acceptance = _load_acceptance()
    duration_sim_sec = acceptance["F1"]["duration_sim_sec"]
    in_band_low_mult = acceptance["F1"]["in_band_low_mult"]    # 0.5
    in_band_high_mult = acceptance["F1"]["in_band_high_mult"]  # 2.0
    in_band_min_pct = acceptance["F1"]["in_band_min_pct"]      # 0.80
    held_out_seeds = acceptance["seeds"]["held_out"]

    burst_pos = [30.0, 30.0, 30.0]
    per_seed_pct_in_band = []
    for seed in held_out_seeds:
        w = World(replace(_growth_config(), rng_seed=seed))
        samples = []
        n_minutes = 5
        samples_per_minute = 12
        for _ in range(n_minutes * samples_per_minute):
            _evolve(w, n_seconds=5.0, burst_position=burst_pos, burst_period_s=0.5)
            samples.append(int(w.s_alive.sum()))
        mean_count = float(np.mean(samples))
        in_band = sum(1 for s in samples
                      if in_band_low_mult * mean_count <= s <= in_band_high_mult * mean_count)
        per_seed_pct_in_band.append(in_band / len(samples))

    # Bootstrap 95% CI lower bound
    rng = np.random.default_rng(0)
    n_resamples = 1000
    lower_bounds = []
    boot = np.array([
        rng.choice(per_seed_pct_in_band, size=len(per_seed_pct_in_band), replace=True).mean()
        for _ in range(n_resamples)
    ])
    ci_lower = float(np.percentile(boot, 2.5))
    print(f"F1 stats: per-seed pct in band = {per_seed_pct_in_band}, "
          f"bootstrap 95% CI lower = {ci_lower:.3f}")
    assert ci_lower >= in_band_min_pct, (
        f"F1: bootstrap 95% CI lower bound {ci_lower:.3f} below "
        f"acceptance threshold {in_band_min_pct}"
    )


@pytest.mark.slow
@pytest.mark.skip(reason="Blocked on Plan A.5 substrate performance + Task 10 implementation")
def test_F2_activity_coupled_growth():
    """F2: input only at A → ≥ 3× level-5+ density at A vs distant locations.
    Reads acceptance.toml; runs across acceptance['seeds']['held_out'];
    bootstrap 95% CI lower bound clears acceptance['F2']['ratio_min'].
    """
    acceptance = _load_acceptance()
    A = np.array([15.0, 30.0, 30.0])
    # Adversarial reviewer C9: spatial locality requires multiple distant sites
    B = np.array([45.0, 45.0, 45.0])  # diagonal corner (max separation in periodic box)
    C = np.array([30.0, 30.0, 30.0])  # box centre
    # density at A must be ≥ ratio_min × density at B AND ≥ ratio_min × density at C
    # ... full implementation deferred to Plan A's Task 10
    raise NotImplementedError(
        "F2 stub — see acceptance.toml for thresholds. "
        "Implementation lands in Plan A Task 10 after A.5 unblocks."
    )


@pytest.mark.slow
@pytest.mark.skip(reason="Blocked on Plan A.5 substrate performance + Task 10 implementation")
def test_F3a_weak_structures_decay():
    """F3a: weak structures (strength ≤ acceptance['F3a']['weak_strength_max'])
    decay ≥ acceptance['F3a']['decay_min_pct'] over silent_sim_sec.
    Bootstrap 95% CI lower bound across acceptance['seeds']['held_out'].

    If acceptance fails on the held-out seed grid, the run is a failure to be
    logged in LOGBOOK.md, not retuned. Parameter changes require a CONCEPT
    amendment commit and a fresh held-out seed set.
    """
    acceptance = _load_acceptance()
    raise NotImplementedError("F3a stub — implementation in Plan A Task 10")


@pytest.mark.slow
@pytest.mark.skip(reason="Blocked on Plan A.5 substrate performance + Task 10 implementation")
def test_F3b_strong_structures_persist():
    """F3b: strong structures (strength ≥ acceptance['F3b']['strong_strength_min'])
    persist ≥ acceptance['F3b']['persistence_min_pct'].

    Precondition: at least acceptance['F3b']['n_strong_required'] strong
    structures must form during training. If fewer, the test calls
    pytest.fail() — this is a precondition failure, not a trivial pass.
    """
    acceptance = _load_acceptance()
    raise NotImplementedError("F3b stub — implementation in Plan A Task 10")


@pytest.mark.slow
@pytest.mark.skip(reason="Blocked on Plan A.5 substrate performance + Task 10 implementation")
def test_F4_molecule_fusion():
    """F4: with mol_fusion_enabled=True, sustained input produces level-7+
    molecules in ≥4 of 5 held-out seeds (treatment), and exactly 0 level-7+
    in every seed when mol_fusion_enabled=False (control).
    """
    acceptance = _load_acceptance()
    raise NotImplementedError("F4 stub — implementation in Plan A Task 10")


@pytest.mark.slow
@pytest.mark.skip(reason="Blocked on Plan A.5 substrate performance + Task 10 implementation")
def test_F5_conservation_ledger():
    """F5: |Σ generated − Σ decayed − Σ bound| / Σ generated ≤
    acceptance['F5']['conservation_tolerance_pct'] across the held-out seed
    grid. Per-seed residuals; bootstrap 95% CI upper bound.
    """
    acceptance = _load_acceptance()
    raise NotImplementedError("F5 stub — implementation in Plan A Task 10")
