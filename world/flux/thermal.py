"""Thermal layer — F1c.

Buoyancy: vel_z gets nudged by (T_local - T_ref) * buoyancy_g * dt.
Damping: vel *= (1 - damping_mu * dt). Both applied per tick to all
alive quanta.

Thermal boundaries clamp grid.T at floor and ceiling layers to keep
the convection driver constant.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass

from world.flux.quantum import Quanta
from world.flux.grid import Grid


@dataclass
class ThermalConfig:
    buoyancy_g: float = 2.0
    damping_mu: float = 0.5
    T_ref: float = 0.0           # if 0, buoyancy is one-sided (T>0 pushes up)
    T_hot_floor: float = 5.0
    T_cold_ceiling: float = 0.0


def apply_buoyancy_and_damping(quanta: Quanta, grid: Grid,
                                cfg: ThermalConfig, dt: float) -> None:
    """In-place update of quanta.vel.

    Buoyancy: vel_z += g * (T_local - T_ref) * dt
    Damping:  vel    *= (1 - μ * dt)
    """
    if quanta.n_alive() == 0:
        return
    alive = quanta.alive
    pos = quanta.pos[alive]
    s = grid.voxel_size
    Lx, Ly, Lz = grid.dims
    ix = np.clip((pos[:, 0] / s).astype(int), 0, Lx - 1)
    iy = np.clip((pos[:, 1] / s).astype(int), 0, Ly - 1)
    iz = np.clip((pos[:, 2] / s).astype(int), 0, Lz - 1)
    T_local = grid.T[ix, iy, iz]
    dvz = cfg.buoyancy_g * (T_local - cfg.T_ref) * dt
    quanta.vel[alive, 2] += dvz
    factor = 1.0 - cfg.damping_mu * dt
    quanta.vel[alive] *= factor


def enforce_thermal_boundaries(grid: Grid, cfg: ThermalConfig) -> None:
    """Clamp the floor layer at T_hot, ceiling layer at T_cold.

    Use max/min so the boundary conditions are a *floor*/*ceiling* on
    T at those layers, not an overwrite. This lets density-driven T
    updates only affect interior voxels.
    """
    grid.T[:, :, 0] = np.maximum(grid.T[:, :, 0], cfg.T_hot_floor)
    grid.T[:, :, -1] = np.minimum(grid.T[:, :, -1], cfg.T_cold_ceiling)
