"""Pressure-gradient force — F1c R-1b architectural extension.

The substrate had only vertical buoyancy and isotropic damping, so a
vertical T gradient could not produce the *horizontal* return flow that
closes a Bénard convection cell. Phase-log 2026-05-14 (F1c close) flagged
the seed=42 T2 pass as a lucky-seed state-detector, not a mechanistic
finding.

This module adds the missing horizontal coupling without leaving the
"energy flux + minimal interaction rules" envelope: pressure is computed
bottom-up from the same quanta the substrate already tracks. P = ρ * T
where ρ is per-voxel quanta density. The per-quantum force is

    Δvel = -pressure_coeff * ∇P * dt

evaluated at the quantum's voxel. np.gradient gives ∇P along each axis
using central differences in the interior and one-sided differences on
boundary voxels. Cost: one density histogram + one np.gradient call per
tick, both O(N_voxel) + O(N_alive).
"""
from __future__ import annotations
import numpy as np

from world.flux.quantum import Quanta
from world.flux.grid import Grid


def apply_pressure_gradient_force(quanta: Quanta, grid: Grid,
                                   *, pressure_coeff: float,
                                   dt: float) -> None:
    """In-place vel update: vel += -pressure_coeff * ∇(ρ*T) * dt at each
    quantum's voxel.

    No-op when no quanta are alive. Quanta sitting in the same voxel
    receive the same force (consistent with the buoyancy pattern).
    """
    if quanta.n_alive() == 0:
        return
    if pressure_coeff == 0.0 or dt == 0.0:
        return

    Lx, Ly, Lz = grid.dims
    s = grid.voxel_size

    alive = quanta.alive
    pos = quanta.pos[alive]
    ix = np.clip((pos[:, 0] / s).astype(int), 0, Lx - 1)
    iy = np.clip((pos[:, 1] / s).astype(int), 0, Ly - 1)
    iz = np.clip((pos[:, 2] / s).astype(int), 0, Lz - 1)

    density = np.zeros(grid.dims, dtype=np.float64)
    np.add.at(density, (ix, iy, iz), 1.0)
    P = density * grid.T

    # np.gradient(..., axis=k) needs dim_k >= 2; otherwise gradient is 0.
    grads = []
    for axis, d in enumerate(grid.dims):
        if d >= 2:
            grads.append(np.gradient(P, s, axis=axis))
        else:
            grads.append(np.zeros_like(P))
    gx, gy, gz = grads

    quanta.vel[alive, 0] -= pressure_coeff * gx[ix, iy, iz] * dt
    quanta.vel[alive, 1] -= pressure_coeff * gy[ix, iy, iz] * dt
    quanta.vel[alive, 2] -= pressure_coeff * gz[ix, iy, iz] * dt
