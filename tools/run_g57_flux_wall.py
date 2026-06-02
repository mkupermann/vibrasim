"""G57 — flux-write + engineered wall for selective PERSISTENT memory. BET-096/097 flux write
achieved selective WRITE but lost it to boundary contamination of control. Add the engineered
compartment wall (mirror, around the stim region) to block transit-contamination. Flux write is
NON-neural (local flux), so the wall cannot starve it (unlike the firing write in G33/BET-103).

Pre-registered bars in docs/amendments/g57_flux_wall_memory.md.
"""
import sys, json, time
from dataclasses import replace
import numpy as np
from pathlib import Path

from world.state import World
from world.physics import tick
from tools.run_bet090 import region_mean
from tools.run_bet093 import region_flux, cull_free_vibrations
from tools._probe094_gradient import inject_confined
from tools.run_bet096 import make_cfg, blank_bridges, WARMUP, STIM_END


def run_arm(name, uniform, wall, wall_budget=260):
    cfg = make_cfg()
    object.__setattr__(cfg, 'bistable_drive_rectified', True)   # BET-097 rectified hold
    box = np.asarray(cfg.box_size)
    STIM_X, CTRL_X = box[0] * 0.25, box[0] * 0.75
    cfg = replace(cfg, bistable_drive_rectified=True, compartment_k=0.0, compartment_mode='mirror',
                  compartment_centre=(float(STIM_X), float(box[1] / 2), float(box[2] / 2)),
                  compartment_radius=6.0)
    world = World(cfg); dt = cfg.dt
    log = []
    sflux, cflux = [], []
    t0 = time.time()
    for step in range(40000):
        if step == WARMUP:
            object.__setattr__(cfg, 'lambda_gen', 0.0)
            cull_free_vibrations(world, keep_frac=0.0)
            blank_bridges(world, cfg.bistable_low)
            if wall:
                object.__setattr__(cfg, 'compartment_k', 1.0)
        if WARMUP <= step < STIM_END:
            if uniform:
                inject_confined(world, cfg, box, STIM_X, n=20, vel_scale=0.0)
                inject_confined(world, cfg, box, CTRL_X, n=20, vel_scale=0.0)
            else:
                inject_confined(world, cfg, box, STIM_X, n=40, vel_scale=0.0)
            if step % 200 == 199:
                sflux.extend(region_flux(world, cfg, STIM_X))
                cflux.extend(region_flux(world, cfg, CTRL_X))
        if step == STIM_END:
            cull_free_vibrations(world, keep_frac=0.0)
        tick(world, dt)
        if step % 1000 == 999:
            sim_s = round((step + 1) * dt, 1)
            sm, sn = region_mean(world, STIM_X)
            cm, cn = region_mean(world, CTRL_X)
            ph = ("WARM" if step < WARMUP else "STIM" if step < STIM_END else "POST")
            log.append({"sim_s": sim_s, "phase": ph, "stim_mean": round(sm, 2),
                        "ctrl_mean": round(cm, 2)})
            print(f"[{name}] {sim_s:.0f}s [{ph}]: stim={sm:.2f} ctrl={cm:.2f}", flush=True)
        if time.time() - t0 > wall_budget:
            break
    return {"name": name, "log": log, "stim_end_s": STIM_END * dt,
            "sflux": float(np.median(sflux)) if sflux else 0.0,
            "cflux": float(np.median(cflux)) if cflux else 0.0}


def selective(log, phase, min_s=None):
    rows = [e for e in log if e["phase"] == phase and (min_s is None or e["sim_s"] >= min_s)]
    return sum(1 for e in rows if e["stim_mean"] > 3.0 and e["ctrl_mean"] < 3.0) / max(len(rows), 1)


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 260
    print("=== G57: flux-write + engineered wall -> selective persistent memory? ===", flush=True)
    locw = run_arm("LOC+wall", uniform=False, wall=True, wall_budget=budget)
    uniw = run_arm("UNI+wall", uniform=True, wall=True, wall_budget=budget)
    locn = run_arm("LOC-nowall", uniform=False, wall=False, wall_budget=budget)

    pm = locw["stim_end_s"] + 2000
    loc_post = selective(locw["log"], "POST", pm)
    uni_post = selective(uniw["log"], "POST", pm)
    nowall_post = selective(locn["log"], "POST", pm)
    loc_stim = selective(locw["log"], "STIM")

    G57a = locw["sflux"] / max(locw["cflux"], 1e-6) >= 1.5
    G57b = loc_stim >= 0.5
    G57c = loc_post >= 0.5
    G57d = uni_post < 0.25
    passed = G57a and G57b and G57c and G57d

    print("\n--- VERDICT ---", flush=True)
    print(f"LOC+wall: stim-frac={loc_stim:.2f} post-frac={loc_post:.2f} | UNI+wall post={uni_post:.2f} | LOC-nowall post={nowall_post:.2f}", flush=True)
    print(f"G57a contrast (>=1.5x)        : {G57a}", flush=True)
    print(f"G57b selective latch (STIM)   : {G57b}", flush=True)
    print(f"G57c persistent recall (POST) : {G57c}", flush=True)
    print(f"G57d uniform control fails    : {G57d}", flush=True)
    verdict = ("PASS - flux-write + wall gives SELECTIVE PERSISTENT MEMORY (deadlock broken)"
               if passed else "NULL/partial - memory deadlock holds even with flux-write + wall")
    print(f"\nG57: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G57"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"locw": locw, "uniw": uniw, "locn": locn,
                                                  "loc_stim": loc_stim, "loc_post": loc_post,
                                                  "uni_post": uni_post, "nowall_post": nowall_post,
                                                  "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
