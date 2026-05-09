"""G13 — bidirectional bridges + cross-modal generative recall.

Novelty claim:
    Continuous-physics neural substrate + Hebbian STDP-formed bridges +
    bidirectional propagation. The same molecule that routed visual→audio
    during training routes audio→visual at recall time, without a separate
    generative model.

    Distinguishing from related work:
    - Hopfield 1982: symmetric weights but discrete units, not 3D-space
      molecule bridges with explicit orientation.
    - Sayama Swarm Chemistry 2009: categorical-label binding, no plasticity
      and no bidirectional routing.
    - SNN STDP literature: typically unidirectional synapses; bidirectional
      requires explicit reciprocal connection learning.
    - Neural CA (Mordvintsev): trained pixel rules, not Hebbian-emergent.

Tests:
  G13-1: bidirectional flag default-off — preserves existing behaviour.
  G13-2: trained bridge fires post-atom from BOTH endpoints when flag on.
  G13-3: cross-modal generative — train (video→audio) bridge, fire the
         audio-side atom alone, measure that the video-side atom receives
         charge. This is the audio-input → visual-output novelty.
"""
import numpy as np
import pytest

from world.config import WorldConfig
from world.state import World
from world.physics import apply_bridge_atom_propagation


def _make_world(bidirectional: bool) -> World:
    cfg = WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=64, n_nodes_max=64,
        box_size=(60.0, 60.0, 60.0),
        rng_seed=42,
        stdp_enabled=True,
        r_bridge=8.0,
        synaptic_transmission_threshold=1.0,
        synaptic_post_search_samples=1,
        bridge_atom_propagation_enabled=True,
        bridge_atom_propagation_strength=4.0,
        neuron_dynamics_enabled=True,
        theta_fire=2.0,
        bidirectional_bridges=bidirectional,
    )
    return World(cfg)


def _seed_atom(w: World, idx: int, pos):
    w.k_pos[idx] = pos
    w.k_level[idx] = 4
    w.k_alive[idx] = True
    w.k_freq[idx] = 1000.0
    w.k_pol[idx] = (idx % 2 == 0)
    w.k_charge[idx] = 0.0
    w.k_count = max(w.k_count, idx + 1)


def _seed_bridge(w: World, idx: int, pos, orientation, strength=100.0):
    w.k_pos[idx] = pos
    w.k_level[idx] = 5
    w.k_alive[idx] = True
    w.k_freq[idx] = 1000.0
    w.k_pol[idx] = True
    w.k_strength[idx] = strength
    o = np.asarray(orientation, dtype=np.float64)
    w.k_orientation[idx] = o / np.linalg.norm(o)
    w.k_count = max(w.k_count, idx + 1)


def test_G13_default_unidirectional():
    """Bidirectional flag default-off — only forward propagation."""
    w = _make_world(bidirectional=False)
    # A at (10,10,10), B at (26,10,10), bridge at (18,10,10) pointing +x.
    # Forward: A fires → B charges via bridge. Reverse: B firing → A NOT.
    _seed_atom(w, 0, (10.0, 10.0, 10.0))
    _seed_atom(w, 1, (26.0, 10.0, 10.0))
    _seed_bridge(w, 2, (18.0, 10.0, 10.0), (1.0, 0.0, 0.0), strength=100.0)

    # Reverse direction: B fires (post end), default-off should NOT
    # propagate to A.
    w.firing_events = [(w.t, 1)]  # B fires
    n = apply_bridge_atom_propagation(w, dt=1.0 / 60)
    assert n == 0, f"unidirectional: B firing must NOT charge A; got {n} events"
    assert float(w.k_charge[0]) == 0.0


def test_G13_bidirectional_routes_both_ends():
    """When the flag is on, a firing atom at either end of the bridge
    charges the atom at the other end."""
    w = _make_world(bidirectional=True)
    _seed_atom(w, 0, (10.0, 10.0, 10.0))
    _seed_atom(w, 1, (26.0, 10.0, 10.0))
    _seed_bridge(w, 2, (18.0, 10.0, 10.0), (1.0, 0.0, 0.0), strength=100.0)

    # Fire A — forward direction: A → B
    w.firing_events = [(w.t, 0)]
    n_forward = apply_bridge_atom_propagation(w, dt=1.0 / 60)
    assert n_forward >= 1
    assert float(w.k_charge[1]) > 0, "bidir: A → B charge expected"
    forward_charge_b = float(w.k_charge[1])

    # Reset charges, fire B — reverse direction: B → A
    w.k_charge[:] = 0.0
    w.firing_events = [(w.t, 1)]
    n_reverse = apply_bridge_atom_propagation(w, dt=1.0 / 60)
    assert n_reverse >= 1, "bidir: B firing must propagate via bridge"
    assert float(w.k_charge[0]) > 0, (
        "bidir: B → A charge expected (cross-modal generative recall)"
    )

    # Both directions deliver the same propagation strength.
    assert abs(float(w.k_charge[0]) - forward_charge_b) < 1e-6


def test_G13_cross_modal_generative_recall():
    """Demonstrate the substrate's novelty: a bridge formed during
    visual→audio training also routes audio→visual at recall time.

    Setup: video atom V at video-port position, audio atom A at audio-
    port position, bridge between them oriented V→A. (This is exactly
    what STDP would form if V and A fired causally during training.)

    Recall: fire ONLY the audio atom A. With bidirectional bridges,
    the bridge propagates back to V. Without, V stays cold.
    """
    w_uni = _make_world(bidirectional=False)
    w_bi = _make_world(bidirectional=True)

    # Video atom V at (5, 5, 15) — video-port-like
    # Audio atom A at (5, 5, 5) — audio-port-like
    # Bridge midway at (5, 5, 10), oriented V→A = (0, 0, -1).
    # Each atom is 5 units from the bridge — inside r_bridge=8 so
    # apply_bridge_atom_propagation finds them as the firing atom.
    for w in (w_uni, w_bi):
        _seed_atom(w, 0, (5.0, 5.0, 15.0))   # V
        _seed_atom(w, 1, (5.0, 5.0, 5.0))    # A
        _seed_bridge(w, 2, (5.0, 5.0, 10.0),
                     (0.0, 0.0, -1.0), strength=100.0)

    # Cross-modal recall probe: fire A only.
    for w in (w_uni, w_bi):
        w.firing_events = [(w.t, 1)]
        apply_bridge_atom_propagation(w, dt=1.0 / 60)

    visual_charge_uni = float(w_uni.k_charge[0])
    visual_charge_bi = float(w_bi.k_charge[0])

    # Unidirectional substrate: audio cannot drive visual recall.
    assert visual_charge_uni == 0.0, (
        f"uni baseline: audio→visual must be 0; got {visual_charge_uni}"
    )
    # Bidirectional substrate: audio-only stimulus charges the visual
    # atom — generative cross-modal recall works.
    assert visual_charge_bi > 0.0, (
        f"bidir generative: audio→visual charge expected; got {visual_charge_bi}"
    )


def test_G13_default_in_world_config():
    """Default cfg.bidirectional_bridges is False — no behaviour change."""
    cfg = WorldConfig()
    assert cfg.bidirectional_bridges is False
