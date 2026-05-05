import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import move_vibrations


def test_motion_no_friction_3d():
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100.0, 100.0, 100.0),
                      n_vibrations_max=4, n_nodes_max=4, rng_seed=42)
    w = World(cfg)
    w.s_pos[0] = [10.0, 10.0, 10.0]
    w.s_vel[0] = [3.0, 4.0, 5.0]
    w.s_alive[0] = True
    w.n_alive = 1
    dt = 0.5
    n_ticks = 10
    box = np.array(cfg.box_size)
    for _ in range(n_ticks):
        move_vibrations(w.s_pos, w.s_vel, w.s_alive, box, dt)
    expected = ((np.array([10., 10., 10.]) + np.array([3., 4., 5.]) * dt * n_ticks)
                % np.array(cfg.box_size))
    assert np.allclose(w.s_pos[0], expected)


def test_motion_periodic_wrap_3d():
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100.0, 100.0, 100.0),
                      n_vibrations_max=4, n_nodes_max=4, rng_seed=42)
    w = World(cfg)
    w.s_pos[0] = [99.0, 99.0, 99.0]
    w.s_vel[0] = [5.0, 5.0, 5.0]
    w.s_alive[0] = True
    w.n_alive = 1
    box = np.array(cfg.box_size)
    move_vibrations(w.s_pos, w.s_vel, w.s_alive, box, 1.0)
    assert np.allclose(w.s_pos[0], [4.0, 4.0, 4.0])


def test_motion_dead_unchanged_3d():
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100.0, 100.0, 100.0),
                      n_vibrations_max=4, n_nodes_max=4, rng_seed=42)
    w = World(cfg)
    w.s_pos[0] = [10.0, 10.0, 10.0]
    w.s_vel[0] = [5.0, 5.0, 5.0]
    w.s_alive[0] = False
    move_vibrations(w.s_pos, w.s_vel, w.s_alive, np.array(cfg.box_size), 1.0)
    assert np.allclose(w.s_pos[0], [10.0, 10.0, 10.0])
