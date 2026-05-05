import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import tick


def test_tick_advances_time(empty_world):
    w = empty_world
    tick(w, 0.5)
    assert w.t == pytest.approx(0.5)
    tick(w, 0.5)
    assert w.t == pytest.approx(1.0)


def test_tick_runs_full_default_world():
    """One tick on the default seeded world should not crash."""
    cfg = WorldConfig(rng_seed=42)
    w = World(cfg)
    tick(w, cfg.dt)
    assert w.t == pytest.approx(cfg.dt)


def test_compact_repacks_alive():
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100.0, 100.0),
                      n_vibrations_max=8, n_nodes_max=4, rng_seed=42)
    w = World(cfg)
    for i in (0, 2, 4, 6):
        w.s_pos[i] = [float(i), 0.0]
        w.s_alive[i] = True
    w.n_alive = 4
    w.compact()
    assert w.s_alive[0] and w.s_alive[1] and w.s_alive[2] and w.s_alive[3]
    assert not w.s_alive[4] and not w.s_alive[5] and not w.s_alive[6] and not w.s_alive[7]
    actual = sorted(w.s_pos[:4, 0].tolist())
    assert actual == [0.0, 2.0, 4.0, 6.0]
