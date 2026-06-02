"""G42 — close compartments + independence metric. Centres 6 apart (radius 2.5), where
emissions readily cross. Six arms {stim-A, stim-B, stim-none} x {seal, no-wall}. A
compartment is independent if its firing is unchanged by the OTHER's stimulus vs a
no-stimulus baseline. Decides whether the seal provides isolation that geometry does not.

Pre-registered bars in docs/amendments/g42_close_compartment_independence.md.
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

AX, BX = 12.0, 18.0
RAD = 2.5
HALF = 2.5


def run_arm(stim_key, wall, wall_budget=90):
    cfg = make_cfg()
    box = np.asarray(cfg.box_size)
    cy, cz = box[1] / 2, box[2] / 2
    cfg = replace(cfg, compartment_k=0.0, compartment_mode='seal',
                  compartments=((AX, cy, cz, RAD), (BX, cy, cz, RAD)))
    world = World(cfg); dt = cfg.dt
    a_fire = b_fire = 0
    t0 = time.time()
    for step in range(STIM_END + 10):
        if step == WARMUP:
            object.__setattr__(cfg, 'lambda_gen', 0.0)
            cull_free_vibrations(world, keep_frac=0.0)
            blank_bridges(world, cfg.bistable_low)
            if wall:
                object.__setattr__(cfg, 'compartment_k', 1.0)
        if WARMUP <= step < STIM_END:
            if stim_key in ("A", "both"):
                inject_tight(world, cfg, box, AX, n=40)
            if stim_key in ("B", "both"):
                inject_tight(world, cfg, box, BX, n=40)
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
        if time.time() - t0 > wall_budget:
            break
    return a_fire, b_fire


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 90
    print("=== G42: close compartments + independence metric ===", flush=True)
    res = {}
    for wall in (True, False):
        tag = "seal" if wall else "nowall"
        for stim in ("A", "B", "none"):
            a, b = run_arm(stim, wall, budget)
            res[(tag, stim)] = (a, b)
            print(f"  [{tag}] stim={stim}: A_fire={a} B_fire={b}", flush=True)

    # independence metrics
    sA_a, sA_b = res[("seal", "A")]
    sB_a, sB_b = res[("seal", "B")]
    sN_a, sN_b = res[("seal", "none")]
    nA_a, nA_b = res[("nowall", "A")]
    nB_a, nB_b = res[("nowall", "B")]
    nN_a, nN_b = res[("nowall", "none")]

    G42a = (sA_a >= 5 * max(sN_a, 1)) and (sB_b >= 5 * max(sN_b, 1))
    G42b = (sA_b <= 1.5 * max(sN_b, 1)) and (sB_a <= 1.5 * max(sN_a, 1))
    G42c = (nA_b >= 2 * max(nN_b, 1)) or (nB_a >= 2 * max(nN_a, 1))
    passed = G42a and G42b and G42c

    print("\n--- VERDICT ---", flush=True)
    print(f"seal: stimA B={sA_b} vs baseline B={sN_b} | stimB A={sB_a} vs baseline A={sN_a}", flush=True)
    print(f"nowall: stimA B={nA_b} vs baseline B={nN_b} | stimB A={nB_a} vs baseline A={nN_a}", flush=True)
    print(f"G42a own-stim activates (>=5x)        : {G42a}", flush=True)
    print(f"G42b seal independence (other<=1.5x)  : {G42b}", flush=True)
    print(f"G42c no-wall cross-talks (>=2x)       : {G42c}", flush=True)
    verdict = ("PASS - sealed close compartments are modularly INDEPENDENT where no-wall cross-talks; "
               "the engineered seal provides isolation geometry does not") if passed else "NULL/partial"
    print(f"\nG42: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G42"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"res": {f"{k[0]}_{k[1]}": v for k, v in res.items()},
         "G42a": G42a, "G42b": G42b, "G42c": G42c, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
