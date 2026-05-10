"""Per-tick orchestration.

Order of operations in one tick (matches spec §6 for F0):
1. Inject at hot floor (if injector provided) → returns E_injected
2. Move free vibrations: pos += vel * dt
3. Absorb at cold faces → returns E_exported
4. Update temperature field from new density

Returns E_exported (the energy that left through cold faces).
The injector closure is responsible for recording E_injected
into the auditor directly — tick does not surface it.
F1 will add structure-flux and binding-attempt steps. F0 is motion +
boundary + temperature only — no plasticity, no binding.
"""
from __future__ import annotations
from typing import Callable, Optional
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
         injector: Optional[Injector],
         cold_face_delta: float = 0.5) -> float:
    """Run one tick. Returns E_exported (energy that left through cold
    faces).

    The caller is responsible for summing injected vs. exported and
    checking conservation — see audit.py.
    """
    # 1. Inject
    if injector is not None:
        # injector mutates `quanta`; we don't use its return here
        # since the auditor tracks injected separately via the
        # boundary helper return value. For F0 this is informational.
        injector(quanta, grid)

    # 2. Move
    alive = quanta.alive
    if alive.any():
        quanta.pos[alive] += quanta.vel[alive] * dt

    # 3. Absorb
    exported = absorb_cold_faces(quanta, grid, delta=cold_face_delta)

    # 4. Temperature
    density = _compute_density(quanta, grid)
    grid.update_temperature(density)

    return exported
