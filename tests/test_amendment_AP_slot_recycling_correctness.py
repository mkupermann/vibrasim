"""Tests for Plan A.5 slot recycling correctness (AP3, AP4)."""
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import _kill_node


def _make_world(n_nodes_max=8):
    cfg = WorldConfig(n_initial_vibrations=0, n_vibrations_max=4, n_nodes_max=n_nodes_max)
    return World(cfg)


def test_AP4a_kill_atom_with_no_references_recycles():
    """An atom that no molecule references → recyclable on kill."""
    w = _make_world()
    w.k_pos[0] = [10, 10, 10]
    w.k_level[0] = 4
    w.k_alive[0] = True
    w.k_count = 1
    w.k_comp_offset[0] = 0
    w.k_comp_offset[1] = 0
    w.k_ref_count[0] = 0
    _kill_node(w, 0)
    assert not w.k_alive[0]
    assert 0 in w._free_slots_set
    assert w._free_slots == [0]


def test_AP4b_kill_atom_with_pending_reference_does_not_recycle():
    """An atom that a molecule still references must NOT be recycled
    when the atom dies — the molecule still depends on it."""
    w = _make_world()
    w.k_pos[0] = [10, 10, 10]
    w.k_level[0] = 4
    w.k_alive[0] = True
    w.k_comp_offset[0] = 0
    w.k_comp_offset[1] = 0
    w.k_ref_count[0] = 1  # referenced by molecule below
    w.k_pos[1] = [10, 10, 10]
    w.k_level[1] = 5
    w.k_alive[1] = True
    w.k_comp_indices[0] = 0  # molecule 1 contains atom 0
    w.k_comp_offset[1] = 0
    w.k_comp_offset[2] = 1
    w.k_comp_used = 1
    w.k_count = 2
    _kill_node(w, 0)
    assert not w.k_alive[0]
    assert 0 not in w._free_slots_set
    # Now kill the molecule — its slot recycles AND the atom's ref count drops to 0
    _kill_node(w, 1)
    assert not w.k_alive[1]
    assert 1 in w._free_slots_set
    assert 0 in w._free_slots_set


@pytest.mark.xfail(strict=True, reason="awaits Plan A.5 Task 5: allocate_node recycling path")
def test_AP3_slot_reused_after_decay():
    """When allocate_node is called and a slot is on the free list, it's reused."""
    w = _make_world()
    w.k_pos[0] = [10, 10, 10]
    w.k_level[0] = 4
    w.k_alive[0] = False
    w.k_comp_offset[0] = 0
    w.k_comp_offset[1] = 0
    w._free_slots = [0]
    w._free_slots_set = {0}
    new_idx = w.allocate_node(
        pos=np.array([20, 20, 20], dtype=np.float64),
        freq=1000.0, pol=True, level=1,
        constituents=np.array([], dtype=np.int32), comp_kind=0,
    )
    assert new_idx == 0
    assert w._free_slots == []
    assert w._free_slots_set == set()
    assert w.k_count == 1
    assert w.k_alive[0]
    assert w.k_level[0] == 1
