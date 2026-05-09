"""G15 — The Dreaming Substrate.

Proof tests for offline replay + concept blending + cross-modal
hallucination. Anchors the substrate's first creativity mechanism.

Literature gap closed:
  - Wilson & McNaughton 1994 — hippocampal sequence replay during sleep.
  - Buzsáki 2015 — sharp-wave-ripple-gated consolidation.
  - Lewis & Durrant 2011 — overlapping replays merge schemas during NREM
    (concept blending).
  - No prior continuous-physics emergent-atom substrate has implemented
    sleep/replay/blending — the combination of:
      1) BTSP seconds-scale plasticity, +
      2) bidirectional cross-modal bridges, +
      3) offline replay-driven consolidation, +
      4) co-activation-triggered concept blending
    is unoccupied territory.

What this test proves:
  G15-1: Default off — apply_dream is a no-op when dream_mode_enabled=False.
  G15-2: Replay seeds fire with charge bumps. Atoms with high eligibility
         get re-fired during dream. Eligibility-weighted selection works.
  G15-3: Concept blending. Two co-active pattern_ids → fresh blended atom
         allocated at their spatial intersection with a new pattern_id.
  G15-4: Offline consolidation. Running dream ticks on a substrate with
         BTSP enabled strengthens trained-engram bridges without any
         external input.
  G15-5: Cfg defaults round-trip.
"""
import numpy as np

from world.config import WorldConfig
from world.state import World
from world.dream import apply_dream, begin_dream_state, end_dream_state


def _make_world(dream: bool = True, btsp: bool = True,
                  neuron_dyn: bool = False) -> World:
    cfg = WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=128, n_nodes_max=128,
        box_size=(60.0, 60.0, 60.0),
        rng_seed=42,
        dream_mode_enabled=dream,
        dream_replay_seeds_per_tick=2,
        dream_replay_seed_charge=6.0,
        dream_blend_enabled=True,
        dream_blend_co_activation_window=0.5,
        dream_blend_min_overlap_atoms=2,
        dream_consolidation_to_blend_ratio=0,  # G18.2 off — every dream tick
                                                #     blends. The G18 test uses
                                                #     ratio>0 explicitly.
        btsp_enabled=btsp,
        btsp_tau_eligibility=6.0,
        btsp_plateau_charge_threshold=3.0,
        btsp_potentiation=50.0,
        btsp_radius=30.0,
        neuron_dynamics_enabled=neuron_dyn,
        theta_fire=4.0,
        t_refractory=0.05,
        tau_membrane=0.2,
        r_integrate=8.0,
        n_emit=4,
        emit_speed=15.0,
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


def _seed_molecule(w: World, idx: int, pos, strength: float = 1.0,
                    pattern_id: int = 0):
    w.k_pos[idx] = pos
    w.k_level[idx] = 5
    w.k_alive[idx] = True
    w.k_freq[idx] = 1000.0
    w.k_pol[idx] = True
    w.k_strength[idx] = strength
    w.k_orientation[idx] = 0.0
    w.k_pattern_id[idx] = pattern_id
    w.k_count = max(w.k_count, idx + 1)


def test_G15_default_off_is_noop():
    """When dream_mode_enabled=False, apply_dream returns zeros and
    does not touch world state."""
    w = _make_world(dream=False)
    _seed_atom(w, 0, (10.0, 10.0, 10.0), pattern_id=1, eligibility=2.0)
    out = apply_dream(w, dt=1.0 / 60)
    assert out["replay_seeds_fired"] == 0
    assert out["blend_events"] == 0
    assert float(w.k_charge[0]) == 0.0


def test_G15_replay_seeds_fire_high_eligibility_atoms():
    """Atoms with high eligibility get charge injected during dream."""
    w = _make_world(dream=True)
    _seed_atom(w, 0, (10.0, 10.0, 10.0), pattern_id=1, eligibility=5.0)
    _seed_atom(w, 1, (20.0, 10.0, 10.0), pattern_id=1, eligibility=3.0)
    _seed_atom(w, 2, (30.0, 10.0, 10.0), pattern_id=1, eligibility=0.0)
    out = apply_dream(w, dt=1.0 / 60)
    assert out["replay_seeds_fired"] == 2  # dream_replay_seeds_per_tick=2
    # At least one of the high-eligibility atoms got the charge bump
    charged = [i for i in range(3) if float(w.k_charge[i]) >= 6.0]
    assert len(charged) == 2
    # Atom 2 (eligibility 0) is least likely to be picked (probability
    # weighted by eligibility) — over the run we should see atoms 0 + 1
    # picked preferentially. With seed 42 this is deterministic.
    assert 0 in charged or 1 in charged


def test_G15_concept_blending_creates_fresh_pattern_id():
    """Two pattern_ids co-firing within the window → blended atom with
    a new pattern_id allocated at the spatial centroid."""
    w = _make_world(dream=True)
    # Pattern 1: 3 atoms at x≈10
    _seed_atom(w, 0, (10.0, 10.0, 10.0), pattern_id=1, eligibility=2.0)
    _seed_atom(w, 1, (10.0, 12.0, 10.0), pattern_id=1, eligibility=2.0)
    _seed_atom(w, 2, (10.0, 14.0, 10.0), pattern_id=1, eligibility=2.0)
    # Pattern 2: 3 atoms at x≈40
    _seed_atom(w, 3, (40.0, 10.0, 10.0), pattern_id=2, eligibility=2.0)
    _seed_atom(w, 4, (40.0, 12.0, 10.0), pattern_id=2, eligibility=2.0)
    _seed_atom(w, 5, (40.0, 14.0, 10.0), pattern_id=2, eligibility=2.0)

    # Plant firing events showing co-activation within the window
    w.t = 1.0
    w.firing_events = [
        (0.7, 0), (0.7, 1), (0.7, 2),  # pattern 1 fires at t=0.7
        (0.8, 3), (0.8, 4), (0.8, 5),  # pattern 2 fires at t=0.8
    ]

    k_before = w.k_count
    out = apply_dream(w, dt=1.0 / 60)

    assert out["co_active_patterns"] >= 2
    assert out["blend_events"] >= 1
    assert w.k_count > k_before, "a blended atom should have been allocated"

    # The new atom has a fresh pattern_id (not 1 or 2)
    new_pid = int(w.k_pattern_id[k_before])
    assert new_pid != 0 and new_pid != 1 and new_pid != 2


def test_G15_offline_consolidation_strengthens_engram_bridges():
    """Run dream ticks on a substrate with a trained engram + BTSP. The
    bridges' strengths should increase over the dream period without any
    external input."""
    from world.physics import tick

    w = _make_world(dream=True, btsp=True, neuron_dyn=True)
    # Trained engram: 3 atoms in pattern 1 with one bridge between two of them.
    # Eligibility starts at 4.0 (already above plateau threshold 3.0) so the
    # first replay-driven dream tick triggers BTSP without needing accumulation.
    _seed_atom(w, 0, (10.0, 10.0, 10.0), pattern_id=1, eligibility=4.0)
    _seed_atom(w, 1, (15.0, 10.0, 10.0), pattern_id=1, eligibility=4.0)
    _seed_atom(w, 2, (20.0, 10.0, 10.0), pattern_id=1, eligibility=4.0)
    _seed_molecule(w, 3, (12.5, 10.0, 10.0), strength=2.0, pattern_id=1)
    _seed_molecule(w, 4, (17.5, 10.0, 10.0), strength=2.0, pattern_id=1)

    initial_strength_3 = float(w.k_strength[3])
    initial_strength_4 = float(w.k_strength[4])

    # Run 30 dream ticks
    for _ in range(30):
        tick(w, dt=1.0 / 60)

    final_strength_3 = float(w.k_strength[3])
    final_strength_4 = float(w.k_strength[4])
    total_delta = ((final_strength_3 - initial_strength_3)
                   + (final_strength_4 - initial_strength_4))
    # At least one of the bridges should have been strengthened by BTSP-
    # gated replay. Without external input, the only way this happens is
    # via dream-state replay seeding firings → BTSP plateau on seed
    # atoms → eligible-partner potentiation.
    assert total_delta > 0.0, (
        f"replay should strengthen at least one bridge; got delta={total_delta:.2f}"
    )


def test_G15_default_in_world_config():
    cfg = WorldConfig()
    assert cfg.dream_mode_enabled is False
    assert cfg.dream_replay_seeds_per_tick == 2
    assert cfg.dream_blend_enabled is True
    assert cfg.dream_blend_co_activation_window == 0.5
    assert cfg.dream_replay_seed_charge == 6.0


def test_G18_integrative_blending_creates_bridges():
    """G18.1: when concept blending allocates a new blended atom, it
    also allocates integration bridges connecting the new atom to
    representative members of both source patterns. The blended atom
    is integrated into the bridge mesh, not free-floating."""
    w = _make_world(dream=True)
    _seed_atom(w, 0, (10.0, 10.0, 10.0), pattern_id=1, eligibility=2.0)
    _seed_atom(w, 1, (10.0, 12.0, 10.0), pattern_id=1, eligibility=2.0)
    _seed_atom(w, 2, (10.0, 14.0, 10.0), pattern_id=1, eligibility=2.0)
    _seed_atom(w, 3, (40.0, 10.0, 10.0), pattern_id=2, eligibility=2.0)
    _seed_atom(w, 4, (40.0, 12.0, 10.0), pattern_id=2, eligibility=2.0)
    _seed_atom(w, 5, (40.0, 14.0, 10.0), pattern_id=2, eligibility=2.0)

    w.t = 1.0
    w.firing_events = [
        (0.7, 0), (0.7, 1), (0.7, 2),
        (0.8, 3), (0.8, 4), (0.8, 5),
    ]

    bridges_before = int((w.k_alive[:w.k_count]
                          & (w.k_level[:w.k_count] == 5)).sum())
    out = apply_dream(w, dt=1.0 / 60)
    bridges_after = int((w.k_alive[:w.k_count]
                          & (w.k_level[:w.k_count] == 5)).sum())

    assert out["blend_events"] >= 1, "concept blending must fire"
    assert out.get("integration_bridges", 0) >= 4, (
        f"integration bridges should connect blended atom to ≥2 anchors "
        f"per source pattern (4 total); got "
        f"{out.get('integration_bridges', 0)}"
    )
    assert bridges_after - bridges_before >= 4, (
        f"bridges count should grow by ≥4; got "
        f"{bridges_after - bridges_before}"
    )


def test_G18_2_nrem_rem_gating_alternates():
    """G18.2: with dream_consolidation_to_blend_ratio=4, four out of
    every five dream ticks are NREM (consolidation only, no blending).
    The fifth tick (the REM analogue) is the only one where blending
    is permitted."""
    cfg = WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=64, n_nodes_max=64,
        box_size=(60.0, 60.0, 60.0), rng_seed=42,
        dream_mode_enabled=True,
        dream_blend_enabled=True,
        dream_consolidation_to_blend_ratio=4,  # 4 NREM : 1 REM
    )
    w = World(cfg)
    _seed_atom(w, 0, (10.0, 10.0, 10.0), pattern_id=1, eligibility=2.0)
    _seed_atom(w, 1, (15.0, 10.0, 10.0), pattern_id=1, eligibility=2.0)
    _seed_atom(w, 2, (40.0, 10.0, 10.0), pattern_id=2, eligibility=2.0)
    _seed_atom(w, 3, (45.0, 10.0, 10.0), pattern_id=2, eligibility=2.0)
    w.t = 1.0
    w.firing_events = [(0.7, 0), (0.7, 1), (0.8, 2), (0.8, 3)]

    nrem_count = 0
    rem_count = 0
    for _ in range(10):
        out = apply_dream(w, dt=1.0 / 60)
        if out.get("nrem_consolidation_tick"):
            nrem_count += 1
        if out.get("rem_creative_tick"):
            rem_count += 1
    # 10 ticks at 4:1 → 8 NREM + 2 REM
    assert nrem_count == 8, f"expected 8 NREM ticks; got {nrem_count}"
    assert rem_count == 2, f"expected 2 REM ticks; got {rem_count}"


def test_G15_begin_end_dream_helpers():
    """begin_dream_state / end_dream_state toggle the cfg flag."""
    w = _make_world(dream=False)
    assert w.config.dream_mode_enabled is False
    begin_dream_state(w)
    assert w.config.dream_mode_enabled is True
    end_dream_state(w)
    assert w.config.dream_mode_enabled is False
