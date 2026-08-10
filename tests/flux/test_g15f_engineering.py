"""G15F engineering done-criteria (docs/amendments/g15f_dream_consolidation.md §2).

E1 — pattern tagging: nodes inherit Nodes.active_pattern_id at allocation;
     explicit pattern_id overrides; recycled slots don't leak stale pids.
E2 — energy-conserving dreaming: blend is a conservative transfer; replay
     seed energy is reported for booking; the F0 auditor holds at 1e-9
     over >=60 simulated seconds with dream mode on and blends occurring.

These are engineering gates, NOT the G15F-1 experiment. No consolidation
claim is tested here.
"""
from __future__ import annotations
import numpy as np

from world.flux.quantum import Quanta
from world.flux.grid import Grid
from world.flux.structures import Nodes
from world.flux.bridges import Bridges
from world.flux.audit import EnergyAuditor
from world.flux.binding import BindingConfig
from world.flux.boundary import inject_hot_floor
from world.flux.dynamics import tick
from world.flux.dream import DreamConfig, apply_dream


# ---------- E1: pattern tagging ----------

def test_E1_add_inherits_active_pattern_id():
    nodes = Nodes(8)
    nodes.active_pattern_id = 3
    s = nodes.add(pos=(1, 1, 1), energy=5.0, freq=100.0, born_tick=0)
    assert nodes.pattern_id[s] == 3

    nodes.active_pattern_id = 0
    s2 = nodes.add(pos=(2, 2, 2), energy=5.0, freq=100.0, born_tick=0)
    assert nodes.pattern_id[s2] == 0


def test_E1_explicit_pattern_id_overrides_active():
    nodes = Nodes(8)
    nodes.active_pattern_id = 3
    s = nodes.add(pos=(1, 1, 1), energy=5.0, freq=100.0, born_tick=0,
                  pattern_id=7)
    assert nodes.pattern_id[s] == 7
    # Explicit 0 must also override a non-zero training signal.
    s2 = nodes.add(pos=(2, 2, 2), energy=5.0, freq=100.0, born_tick=0,
                   pattern_id=0)
    assert nodes.pattern_id[s2] == 0


def test_E1_recycled_slot_does_not_leak_stale_pid():
    nodes = Nodes(4)
    nodes.active_pattern_id = 9
    s = nodes.add(pos=(1, 1, 1), energy=5.0, freq=100.0, born_tick=0)
    assert nodes.pattern_id[s] == 9
    nodes.remove(s)
    assert nodes.pattern_id[s] == 0  # cleared on remove
    nodes.active_pattern_id = 0
    s2 = nodes.add(pos=(2, 2, 2), energy=5.0, freq=100.0, born_tick=1)
    assert s2 == s  # slot actually recycled
    assert nodes.pattern_id[s2] == 0


# ---------- E2: energy-conserving dreaming ----------

def _two_engram_nodes(n_per_pattern: int = 3, energy: float = 10.0) -> Nodes:
    nodes = Nodes(64)
    for k in range(n_per_pattern):
        nodes.add(pos=(5.0 + k, 5.0, 5.0), energy=energy, freq=800.0,
                  born_tick=0, pattern_id=1)
        nodes.add(pos=(15.0 + k, 5.0, 5.0), energy=energy, freq=3200.0,
                  born_tick=0, pattern_id=2)
    return nodes


def test_E2_seed_energy_is_reported():
    nodes = _two_engram_nodes()
    grid = Grid((20, 10, 10), 1.0)
    quanta = Quanta(16)
    cfg = DreamConfig(dream_mode_enabled=True,
                      dream_replay_seeds_per_tick=4,
                      dream_replay_seed_energy=2.5)
    out = apply_dream(quanta, nodes, grid, dt=1 / 60, cfg=cfg,
                      tick_index=0, rng=np.random.default_rng(1))
    assert out["replay_seeds_fired"] == 4
    assert out["energy_injected"] == 4 * 2.5


def test_E2_blend_is_conservative_transfer():
    nodes = _two_engram_nodes()
    grid = Grid((20, 10, 10), 1.0)
    quanta = Quanta(16)
    cfg = DreamConfig(dream_mode_enabled=True,
                      dream_replay_seeds_per_tick=6,  # seed all engram nodes
                      dream_replay_seed_energy=1.0)
    e_before = nodes.total_energy()
    out = apply_dream(quanta, nodes, grid, dt=1 / 60, cfg=cfg,
                      tick_index=0, rng=np.random.default_rng(1))
    assert out["blend_events"] >= 1, "test setup must force a blend"
    e_after = nodes.total_energy()
    # Books exactly: total change == reported external injection; the
    # blend itself moved energy but created none.
    assert abs((e_after - e_before) - out["energy_injected"]) < 1e-9
    # The blend node exists with a fresh pid and positive energy.
    fresh = nodes.alive & (nodes.pattern_id > 2)
    assert fresh.any()
    assert (nodes.energy[fresh] > 0).all()


def test_E2_auditor_green_60s_with_dream_and_blends():
    """E2 done-criterion: F0 ledger holds at 1e-9 over >=60 simulated s
    with dream mode on and >=1 blend event occurring. Harness wiring is
    identical to the G15F-1 experiment: dream applied MANUALLY (not via
    tick's dream_cfg), its injection booked from the diagnostics dict."""
    rng = np.random.default_rng(42)
    quanta = Quanta(5_000)
    grid = Grid((10, 10, 10), 1.0)
    nodes = _two_engram_nodes(n_per_pattern=4, energy=20.0)
    bridges = Bridges(1024)
    audit = EnergyAuditor(quanta=quanta, tol=1e-9, nodes=nodes)
    audit.record_initial()

    binding_cfg = BindingConfig()
    dream_cfg = DreamConfig(dream_mode_enabled=True,
                            dream_replay_seeds_per_tick=4,
                            dream_replay_seed_energy=1.0)

    def injector(q, g):
        # Light injection: the criterion needs the ledger under dream +
        # binding + export traffic, not a high-density regime.
        n_inj = inject_hot_floor(q, g, n=1, energy_per=2.0,
                                 freq_mean=1000.0, rng=rng)
        e = n_inj * 2.0
        audit.record_injection(e)
        return e

    dt = 1.0 / 60.0
    blends = 0
    for k in range(60 * 60):  # 60 simulated seconds
        out = apply_dream(quanta, nodes, grid, dt=dt, cfg=dream_cfg,
                          tick_index=k, rng=np.random.default_rng(42 + k))
        audit.record_injection(out["energy_injected"])
        blends += out["blend_events"]

        result = tick(quanta, grid, dt, injector=injector, nodes=nodes,
                      binding_cfg=binding_cfg, bridges=bridges,
                      rng=np.random.default_rng(42 + k), tick_index=k)
        e_exported, binding_heat, decay_heat = result
        audit.record_export(e_exported)
        audit.record_binding_heat(binding_heat)
        audit.record_decay_heat(decay_heat)
        audit.step()
        if k % 60 == 59:
            audit.check()  # raises ConservationViolation on imbalance

    audit.check()
    assert blends >= 1, "E2 criterion requires >=1 blend during the window"
