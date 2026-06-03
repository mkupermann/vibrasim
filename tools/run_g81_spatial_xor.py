"""G81 — instantaneous SPATIAL XOR (no memory needed). Two input regions A,B driven simultaneously
per a random 2-bit input; task = XOR of the CURRENT input (not temporal). The substrate's
instantaneous nonlinearity (saturation -> interaction feature) must make XOR linearly readable from
the CURRENT state. Tests what the MEMORYLESS substrate CAN compute. Read 27-node atom-charge grid;
ridge readout; held-out balanced accuracy.

Pre-registered bars in docs/amendments/g81_spatial_xor.md.
"""
import sys, json, time
import numpy as np
from pathlib import Path
from world.state import World
from world.physics import tick
from tools.run_bet098 import inject_tight
from tools.run_bet099 import make_cfg
from tools.run_g79_substrate_reservoir import grid_state

WARMUP = 1500
N_TRIAL = 220
WIN = 8


def collect(seed):
    cfg = make_cfg()
    object.__setattr__(cfg, 'rng_seed', seed)
    w = World(cfg); box = np.asarray(cfg.box_size)
    AX, BX = box[0] * 0.25, box[0] * 0.75
    for _ in range(WARMUP):
        tick(w, cfg.dt)
    object.__setattr__(cfg, 'lambda_gen', 0.0)
    rng = np.random.default_rng(5000 + seed)
    inputs = rng.integers(0, 2, (N_TRIAL, 2))
    states = []
    t0 = time.time()
    for t in range(N_TRIAL):
        a, b = inputs[t]
        for k in range(WIN):
            if a:
                inject_tight(w, cfg, box, AX, n=12)
            if b:
                inject_tight(w, cfg, box, BX, n=12)
            tick(w, cfg.dt)
        states.append(grid_state(w, box))
        if time.time() - t0 > 600:
            inputs = inputs[:len(states)]
            break
    return inputs, np.array(states)


def evaluate(states, target, ntr):
    Xtr = np.hstack([states[:ntr], np.ones((ntr, 1))])
    Xte = np.hstack([states[ntr:], np.ones((len(states) - ntr, 1))])
    wts = np.linalg.solve(Xtr.T @ Xtr + 1.0 * np.eye(Xtr.shape[1]), Xtr.T @ (target[:ntr] - 0.5))
    pred = Xte @ wts; yte = target[ntr:]
    pos = yte > 0.5
    tpr = float(np.mean(pred[pos] > 0)) if pos.any() else 0.0
    tnr = float(np.mean(pred[~pos] <= 0)) if (~pos).any() else 0.0
    return 0.5 * (tpr + tnr)


def run(seed):
    inp, states = collect(seed)
    n = len(inp)
    xor = (inp[:, 0] ^ inp[:, 1]).astype(float)
    a_lab = inp[:, 0].astype(float)
    ntr = int(0.7 * n)
    return dict(n=n, xor_bal=evaluate(states, xor, ntr), a_bal=evaluate(states, a_lab, ntr))


if __name__ == "__main__":
    print("=== G81: instantaneous SPATIAL XOR (no memory) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s} (n={R[s]['n']}): spatial XOR balanced-acc={R[s]['xor_bal']:.2f} | single-input(A) acc={R[s]['a_bal']:.2f}", flush=True)

    G81a = all(R[s]['xor_bal'] >= 0.65 for s in seeds)
    G81b = all(R[s]['a_bal'] >= 0.65 for s in seeds)   # can it read a single input at all? (sanity)
    passed = G81a
    print("\n--- VERDICT ---", flush=True)
    print(f"G81a instantaneous spatial XOR >=0.65 (both) : {G81a}", flush=True)
    print(f"G81b single-input readable >=0.65 (sanity)   : {G81b}", flush=True)
    verdict = ("PASS - the memoryless substrate computes instantaneous spatial XOR (nonlinear classification without memory)"
               if passed else "NULL - even instantaneous spatial XOR is not linearly readable")
    print(f"\nG81: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G81"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
