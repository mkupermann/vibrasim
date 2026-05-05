import math
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import decay_unstable_nodes


def _seed_pair(w: World, pair_slot: int, e0_slot: int, e1_slot: int):
    """Seed one pair at pair_slot with constituents at e0_slot, e1_slot.
    All three slots must be distinct and within capacity."""
    w.k_alive[pair_slot] = True
    w.k_level[pair_slot] = 2
    w.k_pol[pair_slot] = True
    w.k_freq[pair_slot] = 4000.0
    w.k_pos[pair_slot] = [50.0, 50.0]
    w.k_alive[e0_slot] = False
    w.k_alive[e1_slot] = False
    w.k_level[e0_slot] = 1
    w.k_level[e1_slot] = 1
    start = w.k_comp_used
    w.k_comp_indices[start] = e0_slot
    w.k_comp_indices[start + 1] = e1_slot
    w.k_comp_offset[pair_slot] = start
    w.k_comp_offset[pair_slot + 1] = start + 2
    w.k_comp_kind[pair_slot] = 1
    w.k_comp_used = start + 2
    last = max(pair_slot, e0_slot, e1_slot)
    if last >= w.k_count:
        w.k_count = last + 1


def test_pair_decays_eventually():
    """Decayed-fraction over many seeded pairs and many ticks should match 1 - exp(-t/tau)."""
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(1000.0, 1000.0),
                      n_vibrations_max=4096, n_nodes_max=1024,
                      pair_decay_time=5.0, dt=1.0 / 60.0, rng_seed=42)
    n_pairs = 200
    w = World(cfg)
    # Pair k at slot k; its two constituents at slots n_pairs + 2k, n_pairs + 2k + 1.
    # No overlap: pair slots 0..199, constituent slots 200..599 — disjoint.
    for k in range(n_pairs):
        _seed_pair(w, k, n_pairs + 2 * k, n_pairs + 2 * k + 1)
    t_end = 5.0
    n_ticks = int(t_end / cfg.dt)
    for _ in range(n_ticks):
        decay_unstable_nodes(w, cfg.dt)
    decayed = sum(1 for k in range(n_pairs) if not w.k_alive[k])
    expected_share = 1.0 - math.exp(-t_end / cfg.pair_decay_time)
    actual_share = decayed / n_pairs
    assert abs(actual_share - expected_share) < 0.08


def test_atom_does_not_decay():
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100.0, 100.0),
                      n_vibrations_max=64, n_nodes_max=32, rng_seed=42)
    w = World(cfg)
    w.k_alive[0] = True
    w.k_level[0] = 4
    w.k_freq[0] = 18000.0
    w.k_pos[0] = [50.0, 50.0]
    w.k_count = 1
    for _ in range(10000):
        decay_unstable_nodes(w, cfg.dt)
    assert w.k_alive[0]
    assert w.k_level[0] == 4


def test_pair_decay_returns_constituents_alive():
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100.0, 100.0),
                      n_vibrations_max=64, n_nodes_max=32,
                      pair_decay_time=0.001,
                      dt=1.0 / 60.0, rng_seed=42)
    w = World(cfg)
    w.k_alive[0] = False
    w.k_level[0] = 1
    w.k_alive[1] = False
    w.k_level[1] = 1
    w.k_alive[2] = True
    w.k_level[2] = 2
    w.k_freq[2] = 4000.0
    w.k_pos[2] = [50.0, 50.0]
    start = w.k_comp_used
    w.k_comp_indices[start] = 0
    w.k_comp_indices[start + 1] = 1
    w.k_comp_offset[2] = start
    w.k_comp_offset[3] = start + 2
    w.k_comp_kind[2] = 1
    w.k_comp_used = start + 2
    w.k_count = 3
    for _ in range(1000):
        decay_unstable_nodes(w, cfg.dt)
        if not w.k_alive[2]:
            break
    assert not w.k_alive[2]
    assert w.k_alive[0]
    assert w.k_alive[1]
