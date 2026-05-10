"""Tests for Quanta SoA container."""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.quantum import Quanta


def test_quanta_empty_on_init():
    q = Quanta(max_quanta=100)
    assert q.max_quanta == 100
    assert q.n_alive() == 0
    assert q.alive.shape == (100,)
    assert q.alive.dtype == np.bool_
    assert q.pos.shape == (100, 3)
    assert q.pos.dtype == np.float64
    assert q.vel.shape == (100, 3)
    assert q.energy.shape == (100,)
    assert q.freq.shape == (100,)
    assert q.polarity.dtype == np.int8


def test_quanta_add_returns_slot_and_writes_fields():
    q = Quanta(max_quanta=10)
    slot = q.add(pos=(1.5, 2.5, 3.5), vel=(0.1, 0.2, 0.3),
                 freq=440.0, polarity=1, energy=1.0)
    assert 0 <= slot < 10
    assert q.alive[slot]
    assert q.pos[slot, 0] == 1.5
    assert q.pos[slot, 1] == 2.5
    assert q.pos[slot, 2] == 3.5
    assert q.vel[slot, 0] == 0.1
    assert q.freq[slot] == 440.0
    assert q.polarity[slot] == 1
    assert q.energy[slot] == 1.0
    assert q.n_alive() == 1


def test_quanta_add_uses_free_slots_in_order():
    q = Quanta(max_quanta=5)
    s0 = q.add((0, 0, 0), (0, 0, 0), 100.0, 1, 1.0)
    s1 = q.add((0, 0, 0), (0, 0, 0), 100.0, 1, 1.0)
    s2 = q.add((0, 0, 0), (0, 0, 0), 100.0, 1, 1.0)
    assert {s0, s1, s2} == {0, 1, 2}
    assert q.n_alive() == 3


def test_quanta_remove_marks_slot_free_and_reusable():
    q = Quanta(max_quanta=5)
    s0 = q.add((0, 0, 0), (0, 0, 0), 100.0, 1, 1.0)
    s1 = q.add((1, 1, 1), (0, 0, 0), 100.0, 1, 1.0)
    q.remove(s0)
    assert not q.alive[s0]
    assert q.alive[s1]
    assert q.n_alive() == 1
    # Re-adding should reuse slot s0
    s2 = q.add((2, 2, 2), (0, 0, 0), 100.0, 1, 1.0)
    assert s2 == s0
    assert q.alive[s0]
    assert q.n_alive() == 2


def test_quanta_add_returns_minus_one_when_full():
    q = Quanta(max_quanta=2)
    q.add((0, 0, 0), (0, 0, 0), 100.0, 1, 1.0)
    q.add((0, 0, 0), (0, 0, 0), 100.0, 1, 1.0)
    full = q.add((0, 0, 0), (0, 0, 0), 100.0, 1, 1.0)
    assert full == -1


def test_quanta_total_energy_sums_alive_only():
    q = Quanta(max_quanta=5)
    q.add((0, 0, 0), (0, 0, 0), 100.0, 1, 1.5)
    q.add((0, 0, 0), (0, 0, 0), 100.0, 1, 2.5)
    s = q.add((0, 0, 0), (0, 0, 0), 100.0, 1, 99.0)
    q.remove(s)
    assert q.total_energy() == 4.0
