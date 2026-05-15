"""R-1c-tris — Bénard multi-seed robustness audit (anti-noise iteration).

Pre-registered acceptance (locked in QUEUE.yaml R-1c-tris at in_progress):

- test_T2_passes_on_at_least_8_of_10_seeds:
    Parametrise the T2 wavelength check across 10 deterministic seeds
    (7, 13, 21, 42, 100, 137, 256, 314, 500, 1000). Assert at least 8/10
    pass the +/-30% tolerance on lambda = 2 * Lz = 20.

- test_T2_FFT_SNR_above_3:
    Mean FFT signal-to-noise ratio (peak amplitude / mean amplitude of
    non-peak non-DC bins) of the horizontal T-profile across passing
    seeds must be >= 3.0. Original F1c run measured ~1.5.

- test_T2_negative_control_fails_all_10_seeds:
    Same setup but with buoyancy_g=0 (no thermal driver). All 10 seeds
    must FAIL the wavelength check. Discriminates between a real
    convection-cell signal and RNG / numerical-noise artifacts.

Substrate configuration (locked by this session for R-1c-tris):
    cube_dims = (80, 40, 10)
    ThermalConfig(buoyancy_g=2.0, damping_mu=0.5, T_ref=0.0,
                  T_hot_floor=5.0, T_cold_ceiling=0.0,
                  pressure_coeff=1.0, T_spatial_sigma=1.0)
    inject_hot_floor(n=20, energy=1.0, freq=200, vel_z_sigma=0.5,
                     vel_xy_sigma=0.5)
    dt=0.1, N_TICKS=10000

Configuration is identical across all 10 seeds — no per-seed tweaks.

R-1c-tris diagnostic (phase-log 2026-05-15) showed the FFT-of-T-profile
metric in R-1c was dominated by per-voxel Poisson density noise. Two
fixes are applied here:

  1. Gaussian spatial smoothing of grid.T (sigma=1.0) inside
     update_temperature — suppresses high-spatial-frequency Poisson
     noise; preserves the long-wavelength thermal gradient that drives
     Bénard convection.
  2. Y-averaging of the horizontal T profile before FFT (mean across
     all 40 y-rows at mid_z, instead of a single row) — reduces residual
     Poisson noise by ~sqrt(40) ~ 6x and increases coherence of the
     true horizontal mode across seeds.

The simulation per seed runs in ~2.5 minutes. The two thermal-ON
positive tests share a module-scoped fixture (one 10-seed pass); the
negative control runs its own 10 seeds. Total wall-clock ~52 minutes
on the autopilot host.
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


# ─── Locked configuration (R-1c-tris) ─────────────────────────────────
SEED_GRID: list[int] = [7, 13, 21, 42, 100, 137, 256, 314, 500, 1000]
LX, LY, LZ = 80, 40, 10
N_PER_TICK = 20
DT = 0.1
N_TICKS = 10000
EXPECTED_WAVELENGTH = 2.0 * LZ      # = 20.0
WAVELENGTH_TOL_FRAC = 0.30          # +/-30% per spec §7 T2

# R-1c-tris substrate change: spatial smoothing of grid.T to suppress
# per-voxel Poisson density-shot-noise.  See module docstring.
T_SPATIAL_SIGMA = 1.0


@dataclass
class SeedRun:
    seed: int
    wavelength: float
    k_peak: int
    profile_std: float
    fft_snr: float
    passed_wavelength_check: bool


def _run_one_seed(seed: int, *, buoyancy_g: float) -> SeedRun:
    """Run one full T2 simulation and extract (wavelength, k_peak, SNR).

    Parameters
    ----------
    seed:
        RNG seed for the injector.
    buoyancy_g:
        Vertical buoyancy strength. 2.0 = production driver, 0.0 = the
        negative control (no thermal driver — substrate must not produce
        horizontal structure spontaneously).
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
        T_spatial_sigma=T_SPATIAL_SIGMA,
    )

    def injector(quanta, grid):
        count = inject_hot_floor(
            quanta, grid, n=N_PER_TICK, energy_per=1.0,
            freq_mean=200.0, vel_z_sigma=0.5, vel_xy_sigma=0.5,
            rng=rng_inject,
        )
        audit.record_injection(count * 1.0)
        return count * 1.0

    for _t in range(N_TICKS):
        exported = tick(
            q, g, dt=DT, injector=injector, thermal_cfg=tcfg,
        )
        audit.record_export(exported)
        audit.check()
        audit.step()

    # FFT of horizontal T profile at mid-height, y-averaged across all
    # 40 y-rows for noise reduction (R-1c-tris anti-Poisson lever).
    mid_z = LZ // 2
    profile = g.T[:, :, mid_z].mean(axis=1)
    profile_centered = profile - profile.mean()
    fft = np.abs(np.fft.rfft(profile_centered))

    if fft.sum() == 0:
        return SeedRun(
            seed=seed,
            wavelength=float("inf"),
            k_peak=0,
            profile_std=float(profile.std()),
            fft_snr=0.0,
            passed_wavelength_check=False,
        )

    k_peak = int(np.argmax(fft))
    if k_peak == 0:
        wavelength = float("inf")
    else:
        wavelength = LX / k_peak

    tol = WAVELENGTH_TOL_FRAC * EXPECTED_WAVELENGTH
    passed = (
        k_peak != 0
        and abs(wavelength - EXPECTED_WAVELENGTH) <= tol
    )

    n_bins = fft.shape[0]
    if n_bins <= 2 or k_peak == 0:
        snr = 0.0
    else:
        mask = np.ones(n_bins, dtype=bool)
        mask[0] = False
        mask[k_peak] = False
        denom = fft[mask].mean()
        snr = float(fft[k_peak] / denom) if denom > 0 else 0.0

    return SeedRun(
        seed=seed,
        wavelength=float(wavelength),
        k_peak=k_peak,
        profile_std=float(profile.std()),
        fft_snr=snr,
        passed_wavelength_check=bool(passed),
    )


@pytest.fixture(scope="module")
def thermal_on_runs() -> list[SeedRun]:
    """Run the 10-seed grid with buoyancy_g=2.0 (production driver).

    Module-scoped: the two passing-side tests (wavelength count + SNR)
    share this cache so the simulation only runs once per session.
    """
    return [_run_one_seed(s, buoyancy_g=2.0) for s in SEED_GRID]


@pytest.fixture(scope="module")
def thermal_off_runs() -> list[SeedRun]:
    """Run the 10-seed grid with buoyancy_g=0.0 (negative control)."""
    return [_run_one_seed(s, buoyancy_g=0.0) for s in SEED_GRID]


def _format_table(runs: list[SeedRun]) -> str:
    lines = [
        f"  seed={r.seed:5d}  k_peak={r.k_peak:3d}  "
        f"lambda={r.wavelength if r.wavelength != float('inf') else float('inf'):7.2f}  "
        f"snr={r.fft_snr:5.2f}  std={r.profile_std:.4f}  "
        f"pass={r.passed_wavelength_check}"
        for r in runs
    ]
    return "\n".join(lines)


# ─── Pre-registered tests ─────────────────────────────────────────────


def test_T2_passes_on_at_least_8_of_10_seeds(
    thermal_on_runs: list[SeedRun],
) -> None:
    """At least 8 of the 10 seeds must satisfy the +/-30% wavelength
    tolerance with the R-1c-tris architecture active.

    Pre-registered threshold (locked, not retunable): 8/10."""
    n_passed = sum(1 for r in thermal_on_runs if r.passed_wavelength_check)
    assert n_passed >= 8, (
        f"T2 multi-seed: only {n_passed}/10 seeds passed the wavelength "
        f"check (threshold: >=8). Locked configuration "
        f"(cube={LX}x{LY}x{LZ}, pressure_coeff=1.0, buoyancy_g=2.0, "
        f"T_spatial_sigma={T_SPATIAL_SIGMA}, n_inject={N_PER_TICK}). "
        f"Per-seed results:\n{_format_table(thermal_on_runs)}"
    )


def test_T2_FFT_SNR_above_3(
    thermal_on_runs: list[SeedRun],
) -> None:
    """Mean FFT SNR (peak / mean-of-non-peak-bins) across the passing
    seeds must be >= 3.0. Original F1c measurement was ~1.5; contract
    requires the new architecture to at least double that.

    If fewer than 8 seeds pass (the 8/10 test NULLed), the mean is
    computed over whichever seeds did pass — empty mean is treated as
    0.0, which fails the threshold. Prevents silent-pass on no-pass.
    """
    passing = [r for r in thermal_on_runs if r.passed_wavelength_check]
    if not passing:
        pytest.fail(
            "No seeds passed the wavelength check — mean SNR undefined. "
            f"Per-seed table:\n{_format_table(thermal_on_runs)}"
        )
    mean_snr = float(np.mean([r.fft_snr for r in passing]))
    assert mean_snr >= 3.0, (
        f"Mean FFT SNR across {len(passing)} passing seeds = "
        f"{mean_snr:.2f} (threshold: >=3.0). "
        f"Per-seed SNRs: {[round(r.fft_snr, 2) for r in passing]}. "
        f"Full table:\n{_format_table(thermal_on_runs)}"
    )


def test_T2_negative_control_fails_all_10_seeds(
    thermal_off_runs: list[SeedRun],
) -> None:
    """With buoyancy_g=0, the substrate has no thermal driver — only the
    pressure-gradient force, isotropic damping, and the cold-ceiling
    boundary. Pre-registered: ALL 10 seeds must FAIL the wavelength
    check. A single spurious pass means the substrate is producing
    horizontal structure from RNG / numerical-noise alone, which would
    invalidate the positive test as a state detector."""
    spurious_passes = [r for r in thermal_off_runs if r.passed_wavelength_check]
    n_spurious = len(spurious_passes)
    assert n_spurious == 0, (
        f"Negative control: {n_spurious}/10 seeds spuriously passed the "
        f"wavelength check with buoyancy_g=0 (threshold: 0). "
        f"Spurious seeds: {[r.seed for r in spurious_passes]}. "
        f"Per-seed table:\n{_format_table(thermal_off_runs)}"
    )
