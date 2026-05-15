"""R-1c — Bénard multi-seed robustness audit.

Pre-registered acceptance (locked in QUEUE.yaml R-1c at in_progress):

- test_T2_passes_on_at_least_8_of_10_seeds:
    Parametrise the existing T2 wavelength check across 10 deterministic seeds
    (7, 13, 21, 42, 100, 137, 256, 314, 500, 1000). Assert at least 8/10 pass
    the +/-30% tolerance on lambda = 2 * Lz = 20.

- test_T2_FFT_SNR_above_3:
    For the 8+ passing seeds (or all 10 if fewer pass — used for diagnostic
    when the first test NULLs), compute the FFT signal-to-noise ratio (peak
    amplitude / mean amplitude of non-peak bins) of the horizontal T-profile
    at mid-height. Assert mean SNR across the passing seeds >= 3.0.
    The original F1c run measured SNR ~1.5; the threshold is locked at 3.0
    (2x baseline) per the R-1 phase-log discussion.

- test_T2_negative_control_fails_all_10_seeds:
    Same setup but with buoyancy_g=0 (no thermal driver). Run all 10 seeds.
    Assert ALL 10 fail the wavelength check. This confirms the substrate is
    not producing horizontal structure from RNG / pressure-force noise alone.

The substrate configuration is the R-1 / R-1b locked envelope:
    cube_dims = (80, 40, 10)
    ThermalConfig(buoyancy_g=2.0, damping_mu=0.5, T_ref=0.0,
                  T_hot_floor=5.0, T_cold_ceiling=0.0, pressure_coeff=1.0)
    inject_hot_floor(n=20, energy=1.0, freq=200, vel_z_sigma=0.5,
                     vel_xy_sigma=0.5)
    dt=0.1, N_TICKS=10000

The configuration is identical across all 10 seeds — no per-seed tweaks.
Per the R-1b phase-log close entry, pressure_coeff = 1.0 is the value the
R-1b session locked. R-1c uses it as-is; that is a charter rule
(open calibration choices, "Same value used in R-1c and R-1d").

The full simulation per seed is expensive (~80 s wall-clock per seed on
the autopilot host). The three tests share a module-scoped cache so the
main and SNR tests reuse the same 10 trajectories; the negative-control
test runs its own 10 trajectories with buoyancy_g=0. Total wall-clock
on the order of ~25-30 minutes.
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


# ─── Locked configuration (R-1 / R-1b) ──────────────────────────────────
SEED_GRID: list[int] = [7, 13, 21, 42, 100, 137, 256, 314, 500, 1000]
LX, LY, LZ = 80, 40, 10
N_PER_TICK = 20
DT = 0.1
N_TICKS = 10000
EXPECTED_WAVELENGTH = 2.0 * LZ      # = 20.0
WAVELENGTH_TOL_FRAC = 0.30          # +/-30% per R-1 acceptance

# The R-1c session uses the pressure_coeff value the R-1b session locked
# (1.0). That is the default in ThermalConfig — we construct configs by
# value below and do NOT override pressure_coeff per seed.


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
        # pressure_coeff defaults to 1.0 (R-1b lock; same value for R-1c
        # and R-1d, no per-seed tweaks).
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

    # FFT of horizontal T profile at mid-height, same slice convention
    # as test_benard.py so the two tests are directly comparable.
    mid_z = LZ // 2
    profile = g.T[:, LY // 2, mid_z]
    profile_centered = profile - profile.mean()
    fft = np.abs(np.fft.rfft(profile_centered))

    if fft.sum() == 0:
        # Flat profile — record an unambiguous failure signature.
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
    passed = abs(wavelength - EXPECTED_WAVELENGTH) <= tol and k_peak != 0

    # SNR definition (matches R-1 phase-log language): peak amplitude
    # divided by the mean of the non-peak, non-DC bins. A bin is
    # "non-peak" if it is not k_peak; we also exclude k=0 (DC was
    # subtracted before FFT so its amplitude is ~0 by construction,
    # but be explicit). Falls back to 0.0 if the substrate failed to
    # produce any non-peak signal at all (n_bins <= 2).
    n_bins = fft.shape[0]
    if n_bins <= 2 or k_peak == 0:
        snr = 0.0
    else:
        mask = np.ones(n_bins, dtype=bool)
        mask[0] = False         # exclude DC
        mask[k_peak] = False    # exclude the peak
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
    """One-line-per-seed diagnostic table for failure messages."""
    lines = [
        f"  seed={r.seed:5d}  k_peak={r.k_peak:3d}  "
        f"lambda={r.wavelength if r.wavelength != float('inf') else float('inf'):7.2f}  "
        f"snr={r.fft_snr:5.2f}  std={r.profile_std:.4f}  "
        f"pass={r.passed_wavelength_check}"
        for r in runs
    ]
    return "\n".join(lines)


# ─── Pre-registered tests ───────────────────────────────────────────────


def test_T2_passes_on_at_least_8_of_10_seeds(
    thermal_on_runs: list[SeedRun],
) -> None:
    """At least 8 of the 10 seeds must satisfy the +/-30% wavelength
    tolerance with the R-1b architecture active.

    Pre-registered threshold (locked, not retunable): 8/10."""
    n_passed = sum(1 for r in thermal_on_runs if r.passed_wavelength_check)
    assert n_passed >= 8, (
        f"T2 multi-seed: only {n_passed}/10 seeds passed the wavelength "
        f"check (threshold: >=8). Locked configuration "
        f"(cube={LX}x{LY}x{LZ}, pressure_coeff=1.0, buoyancy_g=2.0). "
        f"Per-seed results:\n{_format_table(thermal_on_runs)}"
    )


def test_T2_FFT_SNR_above_3(
    thermal_on_runs: list[SeedRun],
) -> None:
    """Mean FFT SNR (peak / mean-of-non-peak-bins) across the passing
    seeds must be >= 3.0. The R-1 phase-log measured ~1.5; the contract
    requires the new architecture to at least double that.

    If fewer than 8 seeds passed (the 8/10 test NULLed), we compute the
    mean over whichever seeds DID pass — empty mean is treated as 0.0,
    which fails the threshold by construction. This keeps the test from
    silently passing when no seeds pass.
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
