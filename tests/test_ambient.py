import math
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import ambient_regeneration


def test_zero_lambda_no_change():
    cfg = WorldConfig(n_initial_vibrations=10, box_size=(100., 100., 100.),
                      lambda_gen=0.0, lambda_dec=0.0, rng_seed=42)
    w = World(cfg)
    before = int(w.s_alive.sum())
    for _ in range(1000):
        ambient_regeneration(w, cfg.dt)
    assert int(w.s_alive.sum()) == before


def test_generation_rate_matches_lambda():
    # n_ticks=200 keeps expected (~3333) well under n_vibrations_max=8192
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100., 100., 100.),
                      lambda_gen=0.001, lambda_dec=0.0,
                      n_vibrations_max=8192, rng_seed=42)
    w = World(cfg)
    n_ticks = 200
    expected = cfg.lambda_gen * 100 * 100 * 100 * cfg.dt * n_ticks
    for _ in range(n_ticks):
        ambient_regeneration(w, cfg.dt)
    actual = int(w.s_alive.sum())
    assert abs(actual - expected) / expected < 0.10


def test_decay_atoms_immune():
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100., 100., 100.),
                      lambda_gen=0.0, lambda_dec=1.0, rng_seed=42)
    w = World(cfg)
    w.k_alive[0] = True
    w.k_level[0] = 4
    w.k_count = 1
    for _ in range(10000):
        ambient_regeneration(w, cfg.dt)
    assert w.k_alive[0]


def test_capacity_overflow_safe():
    cfg = WorldConfig(n_initial_vibrations=10, box_size=(100., 100., 100.),
                      lambda_gen=10.0, lambda_dec=0.0,  # ridiculously high
                      n_vibrations_max=12, rng_seed=42)
    w = World(cfg)
    for _ in range(100):
        ambient_regeneration(w, cfg.dt)  # should not crash
    assert int(w.s_alive.sum()) <= 12
