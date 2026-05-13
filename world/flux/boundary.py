"""Boundary handling — hot floor injection + cold face absorption.

Hot floor is the z=0 face: source of new energy quanta.
Cold faces are z=Lz (ceiling) and the four side walls: energy sinks.
"""
from __future__ import annotations
import numpy as np

from world.flux.quantum import Quanta
from world.flux.grid import Grid


def inject_hot_floor(quanta: Quanta, grid: Grid,
                     n: int,
                     energy_per: float,
                     freq_mean: float,
                     vel_z_mean: float = 0.0,
                     freq_sigma: float = 0.0,
                     vel_xy_sigma: float = 0.1,
                     vel_z_sigma: float | None = None,
                     rng: np.random.Generator | None = None) -> int:
    """Inject up to `n` vibrations at the hot floor.

    Positions are uniform random in the z=0 voxel layer
    (x, y ∈ [0, Lx*size), z ∈ [0, voxel_size)).

    Velocity-z mode:
    - Default (vel_z_sigma=None): F0/F1a/F1b behavior — vel_z is gaussian
      around vel_z_mean with 20% scatter and clamped to vel_z_mean if it
      came out non-positive. Initialization is upward-biased.
    - F1c bidirectional (vel_z_sigma>0): vel_z is gaussian around 0.0 with
      sigma=vel_z_sigma. No upward clamp — buoyancy supplies the upward
      drift. `vel_z_mean` is ignored in this mode.

    Frequencies: Gaussian around freq_mean (sigma=freq_sigma).

    Returns: number actually injected (= n unless buffer fills first).
    """
    if rng is None:
        rng = np.random.default_rng()
    Lx, Ly, _ = grid.dims
    s = grid.voxel_size
    injected = 0
    for _ in range(n):
        x = rng.uniform(0.0, Lx * s)
        y = rng.uniform(0.0, Ly * s)
        z = rng.uniform(0.0, s)  # Z within first voxel layer
        vx = rng.normal(0.0, vel_xy_sigma)
        vy = rng.normal(0.0, vel_xy_sigma)
        if vel_z_sigma is not None:
            vz = rng.normal(0.0, vel_z_sigma)
        else:
            vz = rng.normal(vel_z_mean, vel_z_mean * 0.2)  # 20% scatter
            if vz <= 0.0:
                vz = vel_z_mean  # Floor at mean — keep upward
        freq = rng.normal(freq_mean, freq_sigma) if freq_sigma > 0 \
            else freq_mean
        slot = quanta.add(
            pos=(x, y, z), vel=(vx, vy, vz),
            freq=freq, polarity=1, energy=energy_per,
        )
        if slot < 0:
            break  # Buffer full
        injected += 1
    return injected


def absorb_cold_faces(quanta: Quanta, grid: Grid,
                      delta: float = 0.5) -> float:
    """Remove vibrations within delta of cold faces; return total
    absorbed energy.

    Cold faces: z = Lz*size (ceiling), x = 0, x = Lx*size,
    y = 0, y = Ly*size. The z = 0 face is the HOT FLOOR and is
    NOT absorbing.
    """
    Lx, Ly, Lz = grid.dims
    s = grid.voxel_size
    x_min, x_max = 0.0 + delta, Lx * s - delta
    y_min, y_max = 0.0 + delta, Ly * s - delta
    z_max = Lz * s - delta

    pos = quanta.pos
    alive = quanta.alive

    # Mask of alive quanta within delta of any cold face
    at_ceiling = (pos[:, 2] > z_max)
    at_x_low   = (pos[:, 0] < x_min)
    at_x_high  = (pos[:, 0] > x_max)
    at_y_low   = (pos[:, 1] < y_min)
    at_y_high  = (pos[:, 1] > y_max)

    to_absorb = alive & (at_ceiling | at_x_low | at_x_high |
                         at_y_low | at_y_high)

    idx = np.where(to_absorb)[0]
    return quanta.remove_batch(idx)
