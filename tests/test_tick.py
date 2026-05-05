import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import tick


def test_tick_advances_time(empty_world):
    w = empty_world
    tick(w, 0.5)
    assert w.t == pytest.approx(0.5)


def test_tick_runs_full_default_world():
    """Full default 3D world ticks without crashing."""
    cfg = WorldConfig(rng_seed=42)
    w = World(cfg)
    tick(w, cfg.dt)
    assert w.t == pytest.approx(cfg.dt)


def test_tick_decay_then_bind_order():
    """A tick should update positions before binding scans."""
    # Smoke test — full tick on a world with 100 vibrations should not crash
    cfg = WorldConfig(n_initial_vibrations=100, box_size=(200., 200., 200.),
                      n_vibrations_max=256, n_nodes_max=64, rng_seed=42)
    w = World(cfg)
    for _ in range(10):
        tick(w, cfg.dt)
    assert w.t == pytest.approx(10 * cfg.dt)
