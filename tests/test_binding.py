import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import bind_vibrations_to_electrons, bind_nodes_upward


def _seed_two_vibrations(w: World, p1, p2, f1, f2, pol1, pol2):
    """p1, p2 are now length-3 arrays / lists."""
    w.s_pos[0] = p1
    w.s_pos[1] = p2
    w.s_freq[0] = f1
    w.s_freq[1] = f2
    w.s_pol[0] = pol1
    w.s_pol[1] = pol2
    w.s_alive[0] = True
    w.s_alive[1] = True
    w.s_vel[0] = [0.0, 0.0, 0.0]
    w.s_vel[1] = [0.0, 0.0, 0.0]
    w.n_alive = 2


def test_no_binding_same_polarity_3d(empty_world):
    w = empty_world
    _seed_two_vibrations(w, [10., 10., 10.], [12., 10., 10.],
                         1000.0, 1080.0, True, True)
    bind_vibrations_to_electrons(w)
    assert w.k_count == 0


def test_electron_forms_3d(empty_world):
    w = empty_world
    _seed_two_vibrations(w, [10., 10., 10.], [12., 10., 10.],
                         1000.0, 1080.0, True, False)
    bind_vibrations_to_electrons(w)
    assert w.k_count == 1
    assert w.k_freq[0] == pytest.approx(2080.0)
    assert np.allclose(w.k_pos[0], [11., 10., 10.])
    assert not w.s_alive[0] and not w.s_alive[1]


def test_electron_forms_at_3d_wrap(empty_world):
    w = empty_world
    box = w.config.box_size
    _seed_two_vibrations(w, [box[0] - 1., 10., 10.], [1., 10., 10.],
                         1000.0, 1080.0, True, False)
    bind_vibrations_to_electrons(w)
    assert w.k_count == 1
    mx = w.k_pos[0, 0]
    assert mx < 1.0 or mx > box[0] - 1.0


# Higher binding tests — 3D positions, otherwise identical structure
def _make_electron_3d(w: World, idx: int, pos, freq, pol):
    w.k_pos[idx] = pos
    w.k_freq[idx] = freq
    w.k_pol[idx] = pol
    w.k_level[idx] = 1
    w.k_alive[idx] = True
    w.k_birth[idx] = w.t
    if idx >= w.k_count:
        w.k_count = idx + 1
        w.k_comp_offset[idx + 1] = w.k_comp_offset[idx]
        w.k_comp_end[idx] = w.k_comp_offset[idx]


def test_pair_forms_3d(empty_world):
    w = empty_world
    _make_electron_3d(w, 0, [10., 10., 10.], 2000.0, True)
    _make_electron_3d(w, 1, [13., 10., 10.], 2160.0, False)
    bind_nodes_upward(w)
    pairs = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 2]
    assert len(pairs) == 1


def test_decade_isolation_3d(empty_world):
    w = empty_world
    _make_electron_3d(w, 0, [10., 10., 10.], 9500.0, True)
    _make_electron_3d(w, 1, [13., 10., 10.], 10260.0, False)
    bind_nodes_upward(w)
    pairs = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 2]
    assert len(pairs) == 0


def test_no_binding_freq_off_3d(empty_world):
    w = empty_world
    _seed_two_vibrations(w, [10.0, 10.0, 10.0], [12.0, 10.0, 10.0], 1000.0, 1050.0, True, False)
    bind_vibrations_to_electrons(w)
    assert w.k_count == 0


def test_no_binding_too_far_3d(empty_world):
    w = empty_world
    r1 = w.config.r_1
    _seed_two_vibrations(w, [10.0, 10.0, 10.0], [10.0 + 2 * r1 + 0.5, 10.0, 10.0],
                         1000.0, 1080.0, True, False)
    bind_vibrations_to_electrons(w)
    assert w.k_count == 0


def test_polarity_randomization_at_electron_level_3d():
    """Form 100 electrons from hand-seeded vibration pairs; assert both polarities appear."""
    n_pairs = 100
    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(2000.0, 2000.0, 2000.0),
        n_vibrations_max=2 * n_pairs,
        n_nodes_max=n_pairs,
        rng_seed=42,
        repulsion_cell_size=2000.0,
    )
    w = World(cfg)
    spacing = 20.0
    for k in range(n_pairs):
        x = (k + 1) * spacing
        w.s_pos[2 * k] = [x, 100.0, 100.0]
        w.s_pos[2 * k + 1] = [x + 1.0, 100.0, 100.0]
        w.s_vel[2 * k] = [0.0, 0.0, 0.0]
        w.s_vel[2 * k + 1] = [0.0, 0.0, 0.0]
        w.s_freq[2 * k] = 1000.0
        w.s_freq[2 * k + 1] = 1080.0
        w.s_pol[2 * k] = True
        w.s_pol[2 * k + 1] = False
        w.s_alive[2 * k] = True
        w.s_alive[2 * k + 1] = True
    w.n_alive = 2 * n_pairs

    bind_vibrations_to_electrons(w)
    assert w.k_count == n_pairs, f"expected {n_pairs} electrons, got {w.k_count}"

    even_share = float(np.mean(w.k_pol[:w.k_count]))
    assert 0.30 < even_share < 0.70, f"polarity share {even_share:.2f} outside [0.30, 0.70]"


def test_polarity_randomization_at_pair_level_3d():
    """Form 100 pairs from hand-seeded electrons; assert both polarities appear."""
    n_pairs = 100
    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(2000.0, 2000.0, 2000.0),
        n_vibrations_max=4,
        n_nodes_max=3 * n_pairs,
        rng_seed=42,
        repulsion_cell_size=2000.0,
    )
    w = World(cfg)
    spacing = 30.0
    for k in range(n_pairs):
        x = (k + 1) * spacing
        idx0 = 2 * k
        idx1 = 2 * k + 1
        w.k_pos[idx0] = [x, 100.0, 100.0]
        w.k_pos[idx1] = [x + 2.0, 100.0, 100.0]
        w.k_freq[idx0] = 2000.0
        w.k_freq[idx1] = 2160.0
        w.k_pol[idx0] = True
        w.k_pol[idx1] = False
        w.k_level[idx0] = 1
        w.k_level[idx1] = 1
        w.k_alive[idx0] = True
        w.k_alive[idx1] = True
        w.k_comp_offset[idx0] = w.k_comp_used
        w.k_comp_offset[idx0 + 1] = w.k_comp_used
        w.k_comp_end[idx0] = w.k_comp_used
        w.k_comp_offset[idx1] = w.k_comp_used
        w.k_comp_offset[idx1 + 1] = w.k_comp_used
        w.k_comp_end[idx1] = w.k_comp_used
    w.k_count = 2 * n_pairs

    bind_nodes_upward(w)
    pair_indices = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 2]
    assert len(pair_indices) == n_pairs, f"expected {n_pairs} pairs, got {len(pair_indices)}"

    pair_pols = [bool(w.k_pol[i]) for i in pair_indices]
    even_share = sum(pair_pols) / len(pair_pols)
    assert 0.30 < even_share < 0.70, f"pair polarity share {even_share:.2f} outside [0.30, 0.70]"


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
        w.k_comp_end[idx] = w.k_comp_offset[idx]


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
    w.k_comp_end[idx] = start + n_comp
    w.k_comp_used = start + n_comp
    w.k_comp_kind[idx] = kind
    if idx >= w.k_count:
        w.k_count = idx + 1


def test_pair_forms_with_3d_positions(empty_world):
    w = empty_world
    _make_electron(w, 0, [10.0, 10.0, 10.0], 2000.0, True)
    _make_electron(w, 1, [13.0, 10.0, 10.0], 2160.0, False)
    bind_nodes_upward(w)
    pairs = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 2]
    assert len(pairs) == 1
    p = pairs[0]
    assert w.k_freq[p] == pytest.approx(2000.0 + 2160.0)
    assert not w.k_alive[0]
    assert not w.k_alive[1]
    start = w.k_comp_offset[p]
    end = w.k_comp_end[p]
    assert end - start == 2
    assert sorted(w.k_comp_indices[start:end].tolist()) == [0, 1]
    assert w.k_comp_kind[p] == 1


def test_triad_forms_pair_plus_electron_3d(empty_world):
    w = empty_world
    _make_electron(w, 0, [10.0, 10.0, 10.0], 2000.0, True)
    _make_electron(w, 1, [10.0, 10.0, 10.0], 2000.0, False)
    _make_node(w, 2, [11.0, 10.0, 10.0], 4160.0, True, level=2,
               constituents=np.array([0, 1], dtype=np.int32), kind=1)
    w.k_alive[0] = False
    w.k_alive[1] = False
    _make_electron(w, 3, [13.0, 10.0, 10.0], 4493.0, False)
    bind_nodes_upward(w)
    triads = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 3]
    assert len(triads) == 1


def test_atom_forms_triad_plus_electron_3d(empty_world):
    w = empty_world
    _make_electron(w, 0, [10.0, 10.0, 10.0], 2000.0, True)
    _make_electron(w, 1, [10.0, 10.0, 10.0], 2160.0, False)
    w.k_alive[0] = False
    w.k_alive[1] = False
    _make_node(w, 2, [10.0, 10.0, 10.0], 4160.0, True, level=2,
               constituents=np.array([0, 1], dtype=np.int32), kind=1)
    w.k_alive[2] = False
    _make_electron(w, 3, [10.0, 10.0, 10.0], 4493.0, False)
    w.k_alive[3] = False
    _make_node(w, 4, [11.0, 10.0, 10.0], 8653.0, False, level=3,
               constituents=np.array([2, 3], dtype=np.int32), kind=1)
    _make_electron(w, 5, [12.0, 10.0, 10.0], 9345.0, True)
    bind_nodes_upward(w)
    atoms = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 4]
    assert len(atoms) == 1


def test_decade_isolation_same_decade_3d(empty_world):
    w = empty_world
    _make_electron(w, 0, [10.0, 10.0, 10.0], 500.0, True)
    _make_electron(w, 1, [13.0, 10.0, 10.0], 540.0, False)
    bind_nodes_upward(w)
    pairs = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 2]
    assert len(pairs) == 1, "same-decade pair should form"


def test_decade_isolation_blocks_cross_decade_3d(empty_world):
    w = empty_world
    _make_electron(w, 0, [10.0, 10.0, 10.0], 9500.0, True)
    _make_electron(w, 1, [13.0, 10.0, 10.0], 10260.0, False)
    bind_nodes_upward(w)
    pairs = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 2]
    assert len(pairs) == 0
