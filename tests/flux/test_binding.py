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


from world.flux.structures import Nodes
from world.flux.grid import Grid
from world.flux.binding import attempt_binding


def test_attempt_binding_creates_node_at_centroid_when_temperature_low():
    q = Quanta(max_quanta=10)
    n = Nodes(max_nodes=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0, T_smoothing=1.0)
    cfg = BindingConfig(alpha=10.0, beta=10.0, T_crit=1.0,
                         eta=0.1, r=2.0)
    # Two coherent quanta in a cold voxel
    q.add(pos=(5.0, 5.0, 5.0), vel=(0, 0, 0), freq=200,
          polarity=1, energy=1.0)
    q.add(pos=(5.5, 5.0, 5.0), vel=(0, 0, 0), freq=200,
          polarity=1, energy=1.0)
    # T_local around (5,5,5) is 0 (no smoothing of any density)
    rng = np.random.default_rng(0)
    heat = attempt_binding(quanta=q, nodes=n, grid=g,
                            cfg=cfg, tick_index=0, rng=rng)
    # Both quanta should have bound (high p) into one node
    assert n.n_alive() == 1
    # Centroid at (5.25, 5, 5)
    np.testing.assert_allclose(n.pos[0], [5.25, 5.0, 5.0])
    # Energy: total in = 2.0; heat = 0.1 * 2.0 = 0.2; node holds 1.8
    np.testing.assert_allclose(n.energy[0], 1.8, atol=1e-12)
    np.testing.assert_allclose(heat, 0.2, atol=1e-12)
    # Quanta slots freed
    assert q.n_alive() == 0


def test_attempt_binding_does_not_bind_in_hot_zones():
    q = Quanta(max_quanta=10)
    n = Nodes(max_nodes=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    cfg = BindingConfig(alpha=4.0, beta=10.0, T_crit=1.0,
                         eta=0.1, r=2.0)
    q.add(pos=(5.0, 5.0, 5.0), vel=(0, 0, 0), freq=200,
          polarity=1, energy=1.0)
    q.add(pos=(5.5, 5.0, 5.0), vel=(0, 0, 0), freq=200,
          polarity=1, energy=1.0)
    # Force a hot temperature at that voxel
    g.T[5, 5, 5] = 100.0
    rng = np.random.default_rng(0)
    heat = attempt_binding(quanta=q, nodes=n, grid=g,
                            cfg=cfg, tick_index=0, rng=rng)
    # Hot zone → p_bind ≈ 0 → no binding
    assert n.n_alive() == 0
    assert heat == 0.0
    assert q.n_alive() == 2


def test_attempt_binding_skips_frequency_mismatched_pairs():
    q = Quanta(max_quanta=10)
    n = Nodes(max_nodes=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    cfg = BindingConfig(alpha=10.0, beta=10.0, T_crit=1.0,
                         eta=0.1, r=2.0, coherence_eps=1.0)
    q.add(pos=(5.0, 5.0, 5.0), vel=(0, 0, 0), freq=100,
          polarity=1, energy=1.0)
    q.add(pos=(5.5, 5.0, 5.0), vel=(0, 0, 0), freq=500,
          polarity=1, energy=1.0)
    rng = np.random.default_rng(0)
    heat = attempt_binding(quanta=q, nodes=n, grid=g,
                            cfg=cfg, tick_index=0, rng=rng)
    # Frequencies differ by 400 >> eps=1 → coh=0; the coherence-zero
    # path should skip the pair entirely before computing p_bind.
    assert n.n_alive() == 0
    assert heat == 0.0
    assert q.n_alive() == 2


def test_attempt_binding_with_no_pairs_is_noop():
    q = Quanta(max_quanta=10)
    n = Nodes(max_nodes=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    cfg = BindingConfig()
    rng = np.random.default_rng(0)
    heat = attempt_binding(quanta=q, nodes=n, grid=g,
                            cfg=cfg, tick_index=0, rng=rng)
    assert heat == 0.0
    assert n.n_alive() == 0


def test_attempt_binding_sets_node_freq_to_pair_mean():
    q = Quanta(max_quanta=10)
    n = Nodes(max_nodes=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    cfg = BindingConfig(alpha=10.0, beta=10.0, T_crit=1.0,
                         eta=0.0, r=2.0, coherence_eps=3.0)
    q.add(pos=(5.0, 5.0, 5.0), vel=(0, 0, 0), freq=199,
          polarity=1, energy=1.0)
    q.add(pos=(5.5, 5.0, 5.0), vel=(0, 0, 0), freq=201,
          polarity=1, energy=1.0)
    rng = np.random.default_rng(0)
    attempt_binding(quanta=q, nodes=n, grid=g,
                    cfg=cfg, tick_index=7, rng=rng)
    assert n.n_alive() == 1
    np.testing.assert_allclose(n.freq[0], 200.0)
    assert n.born_tick[0] == 7


# F1b additions: bridge creation at binding

def test_binding_creates_self_bridge_when_no_neighbors():
    """A fresh node should still get one self-bridge so it isn't
    orphaned by the plasticity pass on the same tick."""
    from world.flux.quantum import Quanta
    from world.flux.grid import Grid
    from world.flux.structures import Nodes
    from world.flux.bridges import Bridges
    from world.flux.binding import attempt_binding, BindingConfig

    q = Quanta(max_quanta=10)
    n = Nodes(max_nodes=10)
    b = Bridges(max_bridges=10)
    g = Grid(dims=(5, 5, 5), voxel_size=1.0)
    cfg = BindingConfig(alpha=10.0, beta=10.0, T_crit=1.0,
                         eta=0.1, r=2.0, r_bridge=2.0, bridge_w0=1.0)
    q.add(pos=(2.0, 2.0, 2.0), vel=(0, 0, 0), freq=200,
          polarity=1, energy=1.0)
    q.add(pos=(2.3, 2.0, 2.0), vel=(0, 0, 0), freq=200,
          polarity=1, energy=1.0)
    rng = np.random.default_rng(0)
    attempt_binding(q, n, g, cfg, tick_index=0, rng=rng, bridges=b)
    assert n.n_alive() == 1
    assert b.n_alive() == 1  # exactly the self-bridge
    slot = int(np.where(n.alive)[0][0])
    self_idx = b.find(src=slot, dst=slot)
    assert self_idx == 0
    assert float(b.weight[self_idx]) == 1.0


def test_binding_creates_two_directed_bridges_to_nearby_node():
    """When a new node forms near an existing node, two directed
    bridges connect them (plus the new node's self-bridge)."""
    from world.flux.quantum import Quanta
    from world.flux.grid import Grid
    from world.flux.structures import Nodes
    from world.flux.bridges import Bridges
    from world.flux.binding import attempt_binding, BindingConfig

    q = Quanta(max_quanta=10)
    n = Nodes(max_nodes=10)
    b = Bridges(max_bridges=10)
    g = Grid(dims=(5, 5, 5), voxel_size=1.0)
    # Pre-place an existing node
    n.add(pos=(2.0, 2.0, 2.5), energy=2.0, freq=200, born_tick=0)
    cfg = BindingConfig(alpha=10.0, beta=10.0, T_crit=1.0,
                         eta=0.1, r=2.0, r_bridge=2.0, bridge_w0=1.0)
    q.add(pos=(2.0, 2.0, 2.0), vel=(0, 0, 0), freq=200,
          polarity=1, energy=1.0)
    q.add(pos=(2.3, 2.0, 2.0), vel=(0, 0, 0), freq=200,
          polarity=1, energy=1.0)
    rng = np.random.default_rng(0)
    attempt_binding(q, n, g, cfg, tick_index=0, rng=rng, bridges=b)
    assert n.n_alive() == 2
    # Self-bridge for the new node + 2 directed bridges to/from the pre-existing one
    assert b.n_alive() == 3
