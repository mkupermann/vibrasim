"""T3 — Crystallization preferentially in cold (upper) zones.

Spec §7 T3: uniform-frequency vibration injection at hot floor;
cold ceiling. Run 5000 ticks. Verify
  count_structures(top_half) / count_structures(bottom_half) > 5.0.

This is the F1a acceptance test. When this passes, F1a is done.
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
from world.flux.binding import BindingConfig
from world.flux.decay import DecayConfig


def test_T3_crystallization_in_cold_half():
    """5000 ticks, uniform-frequency injection at hot floor, cold
    ceiling + walls. Nodes should accumulate in the top half (cold).

    F1a adds a minimal node-decay mechanism (spec §5.4 simplified) so
    that hot-zone bindings dissociate over time. Without decay, every
    floor-binding accumulates forever and the cold-zone ratio never
    exceeds 1.0. See docs/flux/phase-log.md for the calibration record.
    """
    rng_inject = np.random.default_rng(42)
    rng_bind = np.random.default_rng(123)
    q = Quanta(max_quanta=50_000)
    n = Nodes(max_nodes=50_000)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0, T_smoothing=0.1)
    audit = EnergyAuditor(quanta=q, nodes=n, tol=1e-9)
    audit.record_initial()

    cfg = BindingConfig(
        alpha=4.0, beta=4.0, T_crit=2.0,
        eta=0.1, r=1.5, coherence_eps=1.0,
    )
    decay_cfg = DecayConfig(gamma=500.0, T_decay_crit=0.035)

    QUANTA_PER_TICK = 5
    ENERGY_PER = 1.0
    N_TICKS = 5000
    DT = 0.1
    FREQ_MEAN = 200.0

    def injector(quanta, grid):
        count = inject_hot_floor(
            quanta, grid,
            n=QUANTA_PER_TICK,
            energy_per=ENERGY_PER,
            freq_mean=FREQ_MEAN,
            vel_z_mean=2.0,
            rng=rng_inject,
        )
        audit.record_injection(count * ENERGY_PER)
        return count * ENERGY_PER

    for t in range(N_TICKS):
        exported, binding_heat, decay_heat = tick(
            q, g, dt=DT, injector=injector,
            nodes=n, binding_cfg=cfg, decay_cfg=decay_cfg,
            rng=rng_bind, tick_index=t,
        )
        audit.record_export(exported)
        audit.record_binding_heat(binding_heat)
        audit.record_decay_heat(decay_heat)
        audit.check()
        audit.step()

    audit.check()  # Conservation must still hold

    # Spatial distribution of nodes
    alive_mask = n.alive
    assert alive_mask.sum() > 0, (
        "No nodes formed — binding never fired. Tune cfg or check "
        "injection / temperature plumbing."
    )

    node_z = n.pos[alive_mask, 2]
    Lz_half = g.dims[2] * g.voxel_size / 2.0  # 5.0 for 10×10×10
    n_top = int((node_z >= Lz_half).sum())
    n_bot = int((node_z < Lz_half).sum())

    # Pre-registered T3 threshold from spec §7
    if n_bot == 0:
        assert n_top > 0  # All in top half — trivially > 5x
    else:
        ratio = n_top / n_bot
        assert ratio > 5.0, (
            f"T3 ratio {ratio:.2f} below threshold 5.0. "
            f"top={n_top}, bot={n_bot}. Adjust BindingConfig in "
            f"docs/flux/phase-log.md."
        )
