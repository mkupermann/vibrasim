"""G39 — scale test: enlarge the engram core (n=120, sigma=2.5, half=5) inside the mirror
wall and test whether selective persistent recall replicates across seeds {42,7,99}.

Pre-registered bars in docs/amendments/g39_large_core_recall.md.
"""
import sys, json, time
from dataclasses import replace
import numpy as np
from pathlib import Path

from world.state import World
from world.physics import tick
from tools.run_bet093 import cull_free_vibrations
from tools.run_bet098 import inject_tight, blank_bridges
from tools.run_bet099 import make_cfg, WARMUP, STIM_END
from tools.run_g34_engram_set import strong_keys

N_INJ = 120
SIGMA = 2.5
HALF = 5.0


def run_arm(seed, wall_budget=200):
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
            object.__setattr__(cfg, 'compartment_k', 1.0)
        if WARMUP <= step < STIM_END:
            inject_tight(world, cfg, box, STIM_X, n=N_INJ, sigma=SIGMA)
        if step == STIM_END:
            cull_free_vibrations(world, keep_frac=0.0)
            E = strong_keys(world, STIM_X, half=HALF)
            C = strong_keys(world, CTRL_X, half=HALF)
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
            log.append({"sim_s": round((step + 1) * dt, 1), "eI": len(E & cur), "cI": len(C & cur)})
        if time.time() - t0 > wall_budget:
            break
    return {"seed": seed, "lenE": len(E) if E else 0, "lenC": len(C) if C else 0,
            "stim_fire": stim_fire, "ctrl_fire": ctrl_fire, "stim_end_s": STIM_END * dt, "log": log}


def horizon(arm):
    win = [e for e in arm["log"] if e["sim_s"] >= arm["stim_end_s"] + 2000]
    return (win[-1]["eI"], win[-1]["cI"]) if win else (0, 0)


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    seeds = [42, 7, 99]
    print("=== G39: large-core scale test (n=120, sigma=2.5, half=5) ===", flush=True)
    rows = {}
    for s in seeds:
        a = run_arm(s, wall_budget=budget)
        eI, cI = horizon(a)
        fr = a["stim_fire"] / max(a["ctrl_fire"], 1)
        rows[s] = dict(lenE=a["lenE"], lenC=a["lenC"], eI=eI, cI=cI, fire=fr)
        print(f"  seed {s}: |E|={a['lenE']} |C|={a['lenC']} horizon E={eI} C={cI} fire={fr:.0f}x", flush=True)

    G39a = all(r["lenE"] >= 10 for r in rows.values())
    G39b = all((r["eI"] / max(r["lenE"], 1)) >= 0.5 for r in rows.values())
    G39c = all((r["eI"] - r["cI"]) >= 0.5 * max(r["lenE"], 1) for r in rows.values())
    G39d = all(r["fire"] >= 10 for r in rows.values())
    passed = G39a and G39b and G39c and G39d

    print("\n--- VERDICT ---", flush=True)
    print(f"G39a large engram |E|>=10 (all)   : {G39a}", flush=True)
    print(f"G39b persists >=0.5 (all)         : {G39b}", flush=True)
    print(f"G39c selective E-C>=0.5|E| (all)  : {G39c}", flush=True)
    print(f"G39d containment >=10x (all)      : {G39d}", flush=True)
    verdict = ("PASS - scale resolves it: ROBUST selective persistent recall on a large core. MILESTONE."
               if passed else "NULL/partial - scale does not make recall robust")
    print(f"\nG39: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G39"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": rows, "G39a": G39a, "G39b": G39b,
                                                  "G39c": G39c, "G39d": G39d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
