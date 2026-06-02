"""G37 — specular mirror wall (r -> 2R-r) + set readout. Contains without pinning, so the
interior co-firing field survives. Does it write AND contain? Identical to G36 except
compartment_mode='mirror'.

Pre-registered bars in docs/amendments/g37_mirror_wall_recall.md.
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


def run(wall_budget=320, seed=42):
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
            inject_tight(world, cfg, box, STIM_X, n=40)
        if step == STIM_END:
            cull_free_vibrations(world, keep_frac=0.0)
            E = strong_keys(world, STIM_X)
            C = strong_keys(world, CTRL_X)
            print(f"[G37] STIM end: |E|={len(E)} |C|={len(C)} |global|={len(strong_keys(world))} "
                  f"fire stim={stim_fire} ctrl={ctrl_fire}", flush=True)
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
            sim_s = round((step + 1) * dt, 1)
            cur = strong_keys(world)
            eI, cI = len(E & cur), len(C & cur)
            log.append({"sim_s": sim_s, "eI": eI, "cI": cI, "n_strong": len(cur)})
            print(f"[G37] {sim_s:.0f}s POST: E_persist={eI}/{len(E)} C_persist={cI}/{len(C)} n_strong={len(cur)}", flush=True)
        if time.time() - t0 > wall_budget:
            print(f"[G37] wall budget hit at step {step}", flush=True)
            break
    return {"lenE": len(E) if E else 0, "lenC": len(C) if C else 0,
            "stim_fire": stim_fire, "ctrl_fire": ctrl_fire,
            "stim_end_s": STIM_END * dt, "log": log}


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 320
    print("=== G37: specular mirror wall + set readout ===", flush=True)
    res = run(wall_budget=budget)
    post_min = res["stim_end_s"] + 2000
    win = [e for e in res["log"] if e["sim_s"] >= post_min]
    eI_h = win[-1]["eI"] if win else 0
    cI_h = win[-1]["cI"] if win else 0
    fire_ratio = res["stim_fire"] / max(res["ctrl_fire"], 1)

    G37a = res["lenE"] >= 1
    G37b = (eI_h / max(res["lenE"], 1)) >= 0.5
    G37c = cI_h <= 1 and (eI_h - cI_h) >= 1
    G37d = fire_ratio >= 10.0
    passed = G37a and G37b and G37c and G37d

    print("\n--- VERDICT ---", flush=True)
    print(f"|E|={res['lenE']} |C|={res['lenC']} | horizon E_persist={eI_h} C_persist={cI_h} "
          f"| fire ratio={fire_ratio:.1f}", flush=True)
    print(f"G37a engram forms (|E|>=1)        : {G37a}", flush=True)
    print(f"G37b engram persists (>=0.5)      : {G37b}", flush=True)
    print(f"G37c selective (C<=1, E-C>=1)     : {G37c}", flush=True)
    print(f"G37d containment active (>=10x)   : {G37d}", flush=True)
    verdict = ("PASS - clean selective persistent recall via specular mirror wall + set readout; "
               "the write/contain tension was a degenerate-reflection artifact") if passed else "NULL/partial"
    print(f"\nG37: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G37"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"res": res, "eI_h": eI_h, "cI_h": cI_h, "fire_ratio": fire_ratio, "passed": passed,
         "G37a": G37a, "G37b": G37b, "G37c": G37c, "G37d": G37d}, indent=2, default=str))
    print("DONE", flush=True)
