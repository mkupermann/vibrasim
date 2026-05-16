"""R-1d-T3 diagnosis: per-seed T3 audit across the 10-seed grid.

Mirrors tests/flux/test_crystallization.py exactly. Prints per-seed:
  - n_alive (number of nodes alive after 5000 ticks)
  - n_top / n_bot (above/below z=5)
  - ratio (n_top / n_bot)
  - passed (ratio > 5.0)
  - T_layer means (z=0, z=5, z=9) at end of run — tells us whether the
    decay layer-mean gradient survives in non-seed=42 RNG draws
"""
from __future__ import annotations
import sys
import numpy as np

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


def run_one(seed: int, quanta_per_tick: int = 5,
             n_ticks: int = 5000, t_decay_crit: float = 0.035,
             decay_gamma: float = 500.0,
             alpha: float = 4.0, beta: float = 4.0,
             T_crit: float = 2.0,
             ceiling_qpt: int = 0,
             ceiling_vz: float = 0.5) -> dict:
    rng_inject = np.random.default_rng(seed)
    rng_bind = np.random.default_rng(seed + 1_000_000)
    q = Quanta(max_quanta=50_000)
    n = Nodes(max_nodes=50_000)
    br = Bridges(max_bridges=500_000)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0, T_smoothing=0.1)
    audit = EnergyAuditor(quanta=q, nodes=n, bridges=br, tol=1e-9)
    audit.record_initial()

    cfg = BindingConfig(
        alpha=alpha, beta=beta, T_crit=T_crit,
        eta=0.1, r=1.5, coherence_eps=1.0,
        r_bridge=2.0, bridge_w0=1.0,
    )
    decay_cfg = DecayConfig(gamma=decay_gamma, T_decay_crit=t_decay_crit)
    pcfg = PlasticityConfig(gamma=0.1, lam=0.1, flux_min=1.0,
                             w_min=0.05, r_flux=0.75)

    QUANTA_PER_TICK = quanta_per_tick
    ENERGY_PER = 1.0
    N_TICKS = n_ticks
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
        n_ceil = 0
        if ceiling_qpt > 0:
            n_ceil = inject_ceiling_layer(
                quanta, grid,
                n=ceiling_qpt,
                energy_per=ENERGY_PER,
                freq_mean=FREQ_MEAN,
                vel_z_mean=ceiling_vz,
                rng=rng_inject,
            )
        e = (n_floor + n_ceil) * ENERGY_PER
        audit.record_injection(e)
        return e

    # Track births/deaths by z-layer for richer diagnosis
    births_by_layer = np.zeros(10, dtype=np.int64)
    peak_alive = 0

    for t in range(N_TICKS):
        alive_before = int(n.alive.sum())
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
        # Count any node not present last tick as a fresh birth
        alive_mask = n.alive
        if alive_mask.sum() > alive_before:
            # Crude — find the new slot(s) just allocated this tick
            # via born_tick = t
            new_mask = alive_mask & (n.born_tick == t)
            for slot in np.where(new_mask)[0]:
                z_layer = min(9, max(0, int(n.pos[int(slot), 2])))
                births_by_layer[z_layer] += 1
        peak_alive = max(peak_alive, int(alive_mask.sum()))

    alive_mask = n.alive
    n_alive = int(alive_mask.sum())
    if n_alive == 0:
        ratio = 0.0
        n_top = n_bot = 0
    else:
        node_z = n.pos[alive_mask, 2]
        n_top = int((node_z >= 5.0).sum())
        n_bot = int((node_z < 5.0).sum())
        ratio = (n_top / n_bot) if n_bot > 0 else float("inf")

    T_layer = g.T.mean(axis=(0, 1))
    passed = ratio > 5.0
    return {
        "seed": seed,
        "n_alive": n_alive,
        "n_top": n_top,
        "n_bot": n_bot,
        "ratio": ratio,
        "passed": passed,
        "peak_alive": peak_alive,
        "births_by_layer": births_by_layer.tolist(),
        "T_z0": float(T_layer[0]),
        "T_z5": float(T_layer[5]),
        "T_z9": float(T_layer[9]),
    }


def main() -> int:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--qpt", type=int, default=5,
                   help="quanta_per_tick (default 5 — canonical)")
    p.add_argument("--ticks", type=int, default=5000)
    p.add_argument("--seeds", type=int, nargs="+", default=SEEDS)
    p.add_argument("--t_dc", type=float, default=0.035,
                   help="T_decay_crit (default 0.035 — F1a-locked)")
    p.add_argument("--gamma", type=float, default=500.0,
                   help="decay gamma (default 500.0)")
    p.add_argument("--alpha", type=float, default=4.0)
    p.add_argument("--beta", type=float, default=4.0)
    p.add_argument("--Tcrit", type=float, default=2.0)
    p.add_argument("--ceil_qpt", type=int, default=0,
                   help="ceiling-scaffold quanta per tick (R-1d-T3-bis)")
    p.add_argument("--ceil_vz", type=float, default=0.5,
                   help="ceiling-scaffold upward vel_z mean")
    args = p.parse_args()

    print(f"Running with QUANTA_PER_TICK={args.qpt}, CEIL_QPT={args.ceil_qpt}, CEIL_VZ={args.ceil_vz}, N_TICKS={args.ticks}, T_dc={args.t_dc}, gamma={args.gamma}, seeds={args.seeds}")
    print(f"{'seed':>5}  {'pass':>4}  {'alive':>5}  {'top':>4}  {'bot':>4}  {'ratio':>8}  {'peak':>5}  T(z0,z5,z9)")
    n_pass = 0
    for seed in args.seeds:
        r = run_one(seed, quanta_per_tick=args.qpt, n_ticks=args.ticks,
                     t_decay_crit=args.t_dc, decay_gamma=args.gamma,
                     alpha=args.alpha, beta=args.beta, T_crit=args.Tcrit,
                     ceiling_qpt=args.ceil_qpt, ceiling_vz=args.ceil_vz)
        if r["passed"]:
            n_pass += 1
        ratio_s = f"{r['ratio']:>8.2f}" if r["ratio"] != float("inf") else "     inf"
        print(
            f"{r['seed']:>5}  {str(r['passed']):>4}  "
            f"{r['n_alive']:>5}  {r['n_top']:>4}  {r['n_bot']:>4}  "
            f"{ratio_s}  {r['peak_alive']:>5}  "
            f"({r['T_z0']:.3f},{r['T_z5']:.3f},{r['T_z9']:.3f})"
        )
    print(f"\nSummary: {n_pass}/{len(args.seeds)} passed (need >=8/10)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
