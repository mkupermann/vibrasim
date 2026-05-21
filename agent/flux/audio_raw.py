"""Encoder-free audio input adapter — R-10.

Injects exactly one energy quantum per audio sample into the substrate's
hot floor with:

- ``energy = abs(sample_value)``     (LOCKED — see detailed plan §"Energy-
                                       mapping rule"; NOT ``sample**2``)
- ``freq   = log(sample_rate_hz/2)`` (LOCKED — Nyquist constant; substrate
                                       receives NO frequency information)
- ``pos``  = deterministic hash of ``sample_index`` over the hot-floor xy
            plane (same input → same xy positions, reproducibility for
            R-11's matched no-input control)
- ``vel_z`` = positive constant       (upward drift, matches F2 cochlea)
- ``polarity`` = +1                    (thermal mass, unlike R-1d-T3-bis
                                       scaffold which is polarity=-1)

Unlike :func:`world.flux.boundary.inject_hot_floor`, the per-sample xy
position is **deterministic** in ``sample_index`` (not random). The
plan specifies this so the encoder-free R-11 training run and the
matched no-input control inject at byte-identical floor positions modulo
trained injecting and control not injecting at all.

See ``docs/superpowers/plans/2026-05-17-flux-encoder-free-audio-detailed.md``
for the locked design decisions. R-10 unit-level acceptance lives in
``tests/flux/test_audio_raw_injection.py``.
"""
from __future__ import annotations

import math
import os

import numpy as np

from world.flux.quantum import Quanta
from world.flux.grid import Grid


# SplitMix64 constants (Vigna 2014). Pure-Python 64-bit integer hash;
# deterministic and dependency-free.
_SM_INC = 0x9E3779B97F4A7C15
_SM_MIX1 = 0xBF58476D1CE4E5B9
_SM_MIX2 = 0x94D049BB133111EB
_MASK64 = 0xFFFFFFFFFFFFFFFF
_INV_UINT32_RANGE = 1.0 / 4294967296.0  # 1 / 2**32


def _splitmix64(x: int, seed: int = 0) -> int:
    """Stateless 64-bit SplitMix64 hash with an additive seed.

    Implementation matches Vigna 2014; used here only for deterministic
    per-sample-index xy mapping (not as a cryptographic hash).
    """
    z = (x + (seed + 1) * _SM_INC) & _MASK64
    z = ((z ^ (z >> 30)) * _SM_MIX1) & _MASK64
    z = ((z ^ (z >> 27)) * _SM_MIX2) & _MASK64
    z ^= z >> 31
    return z


def position_hash(sample_index: int, Lx: int, Ly: int,
                  voxel_size: float, *, seed: int = 0) -> tuple[float, float]:
    """Map ``sample_index`` to a deterministic (x, y) on the hot-floor plane.

    Returns ``(x, y)`` with ``x ∈ [0, Lx*voxel_size)`` and
    ``y ∈ [0, Ly*voxel_size)``. Same ``sample_index`` and ``seed``
    always return the same (x, y). The hash splits a 64-bit SplitMix64
    output into two 32-bit halves and scales each half to the floor
    extent.
    """
    h = _splitmix64(int(sample_index), seed=int(seed))
    hi = (h >> 32) & 0xFFFFFFFF
    lo = h & 0xFFFFFFFF
    x = (hi * _INV_UINT32_RANGE) * (Lx * voxel_size)
    y = (lo * _INV_UINT32_RANGE) * (Ly * voxel_size)
    return float(x), float(y)


DEFAULT_VEL_Z_INIT = 1.0
DEFAULT_VEL_XY_SIGMA = 0.1

# G26 density-by-amplitude parameters (amendment §1.1). Linear scale
# K=4 and hard cap N_MAX=4 chosen pre-data; locked by R-22 protocol.
DENSITY_K = 4
DENSITY_N_MAX = 4


def density_count(sample_value: float) -> int:
    """G26 §3 row 1: schoolbook-rounded count of quanta to inject.

    ``n = clip(round(|sample_value| * DENSITY_K), 0, DENSITY_N_MAX)``
    where ``round`` is the schoolbook rule (always round half away from
    zero), implemented as ``floor(x + 0.5)`` to avoid banker's rounding
    on exact halves. The brief's pseudocode uses ``np.round`` which is
    banker's; the locked acceptance fixtures (n(0.125)=1, etc.) require
    schoolbook rounding, so this implementation pins schoolbook.
    """
    a = abs(float(sample_value))
    n = int(math.floor(a * DENSITY_K + 0.5))
    if n < 0:
        return 0
    if n > DENSITY_N_MAX:
        return DENSITY_N_MAX
    return n


def _use_density_by_amplitude() -> bool:
    """Read EQMOD_USE_DENSITY_BY_AMPLITUDE at call time, not import."""
    return os.environ.get("EQMOD_USE_DENSITY_BY_AMPLITUDE", "0") == "1"


def _subvoxel_offset(sample_index: int, i: int, voxel_size: float) -> tuple[float, float]:
    """Deterministic sub-voxel xy offset for quantum ``i`` of a density burst.

    Uses SplitMix64 on ``(sample_index, i)`` so the offset is bit-stable
    across seeds and OS replays. Spread is ±0.5 voxel in each axis so
    N quanta from one sample land in nearby (but typically distinct)
    grid cells, per amendment §1.1 "distinct sub-voxel positions so
    they don't all stack on a single grid cell".
    """
    mix = (int(sample_index) & 0xFFFFFFFFFFFFFFFF) ^ ((int(i) * 0x9E3779B1) & 0xFFFFFFFFFFFFFFFF)
    h = _splitmix64(mix, seed=0)
    dx = (((h >> 32) & 0xFFFFFFFF) * _INV_UINT32_RANGE - 0.5) * voxel_size
    dy = ((h & 0xFFFFFFFF) * _INV_UINT32_RANGE - 0.5) * voxel_size
    return float(dx), float(dy)


def inject_raw_audio_sample_density(
    quanta: Quanta,
    grid: Grid,
    sample_value: float,
    sample_index: int,
    *,
    sample_rate_hz: int = 16000,
    rng: np.random.Generator | None = None,
    position_hash_seed: int = 0,
    vel_z_init: float = DEFAULT_VEL_Z_INIT,
    vel_xy_sigma: float = DEFAULT_VEL_XY_SIGMA,
) -> int:
    """G26 density-by-amplitude injection: inject ``n`` quanta per sample.

    ``n = density_count(sample_value)``. Each quantum carries energy
    ``|sample_value| / n`` so the sum across the burst equals
    ``|sample_value|`` (T1 conservation invariant identical to legacy).
    For ``n == 0`` no quanta are injected (silent samples consume no
    buffer slots; energy injected is exactly 0, same as legacy zero-
    amplitude case).

    Sub-voxel xy offsets are deterministic in ``(sample_index, i)``
    (not RNG-derived) so test 6's same-audio-different-seed negative
    control sees identical xy patterns from the density burst. RNG
    is still consumed for z-position and xy-velocity scatter to keep
    legacy thermal/Brownian behaviour intact.

    Returns the number of quanta actually injected (= ``n`` unless the
    buffer fills mid-burst, at which point the burst halts).
    """
    if rng is None:
        rng = np.random.default_rng()
    n = density_count(sample_value)
    if n == 0:
        return 0
    Lx, Ly, _ = grid.dims
    s = grid.voxel_size
    base_x, base_y = position_hash(
        sample_index, Lx, Ly, s, seed=position_hash_seed,
    )
    energy_per_quantum = abs(float(sample_value)) / n
    freq = float(np.log(sample_rate_hz / 2.0))
    injected = 0
    for i in range(n):
        dx, dy = _subvoxel_offset(sample_index, i, s)
        x = base_x + dx
        y = base_y + dy
        z = float(rng.uniform(0.0, s))
        vx = float(rng.normal(0.0, vel_xy_sigma))
        vy = float(rng.normal(0.0, vel_xy_sigma))
        vz = float(vel_z_init)
        slot = quanta.add(
            pos=(x, y, z), vel=(vx, vy, vz),
            freq=freq, polarity=1, energy=energy_per_quantum,
        )
        if slot < 0:
            break  # buffer full mid-burst
        injected += 1
    return injected


def inject_raw_audio_sample(
    quanta: Quanta,
    grid: Grid,
    sample_value: float,
    sample_index: int,
    *,
    sample_rate_hz: int = 16000,
    rng: np.random.Generator | None = None,
    position_hash_seed: int = 0,
    vel_z_init: float = DEFAULT_VEL_Z_INIT,
    vel_xy_sigma: float = DEFAULT_VEL_XY_SIGMA,
) -> int:
    """Inject one energy quantum at the hot floor for one audio sample.

    Returns ``1`` on success, ``0`` if the :class:`Quanta` buffer is full.

    The per-sample-index xy is deterministic; ``rng`` is consumed only
    for the small Brownian xy-velocity scatter and the z-position
    within the first voxel layer.
    """
    if rng is None:
        rng = np.random.default_rng()
    if _use_density_by_amplitude():
        return inject_raw_audio_sample_density(
            quanta, grid, sample_value, sample_index,
            sample_rate_hz=sample_rate_hz, rng=rng,
            position_hash_seed=position_hash_seed,
            vel_z_init=vel_z_init, vel_xy_sigma=vel_xy_sigma,
        )
    Lx, Ly, _ = grid.dims
    s = grid.voxel_size
    x, y = position_hash(sample_index, Lx, Ly, s, seed=position_hash_seed)
    z = float(rng.uniform(0.0, s))
    vx = float(rng.normal(0.0, vel_xy_sigma))
    vy = float(rng.normal(0.0, vel_xy_sigma))
    vz = float(vel_z_init)
    freq = float(np.log(sample_rate_hz / 2.0))
    energy = float(abs(sample_value))
    slot = quanta.add(
        pos=(x, y, z), vel=(vx, vy, vz),
        freq=freq, polarity=1, energy=energy,
    )
    return 0 if slot < 0 else 1


def inject_raw_audio_chunk(
    quanta: Quanta,
    grid: Grid,
    chunk_samples: np.ndarray,
    base_sample_index: int,
    *,
    sample_rate_hz: int = 16000,
    rng: np.random.Generator | None = None,
    position_hash_seed: int = 0,
    vel_z_init: float = DEFAULT_VEL_Z_INIT,
    vel_xy_sigma: float = DEFAULT_VEL_XY_SIGMA,
) -> int:
    """Inject one quantum per sample in ``chunk_samples`` in order.

    Returns the number of quanta actually injected (= ``len(chunk_samples)``
    unless the buffer fills, at which point injection stops and the
    remaining samples are silently dropped — caller is responsible for
    sizing ``max_quanta`` to keep up with the per-tick injection rate).
    """
    if rng is None:
        rng = np.random.default_rng()
    injected = 0
    density_mode = _use_density_by_amplitude()
    for i, sample_value in enumerate(chunk_samples):
        added = inject_raw_audio_sample(
            quanta, grid, float(sample_value), base_sample_index + i,
            sample_rate_hz=sample_rate_hz, rng=rng,
            position_hash_seed=position_hash_seed,
            vel_z_init=vel_z_init, vel_xy_sigma=vel_xy_sigma,
        )
        injected += added
        if density_mode:
            # In density mode ``added == 0`` is legitimate (silent sample);
            # only break when the buffer is at hard capacity. Sub-burst
            # truncation (added < density_count) also signals buffer full.
            if quanta.n_alive() >= quanta.max_quanta:
                break
        else:
            # Legacy path: 0 means buffer full.
            if added == 0:
                break
    return injected
