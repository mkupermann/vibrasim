"""G72 — consolidation sleep-sweep. refractory (selective write) + consolidation (lock stim) +
a DISCRETE reset at STIM end that blanks every NON-consolidated bridge to baseline (clears control's
drift while keeping the locked stim engram). The final write-rule attempt at selective persistent
memory.

Pre-registered bars in docs/amendments/g72_sleep_sweep.md.
"""
import sys, json, time
import numpy as np
from pathlib import Path
from world.state import World
from world.physics import tick
from tools.run_bet090 import region_mean
from tools.run_bet093 import cull_free_vibrations
from tools.run_bet098 import inject_tight, blank_bridges
from tools.run_bet099 import make_cfg, WARMUP, STIM_END, HALF


def sleep_sweep(world, low):
    """Blank every NON-consolidated bridge to low (keep the locked engram, clear the slate)."""
    consolidated = getattr(world, '_consolidated', set())
    for b in range(world.b_count):
        if world.b_alive[b] and b not in consolidated:
            world.b_strength[b] = float(low)


def run_arm(name, uniform, threshold, wall_budget=200):
    cfg = make_cfg()
    object.__setattr__(cfg, 't_refractory', 0.5)
    object.__setattr__(cfg, 'bridge_consolidate_threshold', threshold)
    world = World(cfg); dt = cfg.dt
    box = np.asarray(cfg.box_size)
    STIM_X, CTRL_X = box[0] * 0.25, box[0] * 0.75
    log = []
    t0 = time.time()
    for step in range(40000):
        if step == WARMUP:
            object.__setattr__(cfg, 'lambda_gen', 0.0)
            cull_free_vibrations(world, keep_frac=0.0)
            blank_bridges(world, cfg.bistable_low)
        if WARMUP <= step < STIM_END:
            if uniform:
                inject_tight(world, cfg, box, STIM_X, n=20)
                inject_tight(world, cfg, box, CTRL_X, n=20)
            else:
                inject_tight(world, cfg, box, STIM_X, n=40)
        if step == STIM_END:
            cull_free_vibrations(world, keep_frac=0.0)
            sleep_sweep(world, cfg.bistable_low)   # <-- the new mechanism
            print(f"[{name}] field cleared + sleep-sweep at STIM end "
                  f"(kept {len(getattr(world, '_consolidated', set()))} consolidated)", flush=True)
        tick(world, dt)
        if step % 1000 == 999:
            sim_s = round((step + 1) * dt, 1)
            sm, sn = region_mean(world, STIM_X, half=HALF)
            cm, cn = region_mean(world, CTRL_X, half=HALF)
            ph = ("WARM" if step < WARMUP else "STIM" if step < STIM_END else "POST")
            log.append({"sim_s": sim_s, "phase": ph, "stim_mean": round(sm, 2), "ctrl_mean": round(cm, 2)})
        if time.time() - t0 > wall_budget:
            break
    return {"name": name, "log": log, "stim_end_s": STIM_END * dt}


def frac(log, phase, min_s=None):
    rows = [e for e in log if e["phase"] == phase and (min_s is None or e["sim_s"] >= min_s)]
    return (sum(1 for e in rows if e["stim_mean"] > 3.0 and e["ctrl_mean"] < 3.0) / len(rows)) if rows else 0.0


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    print("=== G72: consolidation sleep-sweep (refractory + consolidation + reset non-consolidated) ===", flush=True)
    thresholds = [3.5, 4.0, 4.5]
    results = {}
    for th in thresholds:
        loc = run_arm("LOC", uniform=False, threshold=th, wall_budget=budget)
        uni = run_arm("UNI", uniform=True, threshold=th, wall_budget=budget)
        pm = loc["stim_end_s"] + 2000
        results[th] = dict(stim=frac(loc["log"], "STIM"), post=frac(loc["log"], "POST", pm),
                           uni_post=frac(uni["log"], "POST", pm))
        r = results[th]
        print(f"  threshold={th}: stim-frac={r['stim']:.2f} post-frac={r['post']:.2f} uni-post={r['uni_post']:.2f}", flush=True)

    working = [th for th in thresholds if results[th]['stim'] >= 0.5 and results[th]['post'] >= 0.5 and results[th]['uni_post'] < 0.25]
    passed = len(working) > 0
    print("\n--- VERDICT ---", flush=True)
    print(f"working threshold(s): {working}", flush=True)
    print(f"G72: {'PASS - SELECTIVE PERSISTENT MEMORY (sleep-sweep breaks the deadlock)' if passed else 'NULL/partial'}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G72"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"results": {str(k): v for k, v in results.items()},
                                                  "working": working, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
