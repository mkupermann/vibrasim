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


def position_hash_content_driven(
    sample_index: int, sample_value: float,
    Lx: int, Ly: int, voxel_size: float, *, seed: int = 0,
) -> tuple[float, float]:
    """Audio-content-dependent xy hash (G25).

    Same total range as :func:`position_hash`, same determinism:
    identical ``(sample_index, sample_value, seed)`` reproduce identical
    ``(x, y)``. Differs from :func:`position_hash` only in that
    ``sample_value`` enters the hash function, so two audio waveforms
    with matched RMS but different per-sample values produce different
    spatial distributions.

    Implementation: 64-bit SplitMix64 on a bit-mixed combination of
    ``sample_index`` and a quantised ``sample_value``. The quantisation
    is ``int16`` rounding of ``sample_value * 32767`` clipped to the
    int16 range, which keeps the hash stable under float-precision
    drift across seeds and OS replays.

    See docs/amendments/G25-content-driven-injection.md §1.1.
    """
    # Quantise sample_value to int16 to avoid float-precision instability.
    v = float(sample_value)
    if v > 1.0:
        v = 1.0
    elif v < -1.0:
        v = -1.0
    vq = int(round(v * 32767.0))  # in [-32767, 32767]
    # Map to unsigned 16-bit ([0, 65535]) for clean bit-mixing.
    vq_u16 = (vq + 32768) & 0xFFFF
    # Bit-mix sample_index (low 48 bits) with vq_u16 (16 bits) into a
    # single 64-bit input to splitmix. The index goes in the high bits
    # so consecutive sample_indices already differ before sample_value
    # is even considered; sample_value contributes to the low 16.
    si = int(sample_index) & 0xFFFFFFFFFFFF  # 48 low bits
    mixed = (si << 16) | vq_u16
    h = _splitmix64(mixed, seed=int(seed))
    hi = (h >> 32) & 0xFFFFFFFF
    lo = h & 0xFFFFFFFF
    x = (hi * _INV_UINT32_RANGE) * (Lx * voxel_size)
    y = (lo * _INV_UINT32_RANGE) * (Ly * voxel_size)
    return float(x), float(y)


DEFAULT_VEL_Z_INIT = 1.0
DEFAULT_VEL_XY_SIGMA = 0.1


def _use_content_driven_position() -> bool:
    """Read the EQMOD_USE_CONTENT_DRIVEN_POSITION env var at call time.

    Read at call time (not module load) so tests can toggle via
    monkeypatch.setenv within a single process.
    """
    return os.environ.get("EQMOD_USE_CONTENT_DRIVEN_POSITION", "0") == "1"


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
    Lx, Ly, _ = grid.dims
    s = grid.voxel_size
    if _use_content_driven_position():
        x, y = position_hash_content_driven(
            sample_index, sample_value, Lx, Ly, s,
            seed=position_hash_seed,
        )
    else:
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
    for i, sample_value in enumerate(chunk_samples):
        added = inject_raw_audio_sample(
            quanta, grid, float(sample_value), base_sample_index + i,
            sample_rate_hz=sample_rate_hz, rng=rng,
            position_hash_seed=position_hash_seed,
            vel_z_init=vel_z_init, vel_xy_sigma=vel_xy_sigma,
        )
        if added == 0:
            break  # buffer full
        injected += added
    return injected
