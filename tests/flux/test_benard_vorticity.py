"""R-1c-quad — Bénard falsifier swap: FFT-of-T-profile → vorticity-field FFT.

Pre-registered acceptance (locked in QUEUE.yaml R-1c-quad at in_progress):

- test_T2_vorticity_passes_on_at_least_8_of_10_seeds:
    Parametrise across the same 10 seeds the prior iterations used
    (7, 13, 21, 42, 100, 137, 256, 314, 500, 1000). For each seed,
    run the F1c+R-1b substrate for 10000 ticks, then compute
        v_field[i,j,k] = mass-weighted mean velocity of alive quanta
                         in voxel (i,j,k); empty voxels → 0.
        ω_y = ∂v_z/∂x - ∂v_x/∂z       (curl about the y-axis)
    Take the ω_y(x) profile at mid-height z=LZ//2, averaged over y,
    centre it, FFT along x, find the peak. PASS iff the peak's
    wavelength is within ±20% of the Bénard prediction λ = 2·LZ = 20
    (LX=80 ⇒ k_peak ∈ {4, 5}; 80/4=20, 80/5=16). ≥8/10 must pass.

- test_T2_vorticity_negative_control_fails_all_10_seeds:
    Same 10 seeds with buoyancy_g=0 (no thermal driver). ALL 10
    seeds must FAIL the wavelength check.

This file is the new T2 falsifier. test_benard.py and
test_benard_robustness.py (FFT-of-T) are retained for historical
regression; this file is the locked acceptance for R-1c-quad.

The substrate setup is identical to R-1c-bis / R-1c-tris's F1c+R-1b
envelope. No thermal-parameter changes, no substrate modification —
only the measurement metric is swapped from FFT(T) to FFT(ω_y).
"""
from __future__ import annotations
from dataclasses import dataclass

import numpy as np
import pytest

from world.flux.audit import EnergyAuditor
from world.flux.boundary import inject_hot_floor
from world.flux.dynamics import tick
from world.flux.grid import Grid
from world.flux.quantum import Quanta
from world.flux.thermal import ThermalConfig


# ─── Locked configuration ─────────────────────────────────────────────
SEED_GRID: list[int] = [7, 13, 21, 42, 100, 137, 256, 314, 500, 1000]
LX, LY, LZ = 80, 40, 10
N_PER_TICK = 20
DT = 0.1
N_TICKS = 10000
EXPECTED_WAVELENGTH = 2.0 * LZ          # = 20.0
WAVELENGTH_TOL_FRAC = 0.20              # ±20% per brief; tighter than T2's 30%
# Pass condition derived from the wavelength tolerance: with LX=80, the
# permissible λ range is [16, 24], which the discrete FFT bins satisfy at
# k_peak ∈ {4, 5}. (80/4=20 and 80/5=16 sit inside the window; 80/3≈26.7
# and 80/6≈13.3 sit outside.)
PASS_K = {4, 5}


@dataclass
class SeedRun:
    seed: int
    buoyancy_g: float
    n_alive_final: int
    k_peak: int
    wavelength: float
    fft_snr: float
    omega_y_std: float
    passed: bool


def _v_field(quanta: Quanta, grid: Grid) -> np.ndarray:
    """Voxel-mean velocity field (Lx, Ly, Lz, 3) of alive quanta.

    All quanta in the substrate carry the same unit energy, so the
    "weighted by quanta count" mean reduces to the arithmetic mean.
    Empty voxels stay at 0 — that is the noise floor for the FFT.
    """
    Lx, Ly, Lz = grid.dims
    s = grid.voxel_size
    vsum = np.zeros((Lx, Ly, Lz, 3), dtype=np.float64)
    count = np.zeros((Lx, Ly, Lz), dtype=np.float64)
    if quanta.n_alive() == 0:
        return vsum
    alive = quanta.alive
    pos = quanta.pos[alive]
    vel = quanta.vel[alive]
    ix = np.clip((pos[:, 0] / s).astype(int), 0, Lx - 1)
    iy = np.clip((pos[:, 1] / s).astype(int), 0, Ly - 1)
    iz = np.clip((pos[:, 2] / s).astype(int), 0, Lz - 1)
    np.add.at(count, (ix, iy, iz), 1.0)
    for c in range(3):
        np.add.at(vsum[..., c], (ix, iy, iz), vel[:, c])
    denom = np.maximum(count[..., None], 1.0)
    return np.where(count[..., None] > 0, vsum / denom, 0.0)


def _omega_y_field(v_field: np.ndarray, voxel_size: float) -> np.ndarray:
    """ω_y = ∂v_z/∂x - ∂v_x/∂z (curl component about y-axis).

    Uses np.gradient (central differences in the interior, one-sided
    at the boundary) — matches the pattern already used in
    world.flux.pressure for the pressure-gradient force.
    """
    vx = v_field[..., 0]
    vz = v_field[..., 2]
    dvz_dx = np.gradient(vz, voxel_size, axis=0)
    dvx_dz = np.gradient(vx, voxel_size, axis=2)
    return dvz_dx - dvx_dz


def _vorticity_metric(omega_y: np.ndarray) -> tuple[int, float, float, float]:
    """At mid-height z=LZ//2, mean ω_y over y, FFT along x.

    Returns (k_peak, wavelength, snr, profile_std). k_peak=0 maps to
    wavelength=inf. SNR = peak amplitude / mean of non-peak non-DC
    bins. profile_std lets us tell a flat field from a noisy one.
    """
    Lx, _Ly, Lz = omega_y.shape
    mid_z = Lz // 2
    profile = omega_y[:, :, mid_z].mean(axis=1)
    profile_centered = profile - profile.mean()
    profile_std = float(profile.std())
    fft = np.abs(np.fft.rfft(profile_centered))
    if fft.sum() == 0:
        return 0, float("inf"), 0.0, profile_std
    k_peak = int(np.argmax(fft))
    wavelength = float("inf") if k_peak == 0 else Lx / k_peak
    n_bins = fft.shape[0]
    if n_bins <= 2 or k_peak == 0:
        snr = 0.0
    else:
        mask = np.ones(n_bins, dtype=bool)
        mask[0] = False
        mask[k_peak] = False
        denom = fft[mask].mean()
        snr = float(fft[k_peak] / denom) if denom > 0 else 0.0
    return k_peak, float(wavelength), snr, profile_std


def _run_one_seed(seed: int, *, buoyancy_g: float) -> SeedRun:
    """One full F1c simulation, returning the vorticity-metric snapshot.

    Parameters identical across all 10 seeds and across the positive /
    negative-control runs — only the RNG seed and `buoyancy_g` change.
    """
    rng_inject = np.random.default_rng(seed)
    q = Quanta(max_quanta=200_000)
    g = Grid(dims=(LX, LY, LZ), voxel_size=1.0, T_smoothing=0.1)
    audit = EnergyAuditor(quanta=q, tol=1e-9)
    audit.record_initial()

    tcfg = ThermalConfig(
        buoyancy_g=buoyancy_g,
        damping_mu=0.5,
        T_ref=0.0,
        T_hot_floor=5.0,
        T_cold_ceiling=0.0,
        pressure_coeff=1.0,
    )

    def injector(quanta, grid):
        count = inject_hot_floor(
            quanta, grid, n=N_PER_TICK, energy_per=1.0,
            freq_mean=200.0, vel_z_sigma=0.5, vel_xy_sigma=0.5,
            rng=rng_inject,
        )
        audit.record_injection(count * 1.0)
        return count * 1.0

    for _ in range(N_TICKS):
        exported = tick(q, g, dt=DT, injector=injector, thermal_cfg=tcfg)
        audit.record_export(exported)
        audit.check()
        audit.step()

    v = _v_field(q, g)
    omega_y = _omega_y_field(v, g.voxel_size)
    k_peak, wavelength, snr, profile_std = _vorticity_metric(omega_y)
    passed = k_peak in PASS_K
    return SeedRun(
        seed=seed,
        buoyancy_g=buoyancy_g,
        n_alive_final=q.n_alive(),
        k_peak=k_peak,
        wavelength=wavelength,
        fft_snr=snr,
        omega_y_std=profile_std,
        passed=passed,
    )


@pytest.fixture(scope="module")
def thermal_on_runs() -> list[SeedRun]:
    """Run the 10-seed grid with buoyancy_g=2.0 once per session."""
    return [_run_one_seed(s, buoyancy_g=2.0) for s in SEED_GRID]


@pytest.fixture(scope="module")
def thermal_off_runs() -> list[SeedRun]:
    """Run the 10-seed grid with buoyancy_g=0.0 once per session."""
    return [_run_one_seed(s, buoyancy_g=0.0) for s in SEED_GRID]


def _format_table(runs: list[SeedRun]) -> str:
    header = (
        "  seed  n_alive  k_peak  wavelength    SNR    omega_std  passed"
    )
    lines = [header]
    for r in runs:
        wl = f"{r.wavelength:9.2f}" if np.isfinite(r.wavelength) else "    inf"
        lines.append(
            f"  {r.seed:4d}  {r.n_alive_final:7d}  {r.k_peak:6d}  "
            f"{wl}  {r.fft_snr:6.2f}  {r.omega_y_std:9.4f}  "
            f"{'PASS' if r.passed else 'fail'}"
        )
    return "\n".join(lines)


def test_T2_vorticity_passes_on_at_least_8_of_10_seeds(thermal_on_runs):
    """≥8/10 seeds must produce a vorticity-FFT peak at k_peak ∈ {4, 5}
    (wavelength within ±20% of λ = 2·LZ = 20)."""
    n_pass = sum(1 for r in thermal_on_runs if r.passed)
    assert n_pass >= 8, (
        f"R-1c-quad: vorticity-FFT metric passed only {n_pass}/10 seeds; "
        f"pre-registered threshold ≥8/10.\n"
        + _format_table(thermal_on_runs)
    )


def test_T2_vorticity_negative_control_fails_all_10_seeds(thermal_off_runs):
    """With buoyancy_g=0, ALL 10 seeds must FAIL the wavelength check.
    Any pass here means the metric is firing on RNG/noise, not on
    convection."""
    n_pass = sum(1 for r in thermal_off_runs if r.passed)
    assert n_pass == 0, (
        f"R-1c-quad: negative control passed {n_pass}/10 seeds; "
        f"expected 0/10. Metric is firing on noise, not on convection.\n"
        + _format_table(thermal_off_runs)
    )
