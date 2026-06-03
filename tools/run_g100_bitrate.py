"""G100 — channel bit rate: minimum ticks-per-symbol (WIN) for reliable transmission.
Fix K=8 (one-hot spatial channels, per-symbol active reset, multiclass linear decode). Sweep WIN to
find the fastest symbol rate that still decodes >= 0.90. Bits/tick = log2(K)/WIN.
Bars pre-registered in docs/amendments/g100_bitrate.md.
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
K = 8
NBINS = 24
SPAN = (6.0, 24.0)
WINS = [8, 4, 2, 1]


def vib_grid_x(w, box):
    n = w.s_pos.shape[0]
    alive = w.s_alive[:n]
    x = w.s_pos[:n, 0][alive]
    if len(x) == 0:
        return np.zeros(NBINS)
    idx = np.clip((x / box[0] * NBINS).astype(int), 0, NBINS - 1)
    return np.bincount(idx, minlength=NBINS).astype(float)


def collect(seed, win):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    box = np.asarray(c.box_size)
    chan_x = np.linspace(SPAN[0], SPAN[1], K)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    cull_free_vibrations(w, keep_frac=0.0)
    rng = np.random.default_rng(10000 + seed + win)
    msg = rng.integers(0, K, N_SYM)
    states = []
    t0 = time.time()
    for s in msg:
        for _ in range(win):
            inject_tight(w, c, box, chan_x[s], n=14)
            tick(w, c.dt)
        states.append(vib_grid_x(w, box))
        cull_free_vibrations(w, keep_frac=0.0)
        if time.time() - t0 > 200:
            msg = msg[:len(states)]
            break
    return msg, np.array(states)


def decode_multiclass(states, labels, ntr):
    Xtr = np.hstack([states[:ntr], np.ones((ntr, 1))])
    Xte = np.hstack([states[ntr:], np.ones((len(states) - ntr, 1))])
    W = np.zeros((Xtr.shape[1], K))
    for k in range(K):
        yk = (labels[:ntr] == k).astype(float) - (1.0 / K)
        W[:, k] = np.linalg.solve(Xtr.T @ Xtr + 1.0 * np.eye(Xtr.shape[1]), Xtr.T @ yk)
    pred = (Xte @ W).argmax(axis=1)
    return float(np.mean(pred == labels[ntr:]))


def run_win(seed, win):
    msg, states = collect(seed, win)
    n = len(msg)
    ntr = int(0.7 * n)
    return dict(n=n, acc=decode_multiclass(states, msg, ntr))


if __name__ == "__main__":
    print("=== G100: channel bit rate (min ticks/symbol, K=8) ===", flush=True)
    seeds = [42, 7]
    R = {s: {} for s in seeds}
    for s in seeds:
        for win in WINS:
            r = run_win(s, win)
            R[s][win] = r
            print(f"  seed {s} WIN={win}: symbol-acc={r['acc']:.2f} (chance=0.125, n={r['n']})", flush=True)

    G100a = all(R[s][8]['acc'] >= 0.90 for s in seeds)
    min_win = None
    for win in sorted(WINS):
        if all(R[s][win]['acc'] >= 0.90 for s in seeds):
            min_win = win
            break
    import math
    rate = (math.log2(K) / min_win) if min_win else None
    print("\n--- VERDICT ---", flush=True)
    print(f"G100a sanity (WIN=8 acc>=0.90 both seeds): {G100a}", flush=True)
    print(f"G100b min WIN >=0.90 (both)              : {min_win if min_win else '>8 (none)'}", flush=True)
    if rate:
        print(f"        -> bit rate = log2(8)/{min_win} = {rate:.2f} bits per injection tick", flush=True)
    if G100a:
        print(f"G100: PASS - channel bandwidth characterised; reliable down to WIN={min_win} ticks/symbol", flush=True)
    else:
        print("G100: NULL - WIN=8 failed (instability vs G99)", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G100"
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): {str(w): R[s][w] for w in WINS} for s in seeds},
                                                  "G100a": G100a, "min_win": min_win, "bits_per_tick": rate}, indent=2, default=str))
    print("DONE", flush=True)
