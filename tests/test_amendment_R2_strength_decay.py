"""Tests for R2: strength-modulated decay for level-5+ molecules."""
import numpy as np
from world.config import WorldConfig
from world.state import World
from world.physics import decay_high_level_nodes


def _make_world_with_molecule(strength: float, level: int = 5) -> World:
    cfg = WorldConfig(
        n_initial_vibrations=0,
        n_vibrations_max=16,
        n_nodes_max=8,
        lambda_dec_mol=1.0,  # aggressive decay rate for tests
        rng_seed=42,
    )
    w = World(cfg)
    w.k_pos[0] = [50.0, 50.0, 50.0]
    w.k_level[0] = level
    w.k_alive[0] = True
    w.k_strength[0] = strength
    w.k_count = 1
    return w


def test_weak_molecule_decays_fast():
    """Strength=1 with lambda_dec_mol=1.0 → ~63% decay over 1s."""
    n_trials = 200
    n_alive_at_end = 0
    for trial in range(n_trials):
        w = _make_world_with_molecule(strength=1.0)
        w.rng = np.random.default_rng(trial)
        for _ in range(60):
            decay_high_level_nodes(w, dt=1.0 / 60.0)
        if w.k_alive[0]:
            n_alive_at_end += 1
    survival_rate = n_alive_at_end / n_trials
    # exp(-1) ≈ 0.368
    assert 0.25 < survival_rate < 0.50, f"weak survival {survival_rate:.3f} out of [0.25, 0.50]"


def test_strong_molecule_persists():
    """Strength=100 with lambda_dec_mol=1.0 → ~99% survival over 1s."""
    n_trials = 200
    n_alive_at_end = 0
    for trial in range(n_trials):
        w = _make_world_with_molecule(strength=100.0)
        w.rng = np.random.default_rng(trial)
        for _ in range(60):
            decay_high_level_nodes(w, dt=1.0 / 60.0)
        if w.k_alive[0]:
            n_alive_at_end += 1
    survival_rate = n_alive_at_end / n_trials
    # exp(-1/100) ≈ 0.99
    assert survival_rate >= 0.95, f"strong survival {survival_rate:.3f} below 0.95"


def test_only_level_5_plus_decay():
    """Atoms (level 4) are not subject to R2 decay — they stay forever."""
    w = _make_world_with_molecule(strength=1.0, level=4)
    for _ in range(600):
        decay_high_level_nodes(w, dt=1.0 / 60.0)
    assert w.k_alive[0], "level-4 atoms must not decay under R2"


def test_disabled_when_lambda_dec_mol_zero():
    """When lambda_dec_mol=0, R2 must be a no-op."""
    cfg = WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=16, n_nodes_max=8,
        lambda_dec_mol=0.0,
    )
    w = World(cfg)
    w.k_pos[0] = [50.0, 50.0, 50.0]
    w.k_level[0] = 5
    w.k_alive[0] = True
    w.k_strength[0] = 1.0
    w.k_count = 1
    for _ in range(600):
        decay_high_level_nodes(w, dt=1.0 / 60.0)
    assert w.k_alive[0], "R2 must not fire when lambda_dec_mol == 0"


def test_molecule_near_firing_atom_gets_strengthened():
    """Each tick, level-5+ molecules within r_strengthen of a firing atom
    should have their strength incremented by dt."""
    from world.physics import neuron_dynamics

    cfg = WorldConfig(
        n_initial_vibrations=0,
        n_vibrations_max=128,
        n_nodes_max=4,
        rng_seed=42,
        neuron_dynamics_enabled=True,
        theta_fire=4.0, n_emit=8, r_integrate=5.0,
        t_refractory=0.05, tau_membrane=0.5,
        r_strengthen=10.0,
    )
    w = World(cfg)
    # Atom at (50, 50, 50) — will fire when input vibrations arrive
    w.k_pos[0] = [50.0, 50.0, 50.0]
    w.k_level[0] = 4
    w.k_alive[0] = True
    # Molecule at (52, 50, 50) — within r_strengthen=10 of atom
    w.k_pos[1] = [52.0, 50.0, 50.0]
    w.k_level[1] = 5
    w.k_alive[1] = True
    w.k_strength[1] = 1.0
    # Molecule at (100, 50, 50) — outside r_strengthen
    w.k_pos[2] = [100.0, 50.0, 50.0]
    w.k_level[2] = 5
    w.k_alive[2] = True
    w.k_strength[2] = 1.0
    w.k_count = 3
    # Seed 5 vibrations at the atom to make it fire
    for i in range(5):
        w.s_pos[i] = [50.0, 50.0, 50.0]
        w.s_freq[i] = 1000.0
        w.s_alive[i] = True
    w.n_alive = 5

    initial_strength_near = w.k_strength[1]
    initial_strength_far = w.k_strength[2]
    neuron_dynamics(w, dt=0.001)

    assert w.k_strength[1] > initial_strength_near, "near molecule must be strengthened"
    assert w.k_strength[2] == initial_strength_far, "far molecule must not be strengthened"
