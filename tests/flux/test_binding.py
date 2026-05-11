"""Tests for binding rule — F1a level (no bridges, no plasticity)."""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.binding import pred_coherence


def test_pred_coherence_returns_one_for_equal_frequencies():
    # F1a simplification: pred_coherence is 1.0 if |f_a - f_b| < eps,
    # else 0.0. Full cross-correlation deferred to F2.
    assert pred_coherence(200.0, 200.0, eps=1.0) == 1.0
    # |200.4 - 199.7| = 0.7 < 1.0 → 1.0
    assert pred_coherence(200.4, 199.7, eps=1.0) == 1.0


def test_pred_coherence_returns_zero_for_different_frequencies():
    assert pred_coherence(200.0, 300.0, eps=1.0) == 0.0
    assert pred_coherence(100.0, 100.5, eps=0.1) == 0.0


def test_pred_coherence_at_boundary_is_zero():
    # Exactly at eps the difference is not strictly < eps → 0.0
    assert pred_coherence(200.0, 201.0, eps=1.0) == 0.0


from world.flux.quantum import Quanta
from world.flux.binding import find_pairs_within


def test_find_pairs_within_returns_empty_for_zero_or_one_quanta():
    q = Quanta(max_quanta=10)
    pairs = find_pairs_within(q, r=2.0)
    assert pairs.shape == (0, 2)
    q.add(pos=(0, 0, 0), vel=(0, 0, 0), freq=100, polarity=1, energy=1.0)
    pairs = find_pairs_within(q, r=2.0)
    assert pairs.shape == (0, 2)


def test_find_pairs_within_returns_close_pairs():
    q = Quanta(max_quanta=10)
    q.add(pos=(0.0, 0.0, 0.0), vel=(0, 0, 0), freq=100, polarity=1,
          energy=1.0)
    q.add(pos=(1.0, 0.0, 0.0), vel=(0, 0, 0), freq=100, polarity=1,
          energy=1.0)
    q.add(pos=(5.0, 0.0, 0.0), vel=(0, 0, 0), freq=100, polarity=1,
          energy=1.0)
    pairs = find_pairs_within(q, r=2.0)
    # Only (0, 1) is within r=2.0 of each other; slot 2 is far away
    assert pairs.shape == (1, 2)
    assert {tuple(p) for p in pairs} == {(0, 1)}


def test_find_pairs_within_ignores_dead_slots():
    q = Quanta(max_quanta=10)
    s0 = q.add(pos=(0, 0, 0), vel=(0, 0, 0), freq=100, polarity=1, energy=1.0)
    s1 = q.add(pos=(0.5, 0, 0), vel=(0, 0, 0), freq=100, polarity=1, energy=1.0)
    q.remove(s0)
    pairs = find_pairs_within(q, r=2.0)
    assert pairs.shape == (0, 2)


def test_find_pairs_within_returns_indices_ordered_low_high():
    q = Quanta(max_quanta=10)
    q.add(pos=(0, 0, 0), vel=(0, 0, 0), freq=100, polarity=1, energy=1.0)
    q.add(pos=(0.5, 0, 0), vel=(0, 0, 0), freq=100, polarity=1, energy=1.0)
    pairs = find_pairs_within(q, r=2.0)
    # Should return (0, 1), not (1, 0)
    assert pairs[0, 0] < pairs[0, 1]


def test_find_pairs_within_no_pair_at_exact_r():
    """Distance exactly r → not within r (strict inequality)."""
    q = Quanta(max_quanta=10)
    q.add(pos=(0, 0, 0), vel=(0, 0, 0), freq=100, polarity=1, energy=1.0)
    q.add(pos=(2.0, 0, 0), vel=(0, 0, 0), freq=100, polarity=1, energy=1.0)
    pairs = find_pairs_within(q, r=2.0)
    assert pairs.shape == (0, 2)
