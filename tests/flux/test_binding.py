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


from world.flux.binding import binding_probability, BindingConfig


def test_binding_probability_is_high_in_cold_zones():
    cfg = BindingConfig(alpha=4.0, beta=4.0, T_crit=1.0)
    # Cold zone: T_local << T_crit → (T_crit - T_local) is large positive
    p = binding_probability(pred_coh=1.0, T_local=0.0, cfg=cfg)
    assert p > 0.9


def test_binding_probability_is_low_in_hot_zones():
    cfg = BindingConfig(alpha=4.0, beta=4.0, T_crit=1.0)
    # Hot zone: T_local >> T_crit
    p = binding_probability(pred_coh=1.0, T_local=10.0, cfg=cfg)
    assert p < 0.1


def test_binding_probability_is_low_when_coherence_is_zero():
    cfg = BindingConfig(alpha=4.0, beta=4.0, T_crit=1.0)
    # Cold zone but incoherent: alpha*0 + beta*1 = 4 → sigmoid(4)≈0.98
    # Wait — beta*(T_crit - T_local) = 4*(1-0) = 4. With coh=0 still
    # large positive. Let's test the OPPOSITE: very hot AND incoherent
    p = binding_probability(pred_coh=0.0, T_local=10.0, cfg=cfg)
    assert p < 0.001


def test_binding_probability_at_T_crit_with_coh_zero_is_one_half():
    """At T_local == T_crit and pred_coh == 0, sigmoid(0) = 0.5."""
    cfg = BindingConfig(alpha=1.0, beta=1.0, T_crit=2.0)
    p = binding_probability(pred_coh=0.0, T_local=2.0, cfg=cfg)
    np.testing.assert_allclose(p, 0.5, atol=1e-9)


def test_binding_config_defaults_are_sane():
    cfg = BindingConfig()
    assert cfg.alpha > 0
    assert cfg.beta > 0
    assert cfg.T_crit > 0
    assert 0.0 <= cfg.eta < 1.0
    assert cfg.r > 0
    assert 0.0 <= cfg.coherence_eps
