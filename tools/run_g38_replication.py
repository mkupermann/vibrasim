"""G38 — multi-seed replication of G37 (mirror wall + set readout) with matched no-wall
controls. Seeds {42, 7, 99}. Establishes whether the selective-persistent-recall result
is robust before any milestone claim.

Pre-registered bars in docs/amendments/g38_recall_replication.md.
"""
import sys, json, time
from dataclasses import replace
import numpy as np
from pathlib import Path

from world.state import World
from world.physics import tick
from tools.run_bet093 import cull_free_vibrations
from tools.run_bet098 import inject_tight, blank_bridges
from tools.run_bet099 import make_cfg, WARMUP, STIM_END, HALF
from tools.run_g34_engram_set import strong_keys


def run_arm(seed, wall, wall_budget=200):
    cfg = make_cfg()
    object.__setattr__(cfg, 'rng_seed', seed)
    box = np.asarray(cfg.box_size)
    STIM_X, CTRL_X = box[0] * 0.25, box[0] * 0.75
    cfg = replace(cfg, compartment_k=0.0, compartment_mode='mirror',
                  compartment_centre=(float(STIM_X), float(box[1] / 2), float(box[2] / 2)),
                  compartment_radius=6.0)
    world = World(cfg); dt = cfg.dt
    E = C = None
    log = []
    stim_fire = ctrl_fire = 0
    t0 = time.time()
    for step in range(40000):
        if step == WARMUP:
            object.__setattr__(cfg, 'lambda_gen', 0.0)
            cull_free_vibrations(world, keep_frac=0.0)
            blank_bridges(world, cfg.bistable_low)
            if wall:
                object.__setattr__(cfg, 'compartment_k', 1.0)
        if WARMUP <= step < STIM_END:
            inject_tight(world, cfg, box, STIM_X, n=40)
        if step == STIM_END:
            cull_free_vibrations(world, keep_frac=0.0)
            E = strong_keys(world, STIM_X)
            C = strong_keys(world, CTRL_X)
        tick(world, dt)
        if WARMUP <= step < STIM_END:
            for t_f, ai in world.firing_events:
                if t_f < world.t - dt or ai >= world.k_count or not world.k_alive[ai]:
                    continue
                x = world.k_pos[ai][0]
                if abs(x - STIM_X) < HALF:
                    stim_fire += 1
                elif abs(x - CTRL_X) < HALF:
                    ctrl_fire += 1
        if step % 1000 == 999 and E is not None:
            cur = strong_keys(world)
            log.append({"sim_s": round((step + 1) * dt, 1),
                        "eI": len(E & cur), "cI": len(C & cur)})
        if time.time() - t0 > wall_budget:
            break
    return {"seed": seed, "wall": wall, "lenE": len(E) if E else 0, "lenC": len(C) if C else 0,
            "stim_fire": stim_fire, "ctrl_fire": ctrl_fire, "stim_end_s": STIM_END * dt, "log": log}


def horizon(arm):
    win = [e for e in arm["log"] if e["sim_s"] >= arm["stim_end_s"] + 2000]
    if not win:
        return 0, 0
    return win[-1]["eI"], win[-1]["cI"]


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    seeds = [42, 7, 99]
    print("=== G38: multi-seed replication of selective persistent recall ===", flush=True)
    rows = {}
    for s in seeds:
        mw = run_arm(s, wall=True, wall_budget=budget)
        nw = run_arm(s, wall=False, wall_budget=budget)
        eI, cI = horizon(mw)
        fr = mw["stim_fire"] / max(mw["ctrl_fire"], 1)
        rows[s] = dict(lenE=mw["lenE"], lenC=mw["lenC"], eI=eI, cI=cI, fire=fr, nowall_C=nw["lenC"])
        print(f"  seed {s}: mirror |E|={mw['lenE']} |C|={mw['lenC']} horizon E={eI} C={cI} "
              f"fire={fr:.0f}x | no-wall |C|={nw['lenC']}", flush=True)

    G38a = all(r["lenE"] >= 1 and (r["eI"] / max(r["lenE"], 1)) >= 0.5 and r["fire"] >= 10 for r in rows.values())
    G38b = all(r["cI"] <= 1 and (r["eI"] - r["cI"]) >= 1 for r in rows.values())
    G38c = all(r["nowall_C"] >= 2 for r in rows.values())
    passed = G38a and G38b and G38c

    print("\n--- VERDICT ---", flush=True)
    print(f"G38a mirror writes persistent engram (all seeds) : {G38a}", flush=True)
    print(f"G38b mirror selective (all seeds)                : {G38b}", flush=True)
    print(f"G38c no-wall contaminates (all seeds)            : {G38c}", flush=True)
    verdict = ("PASS - ROBUST selective persistent recall across seeds; wall necessary. MILESTONE."
               if passed else "NULL/partial - seed-dependent; no milestone claim")
    print(f"\nG38: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G38"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": rows, "G38a": G38a, "G38b": G38b,
                                                  "G38c": G38c, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
