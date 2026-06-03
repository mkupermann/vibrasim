"""G96 — membrane-contained maintenance. A two-way SEALED vibration sphere around the stim engram
retains maintenance flux locally (feeds the engram atoms) AND blocks drift to control (keeps it blank
by isolation, not culling). Tests whether physical containment resolves the G94 "maintenance =
contamination" tension. NOSEAL arm = seal off (flux drifts) to isolate the seal as the cause.
Bars pre-registered in docs/amendments/g96_sealed_maintenance.md.
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
R_SEAL = 7.0


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


def run(seed, seal, budget=280):
    cfg = make_cfg()
    object.__setattr__(cfg, 'rng_seed', seed)
    object.__setattr__(cfg, 'compartment_boundary', 15.0)
    object.__setattr__(cfg, 'emit_speed', 6.0)
    object.__setattr__(cfg, 't_refractory', 0.5)
    object.__setattr__(cfg, 'bridge_consolidate_threshold', 4.0)
    box = np.asarray(cfg.box_size)
    STIM_X, CTRL_X = box[0] * 0.25, box[0] * 0.75
    if seal:
        object.__setattr__(cfg, 'compartment_centre',
                           (float(STIM_X), float(box[1] / 2), float(box[2] / 2)))
        object.__setattr__(cfg, 'compartment_radius', R_SEAL)
        object.__setattr__(cfg, 'compartment_mode', 'seal')
    w = World(cfg)
    dt = cfg.dt
    A = Bs = None
    series = []
    t0 = time.time()
    for step in range(40000):
        if step == WARMUP:
            object.__setattr__(cfg, 'lambda_gen', 0.0)
            cull_free_vibrations(w, keep_frac=0.0)
            blank_bridges(w, cfg.bistable_low)
        if WARMUP <= step < STIM_END:
            inject_tight(w, cfg, box, STIM_X, n=N_INJ)
        if step == STIM_END:
            A = atoms_in_region(w, STIM_X)
            Bs = strong_bridges_in_region(w, STIM_X)
        if step > STIM_END:
            inject_tight(w, cfg, box, STIM_X, n=N_MAINT)   # contained maintenance (seal keeps it local)
        tick(w, dt)
        if step > STIM_END and step % 1000 == 999 and A is not None:
            series.append((round((step + 1) * dt, 1),
                           len(A & atoms_in_region(w, STIM_X)),
                           len(Bs & strong_bridges_in_region(w, STIM_X)),
                           len(strong_bridges_in_region(w, CTRL_X))))
        if time.time() - t0 > budget:
            break
    horizon = [s for s in series if s[0] >= STIM_END * dt + 2000]
    aI, bI, cI = (horizon[-1][1], horizon[-1][2], horizon[-1][3]) if horizon else (0, 0, 0)
    lenA, lenB = len(A) if A else 0, len(Bs) if Bs else 0
    return dict(lenA=lenA, lenB=lenB, aI=aI, bI=bI, ctrlI=cI,
                atom_persist=(aI / lenA if lenA else 0.0),
                bridge_persist=(bI / lenB if lenB else 0.0))


if __name__ == "__main__":
    print("=== G96: membrane-contained maintenance (sealed vibration sphere around engram) ===", flush=True)
    seeds = [42, 7]
    S, NS = {}, {}
    for s in seeds:
        S[s] = run(s, seal=True)
        print(f"  [SEAL]   seed {s}: atoms {S[s]['lenA']}->{S[s]['aI']} ({S[s]['atom_persist']:.2f}) | "
              f"bridges {S[s]['lenB']}->{S[s]['bI']} ({S[s]['bridge_persist']:.2f}) | ctrl_persist={S[s]['ctrlI']}",
              flush=True)
    for s in seeds:
        NS[s] = run(s, seal=False)
        print(f"  [NOSEAL] seed {s}: atoms {NS[s]['lenA']}->{NS[s]['aI']} ({NS[s]['atom_persist']:.2f}) | "
              f"bridges {NS[s]['lenB']}->{NS[s]['bI']} ({NS[s]['bridge_persist']:.2f}) | ctrl_persist={NS[s]['ctrlI']}",
              flush=True)
    G96a = all(S[s]['atom_persist'] >= 0.6 and S[s]['bridge_persist'] >= 0.5 for s in seeds)
    G96b = all(S[s]['ctrlI'] <= 1 for s in seeds)
    G96c = all(NS[s]['ctrlI'] >= 2 for s in seeds)
    passed = G96a and G96b and G96c
    print("\n--- VERDICT ---", flush=True)
    print(f"G96a engram persists (SEAL atom>=0.6,bridge>=0.5): {G96a}", flush=True)
    print(f"G96b control blank (SEAL ctrl<=1)                : {G96b}", flush=True)
    print(f"G96c seal is the cause (NOSEAL ctrl>=2)          : {G96c}", flush=True)
    print(("G96: PASS - contained maintenance gives SELECTIVE PERSISTENT memory (persistence horn broken by isolation)"
           if passed else "G96: NULL/partial"), flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G96"
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"SEAL": {str(s): S[s] for s in seeds},
                                                  "NOSEAL": {str(s): NS[s] for s in seeds},
                                                  "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
