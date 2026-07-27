"""Debug script for T2 Bénard convection test.

This script helps tune the ThermalConfig parameters to achieve
stable Bénard convection with wavelength ≈ 2 * cube_height.
"""
from __future__ import annotations
import numpy as np
from world.flux.quantum import Quanta
from world.flux.grid import Grid
from world.flux.audit import EnergyAuditor
from world.flux.boundary import inject_hot_floor
from world.flux.dynamics import tick
from world.flux.thermal import ThermalConfig


def run_benard_test(
    LX: int = 80,
    LY: int = 40,
    LZ: int = 10,
    buoyancy_g: float = 2.0,
    damping_mu: float = 0.5,
    T_hot_floor: float = 5.0,
    T_cold_ceiling: float = 0.0,
    n_per_tick: int = 20,
    dt: float = 0.1,
    n_ticks: int = 10000,
    seed: int = 42,
    verbose: bool = True,
) -> dict:
    """Run a single Bénard test with given parameters.
    
    Returns a dict with:
        - wavelength: Detected wavelength from FFT.
        - expected: Expected wavelength (2 * LZ).
        - k_peak: FFT peak index.
        - profile_std: Standard deviation of horizontal T profile.
        - passed: Whether wavelength is within ±30% of expected.
    """
    rng_inject = np.random.default_rng(seed)
    q = Quanta(max_quanta=200_000)
    g = Grid(dims=(LX, LY, LZ), voxel_size=1.0, T_smoothing=0.1)
    audit = EnergyAuditor(quanta=q, tol=1e-9)
    audit.record_initial()

    tcfg = ThermalConfig(
        buoyancy_g=buoyancy_g,
        damping_mu=damping_mu,
        T_ref=0.0,
        T_hot_floor=T_hot_floor,
        T_cold_ceiling=T_cold_ceiling,
    )

    def injector(quanta, grid):
        count = inject_hot_floor(
            quanta, grid, n=n_per_tick, energy_per=1.0,
            freq_mean=200.0, vel_z_sigma=0.5, vel_xy_sigma=0.5,
            rng=rng_inject,
        )
        audit.record_injection(count * 1.0)
        return count * 1.0

    for t in range(n_ticks):
        exported = tick(
            q, g, dt=dt, injector=injector, thermal_cfg=tcfg,
        )
        audit.record_export(exported)
        audit.check()
        audit.step()

    # FFT of horizontal T profile at mid-height
    mid_z = LZ // 2
    profile = g.T[:, LY // 2, mid_z]   # 1D slice along x
    fft = np.abs(np.fft.rfft(profile - profile.mean()))
    
    if fft.sum() == 0:
        if verbose:
            print(f"FAIL: Flat horizontal T profile (std={profile.std():.6f})")
        return {
            "wavelength": None,
            "expected": 2.0 * LZ,
            "k_peak": None,
            "profile_std": float(profile.std()),
            "passed": False,
        }
    
    k_peak = int(np.argmax(fft))
    if k_peak == 0:
        if verbose:
            print(f"FAIL: FFT peak at DC (k=0), profile_std={profile.std():.6f}")
        return {
            "wavelength": None,
            "expected": 2.0 * LZ,
            "k_peak": 0,
            "profile_std": float(profile.std()),
            "passed": False,
        }
    
    wavelength = LX / k_peak
    expected = 2.0 * LZ
    tol = 0.30 * expected
    passed = abs(wavelength - expected) <= tol
    
    if verbose:
        print(f"LX={LX}, LY={LY}, LZ={LZ} | buoyancy_g={buoyancy_g}, damping_mu={damping_mu}, T_hot={T_hot_floor}")
        print(f"k_peak={k_peak}, wavelength={wavelength:.2f}, expected={expected:.2f} ± {tol:.2f}")
        print(f"profile_std={profile.std():.6f}, passed={passed}")
    
    return {
        "wavelength": wavelength,
        "expected": expected,
        "k_peak": k_peak,
        "profile_std": float(profile.std()),
        "passed": passed,
    }


if __name__ == "__main__":
    print("=" * 80)
    print("T2 Bénard Convection Debugging")
    print("=" * 80)
    
    # Test 1: Original parameters (failing)
    print("\n[Test 1] Original parameters (LX=80, LY=40, LZ=10, g=2.0, mu=0.5, T_hot=5.0)")
    run_benard_test()
    
    # Test 2: Increase buoyancy
    print("\n[Test 2] Increased buoyancy (g=5.0)")
    run_benard_test(buoyancy_g=5.0)
    
    # Test 3: Decrease damping
    print("\n[Test 3] Decreased damping (mu=0.1)")
    run_benard_test(damping_mu=0.1)
    
    # Test 4: Increase temperature gradient
    print("\n[Test 4] Increased T gradient (T_hot=10.0)")
    run_benard_test(T_hot_floor=10.0)
    
    # Test 5: Larger cube (longer wavelength)
    print("\n[Test 5] Larger cube (LX=160, LY=80, LZ=20)")
    run_benard_test(LX=160, LY=80, LZ=20, buoyancy_g=2.0, damping_mu=0.5, T_hot_floor=5.0)
    
    # Test 6: Combined optimizations
    print("\n[Test 6] Combined: Larger cube + higher buoyancy + lower damping")
    run_benard_test(LX=160, LY=80, LZ=20, buoyancy_g=5.0, damping_mu=0.1, T_hot_floor=10.0)
    
    # Test 7: Very high buoyancy, low damping
    print("\n[Test 7] Very high buoyancy (g=10.0), very low damping (mu=0.05)")
    run_benard_test(buoyancy_g=10.0, damping_mu=0.05, T_hot_floor=10.0)
    
    # Test 8: Different seed (check if seed=42 is just unlucky)
    print("\n[Test 8] Different seed (seed=123)")
    run_benard_test(seed=123)
    
    print("\n" + "=" * 80)
    print("Debugging complete. Check which configuration passes.")
    print("=" * 80)
