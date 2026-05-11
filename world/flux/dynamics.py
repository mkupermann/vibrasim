"""Per-tick orchestration.

Order of operations in one tick (spec §6, F1a subset):
1. Inject at hot floor (if injector provided)
2. Move free vibrations: pos += vel * dt
3. Absorb at cold faces → returns E_exported
4. Attempt binding (if nodes + binding_cfg provided) → returns
   binding_heat
5. Update temperature field from new density

Return value:
- If nodes is None: returns E_exported as a float (F0-compatible).
- If nodes is provided: returns (E_exported, binding_heat) tuple.

The injector closure is responsible for recording E_injected into
the auditor directly — tick does not surface it.

F1 plasticity + structure-flux still deferred to F1b.
"""
from __future__ import annotations
from typing import Callable
import numpy as np

from world.flux.quantum import Quanta
from world.flux.grid import Grid
from world.flux.boundary import absorb_cold_faces


Injector = Callable[[Quanta, Grid], float]
"""Function (quanta, grid) -> energy_injected_this_tick."""


def _compute_density(quanta: Quanta, grid: Grid) -> np.ndarray:
    """Histogram alive quanta into voxel bins → counts per voxel."""
    Lx, Ly, Lz = grid.dims
    s = grid.voxel_size
    density = np.zeros(grid.dims, dtype=np.float64)
    if quanta.n_alive() == 0:
        return density
    alive = quanta.alive
    pos = quanta.pos[alive]
    ix = np.clip((pos[:, 0] / s).astype(int), 0, Lx - 1)
    iy = np.clip((pos[:, 1] / s).astype(int), 0, Ly - 1)
    iz = np.clip((pos[:, 2] / s).astype(int), 0, Lz - 1)
    np.add.at(density, (ix, iy, iz), 1.0)
    return density


def tick(quanta: Quanta, grid: Grid, dt: float,
         injector: Injector | None,
         cold_face_delta: float = 0.5,
         *,
         nodes=None,
         binding_cfg=None,
         rng: np.random.Generator | None = None,
         tick_index: int = 0):
    """Run one tick.

    F0 mode (nodes is None): returns E_exported as a float.
    F1a mode (nodes provided): returns (E_exported, binding_heat) tuple.
    """
    # 1. Inject
    if injector is not None:
        injector(quanta, grid)

    # 2. Move
    alive = quanta.alive
    if alive.any():
        quanta.pos[alive] += quanta.vel[alive] * dt

    # 3. Absorb
    exported = absorb_cold_faces(quanta, grid, delta=cold_face_delta)

    # 4. Attempt binding (F1a)
    binding_heat = 0.0
    if nodes is not None and binding_cfg is not None:
        # Lazy import to avoid circular dependency at module load
        from world.flux.binding import attempt_binding
        rng_use = rng if rng is not None else np.random.default_rng()
        binding_heat = attempt_binding(
            quanta=quanta, nodes=nodes, grid=grid,
            cfg=binding_cfg, tick_index=tick_index, rng=rng_use,
        )

    # 5. Temperature
    density = _compute_density(quanta, grid)
    grid.update_temperature(density)

    if nodes is None:
        return exported
    return exported, binding_heat
