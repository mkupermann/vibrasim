"""G107 — can an engineered cleared CORRIDOR add transport the bare substrate lacks?
Maintain an atom-free horizontal corridor (|y-15|<3) each tick; launch moving vibrations down it at one
of K=2 sub-channels; read the far region (x>16). Tests whether engineered structure delivers a packet +
symbol to the far end where G105 (no corridor) delivered ~0.
Bars pre-registered in docs/amendments/g107_engineered_conduit.md.
"""
import sys, json, time
from dataclasses import replace
import numpy as np
from pathlib import Path
from world.state import World
from world.physics import tick
from tools.run_bet093 import cull_free_vibrations
from tools.run_g43_protocell import cfg as protocfg

SETTLE = 200
N_SYM = 220
K = 2
NBINS = 6
SUBY = [13.5, 16.5]
X0 = 4.0
VX = 6.0
PROP = 6
FARX = 16.0
CORR_Y, CORR_HALF = 15.0, 3.0


def clear_corridor(w):
    K_ = w.k_count
    if K_ == 0:
        return
    al = w.k_alive[:K_]
    y = w.k_pos[:K_, 1]
    w.k_alive[:K_][al & (np.abs(y - CORR_Y) < CORR_HALF)] = False


def inject_moving(w, cfg, box, x0, cy, n, vx, sigma=0.8):
    rng = w.rng
    free = np.where(~w.s_alive[:cfg.n_vibrations_max])[0]
    k = min(n, len(free))
    if k == 0:
        return
    sl = free[:k]
    w.s_pos[sl] = np.column_stack([
        rng.normal(x0, sigma, k) % box[0],
        rng.normal(cy, sigma, k) % box[1],
        rng.normal(box[2] / 2, sigma, k) % box[2]])
    w.s_vel[sl] = np.tile([vx, 0.0, 0.0], (k, 1))
    w.s_freq[sl] = w._sample_frequencies(k)
    w.s_pol[sl] = rng.random(k) < 0.5
    w.s_alive[sl] = True
    w.n_alive = max(w.n_alive, int(sl.max()) + 1)


def ygrid_far(w, box, xmin):
    n = w.s_pos.shape[0]
    alive = w.s_alive[:n]
    mask = alive & (w.s_pos[:n, 0] > xmin)
    y = w.s_pos[:n, 1][mask]
    if len(y) == 0:
        return np.zeros(NBINS)
    idx = np.clip((y / box[1] * NBINS).astype(int), 0, NBINS - 1)
    return np.bincount(idx, minlength=NBINS).astype(float)


def collect(seed):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    box = np.asarray(c.box_size)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    cull_free_vibrations(w, keep_frac=0.0)
    clear_corridor(w)
    rng = np.random.default_rng(10700 + seed)
    msg = rng.integers(0, K, N_SYM)
    far = []
    t0 = time.time()
    for s in msg:
        inject_moving(w, c, box, X0, SUBY[s], n=14, vx=VX)
        for _ in range(PROP):
            clear_corridor(w)
            tick(w, c.dt)
        far.append(ygrid_far(w, box, FARX))
        cull_free_vibrations(w, keep_frac=0.0)
        if time.time() - t0 > 200:
            msg = msg[:len(far)]
            break
    return msg, np.array(far)


def decode(states, labels, ntr):
    if states.std() == 0:
        return 0.0
    Xtr = np.hstack([states[:ntr], np.ones((ntr, 1))])
    Xte = np.hstack([states[ntr:], np.ones((len(states) - ntr, 1))])
    W = np.zeros((Xtr.shape[1], K))
    for k in range(K):
        yk = (labels[:ntr] == k).astype(float) - (1.0 / K)
        W[:, k] = np.linalg.solve(Xtr.T @ Xtr + 1.0 * np.eye(Xtr.shape[1]), Xtr.T @ yk)
    pred = (Xte @ W).argmax(axis=1)
    return float(np.mean(pred == labels[ntr:]))


def run(seed):
    msg, far = collect(seed)
    n = len(msg)
    ntr = int(0.7 * n)
    return dict(n=n, far_decode=decode(far, msg, ntr), far_energy=float(far.sum()))


if __name__ == "__main__":
    print("=== G107: engineered cleared corridor — transport over distance? ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: far_energy={R[s]['far_energy']:.1f} | far_decode={R[s]['far_decode']:.2f} (chance=0.50, n={R[s]['n']})", flush=True)
    G107a = all(R[s]['far_energy'] > 0 for s in seeds)
    G107b = all(R[s]['far_decode'] >= 0.85 for s in seeds)
    print("\n--- VERDICT ---", flush=True)
    print(f"G107a packet arrives (far_energy>0 both): {G107a}", flush=True)
    print(f"G107b symbol survives (decode>=0.85 both): {G107b}", flush=True)
    if G107a and G107b:
        print("G107: PASS - an engineered conduit enables genuine transport over distance (structure adds what the bare substrate lacks)", flush=True)
    elif G107a:
        print("G107: PARTIAL - energy arrives via the corridor but the symbol is scrambled (transport without fidelity)", flush=True)
    else:
        print("G107: NULL - even a cleared corridor does not deliver a packet to the far end", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G107"
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds},
                                                  "G107a": G107a, "G107b": G107b}, indent=2, default=str))
    print("DONE", flush=True)
