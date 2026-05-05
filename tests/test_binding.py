import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import bind_vibrations_to_electrons


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


def test_polarity_randomization_at_electron_level(default_config):
    """Run a small simulation; assert both polarities appear at electron level."""
    cfg = WorldConfig(
        n_initial_vibrations=300,
        box_size=(100.0, 100.0),
        r_1=8.0,
        rng_seed=42,
    )
    w = World(cfg)
    bind_vibrations_to_electrons(w)
    if w.k_count >= 20:
        even_share = float(np.mean(w.k_pol[:w.k_count]))
        assert 0.2 < even_share < 0.8
    else:
        pytest.skip(f"Not enough electrons formed for distribution check ({w.k_count})")


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
