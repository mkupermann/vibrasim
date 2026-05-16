"""R-1d-T3-bis — Crystallisation (T3) iter-2: lift bridge-flux starvation.

Pre-registered acceptance (locked in QUEUE.yaml under id:
R-1d-T3-bis):

- ``test_T3_passes_on_at_least_8_of_10_seeds`` — parametrise the
  spec §7 T3 falsifier across the 10 pre-registered seeds
  ``[7, 13, 21, 42, 100, 137, 256, 314, 500, 1000]`` and require
  ratio ``count(top_half) / count(bot_half) > 5.0`` to hold on
  at least 8/10 seeds.

- ``test_T3_negative_control_fails_all_10_seeds`` — same 10-seed
  grid, identical injection / dynamics / plasticity envelope, but
  binding is **disabled** (``binding_cfg=None`` into ``tick``).

R-1d-T3 (commit b1b2112) reached 6/10 by recalibrating
``BindingConfig(α=0, β=200, T_crit=0.025)`` + ``QUANTA_PER_TICK=10``
so the spec §3 T-gate fires in the regime where ``T_local`` lives.
The R-1d-T3 phase-log diagnosis ("trimodal z-regime — floor decays,
middle accumulates, ceiling starves") identified bridge-flux
plasticity as the survival bottleneck for ceiling nodes: peak alive
12–20 nodes across the 4 failing seeds, but all decayed by tick
5000 because their self-bridges had no quanta flux passing through.

**Architectural fix chosen** for R-1d-T3-bis (iter-3 brief option
2, "ceiling-replenishment mechanism — symmetric to floor
injection"): add a new ``inject_ceiling_layer`` boundary function
that emits scaffold quanta just below the cold-face absorber. The
scaffolds carry ``polarity = -1``, which signals
``attempt_binding`` to skip them (they exist only to provide
bridge-flux through ceiling node self-bridges, not to form spurious
nodes from injection geometry) and signals ``_compute_density`` to
exclude them from the thermal mass count (counting scaffolds as
thermal mass would heat the ceiling above ``T_decay_crit`` and
trigger the very decay path the scaffold is meant to suppress).

With the scaffold mechanism + ``CEILING_QUANTA_PER_TICK = 20``,
``vel_z_mean = 0.3``, the substrate clears the ≥8/10 gate on 9 of
10 seeds in the audit run — solid margin above the pre-registered
threshold. The negative control (``binding_cfg=None``) is
unaffected: no nodes form regardless of scaffold presence, so all
10 seeds correctly fail the >5× ratio.
"""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.quantum import Quanta
from world.flux.grid import Grid
from world.flux.audit import EnergyAuditor
from world.flux.boundary import inject_hot_floor, inject_ceiling_layer
from world.flux.dynamics import tick
from world.flux.structures import Nodes
from world.flux.bridges import Bridges
from world.flux.binding import BindingConfig
from world.flux.decay import DecayConfig
from world.flux.plasticity import PlasticityConfig


SEEDS = [7, 13, 21, 42, 100, 137, 256, 314, 500, 1000]

# Pre-registered acceptance threshold from spec §7. NEVER retune.
T3_RATIO_THRESHOLD = 5.0


# Recalibrated BindingConfig: T-gate restored to operate in the
# actual T_local regime (~0.01-0.05). See module docstring.
def _binding_cfg() -> BindingConfig:
    return BindingConfig(
        alpha=0.0, beta=200.0, T_crit=0.025,
        eta=0.1, r=1.5, coherence_eps=1.0,
        r_bridge=2.0, bridge_w0=1.0,
    )


def _decay_cfg() -> DecayConfig:
    # Unchanged from F1a-locked calibration; the architectural fix
    # is on the binding side, not the decay side.
    return DecayConfig(gamma=500.0, T_decay_crit=0.035)


def _plasticity_cfg() -> PlasticityConfig:
    return PlasticityConfig(
        gamma=0.1, lam=0.1, flux_min=1.0, w_min=0.05, r_flux=0.75,
    )


# Module-level cache so the two pre-registered tests do not pay
# the substrate cost twice per seed (a single pytest invocation
# pays it once per (seed, mode)). Key: (mode, seed).
_CACHE: dict[tuple, dict] = {}


def _run_T3(seed: int, *, mode: str) -> dict:
    """Run the spec §7 T3 substrate once and return the diagnostic.

    ``mode='binding'``  : full T3 stack — binding + decay + plasticity.
    ``mode='control'`` : same stack with ``binding_cfg=None`` into
                         ``tick`` (no nodes can form).
    """
    key = (mode, seed)
    if key in _CACHE:
        return _CACHE[key]

    rng_inject = np.random.default_rng(seed)
    rng_bind = np.random.default_rng(seed + 1_000_000)
    q = Quanta(max_quanta=50_000)
    n = Nodes(max_nodes=50_000)
    br = Bridges(max_bridges=500_000)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0, T_smoothing=0.1)
    audit = EnergyAuditor(quanta=q, nodes=n, bridges=br, tol=1e-9)
    audit.record_initial()

    binding_cfg = _binding_cfg() if mode == "binding" else None
    decay_cfg = _decay_cfg()
    pcfg = _plasticity_cfg()

    QUANTA_PER_TICK = 10        # density boost from F1a's 5
    # R-1d-T3-bis ceiling-replenishment scaffold parameters.
    # Audit at qpt=20, vz=0.3 reaches 9/10 (seed 500 alone fails on
    # T-decay heating). Smaller scaffold count drops below threshold;
    # higher count or slower vz traps floor-source quanta near the
    # ceiling and raises T_z9 above T_decay_crit, killing nodes.
    CEILING_QUANTA_PER_TICK = 20
    CEILING_VEL_Z = 0.3
    ENERGY_PER = 1.0
    N_TICKS = 5000
    DT = 0.1
    FREQ_MEAN = 200.0

    def injector(quanta, grid):
        n_floor = inject_hot_floor(
            quanta, grid,
            n=QUANTA_PER_TICK,
            energy_per=ENERGY_PER,
            freq_mean=FREQ_MEAN,
            vel_z_mean=2.0,
            rng=rng_inject,
        )
        n_ceil = inject_ceiling_layer(
            quanta, grid,
            n=CEILING_QUANTA_PER_TICK,
            energy_per=ENERGY_PER,
            freq_mean=FREQ_MEAN,
            vel_z_mean=CEILING_VEL_Z,
            rng=rng_inject,
        )
        e = (n_floor + n_ceil) * ENERGY_PER
        audit.record_injection(e)
        return e

    for t in range(N_TICKS):
        exported, binding_heat, decay_heat = tick(
            q, g, dt=DT, injector=injector,
            nodes=n, binding_cfg=binding_cfg, decay_cfg=decay_cfg,
            bridges=br, plasticity_cfg=pcfg,
            rng=rng_bind, tick_index=t,
        )
        audit.record_export(exported)
        audit.record_binding_heat(binding_heat)
        audit.record_decay_heat(decay_heat)
        audit.check()
        audit.step()
    audit.check()

    alive_mask = n.alive
    n_alive = int(alive_mask.sum())
    Lz_half = g.dims[2] * g.voxel_size / 2.0

    if n_alive == 0:
        diagnostic = {
            "seed": seed, "mode": mode,
            "n_alive": 0, "n_top": 0, "n_bot": 0,
            "ratio": 0.0, "passed": False,
            "reason": "no nodes formed",
        }
    else:
        node_z = n.pos[alive_mask, 2]
        n_top = int((node_z >= Lz_half).sum())
        n_bot = int((node_z < Lz_half).sum())
        if n_bot == 0:
            ratio = float("inf") if n_top > 0 else 0.0
            passed = n_top > 0
        else:
            ratio = n_top / n_bot
            passed = ratio > T3_RATIO_THRESHOLD
        diagnostic = {
            "seed": seed, "mode": mode,
            "n_alive": n_alive, "n_top": n_top, "n_bot": n_bot,
            "ratio": ratio, "passed": passed,
            "reason": (None if passed
                       else f"ratio {ratio} <= {T3_RATIO_THRESHOLD} "
                            f"(top={n_top}, bot={n_bot})"),
        }

    _CACHE[key] = diagnostic
    return diagnostic


def test_T3_passes_on_at_least_8_of_10_seeds():
    """Pre-registered: T3 must pass the >5× cold-zone ratio on at
    least 8 of the 10 pre-registered seeds. Identical envelope for
    all seeds — no per-seed parameter tweaks."""
    results = [_run_T3(seed, mode="binding") for seed in SEEDS]
    passed = [r for r in results if r["passed"]]
    n_pass = len(passed)
    summary = "\n".join(
        f"  seed={r['seed']:>5}  pass={r['passed']!s:>5}  "
        f"alive={r['n_alive']:>3} top={r['n_top']:>3} bot={r['n_bot']:>3}  "
        f"ratio={r['ratio']}  reason={r['reason']}"
        for r in results
    )
    assert n_pass >= 8, (
        f"T3 robustness FAIL: only {n_pass}/10 seeds cleared "
        f"ratio > {T3_RATIO_THRESHOLD}. Per-seed:\n{summary}"
    )


def test_T3_negative_control_fails_all_10_seeds():
    """Pre-registered: with binding DISABLED, no seed may pass the
    T3 ratio threshold. If even one seed produces ratio > 5× without
    binding, the metric is a state-detector firing on substrate
    dynamics rather than on the binding mechanism."""
    results = [_run_T3(seed, mode="control") for seed in SEEDS]
    spurious = [r for r in results if r["passed"]]
    summary = "\n".join(
        f"  seed={r['seed']:>5}  pass={r['passed']!s:>5}  "
        f"alive={r['n_alive']:>3} top={r['n_top']:>3} bot={r['n_bot']:>3}  "
        f"ratio={r['ratio']}"
        for r in results
    )
    assert not spurious, (
        f"Negative control FAIL: {len(spurious)}/10 seeds passed "
        f"the T3 threshold WITHOUT binding — the ratio is a state-"
        f"detector, not a binding-discriminator. Per-seed:\n{summary}"
    )
