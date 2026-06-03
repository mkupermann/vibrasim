"""G90 — selective PERSISTENT memory: low-intensity write (control blank, G89) + consolidation.
G89 found n=4 keeps control cleanly blank (uni-post 0.00) and stim recalls 0.44 (just under 0.5) --
the gap is now STIM PERSISTENCE, not control contamination. Since control is blank, consolidation
locks ONLY stim (the reason consolidation failed before -- control also consolidating -- is gone).
Add bridge_consolidate_threshold to lock the stim engram. Quiet + disconnected + local + n=4.
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

N_INJ = 4


def run_arm(name, threshold, uniform, wall_budget=150):
    cfg = make_cfg()
    object.__setattr__(cfg, 'compartment_boundary', 15.0)
    object.__setattr__(cfg, 'emit_speed', 6.0)
    object.__setattr__(cfg, 'bridge_consolidate_threshold', threshold)
    w = World(cfg); dt = cfg.dt
    box = np.asarray(cfg.box_size); STIM_X, CTRL_X = box[0] * 0.25, box[0] * 0.75
    log = []; t0 = time.time()
    for step in range(40000):
        if step == WARMUP:
            object.__setattr__(cfg, 'lambda_gen', 0.0)
            cull_free_vibrations(w, keep_frac=0.0); blank_bridges(w, cfg.bistable_low)
        if WARMUP <= step < STIM_END:
            cull_free_vibrations(w, keep_frac=0.0)
            if uniform:
                inject_tight(w, cfg, box, STIM_X, n=N_INJ // 2 or 1); inject_tight(w, cfg, box, CTRL_X, n=N_INJ // 2 or 1)
            else:
                inject_tight(w, cfg, box, STIM_X, n=N_INJ)
        if step == STIM_END:
            cull_free_vibrations(w, keep_frac=0.0)
        tick(w, dt)
        if step % 1000 == 999:
            sim_s = round((step + 1) * dt, 1)
            sm, _ = region_mean(w, STIM_X, half=HALF); cm, _ = region_mean(w, CTRL_X, half=HALF)
            ph = ("WARM" if step < WARMUP else "STIM" if step < STIM_END else "POST")
            log.append({"sim_s": sim_s, "phase": ph, "stim_mean": round(sm, 2), "ctrl_mean": round(cm, 2)})
        if time.time() - t0 > wall_budget:
            break
    return {"name": name, "log": log, "stim_end_s": STIM_END * dt}


def frac(log, phase, min_s=None):
    rows = [e for e in log if e["phase"] == phase and (min_s is None or e["sim_s"] >= min_s)]
    return (sum(1 for e in rows if e["stim_mean"] > 3.0 and e["ctrl_mean"] < 3.0) / len(rows)) if rows else 0.0


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    ths = [3.5, 4.0, 5.0]
    print("=== G90: low-intensity write + consolidation (control blank -> only stim locks) ===", flush=True)
    res = {}
    for th in ths:
        loc = run_arm(f"LOC-t{th}", th, uniform=False, wall_budget=budget)
        uni = run_arm(f"UNI-t{th}", th, uniform=True, wall_budget=budget)
        pm = loc["stim_end_s"] + 2000
        res[th] = dict(stim=frac(loc["log"], "STIM"), post=frac(loc["log"], "POST", pm), uni_post=frac(uni["log"], "POST", pm))
        r = res[th]
        print(f"  threshold={th}: stim-frac={r['stim']:.2f} post-frac={r['post']:.2f} uni-post={r['uni_post']:.2f}", flush=True)
    working = [th for th in ths if res[th]['stim'] >= 0.5 and res[th]['post'] >= 0.5 and res[th]['uni_post'] < 0.25]
    passed = len(working) > 0
    print("\n--- VERDICT ---", flush=True)
    print(f"working threshold(s): {working}", flush=True)
    print(("G90: PASS - SELECTIVE PERSISTENT MEMORY (low-intensity write + consolidation; deadlock BROKEN)" if passed
           else "G90: NULL/partial"), flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G90"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"results": {str(k): v for k, v in res.items()}, "working": working, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
