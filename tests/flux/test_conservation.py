"""T1 — Energy conservation under 1000 ticks of constant injection.

Spec §7 T1: |E_initial + E_injected - (E_free + E_exported)| <
  1e-9 * max(|E_injected|, 1.0)

This is the F0 acceptance test. When this passes, F0 is done.
"""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.quantum import Quanta
from world.flux.grid import Grid
from world.flux.audit import EnergyAuditor
from world.flux.boundary import inject_hot_floor
from world.flux.dynamics import tick


def test_T1_conservation_over_1000_ticks():
    """Run 1000 ticks of constant injection on a 10×10×10 cube.

    Each tick injects 5 quanta of energy 1.0 each at the hot floor.
    Absorbing cold ceiling + side walls take the rest.
    Conservation must hold within tolerance for every tick AND at end.
    """
    rng = np.random.default_rng(42)
    q = Quanta(max_quanta=20_000)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0, T_smoothing=0.1)
    audit = EnergyAuditor(quanta=q, tol=1e-9)
    audit.record_initial()

    QUANTA_PER_TICK = 5
    ENERGY_PER = 1.0
    N_TICKS = 1000
    DT = 0.1

    def injector(quanta, grid):
        injected_count = inject_hot_floor(
            quanta, grid,
            n=QUANTA_PER_TICK,
            energy_per=ENERGY_PER,
            freq_mean=200.0,
            vel_z_mean=2.0,
            rng=rng,
        )
        audit.record_injection(injected_count * ENERGY_PER)
        return injected_count * ENERGY_PER

    for _ in range(N_TICKS):
        exported = tick(q, g, dt=DT, injector=injector)
        audit.record_export(exported)
        audit.check()  # Per-tick assertion
        audit.step()

    # Final check (already covered by per-tick, but explicit here)
    audit.check()

    # Sanity: some energy was injected, some exported, some still in
    # the buffer (or all exported if cube is very leaky)
    E_in = q.total_energy()
    assert audit.E_injected_total > 0
    assert audit.E_injected_total <= N_TICKS * QUANTA_PER_TICK * ENERGY_PER
    assert E_in >= 0
    assert audit.E_exported_total >= 0
    # The accounting equation
    np.testing.assert_allclose(
        audit.E_initial + audit.E_injected_total,
        E_in + audit.E_exported_total,
        rtol=0, atol=1e-9 * max(audit.E_injected_total, 1.0),
    )


def test_T1_conservation_zero_injection_zero_export():
    """Empty cube + no injection → nothing changes."""
    q = Quanta(max_quanta=100)
    g = Grid(dims=(5, 5, 5))
    audit = EnergyAuditor(quanta=q, tol=1e-9)
    audit.record_initial()
    for _ in range(100):
        exported = tick(q, g, dt=0.1, injector=None)
        audit.record_export(exported)
        audit.check()
        audit.step()
    assert audit.E_injected_total == 0.0
    assert audit.E_exported_total == 0.0
    assert q.total_energy() == 0.0
