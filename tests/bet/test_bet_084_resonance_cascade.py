"""BET-084 — Resonance-driven binding cascade to atoms.

T84a  max level >= 4 within 30s sim (seed=42)
T84b  atoms form with >= 2 of 3 seeds
T84c  negative control (resonance=0) does NOT reach level 4
T84d  atom count at 30s >= atom count at 20s
"""
import pytest
import numpy as np
from world.config import WorldConfig
from world.state import World
from world.physics import tick


def _base_cfg(**overrides):
    defaults = dict(
        n_initial_vibrations=150, box_size=(30.0, 30.0, 30.0),
        r_1=5.0, r_2=10.0, freq_tolerance=0.02,
        mol_fusion_enabled=True, resonance_coupling=10.0,
        pair_decay_time=15.0, triad_decay_time=120.0, dt=0.1,
        n_nodes_max=2048, n_vibrations_max=1024, vibration_soft_cap=200,
        repulsion_k=0.0, lambda_gen=0.0003,
        neuron_dynamics_enabled=False, stdp_enabled=False, rng_seed=42,
    )
    defaults.update(overrides)
    return WorldConfig(**defaults)


def _run_and_report(cfg, sim_seconds=15.0, checkpoints=(10.0, 15.0)):
    # JIT warmup
    w = World(WorldConfig(n_initial_vibrations=10, rng_seed=1))
    for _ in range(3):
        tick(w, w.config.dt)
    del w

    world = World(cfg)
    dt = cfg.dt
    results = {}
    total_steps = int(sim_seconds / dt)
    checkpoint_steps = {int(t / dt): t for t in checkpoints}

    for step in range(total_steps):
        tick(world, dt)
        if step + 1 in checkpoint_steps:
            t = checkpoint_steps[step + 1]
            K = world.k_count
            alive = world.k_alive[:K]
            levels = world.k_level[:K][alive]
            counts = {}
            for l in range(1, 15):
                c = int(np.sum(levels == l))
                if c > 0:
                    counts[l] = c
            mx = int(levels.max()) if len(levels) > 0 else 0
            results[t] = {"max_level": mx, "counts": counts}

    return results


def test_T84a_cascade_reaches_atoms():
    """Cascade reaches level 4 (atoms) within 30s."""
    cfg = _base_cfg(rng_seed=42)
    results = _run_and_report(cfg)
    mx = results[15.0]["max_level"]
    print(f"\nT84a: max level = {mx}, counts = {results[15.0]['counts']}")
    assert mx >= 4, f"T84a FAIL: max level {mx} < 4"


def test_T84b_reproducible():
    """Atoms form with >= 2 of 3 seeds."""
    seeds_pass = 0
    for seed in [42, 99, 7]:
        cfg = _base_cfg(rng_seed=seed)
        results = _run_and_report(cfg)
        mx = results[15.0]["max_level"]
        counts = results[15.0]["counts"]
        passed = mx >= 4
        seeds_pass += int(passed)
        print(f"\n  seed={seed}: max={mx} {counts} {'PASS' if passed else 'FAIL'}")
    assert seeds_pass >= 2, f"T84b FAIL: only {seeds_pass}/3 seeds reached atoms"


def test_T84c_negative_control():
    """Without resonance, cascade does NOT reach atoms."""
    cfg = _base_cfg(resonance_coupling=0.0, rng_seed=42)
    results = _run_and_report(cfg)
    mx = results[15.0]["max_level"]
    print(f"\nT84c control: max level = {mx}, counts = {results[15.0]['counts']}")
    assert mx < 4, f"T84c FAIL: control reached level {mx} (should be < 4)"


def test_T84d_atoms_persist():
    """Atom count at 15s >= atom count at 10s (no collapse)."""
    cfg = _base_cfg(rng_seed=42)
    results = _run_and_report(cfg, checkpoints=(20.0, 30.0))
    atoms_10 = results[10.0]["counts"].get(4, 0)
    atoms_15 = results[15.0]["counts"].get(4, 0)
    print(f"\nT84d: atoms at 10s={atoms_10}, 15s={atoms_15}")
    assert atoms_15 >= atoms_10, \
        f"T84d FAIL: atoms collapsed ({atoms_15} < {atoms_10})"
