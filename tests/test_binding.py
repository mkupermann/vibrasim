import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import bind_vibrations_to_electrons, bind_nodes_upward


def _seed_two_vibrations(w: World, p1, p2, f1, f2, pol1, pol2):
    w.s_pos[0] = p1
    w.s_pos[1] = p2
    w.s_freq[0] = f1
    w.s_freq[1] = f2
    w.s_pol[0] = pol1
    w.s_pol[1] = pol2
    w.s_alive[0] = True
    w.s_alive[1] = True
    w.s_vel[0] = [0.0, 0.0]
    w.s_vel[1] = [0.0, 0.0]
    w.n_alive = 2


def test_no_binding_same_polarity(empty_world):
    w = empty_world
    _seed_two_vibrations(w, [10.0, 10.0], [12.0, 10.0], 1000.0, 1080.0, True, True)
    bind_vibrations_to_electrons(w)
    assert w.k_count == 0
    assert w.s_alive[0] and w.s_alive[1]


def test_no_binding_freq_off(empty_world):
    w = empty_world
    _seed_two_vibrations(w, [10.0, 10.0], [12.0, 10.0], 1000.0, 1050.0, True, False)
    bind_vibrations_to_electrons(w)
    assert w.k_count == 0


def test_no_binding_too_far(empty_world):
    w = empty_world
    r1 = w.config.r_1
    _seed_two_vibrations(w, [10.0, 10.0], [10.0 + 2 * r1 + 0.5, 10.0],
                         1000.0, 1080.0, True, False)
    bind_vibrations_to_electrons(w)
    assert w.k_count == 0


def test_electron_forms(empty_world):
    w = empty_world
    _seed_two_vibrations(w, [10.0, 10.0], [12.0, 10.0], 1000.0, 1080.0, True, False)
    bind_vibrations_to_electrons(w)
    assert w.k_count == 1
    assert w.k_alive[0]
    assert w.k_level[0] == 1
    assert w.k_freq[0] == pytest.approx(1000.0 + 1080.0)
    assert w.k_pos[0, 0] == pytest.approx(11.0)
    assert w.k_pos[0, 1] == pytest.approx(10.0)
    assert not w.s_alive[0]
    assert not w.s_alive[1]
    start = w.k_comp_offset[0]
    end = w.k_comp_offset[1]
    assert end - start == 2
    assert sorted(w.k_comp_indices[start:end].tolist()) == [0, 1]
    assert w.k_comp_kind[0] == 0


def test_electron_forms_at_periodic_boundary(empty_world):
    w = empty_world
    box = w.config.box_size
    _seed_two_vibrations(w,
                         [box[0] - 1.0, 10.0],
                         [1.0, 10.0],
                         1000.0, 1080.0, True, False)
    bind_vibrations_to_electrons(w)
    assert w.k_count == 1
    mx = w.k_pos[0, 0]
    assert mx < 1.0 or mx > box[0] - 1.0


def test_polarity_randomization_at_electron_level():
    """Form 100 electrons from hand-seeded vibration pairs; assert both polarities appear.

    This is the keystone test of design §2.2: parity is randomized at formation,
    NOT inherited from constituents. If this test ever fails, every level above
    electrons would have only one parity, the binding rule "even meets odd"
    can never be satisfied, and the hierarchy dies.

    Deterministic — no stochastic warm-up. Pairs are placed far apart so each
    binding scan sees exactly one valid pair, freq diff exactly 8%, opposite
    polarity. Polarity of the resulting electron is then a fresh 50/50 sample
    from world.rng.
    """
    n_pairs = 100
    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(2000.0, 2000.0),  # spacious so pairs don't interfere
        n_vibrations_max=2 * n_pairs,
        n_nodes_max=n_pairs,
        rng_seed=42,
    )
    w = World(cfg)
    spacing = 20.0  # well beyond r_1 = 5.0
    for k in range(n_pairs):
        x = (k + 1) * spacing
        w.s_pos[2 * k] = [x, 100.0]
        w.s_pos[2 * k + 1] = [x + 1.0, 100.0]
        w.s_vel[2 * k] = [0.0, 0.0]
        w.s_vel[2 * k + 1] = [0.0, 0.0]
        w.s_freq[2 * k] = 1000.0
        w.s_freq[2 * k + 1] = 1080.0  # exact 8% diff
        w.s_pol[2 * k] = True
        w.s_pol[2 * k + 1] = False
        w.s_alive[2 * k] = True
        w.s_alive[2 * k + 1] = True
    w.n_alive = 2 * n_pairs

    bind_vibrations_to_electrons(w)
    assert w.k_count == n_pairs, f"expected {n_pairs} electrons, got {w.k_count}"

    even_share = float(np.mean(w.k_pol[:w.k_count]))
    # 100 fair coin flips: 95% CI for share is (~0.40, 0.60). Assert with margin.
    assert 0.30 < even_share < 0.70, f"polarity share {even_share:.2f} outside [0.30, 0.70]"


def test_polarity_randomization_at_pair_level():
    """Form 100 pairs from hand-seeded electrons; assert both polarities appear.

    Companion to the electron-level test. Pair formation calls the same
    rng.random() < 0.5 path; this test makes sure no future change accidentally
    derives pair parity from constituents.
    """
    n_pairs = 100
    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(2000.0, 2000.0),
        n_vibrations_max=4,
        n_nodes_max=3 * n_pairs,
        rng_seed=42,
    )
    w = World(cfg)
    spacing = 30.0  # beyond r_2 = 10.0 between pair groups, well within for partners
    # Each "group" is two electrons at adjacent slots, opposite parity, freq diff 8%.
    for k in range(n_pairs):
        x = (k + 1) * spacing
        idx0 = 2 * k
        idx1 = 2 * k + 1
        w.k_pos[idx0] = [x, 100.0]
        w.k_pos[idx1] = [x + 2.0, 100.0]
        w.k_freq[idx0] = 2000.0
        w.k_freq[idx1] = 2160.0  # exact 8% diff
        w.k_pol[idx0] = True
        w.k_pol[idx1] = False
        w.k_level[idx0] = 1
        w.k_level[idx1] = 1
        w.k_alive[idx0] = True
        w.k_alive[idx1] = True
        w.k_comp_offset[idx0] = w.k_comp_used
        w.k_comp_offset[idx0 + 1] = w.k_comp_used
        w.k_comp_offset[idx1] = w.k_comp_used
        w.k_comp_offset[idx1 + 1] = w.k_comp_used
    w.k_count = 2 * n_pairs

    bind_nodes_upward(w)
    pair_indices = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 2]
    assert len(pair_indices) == n_pairs, f"expected {n_pairs} pairs, got {len(pair_indices)}"

    pair_pols = [bool(w.k_pol[i]) for i in pair_indices]
    even_share = sum(pair_pols) / len(pair_pols)
    assert 0.30 < even_share < 0.70, f"pair polarity share {even_share:.2f} outside [0.30, 0.70]"


from world.physics import bind_nodes_upward


def _make_electron(w: World, idx: int, pos, freq, pol):
    w.k_pos[idx] = pos
    w.k_freq[idx] = freq
    w.k_pol[idx] = pol
    w.k_level[idx] = 1
    w.k_alive[idx] = True
    w.k_birth[idx] = w.t
    if idx >= w.k_count:
        w.k_count = idx + 1
        w.k_comp_offset[idx + 1] = w.k_comp_offset[idx]


def test_pair_forms(empty_world):
    w = empty_world
    _make_electron(w, 0, [10.0, 10.0], 2000.0, True)
    _make_electron(w, 1, [13.0, 10.0], 2160.0, False)  # 8% diff
    bind_nodes_upward(w)
    pairs = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 2]
    assert len(pairs) == 1
    p = pairs[0]
    assert w.k_freq[p] == pytest.approx(2000.0 + 2160.0)
    assert not w.k_alive[0]
    assert not w.k_alive[1]
    start = w.k_comp_offset[p]
    end = w.k_comp_offset[p + 1]
    assert end - start == 2
    assert sorted(w.k_comp_indices[start:end].tolist()) == [0, 1]
    assert w.k_comp_kind[p] == 1


def _make_node(w: World, idx: int, pos, freq, pol, level, constituents, kind):
    w.k_pos[idx] = pos
    w.k_freq[idx] = freq
    w.k_pol[idx] = pol
    w.k_level[idx] = level
    w.k_alive[idx] = True
    w.k_birth[idx] = w.t
    n_comp = len(constituents)
    start = w.k_comp_used
    w.k_comp_indices[start:start + n_comp] = constituents
    w.k_comp_offset[idx] = start
    w.k_comp_offset[idx + 1] = start + n_comp
    w.k_comp_used = start + n_comp
    w.k_comp_kind[idx] = kind
    if idx >= w.k_count:
        w.k_count = idx + 1


def test_triad_forms_pair_plus_electron(empty_world):
    w = empty_world
    _make_electron(w, 0, [10.0, 10.0], 2000.0, True)
    _make_electron(w, 1, [10.0, 10.0], 2000.0, False)
    _make_node(w, 2, [11.0, 10.0], 4160.0, True, level=2,
               constituents=np.array([0, 1], dtype=np.int32), kind=1)
    w.k_alive[0] = False
    w.k_alive[1] = False
    _make_electron(w, 3, [13.0, 10.0], 4493.0, False)  # 8% above 4160
    bind_nodes_upward(w)
    triads = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 3]
    assert len(triads) == 1


def test_atom_forms_triad_plus_electron(empty_world):
    w = empty_world
    _make_electron(w, 0, [10.0, 10.0], 2000.0, True)
    _make_electron(w, 1, [10.0, 10.0], 2160.0, False)
    w.k_alive[0] = False
    w.k_alive[1] = False
    _make_node(w, 2, [10.0, 10.0], 4160.0, True, level=2,
               constituents=np.array([0, 1], dtype=np.int32), kind=1)
    w.k_alive[2] = False
    _make_electron(w, 3, [10.0, 10.0], 4493.0, False)
    w.k_alive[3] = False
    _make_node(w, 4, [11.0, 10.0], 8653.0, False, level=3,
               constituents=np.array([2, 3], dtype=np.int32), kind=1)
    _make_electron(w, 5, [12.0, 10.0], 9345.0, True)  # 8% above 8653
    bind_nodes_upward(w)
    atoms = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 4]
    assert len(atoms) == 1


def test_decade_isolation(empty_world):
    w = empty_world
    _make_electron(w, 0, [10.0, 10.0], 500.0, True)
    _make_electron(w, 1, [13.0, 10.0], 540.0, False)  # 8% above 500, same decade
    bind_nodes_upward(w)
    pairs = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 2]
    assert len(pairs) == 1, "same-decade pair should form"


def test_decade_isolation_blocks_cross_decade(empty_world):
    w = empty_world
    _make_electron(w, 0, [10.0, 10.0], 9500.0, True)   # decade 3
    _make_electron(w, 1, [13.0, 10.0], 10260.0, False)  # decade 4
    bind_nodes_upward(w)
    pairs = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 2]
    assert len(pairs) == 0
