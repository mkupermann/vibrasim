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


def test_generation_converges_to_equilibrium_density():
    # R1: generation fills up to lambda_gen/lambda_dec * volume.
    # lambda_gen=0.001, lambda_dec=0.01 → target_density=0.1 → target_count=100
    # Buffer is large enough to hold the target and more.
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(10., 10., 10.),
                      lambda_gen=1.0, lambda_dec=1.0,
                      n_vibrations_max=8192, rng_seed=42)
    w = World(cfg)
    # After one call, deficit = target_count - 0 = 1000; fallback allocation fills it.
    ambient_regeneration(w, cfg.dt)
    actual = int(w.s_alive.sum())
    # target_count = int(1.0 * 10*10*10) = 1000
    assert actual == 1000


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
