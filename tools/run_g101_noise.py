"""G101 — channel noise robustness. Decoder calibrated on CLEAN traffic, tested under interference
(m extra random injections per symbol). Sweep m to find interference tolerance. K=8, WIN=4, reset.
Bars pre-registered in docs/amendments/g101_noise.md.
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
WIN = 4
NBINS = 24
SPAN = (6.0, 24.0)
MS = [0, 4, 8, 14]


def vib_grid_x(w, box):
    n = w.s_pos.shape[0]
    alive = w.s_alive[:n]
    x = w.s_pos[:n, 0][alive]
    if len(x) == 0:
        return np.zeros(NBINS)
    idx = np.clip((x / box[0] * NBINS).astype(int), 0, NBINS - 1)
    return np.bincount(idx, minlength=NBINS).astype(float)


def collect(seed, m, tag):
    """Run one message; m interferer injections per symbol at random x (0 = clean)."""
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    box = np.asarray(c.box_size)
    chan_x = np.linspace(SPAN[0], SPAN[1], K)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    cull_free_vibrations(w, keep_frac=0.0)
    rng = np.random.default_rng(10100 + seed + m + tag)
    msg = rng.integers(0, K, N_SYM)
    states = []
    t0 = time.time()
    for s in msg:
        for _ in range(WIN):
            inject_tight(w, c, box, chan_x[s], n=14)
            if m > 0:
                inject_tight(w, c, box, float(rng.uniform(SPAN[0], SPAN[1])), n=m)
            tick(w, c.dt)
        states.append(vib_grid_x(w, box))
        cull_free_vibrations(w, keep_frac=0.0)
        if time.time() - t0 > 120:
            msg = msg[:len(states)]
            break
    return msg, np.array(states)


def train_decoder(states, labels):
    X = np.hstack([states, np.ones((len(states), 1))])
    W = np.zeros((X.shape[1], K))
    for k in range(K):
        yk = (labels == k).astype(float) - (1.0 / K)
        W[:, k] = np.linalg.solve(X.T @ X + 1.0 * np.eye(X.shape[1]), X.T @ yk)
    return W


def test_decoder(W, states, labels):
    X = np.hstack([states, np.ones((len(states), 1))])
    pred = (X @ W).argmax(axis=1)
    return float(np.mean(pred == labels))


def run(seed):
    # Train on a clean message
    msg_tr, st_tr = collect(seed, 0, tag=1)
    W = train_decoder(st_tr, msg_tr)
    res = {}
    for m in MS:
        msg_te, st_te = collect(seed, m, tag=2)
        res[m] = test_decoder(W, st_te, msg_te)
    return res


if __name__ == "__main__":
    print("=== G101: channel noise robustness (clean-trained decoder under interference) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        line = " ".join(f"m={m}:{R[s][m]:.2f}" for m in MS)
        print(f"  seed {s}: {line} (chance=0.125)", flush=True)

    G101a = all(R[s][0] >= 0.90 for s in seeds)
    max_m = None
    for m in sorted(MS, reverse=True):
        if all(R[s][m] >= 0.90 for s in seeds):
            max_m = m
            break
    print("\n--- VERDICT ---", flush=True)
    print(f"G101a sanity (m=0 transfer >=0.90 both): {G101a}", flush=True)
    print(f"G101b max interferer m at >=0.90 (both): {max_m if max_m is not None else '<0?'}", flush=True)
    if G101a:
        print(f"G101: PASS - channel tolerates interference up to m={max_m} (ratio {max_m/14:.2f}) at >=0.90", flush=True)
    else:
        print("G101: NULL - clean-trained decoder does not transfer", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G101"
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): {str(m): R[s][m] for m in MS} for s in seeds},
                                                  "G101a": G101a, "max_m": max_m}, indent=2, default=str))
    print("DONE", flush=True)
