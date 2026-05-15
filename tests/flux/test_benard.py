"""T2 — Bénard convection acceptance test.

Spec §7 T2: hot floor T_hot, cold ceiling T_cold (no audio).
10000 ticks. At steady state, FFT of the temperature field along
the horizontal axis shows a peak at wavelength λ ≈ 2 * cube_height
within ±30%.

This is the F1c acceptance test. Binding / decay / plasticity all
disabled — pure thermal substrate validation.
"""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.quantum import Quanta
from world.flux.grid import Grid
from world.flux.audit import EnergyAuditor
from world.flux.boundary import inject_cold_ceiling, inject_hot_floor
from world.flux.dynamics import tick
from world.flux.thermal import ThermalConfig


def test_T2_benard_horizontal_wavelength():
    """T2 acceptance — R-1c-bis architecture: return-flow injector at the
    cold ceiling, pressure-gradient force disabled (pressure_coeff=0).
    The @pytest.mark.slow marker added on 2026-05-15 (R-1c pre-flight)
    is removed per R-1c-bis acceptance contract.
    """
    rng_inject = np.random.default_rng(42)
    LX, LY, LZ = 80, 40, 10
    q = Quanta(max_quanta=200_000)
    g = Grid(dims=(LX, LY, LZ), voxel_size=1.0, T_smoothing=0.1)
    audit = EnergyAuditor(quanta=q, tol=1e-9)
    audit.record_initial()

    tcfg = ThermalConfig(
        buoyancy_g=2.0, damping_mu=0.5, T_ref=0.0,
        T_hot_floor=5.0, T_cold_ceiling=0.0,
        pressure_coeff=0.0,        # R-1c-bis: pressure-gradient force OFF
    )

    N_PER_TICK = 20
    DT = 0.1
    N_TICKS = 10000

    def injector(quanta, grid):
        count_floor = inject_hot_floor(
            quanta, grid, n=N_PER_TICK, energy_per=1.0,
            freq_mean=200.0, vel_z_sigma=0.5, vel_xy_sigma=0.5,
            rng=rng_inject,
        )
        count_ceiling = inject_cold_ceiling(
            quanta, grid, n=N_PER_TICK, energy_per=1.0,
            freq_mean=200.0, vel_z_sigma=0.5, vel_xy_sigma=0.5,
            rng=rng_inject,
        )
        total = (count_floor + count_ceiling) * 1.0
        audit.record_injection(total)
        return total

    for t in range(N_TICKS):
        exported = tick(
            q, g, dt=DT, injector=injector, thermal_cfg=tcfg,
        )
        audit.record_export(exported)
        audit.check()
        audit.step()

    # FFT of horizontal T profile at mid-height
    mid_z = LZ // 2
    profile = g.T[:, LY // 2, mid_z]   # 1D slice along x
    fft = np.abs(np.fft.rfft(profile - profile.mean()))
    if fft.sum() == 0:
        pytest.fail("Flat horizontal T profile — no convection cells formed")
    k_peak = int(np.argmax(fft))
    if k_peak == 0:
        pytest.fail(f"FFT peak at DC (k=0) — no spatial modulation")
    wavelength = LX / k_peak
    expected = 2.0 * LZ
    tol = 0.30 * expected
    assert abs(wavelength - expected) <= tol, (
        f"T2 wavelength {wavelength:.2f} not within +/-30% of {expected:.2f}. "
        f"k_peak={k_peak}, profile.std={profile.std():.4f}. "
        f"Tune ThermalConfig or cube dims in docs/flux/phase-log.md."
    )
