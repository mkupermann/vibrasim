"""Tests for plasticity: structure-flux count + Hebbian rules + pruning."""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.quantum import Quanta
from world.flux.structures import Nodes
from world.flux.bridges import Bridges
from world.flux.plasticity import (
    PlasticityConfig,
    count_flux_through,
    apply_plasticity,
    prune_bridges_and_nodes,
)


def test_flux_count_self_bridge_counts_sphere():
    q = Quanta(max_quanta=10)
    n = Nodes(max_nodes=2)
    b = Bridges(max_bridges=2)
    cfg = PlasticityConfig(r_flux=1.0)
    n.add(pos=(5.0, 5.0, 5.0), energy=1.0, freq=1.0, born_tick=0)
    b.add(src=0, dst=0, weight=1.0, born_tick=0)
    # one inside r_flux, one outside
    q.add(pos=(5.5, 5.0, 5.0), vel=(0, 0, 0), freq=1, polarity=1, energy=1.0)
    q.add(pos=(7.0, 7.0, 7.0), vel=(0, 0, 0), freq=1, polarity=1, energy=1.0)
    flux = count_flux_through(b, n, q, cfg)
    assert int(flux[0]) == 1


def test_flux_count_pair_bridge_counts_quanta_near_segment():
    q = Quanta(max_quanta=10)
    n = Nodes(max_nodes=4)
    b = Bridges(max_bridges=4)
    cfg = PlasticityConfig(r_flux=0.5)
    n.add(pos=(0.0, 0.0, 0.0), energy=1.0, freq=1.0, born_tick=0)
    n.add(pos=(10.0, 0.0, 0.0), energy=1.0, freq=1.0, born_tick=0)
    b.add(src=0, dst=1, weight=1.0, born_tick=0)
    # one on the segment, one far away, one near but perpendicular dist > r_flux
    q.add(pos=(5.0, 0.0, 0.0), vel=(0, 0, 0), freq=1, polarity=1, energy=1.0)
    q.add(pos=(5.0, 5.0, 0.0), vel=(0, 0, 0), freq=1, polarity=1, energy=1.0)
    q.add(pos=(5.0, 0.3, 0.0), vel=(0, 0, 0), freq=1, polarity=1, energy=1.0)
    flux = count_flux_through(b, n, q, cfg)
    assert int(flux[0]) == 2  # the on-segment one and the 0.3-perp one


def test_apply_plasticity_strengthens_with_flux():
    b = Bridges(max_bridges=4)
    b.add(src=0, dst=1, weight=1.0, born_tick=0)
    cfg = PlasticityConfig(gamma=0.5, lam=0.1, flux_min=1.0)
    flux = np.zeros(4, dtype=np.int64)
    flux[0] = 4  # well above flux_min
    apply_plasticity(b, flux, cfg, tick_index=5)
    assert float(b.weight[0]) == pytest.approx(1.0 + 0.5 * 4)
    assert int(b.last_flux_tick[0]) == 5


def test_apply_plasticity_decays_without_flux():
    b = Bridges(max_bridges=4)
    b.add(src=0, dst=1, weight=1.0, born_tick=0)
    cfg = PlasticityConfig(gamma=0.1, lam=0.5, flux_min=2.0)
    flux = np.zeros(4, dtype=np.int64)  # zero flux
    apply_plasticity(b, flux, cfg, tick_index=10)
    # deficit = 2.0; decay = 0.5*2.0 = 1.0
    assert float(b.weight[0]) == pytest.approx(0.0)
    # last_flux_tick NOT updated because flux=0
    assert int(b.last_flux_tick[0]) == 0


def test_prune_removes_low_weight_bridges():
    b = Bridges(max_bridges=4)
    n = Nodes(max_nodes=4)
    n.add(pos=(0, 0, 0), energy=1.0, freq=1, born_tick=0)
    n.add(pos=(1, 0, 0), energy=1.0, freq=1, born_tick=0)
    b.add(src=0, dst=1, weight=0.01, born_tick=0)  # below w_min
    b.add(src=1, dst=0, weight=1.0, born_tick=0)
    cfg = PlasticityConfig(w_min=0.05)
    prune_bridges_and_nodes(b, n, cfg)
    assert int(b.alive[0]) == 0
    assert int(b.alive[1]) == 1


def test_prune_dissociates_orphaned_nodes():
    b = Bridges(max_bridges=4)
    n = Nodes(max_nodes=4)
    n.add(pos=(0, 0, 0), energy=2.5, freq=1, born_tick=0)
    n.add(pos=(1, 0, 0), energy=1.5, freq=1, born_tick=0)
    # No bridges → both nodes are orphans
    cfg = PlasticityConfig(w_min=0.05)
    heat = prune_bridges_and_nodes(b, n, cfg)
    assert heat == pytest.approx(4.0)
    assert n.n_alive() == 0


def test_prune_keeps_node_with_self_bridge():
    b = Bridges(max_bridges=4)
    n = Nodes(max_nodes=4)
    n.add(pos=(0, 0, 0), energy=1.0, freq=1, born_tick=0)
    b.add(src=0, dst=0, weight=1.0, born_tick=0)
    cfg = PlasticityConfig(w_min=0.05)
    heat = prune_bridges_and_nodes(b, n, cfg)
    assert heat == 0.0
    assert n.n_alive() == 1
