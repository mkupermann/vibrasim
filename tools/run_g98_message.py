"""G98 — multi-symbol message transmission & inter-symbol interference (ISI).
K=4 symbols one-hot over 4 spatial channels. A random message; each symbol injects at its channel for
WIN ticks, then GAP ticks of no injection / no culling (the substrate clears residual by its own decay).
Decode each symbol from the free-vibration x-grid with a multiclass linear readout. Sweep GAP to find
the max symbol rate (min gap) for clean transmission.
Bars pre-registered in docs/amendments/g98_message_isi.md.
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
N_SYM = 200
WIN = 8
NBINS = 12
CHAN_X = [9.0, 13.0, 17.0, 21.0]
K = len(CHAN_X)
GAPS = [12, 6, 2, 0]


def vib_grid_x(w, box):
    n = w.s_pos.shape[0]
    alive = w.s_alive[:n]
    x = w.s_pos[:n, 0][alive]
    if len(x) == 0:
        return np.zeros(NBINS)
    idx = np.clip((x / box[0] * NBINS).astype(int), 0, NBINS - 1)
    return np.bincount(idx, minlength=NBINS).astype(float)


def collect(seed, gap):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    box = np.asarray(c.box_size)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    cull_free_vibrations(w, keep_frac=0.0)
    rng = np.random.default_rng(9800 + seed + gap)
    msg = rng.integers(0, K, N_SYM)
    states = []
    t0 = time.time()
    for s in msg:
        for _ in range(WIN):
            inject_tight(w, c, box, CHAN_X[s], n=14)
            tick(w, c.dt)
        for _ in range(gap):                 # ISI window: decay only, no injection, no cull
            tick(w, c.dt)
        states.append(vib_grid_x(w, box))
        if time.time() - t0 > 220:
            msg = msg[:len(states)]
            break
    return msg, np.array(states)


def decode_multiclass(states, labels, ntr):
    Xtr = np.hstack([states[:ntr], np.ones((ntr, 1))])
    Xte = np.hstack([states[ntr:], np.ones((len(states) - ntr, 1))])
    W = np.zeros((Xtr.shape[1], K))
    for k in range(K):
        yk = (labels[:ntr] == k).astype(float) - 0.5
        W[:, k] = np.linalg.solve(Xtr.T @ Xtr + 1.0 * np.eye(Xtr.shape[1]), Xtr.T @ yk)
    pred = (Xte @ W).argmax(axis=1)
    return float(np.mean(pred == labels[ntr:]))


def run_gap(seed, gap):
    msg, states = collect(seed, gap)
    n = len(msg)
    ntr = int(0.7 * n)
    acc = decode_multiclass(states, msg, ntr)
    return dict(n=n, acc=acc)


if __name__ == "__main__":
    print("=== G98: multi-symbol message transmission & ISI (K=4 spatial channels) ===", flush=True)
    seeds = [42, 7]
    R = {s: {} for s in seeds}
    for s in seeds:
        for g in GAPS:
            r = run_gap(s, g)
            R[s][g] = r
            print(f"  seed {s} gap={g:>3}: symbol-acc={r['acc']:.2f} (n={r['n']}, chance=0.25)", flush=True)

    G98a = all(R[s][12]['acc'] >= 0.90 for s in seeds)
    min_gap = None
    for g in sorted(GAPS):                   # ascending -> smallest gap that still works both seeds
        if all(R[s][g]['acc'] >= 0.90 for s in seeds):
            min_gap = g
            break
    print("\n--- VERDICT ---", flush=True)
    print(f"G98a sanity (gap=12 symbol-acc>=0.90 both seeds): {G98a}", flush=True)
    print(f"G98b min gap for >=0.90 (both seeds)            : {min_gap if min_gap is not None else '>12 (none)'}", flush=True)
    if G98a:
        print(f"G98: PASS - the substrate channel carries a multi-symbol message; clean down to gap={min_gap if min_gap is not None else '>12'} ticks", flush=True)
    else:
        print("G98: NULL - cannot carry a message without re-quieting between every symbol", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G98"
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): {str(g): R[s][g] for g in GAPS} for s in seeds},
                                                  "G98a": G98a, "min_gap": min_gap}, indent=2, default=str))
    print("DONE", flush=True)
