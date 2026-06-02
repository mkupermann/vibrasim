"""G34 — set-based engram readout. Does the SPECIFIC set of bridges potentiated during
STIM physically persist (turnover-robust), selectively vs the unstimulated control region
and vs a random null set? Replaces the region-mean readout that G33 showed is drowned in
turnover noise.

Pre-registered bars in docs/amendments/g34_engram_set_readout.md.
"""
import sys, json, time
import numpy as np
from pathlib import Path

from world.state import World
from world.physics import tick
from tools.run_bet093 import cull_free_vibrations
from tools.run_bet098 import inject_tight, blank_bridges
from tools.run_bet099 import make_cfg, WARMUP, STIM_END, HALF

STRONG = 5.0


def bridge_key(world, b):
    i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
    bi, bj = round(float(world.k_birth[i]), 3), round(float(world.k_birth[j]), 3)
    a, c = (i, bi), (j, bj)
    return frozenset((a, c))


def strong_keys(world, region_x=None, half=HALF):
    """Keys of alive strong bridges; if region_x given, both atoms must lie in that x-band."""
    keys = set()
    for b in range(world.b_count):
        if not world.b_alive[b] or world.b_strength[b] < STRONG:
            continue
        i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
        if i >= world.k_count or j >= world.k_count or not world.k_alive[i] or not world.k_alive[j]:
            continue
        if region_x is not None:
            if not (abs(world.k_pos[i][0] - region_x) < half and abs(world.k_pos[j][0] - region_x) < half):
                continue
        keys.add(bridge_key(world, b))
    return keys


def run(wall_budget=400, seed=42):
    cfg = make_cfg()
    object.__setattr__(cfg, 'rng_seed', seed)
    world = World(cfg); dt = cfg.dt
    box = np.asarray(cfg.box_size)
    STIM_X, CTRL_X = box[0] * 0.25, box[0] * 0.75
    rng = np.random.default_rng(seed)

    E = C = R = None
    log = []
    t0 = time.time()
    for step in range(40000):
        if step == WARMUP:
            object.__setattr__(cfg, 'lambda_gen', 0.0)
            cull_free_vibrations(world, keep_frac=0.0)
            blank_bridges(world, cfg.bistable_low)
        if WARMUP <= step < STIM_END:
            inject_tight(world, cfg, box, STIM_X, n=40)
        if step == STIM_END:
            cull_free_vibrations(world, keep_frac=0.0)
            E = strong_keys(world, STIM_X)
            C = strong_keys(world, CTRL_X)
            glob = list(strong_keys(world))
            extra = [k for k in glob if k not in E]
            k = min(len(E), len(extra))
            R = set(rng.permutation(np.array(extra, dtype=object))[:k].tolist()) if k > 0 else set()
            print(f"[G34] STIM end: |E|={len(E)} |C|={len(C)} |global_strong|={len(glob)} |R|={len(R)}", flush=True)
        tick(world, dt)
        if step % 1000 == 999 and E is not None:
            sim_s = round((step + 1) * dt, 1)
            cur = strong_keys(world)
            retE = len(E & cur) / max(len(E), 1)
            retC = len(C & cur) / max(len(C), 1) if C else 0.0
            retR = len(R & cur) / max(len(R), 1) if R else 0.0
            log.append({"sim_s": sim_s, "retE": round(retE, 3), "retC": round(retC, 3),
                        "retR": round(retR, 3), "n_strong": len(cur)})
            print(f"[G34] {sim_s:.0f}s POST: retE={retE:.2f} retC={retC:.2f} retR={retR:.2f} n_strong={len(cur)}", flush=True)
        if time.time() - t0 > wall_budget:
            print(f"[G34] wall budget hit at step {step}", flush=True)
            break
    return {"lenE": len(E) if E else 0, "lenC": len(C) if C else 0, "lenR": len(R) if R else 0,
            "stim_end_s": STIM_END * dt, "log": log}


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    print("=== G34: set-based engram persistence readout ===", flush=True)
    res = run(wall_budget=budget)
    post_min = res["stim_end_s"] + 2000
    win = [e for e in res["log"] if e["sim_s"] >= post_min]
    if win:
        retE_h = win[-1]["retE"]; retR_h = win[-1]["retR"]
        meanE = float(np.mean([e["retE"] for e in win]))
        meanC = float(np.mean([e["retC"] for e in win]))
    else:
        retE_h = retR_h = meanE = meanC = 0.0

    G34a = res["lenE"] >= 5
    G34b = retE_h >= 0.5
    G34c = (meanE - meanC) >= 0.3
    G34d = retE_h >= 2 * retR_h and retE_h > 0
    passed = G34a and G34b and G34c and G34d

    print("\n--- VERDICT ---", flush=True)
    print(f"|E|={res['lenE']} | retE(horizon)={retE_h:.2f} retR(horizon)={retR_h:.2f} "
          f"| meanE={meanE:.2f} meanC={meanC:.2f} (POST window, {len(win)} checkpoints)", flush=True)
    print(f"G34a engram forms (|E|>=5)        : {G34a}", flush=True)
    print(f"G34b engram persists (retE>=0.5)  : {G34b}", flush=True)
    print(f"G34c selective (E-C>=0.3)         : {G34c}", flush=True)
    print(f"G34d beats null (E>=2R)           : {G34d}", flush=True)
    verdict = ("PASS - the engram is a persistent, selectively-readable physical structure; "
               "earlier recall failure was a region-mean readout artifact") if passed else "NULL/partial"
    print(f"\nG34: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G34"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"res": res, "retE_h": retE_h, "retR_h": retR_h, "meanE": meanE, "meanC": meanC,
         "passed": passed, "G34a": G34a, "G34b": G34b, "G34c": G34c, "G34d": G34d},
        indent=2, default=str))
    print("DONE", flush=True)
