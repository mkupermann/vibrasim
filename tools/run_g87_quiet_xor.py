"""G87 — instantaneous spatial XOR on a QUIET substrate, low-dim interpretable readout.
Builds on G83 (quiet substrate reads input perfectly, 1.00) and fixes its weakness (weak nonlinear
interaction + coarse grid). Read only 4 features: free-vibration count in the A-region, B-region,
and the OVERLAP region between them, plus atom count in the overlap (binding = the A*B interaction).
4 features vs ~150 samples + held-out split -> no overfitting (the G77 trap). If the overlap encodes
A*B, a linear readout solves XOR.

Pre-registered bars in docs/amendments/g87_quiet_xor.md.
"""
import sys, json, time
from dataclasses import replace
import numpy as np
from pathlib import Path
from world.state import World
from world.physics import tick
from tools.run_bet098 import inject_tight
from tools.run_bet093 import cull_free_vibrations
from tools.run_g43_protocell import cfg as protocfg

SETTLE = 200
N_TRIAL = 240
WIN = 8
AX, BX, MX = 9.0, 13.0, 11.0   # A, B, overlap-middle (close so they interact)


def region_feats(w, box):
    n = w.s_pos.shape[0]
    alive = w.s_alive[:n]
    x = w.s_pos[:n, 0][alive]
    va = float(((x > AX - 2) & (x < AX + 2)).sum())
    vb = float(((x > BX - 2) & (x < BX + 2)).sum())
    vm = float(((x > MX - 1.5) & (x < MX + 1.5)).sum())
    K = w.k_count
    am = 0.0
    if K:
        ka = w.k_alive[:K] & (w.k_level[:K] >= 4)
        kx = w.k_pos[:K, 0]
        am = float((ka & (np.abs(kx - MX) < 2)).sum())
    return np.array([va, vb, vm, am])


def collect(seed):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c); box = np.asarray(c.box_size)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    cull_free_vibrations(w, keep_frac=0.0)
    rng = np.random.default_rng(8700 + seed)
    inputs = rng.integers(0, 2, (N_TRIAL, 2))
    states = []
    t0 = time.time()
    for t in range(N_TRIAL):
        a, b = inputs[t]
        for k in range(WIN):
            if a:
                inject_tight(w, c, box, AX, n=14)
            if b:
                inject_tight(w, c, box, BX, n=14)
            tick(w, c.dt)
        states.append(region_feats(w, box))
        cull_free_vibrations(w, keep_frac=0.0)
        if time.time() - t0 > 600:
            inputs = inputs[:len(states)]; break
    return inputs, np.array(states)


def evaluate(states, target, ntr):
    Xtr = np.hstack([states[:ntr], np.ones((ntr, 1))])
    Xte = np.hstack([states[ntr:], np.ones((len(states) - ntr, 1))])
    wts = np.linalg.solve(Xtr.T @ Xtr + 0.5 * np.eye(Xtr.shape[1]), Xtr.T @ (target[:ntr] - 0.5))
    pred = Xte @ wts; yte = target[ntr:]
    pos = yte > 0.5
    tpr = float(np.mean(pred[pos] > 0)) if pos.any() else 0.0
    tnr = float(np.mean(pred[~pos] <= 0)) if (~pos).any() else 0.0
    return 0.5 * (tpr + tnr)


def run(seed):
    inp, states = collect(seed)
    n = len(inp); ntr = int(0.7 * n)
    xor = (inp[:, 0] ^ inp[:, 1]).astype(float)
    a_lab = inp[:, 0].astype(float)
    return dict(n=n, xor_bal=evaluate(states, xor, ntr), a_bal=evaluate(states, a_lab, ntr))


if __name__ == "__main__":
    print("=== G87: instantaneous spatial XOR on a quiet substrate (low-dim readout) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s} (n={R[s]['n']}): single-input(A)={R[s]['a_bal']:.2f} | spatial XOR={R[s]['xor_bal']:.2f}", flush=True)
    sanity = all(R[s]['a_bal'] >= 0.70 for s in seeds)
    G87a = all(R[s]['xor_bal'] >= 0.70 for s in seeds)
    print("\n--- VERDICT ---", flush=True)
    print(f"sanity single-input readable (>=0.70): {sanity}", flush=True)
    print(f"G87a spatial XOR (>=0.70 both)        : {G87a}", flush=True)
    if G87a:
        v = "PASS - the quiet substrate computes instantaneous spatial XOR (nonlinear multi-input logic)"
    elif sanity:
        v = "NULL - inputs readable but no nonlinear interaction (linear-only spatial computation)"
    else:
        v = "INCONCLUSIVE - sanity failed"
    print(f"G87: {v}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G87"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "sanity": sanity, "passed": G87a}, indent=2, default=str))
    print("DONE", flush=True)
