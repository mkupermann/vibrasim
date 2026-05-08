"""Tests for k_reward_polarity propagation during atom formation (RPP1-RPP5).

Each test builds a world with a pre-formed triad (level 3) and a free
electron (level 1) that will bind into a level-4 atom when
bind_nodes_upward is called. The constituent vibrations' s_reward_polarity
values are set per the test scenario; the atom's k_reward_polarity is
then checked against the propagation rule from spec §5.2.

Propagation rule:
  - All constituent vibrations non-zero AND all identical → atom inherits
  - Otherwise (mixed or any-zero) → atom is 0

Composition tree for a level-4 atom:
  atom (level 4, comp_kind=1)
    ├── triad (level 3, comp_kind=1)
    │     ├── pair (level 2, comp_kind=1)
    │     │     ├── electron_A (level 1, comp_kind=0) → [vib_0, vib_1]
    │     │     └── electron_B (level 1, comp_kind=0) → [vib_2, vib_3]
    │     └── electron_C (level 1, comp_kind=0) → [vib_4, vib_5]
    └── electron_D (level 1, comp_kind=0) → [vib_6, vib_7]

8 leaf vibrations total (matching LEVEL_TO_VIBRATIONS[4] = 8).
"""
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import bind_nodes_upward


def _make_world_with_pre_triad(vib_polarities: list[int]):
    """Create a world with a pre-formed triad + a free electron ready to bind.

    vib_polarities: 8 ints (-1, 0, or +1) assigned to leaf vibrations
    vib_0..vib_7 in tree order above.

    The triad (slots 6) and electron_D (slot 7) are placed close enough
    to satisfy bind_nodes_upward conditions. Returns (world, triad_idx,
    electron_D_idx).
    """
    # Use generous freq_tolerance so binding is guaranteed.
    cfg = WorldConfig(
        n_initial_vibrations=0,
        n_vibrations_max=32,
        n_nodes_max=32,
        box_size=(200.0, 200.0, 200.0),
        r_2=20.0,
        freq_ratio=1.0,          # accept 1:1 freq ratio
        freq_tolerance=0.5,      # very wide tolerance
        slot_recycling_enabled=False,
        numba_jit_enabled=False,  # use Python path for determinism
        rng_seed=0,
    )
    w = World(cfg)

    # --- Place 8 leaf vibrations ---
    # Only need s_reward_polarity set; s_alive not needed (they're bound).
    for i, pol in enumerate(vib_polarities):
        w.s_reward_polarity[i] = np.int8(pol)
    # s_alive left False — they are already bound into electrons

    # Convenience alias: k_comp_indices array
    # We'll use allocate_node to build up the tree.

    # Choose a base frequency in the 1000s decade; all nodes share same decade.
    # freq_ratio=1.0, ftol=0.5 → ratio window [0.5, 1.5]
    # For two nodes to bind: |f1-f2|/min(f1,f2) ∈ [0.5, 1.5]
    # Use f_pair=2000, f_electron_C=3000 (ratio=0.5 exactly, borderline).
    # Safer: f_triad_left=2000, f_electron_D=3000 (ratio=(3000-2000)/2000=0.5 ✓)
    # For polarity: triad and electron_D must have OPPOSITE k_pol.

    # --- Build electrons (level 1, comp_kind=0) ---
    # electron_A: vibs 0,1
    ea_idx = w.allocate_node(
        pos=np.array([10.0, 10.0, 10.0]),
        freq=500.0, pol=False, level=1,
        constituents=np.array([0, 1], dtype=np.int32), comp_kind=0,
    )  # slot 0

    # electron_B: vibs 2,3
    eb_idx = w.allocate_node(
        pos=np.array([11.0, 10.0, 10.0]),
        freq=600.0, pol=True, level=1,
        constituents=np.array([2, 3], dtype=np.int32), comp_kind=0,
    )  # slot 1

    # --- Build pair (level 2, comp_kind=1) from electrons A+B ---
    pair_idx = w.allocate_node(
        pos=np.array([10.5, 10.0, 10.0]),
        freq=1100.0, pol=False, level=2,
        constituents=np.array([ea_idx, eb_idx], dtype=np.int32), comp_kind=1,
    )  # slot 2

    # electron_C: vibs 4,5
    ec_idx = w.allocate_node(
        pos=np.array([10.0, 11.0, 10.0]),
        freq=900.0, pol=True, level=1,
        constituents=np.array([4, 5], dtype=np.int32), comp_kind=0,
    )  # slot 3

    # --- Build triad (level 3, comp_kind=1) from pair+electron_C ---
    # Pair k_pol=False, electron_C k_pol=True → opposite ✓
    # Kill the pair and electron_C (they're now bound)
    w.k_alive[pair_idx] = False
    w.k_alive[ec_idx] = False
    triad_idx = w.allocate_node(
        pos=np.array([100.0, 100.0, 100.0]),
        freq=2000.0, pol=False, level=3,
        constituents=np.array([pair_idx, ec_idx], dtype=np.int32), comp_kind=1,
    )  # slot 4

    # electron_D: vibs 6,7
    # Must have k_pol opposite to triad (triad k_pol=False → electron_D k_pol=True)
    ed_idx = w.allocate_node(
        pos=np.array([105.0, 100.0, 100.0]),  # within r_2=20 of triad
        freq=3000.0, pol=True, level=1,
        constituents=np.array([6, 7], dtype=np.int32), comp_kind=0,
    )  # slot 5

    # Kill the electrons used in the triad (only triad and electron_D alive)
    w.k_alive[ea_idx] = False
    w.k_alive[eb_idx] = False

    # Verify triad and electron_D are alive with opposite polarity
    assert w.k_alive[triad_idx], "triad must be alive"
    assert w.k_alive[ed_idx], "electron_D must be alive"
    assert w.k_pol[triad_idx] != w.k_pol[ed_idx], "triad and electron_D must have opposite polarity"

    # Check decade: triad freq=2000, electron_D freq=3000; both floor(log10)=3 ✓
    import math
    assert math.floor(math.log10(w.k_freq[triad_idx])) == math.floor(math.log10(w.k_freq[ed_idx]))

    # Check freq ratio: (3000-2000)/2000 = 0.5, which equals fmin_ratio=0.5 ✓
    ratio = abs(w.k_freq[triad_idx] - w.k_freq[ed_idx]) / min(w.k_freq[triad_idx], w.k_freq[ed_idx])
    fr = cfg.freq_ratio
    ftol = cfg.freq_tolerance
    assert fr - ftol <= ratio <= fr + ftol, f"ratio {ratio} outside [{fr-ftol}, {fr+ftol}]"

    # Confirm distance within r_2
    dist = float(np.linalg.norm(w.k_pos[triad_idx] - w.k_pos[ed_idx]))
    assert dist < cfg.r_2, f"distance {dist} >= r_2 {cfg.r_2}"

    return w, triad_idx, ed_idx


def test_RPP1_all_positive_constituents_yield_positive_atom():
    """Triad + electron all from fire_positive origin (s_reward_polarity=+1)
    → atom k_reward_polarity = +1."""
    w, triad_idx, ed_idx = _make_world_with_pre_triad([1, 1, 1, 1, 1, 1, 1, 1])
    n_formed = bind_nodes_upward(w)
    assert n_formed >= 1, "Expected at least one binding event"
    # Find the new atom
    atom_mask = (w.k_level[:w.k_count] == 4) & w.k_alive[:w.k_count]
    atom_indices = np.where(atom_mask)[0]
    assert len(atom_indices) == 1, f"Expected exactly 1 atom, got {len(atom_indices)}"
    assert int(w.k_reward_polarity[atom_indices[0]]) == 1, (
        f"RPP1: expected k_reward_polarity=+1, got {w.k_reward_polarity[atom_indices[0]]}"
    )


def test_RPP2_all_negative_constituents_yield_negative_atom():
    """All -1 → atom = -1."""
    w, triad_idx, ed_idx = _make_world_with_pre_triad([-1, -1, -1, -1, -1, -1, -1, -1])
    n_formed = bind_nodes_upward(w)
    assert n_formed >= 1
    atom_mask = (w.k_level[:w.k_count] == 4) & w.k_alive[:w.k_count]
    atom_indices = np.where(atom_mask)[0]
    assert len(atom_indices) == 1
    assert int(w.k_reward_polarity[atom_indices[0]]) == -1, (
        f"RPP2: expected k_reward_polarity=-1, got {w.k_reward_polarity[atom_indices[0]]}"
    )


def test_RPP3_mixed_constituents_yield_zero_atom():
    """Some +1 + some 0 → atom = 0 (mixed origin, no reward signal)."""
    # 6 vibrations are +1, 2 are 0
    w, triad_idx, ed_idx = _make_world_with_pre_triad([1, 1, 1, 1, 1, 1, 0, 0])
    n_formed = bind_nodes_upward(w)
    assert n_formed >= 1
    atom_mask = (w.k_level[:w.k_count] == 4) & w.k_alive[:w.k_count]
    atom_indices = np.where(atom_mask)[0]
    assert len(atom_indices) == 1
    assert int(w.k_reward_polarity[atom_indices[0]]) == 0, (
        f"RPP3: expected k_reward_polarity=0, got {w.k_reward_polarity[atom_indices[0]]}"
    )


def test_RPP4_conflicting_constituents_yield_zero_atom():
    """Some +1 + some -1 → atom = 0 (conflict, no reward signal)."""
    # Half +1, half -1
    w, triad_idx, ed_idx = _make_world_with_pre_triad([1, 1, 1, 1, -1, -1, -1, -1])
    n_formed = bind_nodes_upward(w)
    assert n_formed >= 1
    atom_mask = (w.k_level[:w.k_count] == 4) & w.k_alive[:w.k_count]
    atom_indices = np.where(atom_mask)[0]
    assert len(atom_indices) == 1
    assert int(w.k_reward_polarity[atom_indices[0]]) == 0, (
        f"RPP4: expected k_reward_polarity=0, got {w.k_reward_polarity[atom_indices[0]]}"
    )


def test_RPP5_all_zero_constituents_yield_zero_atom():
    """Default substrate atoms (no reward origin) stay at 0."""
    w, triad_idx, ed_idx = _make_world_with_pre_triad([0, 0, 0, 0, 0, 0, 0, 0])
    n_formed = bind_nodes_upward(w)
    assert n_formed >= 1
    atom_mask = (w.k_level[:w.k_count] == 4) & w.k_alive[:w.k_count]
    atom_indices = np.where(atom_mask)[0]
    assert len(atom_indices) == 1
    assert int(w.k_reward_polarity[atom_indices[0]]) == 0, (
        f"RPP5: expected k_reward_polarity=0, got {w.k_reward_polarity[atom_indices[0]]}"
    )
