"""Activation Field — per-voxel scalar memory trace (spec §5.8).

Pre-registered by R-12 amendment 2026-05-17:
docs/superpowers/specs/2026-05-17-flux-spec-amendment-activation-field.md

The activation field A[x,y,z,t] is a slow per-voxel scalar that decays
exponentially with time constant 1/alpha and is driven by the summed
energy of alive quanta in that voxel. It is bookkeeping — energy
conservation (T1) is unaffected, the substrate's discrete quanta remain
primary.

Update rule (continuous-time ODE discretised, rate semantics so the
steady-state formula A_ss = beta * N / alpha holds for constant input N):

    A[t+1] = A[t] * (1 - alpha*dt) + beta * deposit_rate * dt

where deposit_rate = sum_alive_quanta_in_voxel(energy).

Coincidence read-out for bridge plasticity:

    coincidence(i, j) = sqrt(A_i * A_j) / (A_norm + epsilon)

A_norm is the cube-wide mean of A, recomputed once per second (rolling
stat — NOT a free parameter to tune).
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

from world.flux.quantum import Quanta
from world.flux.grid import Grid


@dataclass
class ActivationFieldConfig:
    """Tunable parameters of the activation field (spec §5.8).

    Defaults are pre-registered and locked for R-12.

    alpha: field decay rate (1/s). Default 1.0 → half-life ln(2)/alpha
        ≈ 0.69 s (phoneme-timescale).
    beta:  firing → field deposit gain. Default 1.0 — each unit of
        deposited energy contributes 1.0 to the field per unit time
        (rate semantics — see module docstring).
    A_init: initial field value at every voxel. Default 0.0.
    norm_update_period_s: how often to recompute A_norm in seconds.
        Default 1.0 (per spec).
    epsilon: numerical-stability floor for the coincidence denominator.
    """
    alpha: float = 1.0
    beta: float = 1.0
    A_init: float = 0.0
    norm_update_period_s: float = 1.0
    epsilon: float = 1e-12


class ActivationField:
    """Per-voxel activation field with rolling A_norm tracking.

    Wraps a numpy array shaped like grid.dims and a rolling normalization
    constant updated on a slow timescale. Energy is NOT tracked here —
    this is a read-only smoothing of the quanta state.
    """

    def __init__(self, grid: Grid, cfg: ActivationFieldConfig | None = None):
        self.cfg = cfg if cfg is not None else ActivationFieldConfig()
        self.dims = tuple(grid.dims)
        self.voxel_size = float(grid.voxel_size)
        self.A = np.full(self.dims, self.cfg.A_init, dtype=np.float64)
        # A_norm starts at 1.0 to give a well-defined coincidence before
        # the first norm-update tick (avoids divide-by-epsilon spikes).
        self.A_norm = 1.0
        self._sec_since_norm_update = 0.0

    def n_voxels(self) -> int:
        return int(np.prod(self.dims))

    def total(self) -> float:
        """Sum of A across the whole cube (diagnostic)."""
        return float(self.A.sum())

    def update(self, quanta: Quanta, dt: float) -> None:
        """Advance the field by one tick of duration dt seconds.

        Step 1: exponential decay  A *= (1 - alpha*dt)
        Step 2: deposit            A += beta * deposit_rate * dt
                                   where deposit_rate is summed alive
                                   quantum energy per voxel.
        Step 3: rolling A_norm     recomputed every norm_update_period_s.

        Quanta with polarity == -1 (R-1d-T3-bis ceiling-scaffold) are
        excluded for consistency with the thermal density calculation —
        their job is bridge-flux for ceiling self-bridges, not thermal /
        plasticity signal.
        """
        # Step 1: decay
        self.A *= (1.0 - self.cfg.alpha * dt)

        # Step 2: deposit
        deposit = _voxel_energy_sum(quanta, self.dims, self.voxel_size)
        if deposit is not None:
            self.A += self.cfg.beta * deposit * dt

        # Step 3: rolling A_norm (mean over the cube, refreshed slowly)
        self._sec_since_norm_update += dt
        if self._sec_since_norm_update >= self.cfg.norm_update_period_s:
            mean = float(self.A.mean())
            # Keep A_norm strictly positive; if the cube is silent the
            # epsilon term in `coincidence` does the work.
            self.A_norm = max(mean, 0.0)
            self._sec_since_norm_update = 0.0

    def coincidence(self, pos_i, pos_j) -> float:
        """sqrt(A[voxel_i] * A[voxel_j]) / (A_norm + epsilon).

        Bridges between voxels that are both currently active get a
        large factor; bridges between silent voxels get ~0.
        """
        ix, iy, iz = _pos_to_voxel(pos_i, self.dims, self.voxel_size)
        jx, jy, jz = _pos_to_voxel(pos_j, self.dims, self.voxel_size)
        a_i = float(self.A[ix, iy, iz])
        a_j = float(self.A[jx, jy, jz])
        if a_i < 0.0:
            a_i = 0.0
        if a_j < 0.0:
            a_j = 0.0
        return float(np.sqrt(a_i * a_j) / (self.A_norm + self.cfg.epsilon))

    def coincidence_for_bridges(self, src_pos: np.ndarray,
                                 dst_pos: np.ndarray) -> np.ndarray:
        """Vectorised coincidence for arrays of bridge endpoints.

        Parameters
        ----------
        src_pos : (B, 3) float array of source-node positions.
        dst_pos : (B, 3) float array of destination-node positions.

        Returns
        -------
        (B,) float array of coincidence values in [0, ~1] in practice.
        """
        if src_pos.shape != dst_pos.shape or src_pos.ndim != 2:
            raise ValueError(
                f"src_pos / dst_pos must be matching (B, 3) arrays; got "
                f"{src_pos.shape} and {dst_pos.shape}"
            )
        a_src = _sample_field_at_positions(self.A, src_pos,
                                            self.dims, self.voxel_size)
        a_dst = _sample_field_at_positions(self.A, dst_pos,
                                            self.dims, self.voxel_size)
        a_src = np.maximum(a_src, 0.0)
        a_dst = np.maximum(a_dst, 0.0)
        return np.sqrt(a_src * a_dst) / (self.A_norm + self.cfg.epsilon)


# --- module-level helpers ---------------------------------------------


def _pos_to_voxel(pos, dims, voxel_size):
    Lx, Ly, Lz = dims
    s = voxel_size
    x, y, z = float(pos[0]), float(pos[1]), float(pos[2])
    ix = int(np.clip(x / s, 0, Lx - 1))
    iy = int(np.clip(y / s, 0, Ly - 1))
    iz = int(np.clip(z / s, 0, Lz - 1))
    return ix, iy, iz


def _sample_field_at_positions(A: np.ndarray, pos: np.ndarray,
                                dims, voxel_size) -> np.ndarray:
    Lx, Ly, Lz = dims
    s = voxel_size
    ix = np.clip((pos[:, 0] / s).astype(int), 0, Lx - 1)
    iy = np.clip((pos[:, 1] / s).astype(int), 0, Ly - 1)
    iz = np.clip((pos[:, 2] / s).astype(int), 0, Lz - 1)
    return A[ix, iy, iz]


def _voxel_energy_sum(quanta: Quanta, dims, voxel_size) -> np.ndarray | None:
    """Sum alive-quantum energy into voxel bins. Polarity == -1 excluded."""
    if quanta.n_alive() == 0:
        return None
    s = voxel_size
    Lx, Ly, Lz = dims
    mask = quanta.alive & (quanta.polarity != -1)
    if not mask.any():
        return None
    pos = quanta.pos[mask]
    energy = quanta.energy[mask]
    ix = np.clip((pos[:, 0] / s).astype(int), 0, Lx - 1)
    iy = np.clip((pos[:, 1] / s).astype(int), 0, Ly - 1)
    iz = np.clip((pos[:, 2] / s).astype(int), 0, Lz - 1)
    out = np.zeros(dims, dtype=np.float64)
    np.add.at(out, (ix, iy, iz), energy)
    return out


# --- functional API (for callers that don't want the class) -----------


def update_field(A: np.ndarray, quanta: Quanta, grid: Grid,
                  cfg: ActivationFieldConfig, dt: float) -> np.ndarray:
    """Pure-functional version of `ActivationField.update`.

    Returns the new A array (in-place modification is fine — A is
    returned for fluent use).
    """
    A *= (1.0 - cfg.alpha * dt)
    deposit = _voxel_energy_sum(quanta, grid.dims, grid.voxel_size)
    if deposit is not None:
        A += cfg.beta * deposit * dt
    return A


def read_coincidence(A: np.ndarray, voxel_size: float,
                      pos_i, pos_j, A_norm: float,
                      epsilon: float = 1e-12) -> float:
    """Compute coincidence(i, j) = sqrt(A_i * A_j) / (A_norm + epsilon)."""
    dims = A.shape
    ix, iy, iz = _pos_to_voxel(pos_i, dims, voxel_size)
    jx, jy, jz = _pos_to_voxel(pos_j, dims, voxel_size)
    a_i = max(float(A[ix, iy, iz]), 0.0)
    a_j = max(float(A[jx, jy, jz]), 0.0)
    return float(np.sqrt(a_i * a_j) / (A_norm + epsilon))
