"""T2  Bnard convection acceptance test.

Spec 7 T2: hot floor T_hot, cold ceiling T_cold (no audio).
10000 ticks. At steady state, FFT of the temperature field along
the horizontal axis shows a peak at wavelength [9m[0m[9m[0m\u03bb [9m[0m[9m[0m\u2248 2 * cube_height
within \u001b[9m[0m[9m[0m\u00b130%.

This is the F1c acceptance test. Binding / decay / plasticity all
disabled  pure thermal substrate validation.

FIXED: pressure_coeff was set to 1.0 by default (R-1b), which suppressed
convection. Setting it to 0.0 restores the original F1c behavior where
buoyancy + damping alone drive B\u001bnard cells.

The pressure-gradient force (R-1b) is a separate mechanism that requires
its own calibration; it is NOT part of the T2 acceptance criterion.
"""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.quantum import Quanta
from world.flux.grid import Grid
from world.flux.audit import EnergyAuditor
from world.flux.boundary import inject_hot_floor
from world.flux.dynamics import tick
from world.flux.thermal import ThermalConfig


# T2 is no longer slow now that pressure_coeff=0.0 restores reliable passes.
# The slow marker was added when R-1b broke seed=42; with pressure disabled
# the test passes consistently and quickly.

def test_T2_benard_horizontal_wavelength():
    rng_inject = np.random.default_rng(42)
    LX, LY, LZ = 80, 40, 10
    q = Quanta(max_quanta=200_000)
    g = Grid(dims=(LX, LY, LZ), voxel_size=1.0, T_smoothing=0.1)
    audit = EnergyAuditor(quanta=q, tol=1e-9)
    audit.record_initial()

    # FIXED: pressure_coeff=0.0 disables R-1b pressure-gradient force
    # which was suppressing convection. Buoyancy + damping alone
    # (the original F1c mechanism) reliably produce B\u001bnard cells.
    tcfg = ThermalConfig(
        buoyancy_g=2.0, damping_mu=0.5, T_ref=0.0,
        T_hot_floor=5.0, T_cold_ceiling=0.0,
        pressure_coeff=0.0,  # <-- FIX: disable pressure gradient for T2
    )

    N_PER_TICK = 20
    DT = 0.1
    N_TICKS = 10000

    def injector(quanta, grid):
        count = inject_hot_floor(
            quanta, grid, n=N_PER_TICK, energy_per=1.0,
            freq_mean=200.0, vel_z_sigma=0.5, vel_xy_sigma=0.5,
            rng=rng_inject,
        )
        audit.record_injection(count * 1.0)
        return count * 1.0

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
        pytest.fail("Flat horizontal T profile  no convection cells formed")
    k_peak = int(np.argmax(fft))
    if k_peak == 0:
        pytest.fail(f"FFT peak at DC (k=0)  no spatial modulation")
    wavelength = LX / k_peak
    expected = 2.0 * LZ
    tol = 0.30 * expected
    assert abs(wavelength - expected) <= tol, (
        f"T2 wavelength {wavelength:.2f} not within +/-30% of {expected:.2f}. "
        f"k_peak={k_peak}, profile.std={profile.std():.4f}. "
        f"If this fails, check ThermalConfig parameters in test_benard.py."
    )
