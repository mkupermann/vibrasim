"""G41 — sealed two-way compartments. Same as G40 but compartment_mode='seal' (reflect
inbound-from-outside AND outbound-from-inside), correcting the one-way valve flaw.

Pre-registered bars in docs/amendments/g41_sealed_modular.md.
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
from tools.run_g40_modular import region_atoms


def run_arm(name, stim_x_key, wall, mode, wall_budget=120):
    cfg = make_cfg()
    box = np.asarray(cfg.box_size)
    AX, BX = box[0] * 0.25, box[0] * 0.75
    stim_x = AX if stim_x_key == "A" else BX
    cfg = replace(cfg, compartment_k=0.0, compartment_mode=mode,
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
    return dict(name=name, a_fire=a_fire, b_fire=b_fire, a_atoms_min=a_atoms_min, b_atoms_min=b_atoms_min)


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    print("=== G41: sealed two-way compartments — modular independence ===", flush=True)
    a_seal = run_arm("A-seal", "A", wall=True, mode='seal', wall_budget=budget)
    b_seal = run_arm("B-seal", "B", wall=True, mode='seal', wall_budget=budget)
    a_nowall = run_arm("A-nowall", "A", wall=False, mode='seal', wall_budget=budget)

    rA = a_seal["a_fire"] / max(a_seal["b_fire"], 1)
    rB = b_seal["b_fire"] / max(b_seal["a_fire"], 1)
    rNo = a_nowall["a_fire"] / max(a_nowall["b_fire"], 1)

    G41a = rA >= 10
    G41b = rB >= 10
    G41c = rNo < 3
    G41d = a_seal["a_atoms_min"] >= 3 and a_seal["b_atoms_min"] >= 3
    passed = G41a and G41b and G41c and G41d

    print("\n--- VERDICT ---", flush=True)
    print(f"A-seal A/B={rA:.1f} | B-seal B/A={rB:.1f} | A-nowall A/B={rNo:.1f}", flush=True)
    print(f"G41a A isolated (A/B>=10)        : {G41a}", flush=True)
    print(f"G41b B isolated (B/A>=10)        : {G41b}", flush=True)
    print(f"G41c no-wall cross-talk (A/B<3)  : {G41c}", flush=True)
    print(f"G41d structure survives (>=3 ea) : {G41d}", flush=True)
    verdict = ("PASS - sealed engineered compartments are modularly INDEPENDENT (no cross-talk)"
               ) if passed else "NULL/partial"
    print(f"\nG41: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G41"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"a_seal": a_seal, "b_seal": b_seal, "a_nowall": a_nowall, "rA": rA, "rB": rB, "rNo": rNo,
         "G41a": G41a, "G41b": G41b, "G41c": G41c, "G41d": G41d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
