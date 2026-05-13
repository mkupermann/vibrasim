"""Tests for thermal layer — F1c."""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.quantum import Quanta
from world.flux.grid import Grid
from world.flux.thermal import (
    ThermalConfig,
    apply_buoyancy_and_damping,
    enforce_thermal_boundaries,
)


def test_buoyancy_pushes_quanta_up_in_hot_voxel():
    q = Quanta(max_quanta=10)
    g = Grid(dims=(5, 5, 5), voxel_size=1.0)
    g.T[2, 2, 0] = 10.0  # hot floor voxel
    slot = q.add(pos=(2.5, 2.5, 0.5), vel=(0, 0, 0),
                 freq=1.0, polarity=1, energy=1.0)
    cfg = ThermalConfig(buoyancy_g=2.0, damping_mu=0.0, T_ref=0.0)
    apply_buoyancy_and_damping(q, g, cfg, dt=0.1)
    # Δvz = buoyancy_g * (T_local - T_ref) * dt = 2.0 * 10.0 * 0.1 = 2.0
    assert q.vel[slot, 2] == pytest.approx(2.0)
    # No buoyancy in x/y
    assert q.vel[slot, 0] == pytest.approx(0.0)
    assert q.vel[slot, 1] == pytest.approx(0.0)


def test_buoyancy_does_not_push_in_cold_voxel():
    q = Quanta(max_quanta=10)
    g = Grid(dims=(5, 5, 5), voxel_size=1.0)
    g.T[:] = 0.0  # uniform cold
    slot = q.add(pos=(2.5, 2.5, 4.5), vel=(0, 0, 0),
                 freq=1.0, polarity=1, energy=1.0)
    cfg = ThermalConfig(buoyancy_g=2.0, damping_mu=0.0, T_ref=0.0)
    apply_buoyancy_and_damping(q, g, cfg, dt=0.1)
    assert q.vel[slot, 2] == pytest.approx(0.0)


def test_damping_shrinks_velocity():
    q = Quanta(max_quanta=10)
    g = Grid(dims=(5, 5, 5), voxel_size=1.0)
    slot = q.add(pos=(2.5, 2.5, 2.5), vel=(1.0, -1.0, 2.0),
                 freq=1.0, polarity=1, energy=1.0)
    cfg = ThermalConfig(buoyancy_g=0.0, damping_mu=0.5, T_ref=0.0)
    apply_buoyancy_and_damping(q, g, cfg, dt=0.1)
    # vel *= (1 - μ*dt) = (1 - 0.05) = 0.95
    np.testing.assert_allclose(q.vel[slot], [0.95, -0.95, 1.9])


def test_damping_only_affects_alive_quanta():
    q = Quanta(max_quanta=10)
    g = Grid(dims=(5, 5, 5), voxel_size=1.0)
    s = q.add(pos=(2.5, 2.5, 2.5), vel=(1.0, 0.0, 0.0),
              freq=1.0, polarity=1, energy=1.0)
    q.remove(s)
    pre_vel = q.vel[s].copy()
    cfg = ThermalConfig(buoyancy_g=0.0, damping_mu=0.5, T_ref=0.0)
    apply_buoyancy_and_damping(q, g, cfg, dt=0.1)
    # Dead slot must be untouched by damping (alive mask gates the update).
    np.testing.assert_allclose(q.vel[s], pre_vel)


def test_thermal_boundaries_clamp_floor_and_ceiling():
    g = Grid(dims=(5, 5, 5), voxel_size=1.0)
    g.T[:, :, 0] = 1.0
    g.T[:, :, 4] = 3.0
    cfg = ThermalConfig(T_hot_floor=5.0, T_cold_ceiling=0.5)
    enforce_thermal_boundaries(g, cfg)
    assert (g.T[:, :, 0] == 5.0).all()  # raised to T_hot
    assert (g.T[:, :, 4] == 0.5).all()  # lowered to T_cold


def test_thermal_boundaries_dont_disturb_middle():
    g = Grid(dims=(5, 5, 5), voxel_size=1.0)
    g.T[:, :, 2] = 1.5
    cfg = ThermalConfig(T_hot_floor=5.0, T_cold_ceiling=0.0)
    enforce_thermal_boundaries(g, cfg)
    assert (g.T[:, :, 2] == 1.5).all()
