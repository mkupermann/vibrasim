"""G40 — modular independence: two engineered port compartments, each fires only on its
own stimulus (no cross-talk). PIVOT positive use of the robust port wall (CONCEPT §4.8).

Pre-registered bars in docs/amendments/g40_modular_independence.md.
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


def region_atoms(world, cx, half=HALF):
    K = world.k_count
    if K == 0:
        return 0
    alive = world.k_alive[:K]
    x = world.k_pos[:K, 0]
    return int((alive & (np.abs(x - cx) < half)).sum())


def run_arm(name, stim_x_key, wall, wall_budget=120):
    cfg = make_cfg()
    box = np.asarray(cfg.box_size)
    AX, BX = box[0] * 0.25, box[0] * 0.75
    stim_x = AX if stim_x_key == "A" else BX
    cfg = replace(cfg, compartment_k=0.0, compartment_mode='mirror',
                  compartments=((float(AX), float(box[1] / 2), float(box[2] / 2), 6.0),
                                (float(BX), float(box[1] / 2), float(box[2] / 2), 6.0)))
    world = World(cfg); dt = cfg.dt
    a_fire = b_fire = 0
    a_atoms_min = b_atoms_min = 10 ** 9
    t0 = time.time()
    for step in range(STIM_END + 10):
        if step == WARMUP:
            object.__setattr__(cfg, 'lambda_gen', 0.0)
            cull_free_vibrations(world, keep_frac=0.0)
            blank_bridges(world, cfg.bistable_low)
            if wall:
                object.__setattr__(cfg, 'compartment_k', 1.0)
        if WARMUP <= step < STIM_END:
            inject_tight(world, cfg, box, stim_x, n=40)
        tick(world, dt)
        if WARMUP <= step < STIM_END:
            for t_f, ai in world.firing_events:
                if t_f < world.t - dt or ai >= world.k_count or not world.k_alive[ai]:
                    continue
                x = world.k_pos[ai][0]
                if abs(x - AX) < HALF:
                    a_fire += 1
                elif abs(x - BX) < HALF:
                    b_fire += 1
            if step % 200 == 199:
                a_atoms_min = min(a_atoms_min, region_atoms(world, AX))
                b_atoms_min = min(b_atoms_min, region_atoms(world, BX))
        if time.time() - t0 > wall_budget:
            break
    print(f"[{name}] A_fire={a_fire} B_fire={b_fire} | A_atoms_min={a_atoms_min} B_atoms_min={b_atoms_min}", flush=True)
    return dict(name=name, a_fire=a_fire, b_fire=b_fire,
                a_atoms_min=a_atoms_min, b_atoms_min=b_atoms_min)


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    print("=== G40: modular independence — two engineered port compartments ===", flush=True)
    a_wall = run_arm("A-wall", "A", wall=True, wall_budget=budget)
    b_wall = run_arm("B-wall", "B", wall=True, wall_budget=budget)
    a_nowall = run_arm("A-nowall", "A", wall=False, wall_budget=budget)

    rA = a_wall["a_fire"] / max(a_wall["b_fire"], 1)
    rB = b_wall["b_fire"] / max(b_wall["a_fire"], 1)
    rNo = a_nowall["a_fire"] / max(a_nowall["b_fire"], 1)

    G40a = rA >= 10
    G40b = rB >= 10
    G40c = rNo < 3
    G40d = a_wall["a_atoms_min"] >= 3 and a_wall["b_atoms_min"] >= 3
    passed = G40a and G40b and G40c and G40d

    print("\n--- VERDICT ---", flush=True)
    print(f"A-wall A/B={rA:.1f} | B-wall B/A={rB:.1f} | A-nowall A/B={rNo:.1f}", flush=True)
    print(f"G40a A isolated (A/B>=10)        : {G40a}", flush=True)
    print(f"G40b B isolated (B/A>=10)        : {G40b}", flush=True)
    print(f"G40c no-wall cross-talk (A/B<3)  : {G40c}", flush=True)
    print(f"G40d structure survives (>=3 ea) : {G40d}", flush=True)
    verdict = ("PASS - two engineered port compartments are modularly INDEPENDENT (no cross-talk); "
               "the wall creates the independence") if passed else "NULL/partial"
    print(f"\nG40: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G40"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"a_wall": a_wall, "b_wall": b_wall, "a_nowall": a_nowall, "rA": rA, "rB": rB, "rNo": rNo,
         "G40a": G40a, "G40b": G40b, "G40c": G40c, "G40d": G40d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
