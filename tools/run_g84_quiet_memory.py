"""G84 — selective persistent memory on a QUIET substrate. G83 proved homogeneous self-activity is
the root that drowns signal; the memory deadlock (G33-G73) was measured on the ACTIVE substrate where
control is never blank. Here: cull the free-vibration background EVERY tick so the ONLY activity is
the stim injection. Stim atoms co-fire (driven by the local injection field) and write; control gets
NO input -> silent -> its bridges can't latch -> selective. Read stim vs control region bridge means
through POST.

Pre-registered bars in docs/amendments/g84_quiet_memory.md.
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


def run_arm(name, uniform, wall_budget=200):
    cfg = make_cfg()
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
            # MAXIMALLY QUIET: cull all free vibrations each tick, then inject ONLY the stimulus.
            cull_free_vibrations(world, keep_frac=0.0)
            if uniform:
                inject_tight(world, cfg, box, STIM_X, n=20)
                inject_tight(world, cfg, box, CTRL_X, n=20)
            else:
                inject_tight(world, cfg, box, STIM_X, n=40)
        if step == STIM_END:
            cull_free_vibrations(world, keep_frac=0.0)
        tick(world, dt)
        if step % 1000 == 999:
            sim_s = round((step + 1) * dt, 1)
            sm, _ = region_mean(world, STIM_X, half=HALF)
            cm, _ = region_mean(world, CTRL_X, half=HALF)
            ph = ("WARM" if step < WARMUP else "STIM" if step < STIM_END else "POST")
            log.append({"sim_s": sim_s, "phase": ph, "stim_mean": round(sm, 2), "ctrl_mean": round(cm, 2)})
            print(f"[{name}] {sim_s:.0f}s [{ph}]: stim={sm:.2f} ctrl={cm:.2f}", flush=True)
        if time.time() - t0 > wall_budget:
            break
    return {"name": name, "log": log, "stim_end_s": STIM_END * dt}


def frac(log, phase, min_s=None):
    rows = [e for e in log if e["phase"] == phase and (min_s is None or e["sim_s"] >= min_s)]
    return (sum(1 for e in rows if e["stim_mean"] > 3.0 and e["ctrl_mean"] < 3.0) / len(rows)) if rows else 0.0


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    print("=== G84: selective persistent memory on a QUIET substrate ===", flush=True)
    loc = run_arm("LOC", uniform=False, wall_budget=budget)
    uni = run_arm("UNI", uniform=True, wall_budget=budget)
    pm = loc["stim_end_s"] + 2000
    stim = frac(loc["log"], "STIM")
    post = frac(loc["log"], "POST", pm)
    uni_post = frac(uni["log"], "POST", pm)

    G84a = stim >= 0.5
    G84b = post >= 0.5
    G84c = uni_post < 0.25
    passed = G84a and G84b and G84c
    print("\n--- VERDICT ---", flush=True)
    print(f"LOC stim-frac={stim:.2f} post-frac={post:.2f} | UNI post-frac={uni_post:.2f}", flush=True)
    print(f"G84a selective write (>=0.5)   : {G84a}", flush=True)
    print(f"G84b persistent recall (>=0.5) : {G84b}", flush=True)
    print(f"G84c uniform control fails      : {G84c}", flush=True)
    verdict = ("PASS - SELECTIVE PERSISTENT MEMORY on a quiet substrate (deadlock BROKEN by removing the root)"
               if passed else "NULL/partial - deadlock persists even on a quiet substrate")
    print(f"\nG84: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G84"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"loc": loc, "uni": uni, "stim": stim, "post": post,
                                                  "uni_post": uni_post, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
