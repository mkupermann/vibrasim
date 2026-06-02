"""G33 — engineered compartment containment resolves the write/contaminate tension.

Reuses the BET-099/100 correlation-memory protocol verbatim. The only addition: an
engineered compartment sphere (radius 6, centred on the stim region) whose wall reflects
OUTBOUND free vibrations, switched ON at STIM start (after the lattice has formed
everywhere during WARMUP, so the control region has atoms that can stay blank).

Arms: LOC+wall (test), UNI+wall (neg control: can't fake selectivity),
LOC no-wall (matched-wallclock control: percolation must destroy selectivity).
Pre-registered bars in docs/amendments/g33_compartment_recall.md.
"""
import sys, json, time
from dataclasses import replace
import numpy as np
from pathlib import Path

from world.state import World
from world.physics import tick
from tools.run_bet090 import region_mean
from tools.run_bet093 import cull_free_vibrations
from tools.run_bet098 import inject_tight, blank_bridges
from tools.run_bet099 import make_cfg, WARMUP, STIM_END, HALF


def run_arm(name, uniform, wall, wall_budget=480):
    cfg = make_cfg()
    box = np.asarray(cfg.box_size)
    STIM_X, CTRL_X = box[0] * 0.25, box[0] * 0.75
    # Engineered compartment around the stim region (off until STIM start).
    cfg = replace(cfg, compartment_k=0.0,
                  compartment_centre=(float(STIM_X), float(box[1] / 2), float(box[2] / 2)),
                  compartment_radius=6.0)
    world = World(cfg); dt = cfg.dt
    log = []
    stim_fire = ctrl_fire = 0
    t0 = time.time()
    for step in range(40000):
        if step == WARMUP:
            object.__setattr__(cfg, 'lambda_gen', 0.0)
            cull_free_vibrations(world, keep_frac=0.0)
            blank_bridges(world, cfg.bistable_low)
            if wall:
                object.__setattr__(cfg, 'compartment_k', 1.0)  # raise the port wall
        if WARMUP <= step < STIM_END:
            if uniform:
                inject_tight(world, cfg, box, STIM_X, n=20)
                inject_tight(world, cfg, box, CTRL_X, n=20)
            else:
                inject_tight(world, cfg, box, STIM_X, n=40)
        if step == STIM_END:
            cull_free_vibrations(world, keep_frac=0.0)
            print(f"[{name}] field cleared at STIM end", flush=True)
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
        if step % 1000 == 999:
            sim_s = round((step + 1) * dt, 1)
            sm, sn = region_mean(world, STIM_X, half=HALF)
            cm, cn = region_mean(world, CTRL_X, half=HALF)
            ph = ("WARM" if step < WARMUP else "STIM" if step < STIM_END else "POST")
            log.append({"sim_s": sim_s, "phase": ph, "stim_mean": round(sm, 2),
                        "stim_n": sn, "ctrl_mean": round(cm, 2), "ctrl_n": cn})
            print(f"[{name}] {sim_s:.0f}s [{ph}]: stim={sm:.2f}(n={sn}) ctrl={cm:.2f}(n={cn})", flush=True)
        if time.time() - t0 > wall_budget:
            print(f"[{name}] wall budget hit at step {step}", flush=True)
            break
    return {"name": name, "uniform": uniform, "wall": wall, "log": log,
            "stim_fire": stim_fire, "ctrl_fire": ctrl_fire, "stim_end_s": STIM_END * dt}


def frac_selective(log, phase, min_s=None):
    rows = [e for e in log if e["phase"] == phase and (min_s is None or e["sim_s"] >= min_s)]
    if not rows:
        return 0.0
    sel = sum(1 for e in rows if e["stim_mean"] > 3.0 and e["ctrl_mean"] < 3.0)
    return sel / len(rows)


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 480
    print("=== G33: engineered compartment containment + selective persistent recall ===", flush=True)
    loc_wall = run_arm("LOC+wall", uniform=False, wall=True, wall_budget=budget)
    uni_wall = run_arm("UNI+wall", uniform=True, wall=True, wall_budget=budget)
    loc_nowall = run_arm("LOC-nowall", uniform=False, wall=False, wall_budget=budget)

    fire_ratio = loc_wall["stim_fire"] / max(loc_wall["ctrl_fire"], 1)
    post_min = loc_wall["stim_end_s"] + 2000
    loc_stim = frac_selective(loc_wall["log"], "STIM")
    loc_post = frac_selective(loc_wall["log"], "POST", min_s=post_min)
    uni_post = frac_selective(uni_wall["log"], "POST", min_s=post_min)
    nowall_post = frac_selective(loc_nowall["log"], "POST", min_s=post_min)

    G33a = fire_ratio >= 3.0
    G33b = loc_stim >= 0.5
    G33c = loc_post >= 0.5
    G33d = uni_post < 0.25
    G33e = nowall_post < 0.25
    passed = G33a and G33b and G33c and G33d and G33e

    print("\n--- VERDICT ---", flush=True)
    print(f"fire ratio={fire_ratio:.1f} | LOC+wall stim={loc_stim:.2f} post={loc_post:.2f} "
          f"| UNI+wall post={uni_post:.2f} | LOC-nowall post={nowall_post:.2f}", flush=True)
    print(f"G33a selective firing (>=3x)        : {G33a}", flush=True)
    print(f"G33b selective write (>=0.5)        : {G33b}", flush=True)
    print(f"G33c persistent recall (>=0.5)      : {G33c}", flush=True)
    print(f"G33d UNI+wall control fails (<0.25) : {G33d}", flush=True)
    print(f"G33e no-wall control fails (<0.25)  : {G33e}", flush=True)
    verdict = ("PASS - engineered compartment containment yields clean persistent selective "
               "recall; both controls behave") if passed else "NULL/partial"
    print(f"\nG33: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G33"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"fire_ratio": fire_ratio, "loc_stim": loc_stim, "loc_post": loc_post,
         "uni_post": uni_post, "nowall_post": nowall_post, "passed": passed,
         "loc_wall": loc_wall, "uni_wall": uni_wall, "loc_nowall": loc_nowall},
        indent=2, default=str))
    print("DONE", flush=True)
