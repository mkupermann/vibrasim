"""G92 — read the engram with the SET metric (not region-mean). G91: quiet + disconnected +
refractory + consolidation gives a STRONG selective write (stim-frac 0.83) and BLANK control
(uni-post 0.00), but recall caps at 0.44 -- the recurring plateau = the G34 region-mean artifact
(weak bridges dilute the region mean even though the consolidated engram is permanent). Read the
SET of strong bridges (>=5.0) in the stim vs control region, tracked into POST. With control blank,
the set readout should reveal clean selective persistent memory.
"""
import sys, json, time
import numpy as np
from pathlib import Path
from world.state import World
from world.physics import tick
from tools.run_bet093 import cull_free_vibrations
from tools.run_bet098 import inject_tight, blank_bridges
from tools.run_bet099 import make_cfg, WARMUP, STIM_END, HALF

N_INJ = 6
STRONG = 5.0


def strong_in_region(w, cx, half=HALF):
    keys = set()
    for b in range(w.b_count):
        if not w.b_alive[b] or w.b_strength[b] < STRONG:
            continue
        i, j = int(w.b_atom_i[b]), int(w.b_atom_j[b])
        if i >= w.k_count or j >= w.k_count or not w.k_alive[i] or not w.k_alive[j]:
            continue
        mx = 0.5 * (w.k_pos[i][0] + w.k_pos[j][0])
        if abs(mx - cx) < half + 1.0:
            bi, bj = round(float(w.k_birth[i]), 3), round(float(w.k_birth[j]), 3)
            keys.add(frozenset({(i, bi), (j, bj)}))
    return keys


def run(seed, budget=300):
    cfg = make_cfg()
    object.__setattr__(cfg, 'rng_seed', seed)
    object.__setattr__(cfg, 'compartment_boundary', 15.0)
    object.__setattr__(cfg, 'emit_speed', 6.0)
    object.__setattr__(cfg, 't_refractory', 0.5)
    object.__setattr__(cfg, 'bridge_consolidate_threshold', 4.0)
    w = World(cfg); dt = cfg.dt
    box = np.asarray(cfg.box_size); STIM_X, CTRL_X = box[0] * 0.25, box[0] * 0.75
    E = C = None; series = []
    t0 = time.time()
    for step in range(40000):
        if step == WARMUP:
            object.__setattr__(cfg, 'lambda_gen', 0.0)
            cull_free_vibrations(w, keep_frac=0.0); blank_bridges(w, cfg.bistable_low)
        if WARMUP <= step < STIM_END:
            cull_free_vibrations(w, keep_frac=0.0)
            inject_tight(w, cfg, box, STIM_X, n=N_INJ)
        if step == STIM_END:
            cull_free_vibrations(w, keep_frac=0.0)
            E = strong_in_region(w, STIM_X); C = strong_in_region(w, CTRL_X)
        tick(w, dt)
        if step > STIM_END and step % 1000 == 999 and E is not None:
            cur = strong_in_region(w, STIM_X) | strong_in_region(w, CTRL_X)
            series.append((round((step + 1) * dt, 1), len(E & cur), len(C & cur)))
        if time.time() - t0 > budget:
            break
    horizon = [s for s in series if s[0] >= STIM_END * dt + 2000]
    eI, cI = (horizon[-1][1], horizon[-1][2]) if horizon else (0, 0)
    return dict(lenE=len(E) if E else 0, lenC=len(C) if C else 0, eI=eI, cI=cI)


if __name__ == "__main__":
    print("=== G92: set-based readout (quiet + refractory + consolidation, n=6) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: |E(stim)|={R[s]['lenE']} |C(ctrl)|={R[s]['lenC']} | horizon E_persist={R[s]['eI']} C_persist={R[s]['cI']}", flush=True)
    G92a = all(R[s]['lenE'] >= 3 for s in seeds)
    G92b = all(R[s]['eI'] >= max(1, 0.5 * R[s]['lenE']) for s in seeds)
    G92c = all(R[s]['cI'] <= 1 and (R[s]['eI'] - R[s]['cI']) >= 2 for s in seeds)
    passed = G92a and G92b and G92c
    print("\n--- VERDICT ---", flush=True)
    print(f"G92a stim engram forms (|E|>=3)   : {G92a}", flush=True)
    print(f"G92b engram persists (>=0.5)      : {G92b}", flush=True)
    print(f"G92c selective (C<=1, E-C>=2)     : {G92c}", flush=True)
    print(("G92: PASS - SELECTIVE PERSISTENT MEMORY (set readout; deadlock BROKEN)" if passed else "G92: NULL/partial"), flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G92"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
