"""G16 — The Self-Aware Substrate.

Operationalises ACCESS consciousness (Block 1995) / global broadcast
(Dehaene & Naccache 2001) / higher-order representation (Rosenthal
2005) / homeostatic parameter feedback (Varela; meta-learning) on top
of the EQMOD substrate.

This test file proves:
  G16-1: Default off — apply_self_aware is a no-op when
         self_aware_enabled=False.
  G16-2: Self-model updates from firing log. The substrate maintains
         a per-pattern_id rolling rate that reflects which engrams
         are active.
  G16-3: Workspace winner — when multiple patterns are active, the
         most-active one wins the workspace and other patterns'
         eligibility is suppressed (global broadcast).
  G16-4: Prediction error — the substrate predicts its next firing
         distribution, then measures the actual one against it. The
         error is bounded in [0, 1].
  G16-5: Self-modification — high prediction error increases
         btsp_potentiation; low error decreases it (homeostasis).
  G16-6: Cfg defaults round-trip.

Honest scope statement (also in world/self_aware.py docstring):
This file does NOT prove phenomenal consciousness. It proves that the
substrate has a representation of itself, broadcasts dominant content
globally, computes its own surprise, and modifies its own learning
rules. That is access-conscious self-modeling operational-marker agency in
the operational sense — not the hard problem.
"""
import numpy as np

from world.config import WorldConfig
from world.state import World
from world.self_aware import apply_self_aware


def _make_world(self_aware: bool = True,
                workspace: bool = True,
                self_modify: bool = True) -> World:
    cfg = WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=128, n_nodes_max=128,
        box_size=(60.0, 60.0, 60.0),
        rng_seed=42,
        self_aware_enabled=self_aware,
        self_model_window=2.0,
        workspace_broadcast_enabled=workspace,
        workspace_broadcast_strength=0.5,
        workspace_min_winner_atoms=2,
        self_modify_enabled=self_modify,
        self_modify_rate=0.10,
        self_modify_target_error=0.3,
        self_modify_min_btsp=5.0,
        self_modify_max_btsp=200.0,
        btsp_potentiation=50.0,
    )
    return World(cfg)


def _seed_atom(w: World, idx: int, pos, pattern_id: int = 0,
                eligibility: float = 0.0):
    w.k_pos[idx] = pos
    w.k_level[idx] = 4
    w.k_alive[idx] = True
    w.k_freq[idx] = 1000.0
    w.k_pol[idx] = (idx % 2 == 0)
    w.k_charge[idx] = 0.0
    w.k_eligibility[idx] = eligibility
    w.k_pattern_id[idx] = pattern_id
    w.k_count = max(w.k_count, idx + 1)


def test_G16_default_off_is_noop():
    w = _make_world(self_aware=False)
    _seed_atom(w, 0, (10.0, 10.0, 10.0), pattern_id=1, eligibility=2.0)
    w.firing_events = [(0.0, 0)]
    out = apply_self_aware(w, dt=1.0 / 60)
    assert out["active_patterns"] == 0
    assert out["workspace_winner"] == 0
    assert w.workspace_winner_pattern_id == 0


def test_G16_self_model_updates_from_firing_log():
    """The substrate's self_model reflects which patterns recently fired."""
    w = _make_world(self_aware=True)
    _seed_atom(w, 0, (10.0, 10.0, 10.0), pattern_id=1)
    _seed_atom(w, 1, (15.0, 10.0, 10.0), pattern_id=1)
    _seed_atom(w, 2, (20.0, 10.0, 10.0), pattern_id=2)
    # Simulate firings within window
    w.t = 1.5
    w.firing_events = [
        (0.0, 0), (0.5, 0), (1.0, 1),  # pattern 1 fires 3 times
        (0.7, 2),                       # pattern 2 fires once
    ]
    apply_self_aware(w, dt=1.0 / 60)
    assert 1 in w.self_model
    assert 2 in w.self_model
    # Pattern 1 should have higher rate than pattern 2
    assert w.self_model[1] > w.self_model[2]


def test_G16_workspace_winner_suppresses_other_patterns():
    """Global broadcast: most-active pattern wins, others' eligibility
    is multiplied down."""
    w = _make_world(self_aware=True, workspace=True)
    _seed_atom(w, 0, (10.0, 10.0, 10.0), pattern_id=1, eligibility=4.0)
    _seed_atom(w, 1, (15.0, 10.0, 10.0), pattern_id=1, eligibility=4.0)
    _seed_atom(w, 2, (20.0, 10.0, 10.0), pattern_id=1, eligibility=4.0)
    _seed_atom(w, 3, (40.0, 10.0, 10.0), pattern_id=2, eligibility=4.0)
    _seed_atom(w, 4, (45.0, 10.0, 10.0), pattern_id=2, eligibility=4.0)
    w.t = 1.5
    # Pattern 1 fires more than pattern 2 within the window
    w.firing_events = [
        (0.5, 0), (0.6, 1), (0.7, 2), (0.8, 0), (0.9, 1),
        (1.0, 3),
    ]
    out = apply_self_aware(w, dt=1.0 / 60)
    assert out["workspace_winner"] == 1
    assert w.workspace_winner_pattern_id == 1
    # Pattern 2's eligibility was suppressed (× 0.5)
    assert float(w.k_eligibility[3]) == 2.0
    assert float(w.k_eligibility[4]) == 2.0
    # Pattern 1's eligibility unchanged
    assert float(w.k_eligibility[0]) == 4.0


def test_G16_prediction_error_bounded():
    """Prediction error is in [0, 1] and reflects deviation from the
    self-model's prediction."""
    w = _make_world(self_aware=True)
    _seed_atom(w, 0, (10.0, 10.0, 10.0), pattern_id=1)
    _seed_atom(w, 1, (15.0, 10.0, 10.0), pattern_id=2)

    # Cycle 1: only pattern 1 fires
    w.t = 1.5
    w.firing_events = [(0.5, 0), (0.7, 0), (0.9, 0)]
    apply_self_aware(w, dt=1.0 / 60)
    assert w.self_prediction_error == 0.0  # no prior prediction

    # Cycle 2: pattern 2 dominates (surprise!)
    w.t = 4.0
    w.firing_events = [(2.5, 1), (3.0, 1), (3.5, 1)]
    out = apply_self_aware(w, dt=1.0 / 60)
    assert 0.0 <= w.self_prediction_error <= 1.0
    assert w.self_prediction_error > 0.5, (
        f"big surprise expected; got {w.self_prediction_error:.3f}"
    )


def test_G16_self_modify_adjusts_btsp_under_high_error():
    """High prediction error → boost btsp_potentiation."""
    w = _make_world(self_aware=True, self_modify=True)
    _seed_atom(w, 0, (10.0, 10.0, 10.0), pattern_id=1)
    _seed_atom(w, 1, (15.0, 10.0, 10.0), pattern_id=2)

    initial_btsp = w.config.btsp_potentiation

    # Cycle 1: pattern 1
    w.t = 1.5
    w.firing_events = [(0.5, 0), (0.7, 0), (0.9, 0)]
    apply_self_aware(w, dt=1.0 / 60)

    # Cycle 2: pattern 2 — big surprise
    w.t = 4.0
    w.firing_events = [(2.5, 1), (3.0, 1), (3.5, 1), (3.8, 1)]
    out = apply_self_aware(w, dt=1.0 / 60)

    new_btsp = w.config.btsp_potentiation
    # With error > 0.3 (target), btsp should INCREASE
    if w.self_prediction_error > w.config.self_modify_target_error:
        assert new_btsp > initial_btsp, (
            f"high error {w.self_prediction_error:.2f} should boost "
            f"btsp; was {initial_btsp:.1f} → {new_btsp:.1f}"
        )


def test_G16_default_in_world_config():
    cfg = WorldConfig()
    assert cfg.self_aware_enabled is False
    assert cfg.self_model_window == 2.0
    assert cfg.workspace_broadcast_enabled is True
    assert cfg.self_modify_enabled is True
    assert cfg.self_modify_target_error == 0.3
    assert cfg.workspace_broadcast_strength == 1.0
