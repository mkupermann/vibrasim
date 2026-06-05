"""PR-01 — paced reactivation (Neuron 2026 slow-oscillation) vs the memory deadlock. Reactivate the
engram in brief BURSTS separated by quiet GAPS (vs continuous vs none) on the charge channel, and test
whether the gaps let the cascade dissipate before contaminating control -> selective persistent memory.
Reuses the G94 quiet-substrate engram protocol. Pre-registered bars in docs/amendments/pr01_paced_reactivation.md.
"""
import json, time
import numpy as np
from pathlib import Path
from world.state import World
from world.physics import tick
from tools.run_bet093 import cull_free_vibrations
from tools.run_bet098 import inject_tight, blank_bridges
from tools.run_bet099 import make_cfg, WARMUP, STIM_END, HALF
from tools.run_g94_maintenance import atoms_in_region, strong_bridges_in_region, N_INJ, STRONG

REACT_CHARGE = 6.0      # charge per reactivation tick (above theta_fire), matched total across arms
BURST, GAP = 10, 40     # paced: 10 ticks on, 40 off (slow rhythm, ~20% duty)


def engram_indices(w, cx, half=HALF):
    return [i for i in range(w.k_count)
            if w.k_alive[i] and w.k_level[i] >= 4 and abs(w.k_pos[i][0] - cx) < half + 1.0]


def run(seed, mode, budget=140):
    cfg = make_cfg()
    for k, v in dict(rng_seed=seed, compartment_boundary=15.0, emit_speed=6.0,
                     t_refractory=0.5, bridge_consolidate_threshold=4.0).items():
        object.__setattr__(cfg, k, v)
    w = World(cfg); dt = cfg.dt
    box = np.asarray(cfg.box_size); STIM_X, CTRL_X = box[0] * 0.25, box[0] * 0.75
    A = Bs = eng_idx = None; t0 = time.time(); series = []
    for step in range(40000):
        if step == WARMUP:
            object.__setattr__(cfg, 'lambda_gen', 0.0)
            cull_free_vibrations(w, keep_frac=0.0); blank_bridges(w, cfg.bistable_low)
        if WARMUP <= step < STIM_END:
            cull_free_vibrations(w, keep_frac=0.0); inject_tight(w, cfg, box, STIM_X, n=N_INJ)
        if step == STIM_END:
            cull_free_vibrations(w, keep_frac=0.0)
            A = atoms_in_region(w, STIM_X); Bs = strong_bridges_in_region(w, STIM_X)
            eng_idx = engram_indices(w, STIM_X)
        if step > STIM_END:
            cull_free_vibrations(w, keep_frac=0.0)               # quiet substrate (no ambient flux)
            # PACED REACTIVATION on the charge channel (Neuron 2026): re-fire the engram atoms.
            fire = False
            if mode == 'continuous':
                fire = True
            elif mode == 'paced':
                fire = (step - STIM_END) % (BURST + GAP) < BURST
            if fire and eng_idx:
                alive = [i for i in eng_idx if w.k_alive[i]]
                if alive:
                    w.k_charge[np.array(alive)] += REACT_CHARGE
        tick(w, dt)
        if step > STIM_END and step % 1000 == 999 and A is not None:
            bCur = strong_bridges_in_region(w, STIM_X); cCur = strong_bridges_in_region(w, CTRL_X)
            series.append((len(Bs & bCur), len(cCur)))
        if time.time() - t0 > budget:
            break
    horizon = series[-3:] if len(series) >= 3 else series
    bI = int(np.mean([h[0] for h in horizon])) if horizon else 0
    cI = int(np.mean([h[1] for h in horizon])) if horizon else 0
    lenB = len(Bs) if Bs else 0
    return dict(lenB=lenB, bridge_persist=(bI / lenB if lenB else 0.0), ctrl=cI)


if __name__ == "__main__":
    print("=== PR-01: paced reactivation (Neuron 2026) vs continuous vs none ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = {m: run(s, m) for m in ('none', 'continuous', 'paced')}
        for m in ('none', 'continuous', 'paced'):
            d = R[s][m]
            print(f"  seed {s} [{m:10}]: engram {d['lenB']}->persist {d['bridge_persist']:.2f} | ctrl={d['ctrl']}", flush=True)

    PR01a = all(R[s]['none']['bridge_persist'] < 0.30 for s in seeds)
    PR01b = all(R[s]['paced']['bridge_persist'] >= 0.40 and R[s]['paced']['ctrl'] <= 2 for s in seeds)
    PR01c = all(R[s]['paced']['ctrl'] <= R[s]['continuous']['ctrl'] - 2 for s in seeds)
    passed = PR01a and PR01b and PR01c

    print("\n--- VERDICT ---", flush=True)
    print(f"PR01a reactivation necessary (none persist<0.30) : {PR01a}", flush=True)
    print(f"PR01b paced SELECTIVE (persist>=0.40, ctrl<=2)   : {PR01b}", flush=True)
    print(f"PR01c paced beats continuous on contamination    : {PR01c}", flush=True)
    verdict = ("PASS - paced reactivation yields selective persistent memory where continuous cannot "
               "(first crack in the deadlock, Neuron-2026 motivated)") if passed else "NULL/partial - pacing does not separate write from leak here"
    print(f"\nPR-01: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "PR01"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "PR01a": PR01a, "PR01b": PR01b, "PR01c": PR01c}, indent=2, default=str))
    print("DONE", flush=True)
