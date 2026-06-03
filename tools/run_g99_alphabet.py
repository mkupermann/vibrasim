"""G99 — message transmission WITH active reset; alphabet-size (symbol resolution) sweep.
Constructive complement to G98 (which showed natural decay alone cannot clear ISI). Here each symbol is
followed by an active re-quiet (cull_free_vibrations) — the same reset G97 used between trials. K symbols
map one-hot to K spatial channels evenly spaced across the usable span; sweep K to find how many distinct
symbols the channel resolves with held-out message accuracy. Measures the substrate's symbol alphabet.
Bars pre-registered in docs/amendments/g99_alphabet.md.
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
N_SYM = 240
WIN = 8
NBINS = 24
SPAN = (6.0, 24.0)        # usable x-span for channels (box=30)
KS = [4, 8, 16]


def vib_grid_x(w, box):
    n = w.s_pos.shape[0]
    alive = w.s_alive[:n]
    x = w.s_pos[:n, 0][alive]
    if len(x) == 0:
        return np.zeros(NBINS)
    idx = np.clip((x / box[0] * NBINS).astype(int), 0, NBINS - 1)
    return np.bincount(idx, minlength=NBINS).astype(float)


def collect(seed, K):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    box = np.asarray(c.box_size)
    chan_x = np.linspace(SPAN[0], SPAN[1], K)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    cull_free_vibrations(w, keep_frac=0.0)
    rng = np.random.default_rng(9900 + seed + K)
    msg = rng.integers(0, K, N_SYM)
    states = []
    t0 = time.time()
    for s in msg:
        for _ in range(WIN):
            inject_tight(w, c, box, chan_x[s], n=14)
            tick(w, c.dt)
        states.append(vib_grid_x(w, box))
        cull_free_vibrations(w, keep_frac=0.0)     # ACTIVE reset between symbols
        if time.time() - t0 > 200:
            msg = msg[:len(states)]
            break
    return msg, np.array(states), K


def decode_multiclass(states, labels, ntr, K):
    Xtr = np.hstack([states[:ntr], np.ones((ntr, 1))])
    Xte = np.hstack([states[ntr:], np.ones((len(states) - ntr, 1))])
    W = np.zeros((Xtr.shape[1], K))
    for k in range(K):
        yk = (labels[:ntr] == k).astype(float) - (1.0 / K)
        W[:, k] = np.linalg.solve(Xtr.T @ Xtr + 1.0 * np.eye(Xtr.shape[1]), Xtr.T @ yk)
    pred = (Xte @ W).argmax(axis=1)
    return float(np.mean(pred == labels[ntr:]))


def run_K(seed, K):
    msg, states, K = collect(seed, K)
    n = len(msg)
    ntr = int(0.7 * n)
    acc = decode_multiclass(states, msg, ntr, K)
    return dict(n=n, acc=acc, chance=1.0 / K)


if __name__ == "__main__":
    print("=== G99: message transmission with reset; alphabet-size sweep ===", flush=True)
    seeds = [42, 7]
    R = {s: {} for s in seeds}
    for s in seeds:
        for K in KS:
            r = run_K(s, K)
            R[s][K] = r
            print(f"  seed {s} K={K:>2}: symbol-acc={r['acc']:.2f} (chance={r['chance']:.3f}, n={r['n']})", flush=True)

    G99a = all(R[s][4]['acc'] >= 0.90 for s in seeds)
    max_K = None
    for K in sorted(KS, reverse=True):       # largest alphabet that still works both seeds
        if all(R[s][K]['acc'] >= 0.90 for s in seeds):
            max_K = K
            break
    print("\n--- VERDICT ---", flush=True)
    print(f"G99a sanity (K=4 acc>=0.90 both seeds): {G99a}", flush=True)
    print(f"G99b max alphabet at >=0.90 (both)    : {max_K if max_K else '<4'}", flush=True)
    if G99a:
        print(f"G99: PASS - with active reset the substrate transmits messages; alphabet up to K={max_K if max_K else 4} symbols", flush=True)
    else:
        print("G99: NULL - message not transmissible even at K=4 with reset", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G99"
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): {str(K): R[s][K] for K in KS} for s in seeds},
                                                  "G99a": G99a, "max_K": max_K}, indent=2, default=str))
    print("DONE", flush=True)
