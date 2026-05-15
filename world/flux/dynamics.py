"""Per-tick orchestration.

Order of operations in one tick (spec §6, F1b subset):
1. Inject at hot floor (if injector provided)
2. Move free vibrations: pos += vel * dt
3. Absorb at cold faces → returns E_exported
4. Attempt binding (creates nodes + bridges via attempt_binding)
5. Structure-flux: count quanta through each bridge
6. Plasticity: strengthen bridges with flux, decay bridges without
7. Prune: remove w<w_min bridges; dissociate orphaned nodes
   → contributes to decay_heat
8. Update temperature field from current density

Return value:
- If nodes is None: returns E_exported as a float (F0-compatible).
- If nodes is provided: returns (E_exported, binding_heat, decay_heat).
  binding_heat = sum of η-export across binding events.
  decay_heat   = sum of dissociation energy across pruned nodes.

The injector closure is responsible for recording E_injected into
the auditor directly — tick does not surface it.

Cochlea + Synthesis + Attention reallocate remain deferred to F2.
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
         decay_cfg=None,
         bridges=None,
         plasticity_cfg=None,
         thermal_cfg=None,
         rng: np.random.Generator | None = None,
         tick_index: int = 0):
    """Run one tick.

    F0 mode (nodes is None): returns E_exported as a float.
    F1b mode (nodes provided): returns (E_exported, binding_heat,
    decay_heat) tuple. binding_heat / decay_heat are 0.0 when their
    configs aren't provided.

    F1c thermal: when `thermal_cfg` is provided, buoyancy + damping
    are applied right after move (step 3 in the amended tick order),
    and the thermal boundary clamp is applied right after the T-update
    (final step). Pure-substrate convection — no coupling to binding.
    """
    # 1. Inject
    if injector is not None:
        injector(quanta, grid)

    # 2. Move
    alive = quanta.alive
    if alive.any():
        quanta.pos[alive] += quanta.vel[alive] * dt

    # 3. Buoyancy + damping (F1c). Uses *this* tick's T_local from the
    # previous tick's update — consistent with the move-before-T pattern.
    # R-1b: pressure-gradient force (horizontal coupling) applied right
    # after buoyancy on the same T snapshot.
    if thermal_cfg is not None:
        from world.flux.thermal import apply_buoyancy_and_damping
        from world.flux.pressure import apply_pressure_gradient_force
        apply_buoyancy_and_damping(quanta, grid, thermal_cfg, dt)
        apply_pressure_gradient_force(
            quanta, grid,
            pressure_coeff=thermal_cfg.pressure_coeff, dt=dt,
        )

    # 4. Absorb
    exported = absorb_cold_faces(quanta, grid, delta=cold_face_delta)

    # 4. Attempt binding
    binding_heat = 0.0
    if nodes is not None and binding_cfg is not None:
        from world.flux.binding import attempt_binding
        rng_use = rng if rng is not None else np.random.default_rng()
        binding_heat = attempt_binding(
            quanta=quanta, nodes=nodes, grid=grid,
            cfg=binding_cfg, tick_index=tick_index, rng=rng_use,
            bridges=bridges,
        )

    # 5. F1a T-based decay (handles hot-zone suppression). Sums into
    # the same decay_heat channel as the F1b bridge-flux dissociation.
    decay_heat = 0.0
    if nodes is not None and decay_cfg is not None:
        from world.flux.decay import attempt_decay
        rng_use = rng if rng is not None else np.random.default_rng()
        decay_heat += attempt_decay(
            nodes=nodes, grid=grid, cfg=decay_cfg, rng=rng_use,
        )

    # 6-7. Structure-flux + plasticity + pruning (F1b: handles
    # decay-without-flux for T4)
    if (nodes is not None and bridges is not None
            and plasticity_cfg is not None):
        from world.flux.plasticity import (
            count_flux_through, apply_plasticity,
            prune_bridges_and_nodes,
        )
        flux_counts = count_flux_through(bridges, nodes, quanta,
                                          plasticity_cfg)
        apply_plasticity(bridges, flux_counts, plasticity_cfg,
                          tick_index=tick_index)
        decay_heat += prune_bridges_and_nodes(bridges, nodes,
                                               plasticity_cfg)

    # 8. Temperature
    density = _compute_density(quanta, grid)
    if thermal_cfg is not None:
        grid.update_temperature(
            density, spatial_sigma=thermal_cfg.T_spatial_sigma,
        )
    else:
        grid.update_temperature(density)

    # 9. Thermal boundary clamp (F1c). Pinned floor stays >= T_hot,
    # ceiling stays <= T_cold; interior voxels free to evolve from
    # density.
    if thermal_cfg is not None:
        from world.flux.thermal import enforce_thermal_boundaries
        enforce_thermal_boundaries(grid, thermal_cfg)

    if nodes is None:
        return exported
    return exported, binding_heat, decay_heat
