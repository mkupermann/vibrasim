"""G35 — wall + set-based readout = clean selective persistent recall (synthesis of
G33 containment + G34 permanent-engram set readout). Soft wall removes G33's write
-suppression confound.

Pre-registered bars in docs/amendments/g35_wall_set_recall.md.
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
from tools.run_g34_engram_set import strong_keys, STRONG


def run_arm(name, wall, wall_budget=350, seed=42):
    cfg = make_cfg()
    object.__setattr__(cfg, 'rng_seed', seed)
    box = np.asarray(cfg.box_size)
    STIM_X, CTRL_X = box[0] * 0.25, box[0] * 0.75
    cfg = replace(cfg, compartment_k=0.0, compartment_mode='soft',
                  compartment_centre=(float(STIM_X), float(box[1] / 2), float(box[2] / 2)),
                  compartment_radius=6.0)
    world = World(cfg); dt = cfg.dt
    E = C = None
    log = []
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
            print(f"[{name}] STIM end: |E|={len(E)} |C|={len(C)} |global|={len(strong_keys(world))}", flush=True)
        tick(world, dt)
        if step % 1000 == 999 and E is not None:
            sim_s = round((step + 1) * dt, 1)
            cur = strong_keys(world)
            eI, cI = len(E & cur), len(C & cur)
            log.append({"sim_s": sim_s, "eI": eI, "cI": cI, "n_strong": len(cur)})
            print(f"[{name}] {sim_s:.0f}s POST: E_persist={eI}/{len(E)} C_persist={cI}/{len(C)} n_strong={len(cur)}", flush=True)
        if time.time() - t0 > wall_budget:
            print(f"[{name}] wall budget hit at step {step}", flush=True)
            break
    return {"name": name, "wall": wall, "lenE": len(E) if E else 0, "lenC": len(C) if C else 0,
            "stim_end_s": STIM_END * dt, "log": log}


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 350
    print("=== G35: wall + set readout — selective persistent recall ===", flush=True)
    on = run_arm("LOC+soft-wall", wall=True, wall_budget=budget)
    off = run_arm("LOC-nowall", wall=False, wall_budget=budget)

    post_min = on["stim_end_s"] + 2000
    won = [e for e in on["log"] if e["sim_s"] >= post_min]
    eI_h = won[-1]["eI"] if won else 0
    cI_h = won[-1]["cI"] if won else 0

    G35a = on["lenE"] >= 3
    G35b = (eI_h / max(on["lenE"], 1)) >= 0.5
    G35c = cI_h <= 1 and (eI_h - cI_h) >= 2
    G35d = off["lenC"] >= 2
    passed = G35a and G35b and G35c and G35d

    print("\n--- VERDICT ---", flush=True)
    print(f"wall arm: |E|={on['lenE']} |C|={on['lenC']} | horizon E_persist={eI_h} C_persist={cI_h}", flush=True)
    print(f"no-wall arm: |C|={off['lenC']} (contamination baseline)", flush=True)
    print(f"G35a engram forms under wall (|E|>=3) : {G35a}", flush=True)
    print(f"G35b engram persists (>=0.5)          : {G35b}", flush=True)
    print(f"G35c selective (C<=1, E-C>=2)         : {G35c}", flush=True)
    print(f"G35d no-wall contaminates (|C|>=2)    : {G35d}", flush=True)
    verdict = ("PASS - clean selective persistent recall: write by co-firing, contain by "
               "the engineered wall, persist by the bistable well, recall by the set") if passed else "NULL/partial"
    print(f"\nG35: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G35"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"on": on, "off": off, "eI_h": eI_h, "cI_h": cI_h, "passed": passed,
         "G35a": G35a, "G35b": G35b, "G35c": G35c, "G35d": G35d}, indent=2, default=str))
    print("DONE", flush=True)
