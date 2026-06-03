"""G97 — spatial channel capacity of the quiet substrate (real-time linear MIMO readout).
Two input channels at x = centre +/- d/2. Independent random bits per channel; inject iff bit=1.
Linear ridge decoder per channel on a held-out split; report per-channel balanced accuracy and
crosstalk. Sweep separation d to find the minimum pitch at which both channels stay separable.
Bars pre-registered in docs/amendments/g97_channel_capacity.md.
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
N_TRIAL = 260
WIN = 8
NBINS = 10           # fine grid along x to resolve channels
SEPARATIONS = [12.0, 8.0, 5.0, 3.0]


def vib_grid_x(w, box):
    n = w.s_pos.shape[0]
    alive = w.s_alive[:n]
    x = w.s_pos[:n, 0][alive]
    if len(x) == 0:
        return np.zeros(NBINS)
    idx = np.clip((x / box[0] * NBINS).astype(int), 0, NBINS - 1)
    return np.bincount(idx, minlength=NBINS).astype(float)


def collect(seed, d, centre):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    box = np.asarray(c.box_size)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    cull_free_vibrations(w, keep_frac=0.0)
    AX, BX = centre - d / 2, centre + d / 2
    rng = np.random.default_rng(9700 + seed + int(d * 10))
    inputs = rng.integers(0, 2, (N_TRIAL, 2))
    states = []
    t0 = time.time()
    for t in range(N_TRIAL):
        a, b = inputs[t]
        for _ in range(WIN):
            if a:
                inject_tight(w, c, box, AX, n=14)
            if b:
                inject_tight(w, c, box, BX, n=14)
            tick(w, c.dt)
        states.append(vib_grid_x(w, box))
        cull_free_vibrations(w, keep_frac=0.0)
        if time.time() - t0 > 240:
            inputs = inputs[:len(states)]
            break
    return inputs, np.array(states)


def decode(states, target, ntr):
    Xtr = np.hstack([states[:ntr], np.ones((ntr, 1))])
    Xte = np.hstack([states[ntr:], np.ones((len(states) - ntr, 1))])
    wts = np.linalg.solve(Xtr.T @ Xtr + 1.0 * np.eye(Xtr.shape[1]), Xtr.T @ (target[:ntr] - 0.5))
    pred = Xte @ wts
    yte = target[ntr:]
    pos = yte > 0.5
    tpr = float(np.mean(pred[pos] > 0)) if pos.any() else 0.0
    tnr = float(np.mean(pred[~pos] <= 0)) if (~pos).any() else 0.0
    return 0.5 * (tpr + tnr), pred, yte


def run_sep(seed, d, centre):
    inp, states = collect(seed, d, centre)
    n = len(inp)
    ntr = int(0.7 * n)
    a, b = inp[:, 0].astype(float), inp[:, 1].astype(float)
    accA, _, _ = decode(states, a, ntr)
    accB, _, _ = decode(states, b, ntr)
    # crosstalk: decoder trained on A, evaluated against B (how much A-state leaks B)
    Xtr = np.hstack([states[:ntr], np.ones((ntr, 1))])
    Xte = np.hstack([states[ntr:], np.ones((n - ntr, 1))])
    wA = np.linalg.solve(Xtr.T @ Xtr + 1.0 * np.eye(Xtr.shape[1]), Xtr.T @ (a[:ntr] - 0.5))
    predA = Xte @ wA
    bte = b[ntr:]
    posb = bte > 0.5
    xtalk = 0.5 * ((np.mean(predA[posb] > 0) if posb.any() else 0.0) +
                   (np.mean(predA[~posb] <= 0) if (~posb).any() else 0.0))
    return dict(n=n, accA=accA, accB=accB, crosstalk=xtalk)


if __name__ == "__main__":
    print("=== G97: spatial channel capacity (quiet substrate, linear MIMO readout) ===", flush=True)
    seeds = [42, 7]
    centre = 15.0
    R = {s: {} for s in seeds}
    for s in seeds:
        for d in SEPARATIONS:
            r = run_sep(s, d, centre)
            R[s][d] = r
            print(f"  seed {s} d={d:>4}: accA={r['accA']:.2f} accB={r['accB']:.2f} crosstalk={r['crosstalk']:.2f} (n={r['n']})", flush=True)

    def ok(s, d):
        r = R[s][d]
        return r['accA'] >= 0.85 and r['accB'] >= 0.85 and r['crosstalk'] <= 0.60

    G97a = all(ok(s, 12.0) for s in seeds)
    min_d = None
    for d in sorted(SEPARATIONS):           # ascending -> smallest that works on both seeds
        if all(ok(s, d) for s in seeds):
            min_d = d
            break
    print("\n--- VERDICT ---", flush=True)
    print(f"G97a sanity d=12 both channels separable (acc>=0.85, xtalk<=0.60): {G97a}", flush=True)
    print(f"G97b minimum crosstalk-free separation (both seeds)             : {min_d if min_d else '>12 (none)'}", flush=True)
    if G97a:
        print(f"G97: PASS - the quiet substrate is a clean parallel communication line; channel pitch ~ {min_d if min_d else '>12'} (box=30)", flush=True)
    else:
        print("G97: NULL - not a clean parallel channel even at wide separation", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G97"
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): {str(d): R[s][d] for d in SEPARATIONS} for s in seeds},
                                                  "G97a": G97a, "min_d": min_d}, indent=2, default=str))
    print("DONE", flush=True)
