"""BET-001 — Reaction-diffusion (Turing 1952) as learning substrate.

Gray-Scott activator-inhibitor PDE on a 3D voxel grid, with audio-amplitude
forcing localised at the hot floor. The substrate has no plasticity rule,
no learning rate, no weight updates — only PDE dynamics. The hypothesis is
that audio-content-dependent forcing at the boundary perturbs the
bifurcation onset of Turing-pattern formation, producing steady-state
patterns that differ measurably under English vs matched-RMS white noise.

Per LOGBOOK 2026-05-22 bet pre-registration, BET-001 is the first
iteration in the relaxed-constraint bet programme (existing technologies
permitted; LLMs/transformers/embeddings/BPE-tokenizers disallowed).
References verknüpft: Turing 1952, Murray Mathematical Biology vol. 2,
Cross & Hohenberg 1993, Kondo & Miura 2010.

PDE:
    ∂u/∂t = D_u ∇²u - u v² + F(1-u) + I(x,t)
    ∂v/∂t = D_v ∇²v + u v² - (F+k) v

where I(x,t) is the audio-amplitude forcing applied to the bottom face
(z=0 voxels). Initial conditions: u=1.0 everywhere, v=0.0 everywhere
except a small noise patch at the centre to break the trivial steady state.

Stability: forward Euler with dt = 0.5 (CFL-stable for these diffusion
constants on a unit-voxel grid).
"""
from __future__ import annotations

import numpy as np
from dataclasses import dataclass


@dataclass
class RDConfig:
    """Gray-Scott parameters + grid dimensions. All locked pre-data per BET-001."""
    grid_dims: tuple[int, int, int] = (30, 15, 8)  # x, y, z
    Du: float = 0.16
    Dv: float = 0.08
    F: float = 0.040
    k: float = 0.060
    dt: float = 0.5
    audio_gain: float = 0.5     # multiplier on amplitude → u-source at floor
    seed_patch_size: int = 4    # initial v-noise patch radius
    seed_patch_v: float = 0.5   # initial v amplitude inside patch


def initialise(cfg: RDConfig, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """u(0)=1.0 everywhere, v(0)=0 except a centred noise patch."""
    Lx, Ly, Lz = cfg.grid_dims
    u = np.ones((Lx, Ly, Lz), dtype=np.float64)
    v = np.zeros_like(u)
    cx, cy, cz = Lx // 2, Ly // 2, Lz // 2
    r = cfg.seed_patch_size
    x_slice = slice(max(0, cx - r), min(Lx, cx + r + 1))
    y_slice = slice(max(0, cy - r), min(Ly, cy + r + 1))
    z_slice = slice(max(0, cz - r), min(Lz, cz + r + 1))
    v[x_slice, y_slice, z_slice] = cfg.seed_patch_v * rng.random(
        v[x_slice, y_slice, z_slice].shape
    )
    u[x_slice, y_slice, z_slice] = 1.0 - v[x_slice, y_slice, z_slice]
    return u, v


def _laplacian_3d(f: np.ndarray) -> np.ndarray:
    """6-point stencil 3D Laplacian with zero-flux (Neumann) boundary."""
    L = np.zeros_like(f)
    L[1:-1, :, :] += f[2:, :, :] + f[:-2, :, :] - 2 * f[1:-1, :, :]
    L[0, :, :] += f[1, :, :] - f[0, :, :]
    L[-1, :, :] += f[-2, :, :] - f[-1, :, :]
    L[:, 1:-1, :] += f[:, 2:, :] + f[:, :-2, :] - 2 * f[:, 1:-1, :]
    L[:, 0, :] += f[:, 1, :] - f[:, 0, :]
    L[:, -1, :] += f[:, -2, :] - f[:, -1, :]
    L[:, :, 1:-1] += f[:, :, 2:] + f[:, :, :-2] - 2 * f[:, :, 1:-1]
    L[:, :, 0] += f[:, :, 1] - f[:, :, 0]
    L[:, :, -1] += f[:, :, -2] - f[:, :, -1]
    return L


def step(
    u: np.ndarray,
    v: np.ndarray,
    cfg: RDConfig,
    audio_amplitude_per_floor_voxel: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """One forward-Euler step. Audio forcing applied at z=0 floor if given.

    audio_amplitude_per_floor_voxel: shape (Lx, Ly) or None. Values are
    interpreted as `abs(sample_value)` and multiplied by cfg.audio_gain
    before being added as a source term to u at z=0.
    """
    Lu = _laplacian_3d(u)
    Lv = _laplacian_3d(v)
    uvv = u * v * v
    du = cfg.Du * Lu - uvv + cfg.F * (1.0 - u)
    dv = cfg.Dv * Lv + uvv - (cfg.F + cfg.k) * v
    if audio_amplitude_per_floor_voxel is not None:
        du[:, :, 0] += cfg.audio_gain * audio_amplitude_per_floor_voxel
    u_new = u + cfg.dt * du
    v_new = v + cfg.dt * dv
    np.clip(u_new, 0.0, 2.0, out=u_new)
    np.clip(v_new, 0.0, 2.0, out=v_new)
    return u_new, v_new


def run(
    cfg: RDConfig,
    n_ticks: int,
    audio_samples: np.ndarray | None,
    samples_per_tick: int = 16,
    seed: int = 4242,
) -> tuple[np.ndarray, np.ndarray]:
    """Run the substrate for n_ticks. audio_samples is a 1D array of raw audio.

    If audio_samples is None, runs without any forcing (negative control).
    Otherwise samples_per_tick samples are consumed per tick; their |x| is
    averaged across the floor xy plane (uniform broadcast — the per-sample
    spatial index is not used in this iteration, deliberately, to keep the
    forcing simple).
    """
    rng = np.random.default_rng(seed)
    u, v = initialise(cfg, rng)
    Lx, Ly, _ = cfg.grid_dims
    floor_uniform = np.ones((Lx, Ly), dtype=np.float64)
    for tick in range(n_ticks):
        forcing: np.ndarray | None
        if audio_samples is None:
            forcing = None
        else:
            i0 = tick * samples_per_tick
            i1 = i0 + samples_per_tick
            chunk = audio_samples[i0:i1]
            if chunk.size == 0:
                forcing = None
            else:
                amp = float(np.mean(np.abs(chunk)))
                forcing = floor_uniform * amp
        u, v = step(u, v, cfg, forcing)
    return u, v
