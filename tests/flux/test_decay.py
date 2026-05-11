"""T4 — Structures decay when flux stops.

Spec §7 T4: form structures via T3 (5000 ticks with injection),
then disable injection and run 5000 more ticks. Structure count at
end should be < 10% of peak count (during the injection phase).

This is the F1b acceptance test.
"""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.quantum import Quanta
from world.flux.grid import Grid
from world.flux.audit import EnergyAuditor
from world.flux.boundary import inject_hot_floor
from world.flux.dynamics import tick
from world.flux.structures import Nodes
from world.flux.bridges import Bridges
from world.flux.binding import BindingConfig
from world.flux.decay import DecayConfig
from world.flux.plasticity import PlasticityConfig


def test_T4_decay_without_flux():
    """T3 setup, then 5000 ticks without injection.

    Peak count = max(n_alive) over the injection phase.
    End count  = n_alive at the very end of the no-injection phase.
    Pass: end / peak < 0.10.
    """
    rng_inject = np.random.default_rng(42)
    rng_bind = np.random.default_rng(123)
    q = Quanta(max_quanta=50_000)
    n = Nodes(max_nodes=50_000)
    br = Bridges(max_bridges=500_000)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0, T_smoothing=0.1)
    audit = EnergyAuditor(quanta=q, nodes=n, bridges=br, tol=1e-9)
    audit.record_initial()

    cfg = BindingConfig(alpha=4.0, beta=4.0, T_crit=2.0, eta=0.1,
                        r=1.5, coherence_eps=1.0,
                        r_bridge=2.0, bridge_w0=1.0)
    decay_cfg = DecayConfig(gamma=500.0, T_decay_crit=0.035)
    pcfg = PlasticityConfig(gamma=0.1, lam=0.1, flux_min=1.0,
                             w_min=0.05, r_flux=0.75)

    QUANTA_PER_TICK = 5
    ENERGY_PER = 1.0
    DT = 0.1

    def injector(quanta, grid):
        count = inject_hot_floor(
            quanta, grid,
            n=QUANTA_PER_TICK, energy_per=ENERGY_PER,
            freq_mean=200.0, vel_z_mean=2.0,
            rng=rng_inject,
        )
        audit.record_injection(count * ENERGY_PER)
        return count * ENERGY_PER

    # Phase A: 5000 ticks WITH injection
    peak = 0
    for t in range(5000):
        exported, binding_heat, decay_heat = tick(
            q, g, dt=DT, injector=injector,
            nodes=n, binding_cfg=cfg, decay_cfg=decay_cfg,
            bridges=br, plasticity_cfg=pcfg,
            rng=rng_bind, tick_index=t,
        )
        audit.record_export(exported)
        audit.record_binding_heat(binding_heat)
        audit.record_decay_heat(decay_heat)
        audit.check()
        audit.step()
        peak = max(peak, int(n.n_alive()))

    assert peak > 0, "No structures formed in Phase A"

    # Phase B: 5000 ticks WITHOUT injection
    for t in range(5000, 10000):
        exported, binding_heat, decay_heat = tick(
            q, g, dt=DT, injector=None,
            nodes=n, binding_cfg=cfg, decay_cfg=decay_cfg,
            bridges=br, plasticity_cfg=pcfg,
            rng=rng_bind, tick_index=t,
        )
        audit.record_export(exported)
        audit.record_binding_heat(binding_heat)
        audit.record_decay_heat(decay_heat)
        audit.check()
        audit.step()

    end_count = int(n.n_alive())
    ratio = end_count / peak if peak > 0 else 0.0
    assert ratio < 0.10, (
        f"T4 decay ratio {ratio:.3f} not below 0.10. "
        f"peak={peak}, end={end_count}. Adjust PlasticityConfig in "
        f"docs/flux/phase-log.md."
    )
