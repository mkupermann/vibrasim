"""ER-02 — freeze constituent turnover at consolidation and test whether a STATIC engram persists by
IDENTITY in a quiet substrate without contaminating control (the structural-fix test for the memory
deadlock). Reuses the G94 quiet-substrate protocol. Pre-registered bars in docs/amendments/er02_static_engram.md.
"""
import json, time
import numpy as np
from pathlib import Path
from world.state import World
from world.physics import tick
from tools.run_bet093 import cull_free_vibrations
from tools.run_bet098 import inject_tight, blank_bridges
from tools.run_bet099 import make_cfg, WARMUP, STIM_END, HALF
from tools.run_g94_maintenance import atoms_in_region, strong_bridges_in_region, N_INJ


def run(seed, frozen, budget=140):
    cfg = make_cfg()
    for k, v in dict(rng_seed=seed, compartment_boundary=15.0, emit_speed=6.0,
                     t_refractory=0.5, bridge_consolidate_threshold=4.0).items():
        object.__setattr__(cfg, k, v)
    w = World(cfg); dt = cfg.dt
    box = np.asarray(cfg.box_size); STIM_X, CTRL_X = box[0] * 0.25, box[0] * 0.75
    A = Bs = None; t0 = time.time(); series = []
    for step in range(40000):
        if step == WARMUP:
            object.__setattr__(cfg, 'lambda_gen', 0.0)
            cull_free_vibrations(w, keep_frac=0.0); blank_bridges(w, cfg.bistable_low)
        if WARMUP <= step < STIM_END:
            cull_free_vibrations(w, keep_frac=0.0); inject_tight(w, cfg, box, STIM_X, n=N_INJ)
        if step == STIM_END:
            cull_free_vibrations(w, keep_frac=0.0)
            A = atoms_in_region(w, STIM_X); Bs = strong_bridges_in_region(w, STIM_X)
            if frozen:                                  # consolidate by FREEZING turnover
                object.__setattr__(cfg, 'pair_decay_time', 1e9)
                object.__setattr__(cfg, 'triad_decay_time', 1e9)
        if step > STIM_END:
            cull_free_vibrations(w, keep_frac=0.0)
        tick(w, dt)
        if step > STIM_END and step % 1000 == 999 and A is not None:
            aCur = atoms_in_region(w, STIM_X); bCur = strong_bridges_in_region(w, STIM_X)
            cCur = strong_bridges_in_region(w, CTRL_X)
            series.append((len(A & aCur), len(Bs & bCur), len(cCur)))
        if time.time() - t0 > budget:
            break
    hz = series[-3:] if len(series) >= 3 else series
    aI = int(np.mean([h[0] for h in hz])) if hz else 0
    bI = int(np.mean([h[1] for h in hz])) if hz else 0
    cI = int(np.mean([h[2] for h in hz])) if hz else 0
    lenA, lenB = len(A) if A else 0, len(Bs) if Bs else 0
    return dict(lenA=lenA, lenB=lenB, atom_persist=(aI / lenA if lenA else 0.0),
                bridge_persist=(bI / lenB if lenB else 0.0), ctrl=cI)


if __name__ == "__main__":
    print("=== ER-02: static engram (freeze turnover at consolidation) vs default ===", flush=True)
    seeds = [42, 7]
    D, F = {}, {}
    for s in seeds:
        D[s] = run(s, frozen=False)
        F[s] = run(s, frozen=True)
        print(f"  seed {s}: DEFAULT atom_persist={D[s]['atom_persist']:.2f} bridge={D[s]['bridge_persist']:.2f} ctrl={D[s]['ctrl']} | "
              f"FROZEN atom_persist={F[s]['atom_persist']:.2f} bridge={F[s]['bridge_persist']:.2f} ctrl={F[s]['ctrl']}", flush=True)

    ER02a = all(F[s]['atom_persist'] >= 0.70 for s in seeds)
    ER02b = all(F[s]['bridge_persist'] >= 0.40 and F[s]['ctrl'] <= 2 for s in seeds)
    ER02c = all(F[s]['atom_persist'] - D[s]['atom_persist'] >= 0.30 for s in seeds)
    passed = ER02a and ER02b and ER02c

    print("\n--- VERDICT ---", flush=True)
    print(f"ER02a frozen preserves atom identity (>=0.70) : {ER02a}", flush=True)
    print(f"ER02b SELECTIVE persistent recall (br>=0.4,ctrl<=2): {ER02b}", flush=True)
    print(f"ER02c frozen beats default (atom +0.30)       : {ER02c}", flush=True)
    verdict = ("PASS - freezing turnover at consolidation yields a persistent SELECTIVE engram in a quiet "
               "substrate: the deadlock cracked at its turnover root") if passed else "NULL/partial - turnover freeze does not give selective persistence"
    print(f"\nER-02: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "ER02"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"default": {str(s): D[s] for s in seeds},
                                                  "frozen": {str(s): F[s] for s in seeds}, "passed": passed,
                                                  "ER02a": ER02a, "ER02b": ER02b, "ER02c": ER02c}, indent=2, default=str))
    print("DONE", flush=True)
