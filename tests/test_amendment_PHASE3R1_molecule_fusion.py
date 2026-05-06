"""Tests for PHASE3-R1: molecule + molecule binding."""
import numpy as np
from world.config import WorldConfig
from world.state import World
from world.physics import bind_nodes_upward


def _world_with_two_molecules(level_a: int, level_b: int,
                              freq_a: float, freq_b: float,
                              mol_fusion_enabled: bool = True,
                              freq_tolerance: float = 0.05) -> World:
    cfg = WorldConfig(
        n_initial_vibrations=0,
        n_vibrations_max=16,
        n_nodes_max=8,
        box_size=(100.0, 100.0, 100.0),
        r_2=20.0,
        freq_ratio=0.08,
        freq_tolerance=freq_tolerance,
        mol_fusion_enabled=mol_fusion_enabled,
        rng_seed=42,
    )
    w = World(cfg)
    w.k_pos[0] = [50.0, 50.0, 50.0]
    w.k_level[0] = level_a
    w.k_freq[0] = freq_a
    w.k_pol[0] = True
    w.k_alive[0] = True
    w.k_pos[1] = [55.0, 50.0, 50.0]
    w.k_level[1] = level_b
    w.k_freq[1] = freq_b
    w.k_pol[1] = False
    w.k_alive[1] = True
    w.k_count = 2
    return w


def test_two_level5_molecules_bind_to_level6():
    """When mol_fusion_enabled, two level-5 molecules with frequency ratio
    near freq_ratio should bind into a level-6."""
    w = _world_with_two_molecules(5, 5, freq_a=10000.0, freq_b=10800.0)
    n_bindings = bind_nodes_upward(w)
    assert n_bindings == 1
    assert w.k_count == 3
    assert w.k_level[2] == 6
    assert not w.k_alive[0]
    assert not w.k_alive[1]


def test_level5_level6_bind_to_level7():
    w = _world_with_two_molecules(5, 6, freq_a=10000.0, freq_b=10800.0)
    n_bindings = bind_nodes_upward(w)
    assert n_bindings == 1
    assert w.k_count == 3
    assert w.k_level[2] == 7


def test_disabled_when_flag_off():
    """With mol_fusion_enabled=False, level-5 + level-5 must NOT bind."""
    w = _world_with_two_molecules(5, 5, freq_a=10000.0, freq_b=10800.0,
                                   mol_fusion_enabled=False)
    n_bindings = bind_nodes_upward(w)
    assert n_bindings == 0
    assert w.k_count == 2
    assert w.k_alive[0] and w.k_alive[1]


def test_atom_plus_molecule_still_works_when_fusion_enabled():
    """Existing atom→molecule binding must still work with the flag on."""
    w = _world_with_two_molecules(4, 5, freq_a=10000.0, freq_b=10800.0,
                                   mol_fusion_enabled=True)
    n_bindings = bind_nodes_upward(w)
    assert n_bindings == 1
    assert w.k_level[2] == 6
