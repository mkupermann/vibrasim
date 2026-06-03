"""G93 — is the persistence blocker ATOM EROSION, not bridge-strength decay? G92 showed the
consolidated/strong engram bridges do NOT hold into POST (only ~1 of 6 survive >=5). Consolidation
re-pins bridge STRENGTH to high every tick, but only while the bridge stays ALIVE — and a bridge dies
when its anchoring atoms die. In the QUIET substrate (free vibrations culled, lambda_gen=0, no
regeneration) the engram atoms have no flux to sustain them, so decay_unstable/high_level_nodes may
erode them. Track, through POST, BOTH the engram atom set (level>=4 nodes in the stim region at
STIM_END) and the consolidated bridge set. If atom_persist falls in lockstep with bridge_persist,
atom erosion is the root and the fix is LOCALIZED maintenance (keep the engram fed while the rest of
the substrate stays quiet -> control blank).

Pre-registered bars (locked before run):
  G93a  engram atoms erode in POST   : atom_persist(horizon) < 0.6   (confirms erosion)
  G93b  bridges erode WITH atoms     : bridge_persist <= atom_persist + 0.1 (bridges track atoms)
  If both hold -> ROOT = atom erosion (mechanistic). If atoms persist but bridges die -> root is
  bridge-level (consolidation/turnover), atoms innocent.
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


def atoms_in_region(w, cx, half=HALF):
    keys = set()
    K = w.k_count
    for i in range(K):
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


def run(seed, budget=300):
    cfg = make_cfg()
    object.__setattr__(cfg, 'rng_seed', seed)
    object.__setattr__(cfg, 'compartment_boundary', 15.0)
    object.__setattr__(cfg, 'emit_speed', 6.0)
    object.__setattr__(cfg, 't_refractory', 0.5)
    object.__setattr__(cfg, 'bridge_consolidate_threshold', 4.0)
    w = World(cfg); dt = cfg.dt
    box = np.asarray(cfg.box_size); STIM_X = box[0] * 0.25
    A = B = None; series = []
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
            A = atoms_in_region(w, STIM_X); B = strong_bridges_in_region(w, STIM_X)
        tick(w, dt)
        if step > STIM_END and step % 1000 == 999 and A is not None:
            aCur = atoms_in_region(w, STIM_X); bCur = strong_bridges_in_region(w, STIM_X)
            series.append((round((step + 1) * dt, 1), len(A & aCur), len(B & bCur)))
        if time.time() - t0 > budget:
            break
    horizon = [s for s in series if s[0] >= STIM_END * dt + 2000]
    aI, bI = (horizon[-1][1], horizon[-1][2]) if horizon else (0, 0)
    lenA, lenB = len(A) if A else 0, len(B) if B else 0
    return dict(lenA=lenA, lenB=lenB, aI=aI, bI=bI,
                atom_persist=(aI / lenA if lenA else 0.0),
                bridge_persist=(bI / lenB if lenB else 0.0))


if __name__ == "__main__":
    print("=== G93: atom erosion vs bridge decay (quiet + refractory + consolidation, n=6) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: atoms |A|={R[s]['lenA']}->{R[s]['aI']} ({R[s]['atom_persist']:.2f}) | "
              f"bridges |B|={R[s]['lenB']}->{R[s]['bI']} ({R[s]['bridge_persist']:.2f})", flush=True)
    G93a = all(R[s]['atom_persist'] < 0.6 for s in seeds)
    G93b = all(R[s]['bridge_persist'] <= R[s]['atom_persist'] + 0.1 for s in seeds)
    print("\n--- VERDICT ---", flush=True)
    print(f"G93a engram atoms erode (<0.6 persist) : {G93a}", flush=True)
    print(f"G93b bridges die with atoms            : {G93b}", flush=True)
    if G93a and G93b:
        v = "ROOT CONFIRMED — persistence blocked by ATOM EROSION in the quiet substrate; fix = localized maintenance"
    elif not G93a:
        v = "atoms PERSIST — erosion is NOT the blocker; root is bridge-level (consolidation/turnover)"
    else:
        v = "atoms erode but bridges die faster — mixed; bridge-level decay also contributes"
    print(f"G93: {v}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G93"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}}, indent=2, default=str))
    print("DONE", flush=True)
