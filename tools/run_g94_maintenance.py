"""G94 — localized maintenance restores engram persistence while control stays blank?
G93 root: atom erosion in the quiet substrate. Fix under test: spatially-selective quiet — cull the
CONTROL side every POST tick (keep it blank) while feeding the STIM side a minimal maintenance flux
(n=2) so the engram atoms survive. NOMAINT arm = same but no POST feeding (engram must still die ->
maintenance is the causal ingredient, per negative-control discipline).
Bars pre-registered in docs/amendments/g94_localized_maintenance.md.
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
N_MAINT = 2
STRONG = 5.0
CTRL_CULL_X = 15.0


def cull_control_side(w, x_thresh=CTRL_CULL_X):
    n = w.config.n_vibrations_max
    alive = w.s_alive[:n]
    idx = np.where(alive & (w.s_pos[:n, 0] > x_thresh))[0]
    if len(idx):
        w.s_alive[idx] = False


def atoms_in_region(w, cx, half=HALF):
    keys = set()
    for i in range(w.k_count):
        if not w.k_alive[i] or w.k_level[i] < 4:
            continue
        if abs(w.k_pos[i][0] - cx) < half + 1.0:
            keys.add((i, round(float(w.k_birth[i]), 3)))
    return keys


def strong_bridges_in_region(w, cx, half=HALF):
    keys = set()
    for b in range(w.b_count):
        if not w.b_alive[b] or w.b_strength[b] < STRONG:
            continue
        i, j = int(w.b_atom_i[b]), int(w.b_atom_j[b])
        if i >= w.k_count or j >= w.k_count or not w.k_alive[i] or not w.k_alive[j]:
            continue
        mx = 0.5 * (w.k_pos[i][0] + w.k_pos[j][0])
        if abs(mx - cx) < half + 1.0:
            keys.add(frozenset({(i, round(float(w.k_birth[i]), 3)), (j, round(float(w.k_birth[j]), 3))}))
    return keys


def run(seed, maint, budget=300):
    cfg = make_cfg()
    object.__setattr__(cfg, 'rng_seed', seed)
    object.__setattr__(cfg, 'compartment_boundary', 15.0)
    object.__setattr__(cfg, 'emit_speed', 6.0)
    object.__setattr__(cfg, 't_refractory', 0.5)
    object.__setattr__(cfg, 'bridge_consolidate_threshold', 4.0)
    w = World(cfg); dt = cfg.dt
    box = np.asarray(cfg.box_size); STIM_X, CTRL_X = box[0] * 0.25, box[0] * 0.75
    A = Bs = None; series = []
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
            A = atoms_in_region(w, STIM_X); Bs = strong_bridges_in_region(w, STIM_X)
        if step > STIM_END:
            cull_free_vibrations(w, keep_frac=0.0)   # quiet EVERYWHERE (bounded) — control stays blank
            if maint:
                inject_tight(w, cfg, box, STIM_X, n=N_MAINT)   # tiny local maintenance pulse (bounded by the cull)
        tick(w, dt)
        if step > STIM_END and step % 1000 == 999 and A is not None:
            aCur = atoms_in_region(w, STIM_X)
            bCur = strong_bridges_in_region(w, STIM_X)
            cCur = strong_bridges_in_region(w, CTRL_X)
            series.append((round((step + 1) * dt, 1), len(A & aCur), len(Bs & bCur), len(cCur)))
        if time.time() - t0 > budget:
            break
    horizon = [s for s in series if s[0] >= STIM_END * dt + 2000]
    aI, bI, cI = (horizon[-1][1], horizon[-1][2], horizon[-1][3]) if horizon else (0, 0, 0)
    lenA, lenB = len(A) if A else 0, len(Bs) if Bs else 0
    return dict(lenA=lenA, lenB=lenB, aI=aI, bI=bI, ctrlI=cI,
                atom_persist=(aI / lenA if lenA else 0.0),
                bridge_persist=(bI / lenB if lenB else 0.0))


if __name__ == "__main__":
    print("=== G94: localized maintenance (cull control side; feed stim) ===", flush=True)
    seeds = [42, 7]
    M, NM = {}, {}
    for s in seeds:
        M[s] = run(s, maint=True)
        print(f"  [MAINT]   seed {s}: atoms {M[s]['lenA']}->{M[s]['aI']} ({M[s]['atom_persist']:.2f}) | "
              f"bridges {M[s]['lenB']}->{M[s]['bI']} ({M[s]['bridge_persist']:.2f}) | ctrl_persist={M[s]['ctrlI']}", flush=True)
    for s in seeds:
        NM[s] = run(s, maint=False)
        print(f"  [NOMAINT] seed {s}: atoms {NM[s]['lenA']}->{NM[s]['aI']} ({NM[s]['atom_persist']:.2f}) | "
              f"bridges {NM[s]['lenB']}->{NM[s]['bI']} ({NM[s]['bridge_persist']:.2f}) | ctrl_persist={NM[s]['ctrlI']}", flush=True)
    G94a = all(M[s]['atom_persist'] >= 0.6 and M[s]['bridge_persist'] >= 0.5 for s in seeds)
    G94b = all(M[s]['ctrlI'] <= 1 for s in seeds)
    G94c = all(NM[s]['bridge_persist'] < 0.3 for s in seeds)
    passed = G94a and G94b and G94c
    print("\n--- VERDICT ---", flush=True)
    print(f"G94a maintenance restores engram (atom>=0.6, bridge>=0.5): {G94a}", flush=True)
    print(f"G94b control stays blank (ctrl_persist<=1)               : {G94b}", flush=True)
    print(f"G94c engram dies without maintenance (NOMAINT bridge<0.3) : {G94c}", flush=True)
    print(("G94: PASS - localized maintenance yields a PERSISTENT, SELECTIVE engram (memory holds under local upkeep, control blank)"
           if passed else "G94: NULL/partial"), flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G94"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"MAINT": {str(s): M[s] for s in seeds},
                                                  "NOMAINT": {str(s): NM[s] for s in seeds},
                                                  "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
