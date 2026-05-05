import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import move_vibrations


def test_motion_no_friction():
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100.0, 100.0),
                      n_vibrations_max=4, n_nodes_max=4, rng_seed=42)
    w = World(cfg)
    w.s_pos[0] = [10.0, 10.0]
    w.s_vel[0] = [3.0, 4.0]
    w.s_alive[0] = True
    w.n_alive = 1
    dt = 0.5
    n_ticks = 10
    expected_x = (10.0 + 3.0 * dt * n_ticks) % 100.0
    expected_y = (10.0 + 4.0 * dt * n_ticks) % 100.0
    for _ in range(n_ticks):
        move_vibrations(w.s_pos, w.s_vel, w.s_alive, np.array(cfg.box_size), dt)
    assert w.s_pos[0, 0] == pytest.approx(expected_x)
    assert w.s_pos[0, 1] == pytest.approx(expected_y)


def test_motion_periodic_boundary_wraps():
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100.0, 100.0),
                      n_vibrations_max=4, n_nodes_max=4, rng_seed=42)
    w = World(cfg)
    w.s_pos[0] = [99.0, 50.0]
    w.s_vel[0] = [5.0, 0.0]
    w.s_alive[0] = True
    w.n_alive = 1
    move_vibrations(w.s_pos, w.s_vel, w.s_alive, np.array(cfg.box_size), 1.0)
    assert w.s_pos[0, 0] == pytest.approx(4.0)
    assert w.s_pos[0, 1] == pytest.approx(50.0)


def test_motion_dead_vibrations_unchanged():
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100.0, 100.0),
                      n_vibrations_max=4, n_nodes_max=4, rng_seed=42)
    w = World(cfg)
    w.s_pos[0] = [10.0, 10.0]
    w.s_vel[0] = [5.0, 5.0]
    w.s_alive[0] = False
    move_vibrations(w.s_pos, w.s_vel, w.s_alive, np.array(cfg.box_size), 1.0)
    assert w.s_pos[0, 0] == pytest.approx(10.0)
    assert w.s_pos[0, 1] == pytest.approx(10.0)


def test_motion_speed_unchanged_after_wrap():
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100.0, 100.0),
                      n_vibrations_max=4, n_nodes_max=4, rng_seed=42)
    w = World(cfg)
    w.s_pos[0] = [99.0, 99.0]
    w.s_vel[0] = [3.0, 4.0]
    w.s_alive[0] = True
    w.n_alive = 1
    speed_before = float(np.linalg.norm(w.s_vel[0]))
    move_vibrations(w.s_pos, w.s_vel, w.s_alive, np.array(cfg.box_size), 1.0)
    speed_after = float(np.linalg.norm(w.s_vel[0]))
    assert speed_after == pytest.approx(speed_before)
