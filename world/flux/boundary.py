"""Boundary handling — hot floor injection + cold face absorption.

Hot floor is the z=0 face: source of new energy quanta.
Cold faces are z=Lz (ceiling) and the four side walls: energy sinks.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

from world.flux.quantum import Quanta
from world.flux.grid import Grid


@dataclass
class CeilingReturnConfig:
    """R-1c-bis position-preserving return-flow configuration.

    When a quantum is absorbed at the cold ceiling, immediately re-inject
    a new quantum at the SAME (x, y) location with downward velocity.
    Side-wall absorption is unaffected — those quanta are simply lost.
    The (x, y) signature of where rising plumes are arriving is preserved
    in the return injection, which closes the Bénard cell loop.
    """
    vel_z_sigma: float = 0.5
    vel_xy_sigma: float = 0.5
    freq_mean: float = 200.0
    energy_per: float = 1.0


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


def inject_cold_ceiling(quanta: Quanta, grid: Grid,
                        n: int,
                        energy_per: float,
                        freq_mean: float,
                        vel_z_sigma: float,
                        vel_xy_sigma: float = 0.1,
                        rng: np.random.Generator | None = None) -> int:
    """R-1c-bis return-flow injector at the cold ceiling.

    Symmetric to `inject_hot_floor` (bidirectional mode): uniform random
    `(x, y)` in the ceiling voxel layer `z ∈ [(Lz-1)·s, Lz·s)`. Velocity
    is gaussian on the horizontal axes; `vel_z = -|N(0, vel_z_sigma)|`
    is strictly non-positive (downward) so the injected quantum drifts
    into the bulk on the next move step instead of being absorbed
    immediately at the cold-face boundary.

    Polarity = -1 marks ceiling-injected quanta (informational; T2 and
    F1c thermal physics do not gate on polarity).

    Returns the number actually injected (= n unless the quanta buffer
    fills first).
    """
    if rng is None:
        rng = np.random.default_rng()
    Lx, Ly, Lz = grid.dims
    s = grid.voxel_size
    z_lo = (Lz - 1) * s
    z_hi = Lz * s
    injected = 0
    for _ in range(n):
        x = rng.uniform(0.0, Lx * s)
        y = rng.uniform(0.0, Ly * s)
        z = rng.uniform(z_lo, z_hi)
        vx = rng.normal(0.0, vel_xy_sigma)
        vy = rng.normal(0.0, vel_xy_sigma)
        vz = -abs(rng.normal(0.0, vel_z_sigma))
        slot = quanta.add(
            pos=(x, y, z), vel=(vx, vy, vz),
            freq=freq_mean, polarity=-1, energy=energy_per,
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


def absorb_cold_faces_with_ceiling_return(
    quanta: Quanta, grid: Grid,
    *, delta: float = 0.5,
    return_cfg: CeilingReturnConfig,
    rng: np.random.Generator,
) -> float:
    """R-1c-bis position-preserving return-flow absorber.

    Drop-in replacement for `absorb_cold_faces`. For each quantum
    absorbed at the cold ceiling (and *not* simultaneously at a side
    wall), immediately re-inject a new quantum at the SAME (x, y)
    location, at the top of the ceiling voxel layer just below the
    absorption threshold, with downward velocity. Side-wall absorption
    proceeds without return injection.

    Audit accounting: the re-injection is treated as "delayed
    non-absorption" from the energy-conservation perspective — the
    returned value is the NET exported energy
    (`e_absorbed - e_returned`). The caller records that single value
    via `audit.record_export()`, and the re-injected quanta show up in
    `quanta.total_energy()` naturally. The conservation law balances
    without any additional record_injection call.

    Returns the net exported energy.
    """
    Lx, Ly, Lz = grid.dims
    s = grid.voxel_size
    x_min, x_max = delta, Lx * s - delta
    y_min, y_max = delta, Ly * s - delta
    z_max = Lz * s - delta

    pos = quanta.pos
    alive = quanta.alive

    at_ceiling = (pos[:, 2] > z_max)
    at_sides = (
        (pos[:, 0] < x_min) | (pos[:, 0] > x_max)
        | (pos[:, 1] < y_min) | (pos[:, 1] > y_max)
    )

    only_ceiling = alive & at_ceiling & ~at_sides
    any_absorption = alive & (at_ceiling | at_sides)

    # Snapshot (x, y) of pure-ceiling absorptions BEFORE removal.
    only_ceiling_idx = np.where(only_ceiling)[0]
    rx = pos[only_ceiling_idx, 0].copy()
    ry = pos[only_ceiling_idx, 1].copy()

    # Remove all absorbed quanta in one batched call.
    abs_idx = np.where(any_absorption)[0]
    e_absorbed = quanta.remove_batch(abs_idx)

    # Re-inject downward at each pure-ceiling absorption position.
    # Place just below the absorption threshold so the next absorb step
    # does not immediately re-remove them.
    z_inj = max(z_max - 1e-3, (Lz - 1) * s)
    e_returned = 0.0
    n_xy = rx.shape[0]
    if n_xy > 0:
        # Vectorise the per-quantum random draws — the Python loop only
        # handles quanta.add (still O(N_alive) per call, but the count
        # is small relative to total alive).
        vxs = rng.normal(0.0, return_cfg.vel_xy_sigma, size=n_xy)
        vys = rng.normal(0.0, return_cfg.vel_xy_sigma, size=n_xy)
        vzs = -np.abs(rng.normal(0.0, return_cfg.vel_z_sigma, size=n_xy))
        for k in range(n_xy):
            slot = quanta.add(
                pos=(rx[k], ry[k], z_inj),
                vel=(vxs[k], vys[k], vzs[k]),
                freq=return_cfg.freq_mean, polarity=-1,
                energy=return_cfg.energy_per,
            )
            if slot < 0:
                break  # buffer full — remaining returns lost as export
            e_returned += return_cfg.energy_per

    return float(e_absorbed - e_returned)
