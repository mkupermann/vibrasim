"""Tests for the single-tick orchestration."""
from __future__ import annotations
import numpy as np

from world.flux.quantum import Quanta
from world.flux.grid import Grid
from world.flux.dynamics import tick


def test_tick_moves_quanta_by_velocity_times_dt():
    q = Quanta(max_quanta=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    q.add(pos=(5.0, 5.0, 5.0), vel=(1.0, 0.0, 0.5),
          freq=100, polarity=1, energy=1.0)
    tick(q, g, dt=0.1, injector=None)
    # Position should be (5.1, 5.0, 5.05)
    np.testing.assert_allclose(q.pos[0], [5.1, 5.0, 5.05])


def test_tick_absorbs_quanta_that_cross_cold_face():
    q = Quanta(max_quanta=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    # Quantum that will cross the ceiling in 1 tick
    q.add(pos=(5.0, 5.0, 9.0), vel=(0, 0, 5.0), freq=100, polarity=1,
          energy=1.0)
    exported = tick(q, g, dt=1.0, injector=None)
    assert exported == 1.0
    assert q.n_alive() == 0


def test_tick_updates_temperature_from_quanta_density():
    q = Quanta(max_quanta=10)
    g = Grid(dims=(4, 4, 4), voxel_size=1.0, T_smoothing=1.0)
    # 3 quanta all inside voxel (1, 1, 1)
    for _ in range(3):
        q.add(pos=(1.5, 1.5, 1.5), vel=(0, 0, 0),
              freq=100, polarity=1, energy=1.0)
    tick(q, g, dt=0.0, injector=None)  # dt=0: no motion
    # With T_smoothing=1.0 the new T is just the density
    assert g.T[1, 1, 1] == 3.0
    assert g.T[0, 0, 0] == 0.0


def test_tick_calls_injector_when_provided():
    q = Quanta(max_quanta=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    calls = {"count": 0, "injected": 0}
    def fake_injector(quanta, grid):
        quanta.add(pos=(5, 5, 0.1), vel=(0, 0, 1),
                   freq=100, polarity=1, energy=1.0)
        quanta.add(pos=(5, 5, 0.2), vel=(0, 0, 1),
                   freq=100, polarity=1, energy=1.0)
        calls["count"] += 1
        calls["injected"] += 2
        return 2.0
    # tick returns exported energy only; injector return value is
    # ignored by tick (the auditor tracks injection separately).
    exported = tick(q, g, dt=0.1, injector=fake_injector)
    assert calls["count"] == 1
    assert calls["injected"] == 2
    assert q.n_alive() == 2
    # At dt=0.1 and vel_z=1.0, neither quantum reaches the ceiling
    # (z=10) — nothing absorbed yet.
    assert exported == 0.0
