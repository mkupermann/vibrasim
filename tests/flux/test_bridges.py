"""Tests for Bridges SoA container — F1b level."""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.bridges import Bridges


def test_bridges_empty_on_init():
    b = Bridges(max_bridges=100)
    assert b.max_bridges == 100
    assert b.n_alive() == 0
    assert b.alive.shape == (100,)
    assert b.alive.dtype == np.bool_
    assert b.src.shape == (100,)
    assert b.dst.shape == (100,)
    assert b.weight.shape == (100,)
    assert b.last_flux_tick.shape == (100,)


def test_bridges_add_returns_slot_and_writes_fields():
    b = Bridges(max_bridges=10)
    slot = b.add(src=3, dst=7, weight=0.5, born_tick=42)
    assert slot == 0
    assert bool(b.alive[0])
    assert int(b.src[0]) == 3
    assert int(b.dst[0]) == 7
    assert float(b.weight[0]) == 0.5
    assert int(b.last_flux_tick[0]) == 42
    assert b.n_alive() == 1


def test_bridges_add_uses_free_slots_in_order():
    b = Bridges(max_bridges=5)
    for i in range(3):
        b.add(src=i, dst=i + 1, weight=1.0, born_tick=0)
    assert b.n_alive() == 3
    b.remove(1)
    assert not bool(b.alive[1])
    slot = b.add(src=99, dst=100, weight=2.0, born_tick=10)
    assert slot == 1
    assert int(b.src[1]) == 99
    assert int(b.dst[1]) == 100


def test_bridges_remove_marks_slot_free():
    b = Bridges(max_bridges=5)
    s = b.add(src=1, dst=2, weight=1.0, born_tick=0)
    b.remove(s)
    assert not bool(b.alive[s])
    assert float(b.weight[s]) == 0.0


def test_bridges_add_returns_minus_one_when_full():
    b = Bridges(max_bridges=2)
    b.add(src=0, dst=1, weight=1.0, born_tick=0)
    b.add(src=1, dst=2, weight=1.0, born_tick=0)
    slot = b.add(src=2, dst=3, weight=1.0, born_tick=0)
    assert slot == -1


def test_bridges_find_by_endpoints_is_directed():
    b = Bridges(max_bridges=10)
    b.add(src=1, dst=2, weight=1.0, born_tick=0)
    b.add(src=2, dst=3, weight=2.0, born_tick=0)
    assert b.find(src=1, dst=2) == 0
    assert b.find(src=2, dst=3) == 1
    assert b.find(src=3, dst=4) == -1
    # Directed: reverse direction is NOT the same bridge
    assert b.find(src=2, dst=1) == -1
