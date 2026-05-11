"""Tests for Nodes SoA container — F1a level (no bridges yet)."""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.structures import Nodes


def test_nodes_empty_on_init():
    n = Nodes(max_nodes=100)
    assert n.max_nodes == 100
    assert n.n_alive() == 0
    assert n.alive.shape == (100,)
    assert n.alive.dtype == np.bool_
    assert n.pos.shape == (100, 3)
    assert n.pos.dtype == np.float64
    assert n.energy.shape == (100,)
    assert n.energy.dtype == np.float64
    assert n.freq.shape == (100,)
    assert n.born_tick.shape == (100,)
    assert n.born_tick.dtype == np.int64


def test_nodes_add_returns_slot_and_writes_fields():
    n = Nodes(max_nodes=10)
    slot = n.add(pos=(1.5, 2.5, 3.5), energy=2.0, freq=440.0,
                 born_tick=42)
    assert 0 <= slot < 10
    assert n.alive[slot]
    assert n.pos[slot, 0] == 1.5
    assert n.pos[slot, 1] == 2.5
    assert n.pos[slot, 2] == 3.5
    assert n.energy[slot] == 2.0
    assert n.freq[slot] == 440.0
    assert n.born_tick[slot] == 42
    assert n.n_alive() == 1


def test_nodes_total_energy_sums_alive_only():
    n = Nodes(max_nodes=5)
    n.add(pos=(0, 0, 0), energy=1.0, freq=100.0, born_tick=0)
    n.add(pos=(0, 0, 0), energy=2.0, freq=100.0, born_tick=0)
    s = n.add(pos=(0, 0, 0), energy=99.0, freq=100.0, born_tick=0)
    n.remove(s)
    assert n.total_energy() == 3.0


def test_nodes_remove_marks_slot_free():
    n = Nodes(max_nodes=5)
    s0 = n.add(pos=(0, 0, 0), energy=1.5, freq=100.0, born_tick=0)
    released = n.remove(s0)
    assert released == 1.5
    assert not n.alive[s0]
    assert n.n_alive() == 0


def test_nodes_add_returns_minus_one_when_full():
    n = Nodes(max_nodes=2)
    n.add(pos=(0, 0, 0), energy=1.0, freq=100.0, born_tick=0)
    n.add(pos=(0, 0, 0), energy=1.0, freq=100.0, born_tick=0)
    full = n.add(pos=(0, 0, 0), energy=1.0, freq=100.0, born_tick=0)
    assert full == -1
