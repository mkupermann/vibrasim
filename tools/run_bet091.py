"""BET-091: atom persistence via valence commitment. A bonded atom resists
fusion (fusion_bond_block), so the lattice persists; then BET-090's anchoring
has something durable to anchor and selective memory can form.

Two arms, identical except fusion_bond_block (ON=1 vs OFF=0). Each arm measures
both atom lifetime (T91a/b) and selective memory (T91c/d). Anchoring is ON in
both arms so the only difference is the persistence mechanism.

Pre-registered bars in docs/amendments/bet_091_atom_persistence.md.
"""
import sys, json, time
import numpy as np
from pathlib import Path
from world.config import WorldConfig
from world.state import World
from world.physics import tick
from tools.run_bet090 import inject, region_mean

MEASURE_BOND = 3   # valence-saturated atom (= atom_valence); the protected population
STIM_STEPS = 12000
BLOCK_ON = 3       # fusion_bond_block for the ON arm (= atom_valence; see marker_protocol correction)


def make_cfg(fusion_bond_block: int) -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=400, box_size=(30.0, 30.0, 30.0),
        r_1=5.0, r_2=10.0, freq_tolerance=0.03,
        mol_fusion_enabled=False, resonance_coupling=15.0,
        node_thermal_speed=0.3, atom_valence=3,
        node_freq_binding=False, atom_repulsion_k=1.0, curvature_k=1.0,
        bistable_rate=1.0, bistable_low=1.0, bistable_mid=3.0, bistable_high=6.0,
        bistable_well_k=0.04, bistable_flux_gain=0.3, bistable_flux_ref=40.0,
        anchor_damping=0.7, anchor_bond_min=2, anchor_age=50.0,
        fusion_bond_block=fusion_bond_block,
        pair_decay_time=40.0, triad_decay_time=400.0, dt=0.5,
        n_nodes_max=8192, n_vibrations_max=4096, vibration_soft_cap=500,
        repulsion_k=0.0, lambda_gen=0.006, lambda_dec=0.0,
        neuron_dynamics_enabled=False, stdp_enabled=False,
        slot_recycling_enabled=False, graceful_capacity=True, rng_seed=42,
    )


def run_arm(name, fusion_bond_block, wall_budget=360):
    cfg = make_cfg(fusion_bond_block)
    world = World(cfg)
    dt = cfg.dt
    box = np.asarray(cfg.box_size)
    STIM_X, CTRL_X = box[0] * 0.25, box[0] * 0.75

    # Lifetime tracking for atoms that reach >= MEASURE_BOND bridges.
    tracking = {}          # atom idx -> birth sim-time
    completed = []         # observed lifespans (sim-s)
    log = []
    t0 = time.time()
    last_step = 0
    for step in range(40000):
        last_step = step
        if step < STIM_STEPS and step % 4 == 0:
            inject(world, cfg, box, STIM_X, n=20)
        tick(world, dt)

        # update lifetime tracking every tick
        K = world.k_count
        for a in range(K):
            if (world.k_alive[a] and world.k_level[a] == 4
                    and world.k_bond_count[a] >= MEASURE_BOND
                    and a not in tracking):
                tracking[a] = float(world.k_birth[a])
        for a in list(tracking):
            if a >= world.k_count or not world.k_alive[a] or world.k_level[a] != 4:
                completed.append(world.t - tracking[a])
                del tracking[a]

        if step % 2000 == 1999:
            sim_s = round((step + 1) * dt, 1)
            sm, sn = region_mean(world, STIM_X)
            cm, cn = region_mean(world, CTRL_X)
            ph = "STIM" if step < STIM_STEPS else "POST"
            n_bonded = int(sum(1 for a in range(world.k_count)
                               if world.k_alive[a] and world.k_level[a] == 4
                               and world.k_bond_count[a] >= MEASURE_BOND))
            e = {"sim_s": sim_s, "phase": ph, "stim_mean": round(sm, 2),
                 "stim_n": sn, "ctrl_mean": round(cm, 2), "ctrl_n": cn,
                 "n_bonded_atoms": n_bonded}
            log.append(e)
            print(f"[{name}] {sim_s:.0f}s [{ph}]: stim={sm:.2f}(n={sn}) "
                  f"ctrl={cm:.2f}(n={cn}) bonded_atoms={n_bonded}", flush=True)
        if time.time() - t0 > wall_budget:
            print(f"[{name}] wall budget hit at step {step}", flush=True)
            break

    # include still-alive tracked atoms (right-censored at their current age)
    observed = completed + [world.t - b for b in tracking.values()]
    mean_life = float(np.mean(observed)) if observed else 0.0
    return {"name": name, "fusion_bond_block": fusion_bond_block, "log": log,
            "mean_bonded_lifetime": mean_life, "n_observed": len(observed),
            "still_alive_bonded": len(tracking), "end_sim_s": (last_step + 1) * dt}


def memory_selective(log, phase, min_s=None):
    rows = [e for e in log if e["phase"] == phase
            and (min_s is None or e["sim_s"] >= min_s)]
    return any(e["stim_mean"] > 3.0 and e["ctrl_mean"] < 3.0 for e in rows)


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 360
    print("=== BET-091: atom persistence via valence commitment ===", flush=True)
    on = run_arm("ON ", fusion_bond_block=BLOCK_ON, wall_budget=budget)
    off = run_arm("OFF", fusion_bond_block=0, wall_budget=budget)

    # Pre-registered bars
    T91a = on["mean_bonded_lifetime"] > 100.0
    T91b = off["mean_bonded_lifetime"] < 30.0
    T91c = (memory_selective(on["log"], "STIM")
            and memory_selective(on["log"], "POST", min_s=8000))
    T91d = not (memory_selective(off["log"], "STIM")
                and memory_selective(off["log"], "POST", min_s=8000))
    passed = T91a and T91b and T91c and T91d

    print("\n--- VERDICT ---", flush=True)
    print(f"ON  bonded-atom mean lifetime: {on['mean_bonded_lifetime']:.1f}s "
          f"(n={on['n_observed']}, still-alive={on['still_alive_bonded']})", flush=True)
    print(f"OFF bonded-atom mean lifetime: {off['mean_bonded_lifetime']:.1f}s "
          f"(n={off['n_observed']}, still-alive={off['still_alive_bonded']})", flush=True)
    print(f"T91a persistence(ON>100s)      : {T91a}", flush=True)
    print(f"T91b control persistence(<30s) : {T91b}", flush=True)
    print(f"T91c selective memory (ON)     : {T91c}", flush=True)
    print(f"T91d control memory fails      : {T91d}", flush=True)
    print(f"\nBET-091: {'PASS' if passed else 'NULL/FAIL'}", flush=True)

    outdir = Path.home() / '.eqmod' / 'bet' / 'BET-091'
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'result.json').write_text(json.dumps(
        {"on": on, "off": off, "T91a": T91a, "T91b": T91b, "T91c": T91c,
         "T91d": T91d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
