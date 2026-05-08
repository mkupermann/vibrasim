"""G6 — bridge atom-to-atom direct charge propagation.

CONCEPT §10.8 G5 outcome: the M4 chain is blocked at vibration-travel from
firing pre-atoms across bridges to post-atoms in 1 sim-sec test phase. G6
adds a substrate amendment in which a strong oriented bridge near a firing
pre-atom deposits charge directly into the post-atom along its orientation,
without requiring vibration travel.

Default off via cfg.bridge_atom_propagation_enabled = False.

G6-1: flag off → behaviour unchanged (regression).
G6-2: flag on + firing pre-atom + strong oriented bridge near A pointing at
      B → B receives charge in same tick.
G6-3: flag on + firing pre-atom + WEAK bridge → no propagation.
G6-4: flag on + firing pre-atom + bridge orientation NOT pointing toward
      any atom → no propagation.
G6-5: flag on + firing pre-atom + bridge → post-atom fires in next tick
      (full chain: charge deposit → integrate-and-fire → fire).
"""
import numpy as np
import pytest

from world.config import WorldConfig
from world.state import World
from world.physics import (
    apply_bridge_atom_propagation, neuron_dynamics, tick,
)


def _make_world(g6_on: bool = True) -> World:
    cfg = WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=128, n_nodes_max=64,
        box_size=(60.0, 60.0, 60.0),
        rng_seed=42,
        stdp_enabled=True,
        r_bridge=8.0,
        synaptic_transmission_threshold=1.0,
        bridge_atom_propagation_enabled=g6_on,
        bridge_atom_propagation_strength=4.0,
        # Strong threshold so propagation triggers immediate fire when on.
        neuron_dynamics_enabled=True,
        theta_fire=2.0,
        n_emit=4,
        r_integrate=5.0,
        t_refractory=0.05,
        tau_membrane=0.3,
    )
    return World(cfg)


def _seed_atom(w: World, idx: int, pos, freq: float = 1000.0,
               polarity: bool = True):
    w.k_pos[idx] = pos
    w.k_level[idx] = 4
    w.k_alive[idx] = True
    w.k_freq[idx] = freq
    w.k_pol[idx] = polarity
    w.k_charge[idx] = 0.0
    w.k_count = max(w.k_count, idx + 1)


def _seed_bridge(w: World, idx: int, pos, orientation, strength: float = 100.0):
    w.k_pos[idx] = pos
    w.k_level[idx] = 5
    w.k_alive[idx] = True
    w.k_freq[idx] = 1000.0
    w.k_pol[idx] = True
    w.k_strength[idx] = strength
    o = np.asarray(orientation, dtype=np.float64)
    w.k_orientation[idx] = o / np.linalg.norm(o)
    w.k_count = max(w.k_count, idx + 1)


def test_G6_default_off():
    """Default flag is False — no propagation events."""
    w = _make_world(g6_on=False)
    _seed_atom(w, 0, (10.0, 10.0, 10.0))
    _seed_atom(w, 1, (28.0, 10.0, 10.0))
    _seed_bridge(w, 2, (15.0, 10.0, 10.0), (1.0, 0.0, 0.0))
    w.firing_events = [(w.t, 0)]
    n_events = apply_bridge_atom_propagation(w, dt=1.0 / 60)
    assert n_events == 0, "G6-1: flag off must produce no events"
    assert float(w.k_charge[1]) == 0.0


def test_G6_strong_aligned_bridge_propagates():
    """Strong oriented bridge near firing atom A pointing at B → B charged."""
    w = _make_world(g6_on=True)
    _seed_atom(w, 0, (10.0, 10.0, 10.0))             # pre A (fires)
    _seed_atom(w, 1, (28.0, 10.0, 10.0))             # post B (target along +x)
    _seed_bridge(w, 2, (15.0, 10.0, 10.0), (1.0, 0.0, 0.0), strength=100.0)
    # B at distance 18 from M=(15,10,10) along (1,0,0) → in samples=1 sphere
    # with r_bridge=8 (post-centre at 15+8=23, B at 28 → distance 5, inside).
    w.firing_events = [(w.t, 0)]
    n_events = apply_bridge_atom_propagation(w, dt=1.0 / 60)
    assert n_events == 1, f"G6-2: expected 1 event, got {n_events}"
    assert float(w.k_charge[1]) == 4.0, (
        f"G6-2: expected +4.0 charge on B, got {w.k_charge[1]}"
    )


def test_G6_weak_bridge_does_not_propagate():
    """Bridge below synaptic_transmission_threshold → no propagation."""
    w = _make_world(g6_on=True)
    _seed_atom(w, 0, (10.0, 10.0, 10.0))
    _seed_atom(w, 1, (28.0, 10.0, 10.0))
    _seed_bridge(w, 2, (15.0, 10.0, 10.0), (1.0, 0.0, 0.0), strength=0.5)
    w.firing_events = [(w.t, 0)]
    n_events = apply_bridge_atom_propagation(w, dt=1.0 / 60)
    assert n_events == 0, "G6-3: weak bridge must NOT propagate"
    assert float(w.k_charge[1]) == 0.0


def test_G6_unaligned_bridge_does_not_reach_target():
    """Bridge orientation pointing away from any atom → no propagation."""
    w = _make_world(g6_on=True)
    _seed_atom(w, 0, (10.0, 10.0, 10.0))
    _seed_atom(w, 1, (28.0, 10.0, 10.0))
    # Bridge pointing in -y direction; sample at (15, 10-8, 10) = (15, 2, 10).
    # No atom near (15, 2, 10) within r_bridge=8.
    _seed_bridge(w, 2, (15.0, 10.0, 10.0), (0.0, -1.0, 0.0), strength=100.0)
    w.firing_events = [(w.t, 0)]
    n_events = apply_bridge_atom_propagation(w, dt=1.0 / 60)
    assert n_events == 0, "G6-4: orientation must point toward target atom"
    assert float(w.k_charge[1]) == 0.0


def test_G6_full_chain_post_fires_next_tick():
    """A fires (tick T) → G6 deposits charge into B (tick T) → B fires (tick T+1)."""
    w = _make_world(g6_on=True)
    _seed_atom(w, 0, (10.0, 10.0, 10.0))
    _seed_atom(w, 1, (28.0, 10.0, 10.0))
    _seed_bridge(w, 2, (15.0, 10.0, 10.0), (1.0, 0.0, 0.0), strength=100.0)

    # Tick 1: manually trigger A firing by directly populating firing_events.
    # apply_bridge_atom_propagation deposits charge on B.
    w.firing_events = [(w.t, 0)]
    apply_bridge_atom_propagation(w, dt=1.0 / 60)
    assert float(w.k_charge[1]) == 4.0

    # Tick T+1: neuron_dynamics processes B; charge ≥ theta_fire → B fires.
    w.t += 1.0 / 60
    n_fires_before = len(w.firing_events)
    neuron_dynamics(w, dt=1.0 / 60)
    n_fires_after = len(w.firing_events)
    assert n_fires_after > n_fires_before, (
        f"G6-5: B should have fired in tick T+1; firing_events grew "
        f"{n_fires_before} → {n_fires_after}"
    )
    fired_atoms = {ai for _t, ai in w.firing_events[n_fires_before:]}
    assert 1 in fired_atoms, (
        f"G6-5: atom 1 (B) should be among the new fires; got {fired_atoms}"
    )


def test_G6_default_value_in_world_config():
    """Default cfg.bridge_atom_propagation_enabled is False."""
    cfg = WorldConfig()
    assert cfg.bridge_atom_propagation_enabled is False
