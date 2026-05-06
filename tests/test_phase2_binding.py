"""Phase 2 — atom binding into molecules.

These tests hand-place atoms (level 4) and verify that the upgrade rules
in `_UPGRADE_TARGET` produce molecules at levels 5..11. They mirror
test_binding.py's helpers for the lower hierarchy.
"""
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import bind_nodes_upward


def _empty_world(box=200.0, n_max=128):
    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(box, box, box),
        n_vibrations_max=128,
        n_nodes_max=n_max,
        rng_seed=42,
    )
    return World(cfg)


def _make_atom(w: World, idx: int, pos, freq, pol):
    """Hand-place an atom (level 4) at slot idx."""
    w.k_pos[idx] = pos
    w.k_freq[idx] = freq
    w.k_pol[idx] = pol
    w.k_level[idx] = 4
    w.k_alive[idx] = True
    w.k_birth[idx] = w.t
    w.k_comp_kind[idx] = 1
    if idx >= w.k_count:
        w.k_count = idx + 1
        w.k_comp_offset[idx + 1] = w.k_comp_offset[idx]
        w.k_comp_end[idx] = w.k_comp_offset[idx]


def test_atom_atom_forms_molecule_l5():
    w = _empty_world()
    _make_atom(w, 0, [10.0, 10.0, 10.0], 16000.0, True)
    _make_atom(w, 1, [13.0, 10.0, 10.0], 17280.0, False)  # 8% diff, same decade (10^4)
    bind_nodes_upward(w)
    molecules = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 5]
    assert len(molecules) == 1
    assert not w.k_alive[0] and not w.k_alive[1]
    m = molecules[0]
    assert w.k_freq[m] == pytest.approx(16000.0 + 17280.0)


def test_atom_polarity_same_no_molecule():
    w = _empty_world()
    _make_atom(w, 0, [10.0, 10.0, 10.0], 16000.0, True)
    _make_atom(w, 1, [13.0, 10.0, 10.0], 17280.0, True)  # same polarity
    bind_nodes_upward(w)
    assert not any(w.k_alive[i] and w.k_level[i] == 5 for i in range(w.k_count))


def test_atom_freq_off_no_molecule():
    w = _empty_world()
    _make_atom(w, 0, [10.0, 10.0, 10.0], 16000.0, True)
    _make_atom(w, 1, [13.0, 10.0, 10.0], 17000.0, False)  # ~6% — outside tolerance
    bind_nodes_upward(w)
    assert not any(w.k_alive[i] and w.k_level[i] == 5 for i in range(w.k_count))


def test_atom_decade_off_no_molecule():
    w = _empty_world()
    _make_atom(w, 0, [10.0, 10.0, 10.0], 9500.0, True)   # decade 3
    _make_atom(w, 1, [13.0, 10.0, 10.0], 10260.0, False)  # decade 4
    bind_nodes_upward(w)
    assert not any(w.k_alive[i] and w.k_level[i] == 5 for i in range(w.k_count))


def test_l5_plus_atom_forms_l6():
    """A di-atomic molecule + a third atom of opposite parity → tri-atomic."""
    w = _empty_world()
    # First, form a level-5 molecule manually (slot 2)
    w.k_pos[2] = [10.0, 10.0, 10.0]
    w.k_freq[2] = 33280.0  # 16000 + 17280
    w.k_pol[2] = True
    w.k_level[2] = 5
    w.k_alive[2] = True
    w.k_count = 3
    # Add an opposite-parity atom that satisfies 8% rule and same decade.
    # 33280 * 1.08 = 35942 (decade 4, same as 33280). Use opposite parity.
    _make_atom(w, 3, [13.0, 10.0, 10.0], 35942.4, False)
    bind_nodes_upward(w)
    triatomic = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 6]
    assert len(triatomic) == 1


def test_l11_plus_atom_does_not_upgrade():
    """Level 11 (cap) + atom should NOT form level 12 (no upgrade entry)."""
    w = _empty_world()
    # Hand-place a level-11 node and an atom satisfying all binding rules.
    w.k_pos[0] = [10.0, 10.0, 10.0]
    w.k_freq[0] = 80000.0
    w.k_pol[0] = True
    w.k_level[0] = 11
    w.k_alive[0] = True
    w.k_count = 1
    _make_atom(w, 1, [13.0, 10.0, 10.0], 86400.0, False)
    bind_nodes_upward(w)
    higher = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] >= 12]
    assert len(higher) == 0
    # Both originals still alive.
    assert w.k_alive[0] and w.k_alive[1]


def test_molecule_does_not_bind_to_molecule():
    """Two level-5 molecules satisfying all rules should NOT bind (no (5,5) entry)."""
    w = _empty_world()
    w.k_pos[0] = [10.0, 10.0, 10.0]
    w.k_freq[0] = 33280.0
    w.k_pol[0] = True
    w.k_level[0] = 5
    w.k_alive[0] = True
    w.k_pos[1] = [13.0, 10.0, 10.0]
    w.k_freq[1] = 35942.4  # 8% above
    w.k_pol[1] = False
    w.k_level[1] = 5
    w.k_alive[1] = True
    w.k_count = 2
    bind_nodes_upward(w)
    higher = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] > 5]
    assert len(higher) == 0


def test_molecule_polarity_random_at_formation():
    """Form 60 di-atomic molecules from hand-seeded atoms; both polarities appear."""
    n_molecules = 60
    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(2000.0, 2000.0, 2000.0),
        n_vibrations_max=4,
        n_nodes_max=3 * n_molecules + 10,
        rng_seed=42,
    )
    w = World(cfg)
    spacing = 25.0
    for k in range(n_molecules):
        x = (k + 1) * spacing
        idx0 = 2 * k
        idx1 = 2 * k + 1
        for idx, pol, freq in [(idx0, True, 16000.0), (idx1, False, 17280.0)]:
            w.k_pos[idx] = [x + (0 if idx == idx0 else 2.0), 100.0, 100.0]
            w.k_freq[idx] = freq
            w.k_pol[idx] = pol
            w.k_level[idx] = 4
            w.k_alive[idx] = True
            w.k_comp_offset[idx] = w.k_comp_used
            w.k_comp_offset[idx + 1] = w.k_comp_used
            w.k_comp_end[idx] = w.k_comp_used
    w.k_count = 2 * n_molecules

    bind_nodes_upward(w)
    molecules = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 5]
    assert len(molecules) == n_molecules

    even_share = float(np.mean([w.k_pol[i] for i in molecules]))
    assert 0.30 < even_share < 0.70, f"molecule polarity share {even_share:.2f} outside [0.30, 0.70]"
