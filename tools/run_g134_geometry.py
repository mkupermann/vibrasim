"""G134 — does the substrate EARN its place on GEOMETRY? Proximity-detection: do the substrate's binding
physics natively compute a spatial proximity that raw+linear can't, and that matches/beats the abstract
ELM? Inputs = K point positions; target = 1 if any two points are within distance d (a nonlinear spatial
threshold). Compare held-out balanced accuracy of: raw+linear, abstract-ELM, PHYSICAL-substrate features.
If physical >> raw+linear (and ~ ELM), the physics computes the proximity geometrically -> earns its place.
"""
import sys, time
from dataclasses import replace
import numpy as np
from world.state import World
from world.physics import tick
from tools.run_bet098 import inject_tight
from tools.run_g43_protocell import cfg as protocfg

SETTLE = 200
N = 120
KP = 5
SPAN = (6.0, 24.0)
DTHRESH = 1.6
TICKS = 25
NB = 16


def snapshot(w):
    return {k: (v.copy() if isinstance(v, np.ndarray) else v)
            for k, v in vars(w).items()
            if isinstance(v, (np.ndarray, int, float, bool, np.integer, np.floating))}


def restore(w, snap):
    for k, v in snap.items():
        cur = getattr(w, k, None)
        if isinstance(cur, np.ndarray) and cur.shape == np.shape(v):
            cur[:] = v
        else:
            setattr(w, k, v)


def phys_features(w, c, snap, pts, box):
    restore(w, snap)
    for px in pts:
        inject_tight(w, c, box, float(px), n=12)
    for _ in range(TICKS):
        tick(w, c.dt)
    n = w.s_pos.shape[0]; al = w.s_alive[:n]
    sx = w.s_pos[:n, 0][al]
    vib = np.histogram(sx, bins=NB, range=(0, box[0]))[0].astype(float)
    K_ = w.k_count
    atoms = np.histogram(w.k_pos[:K_, 0][w.k_alive[:K_]], bins=NB, range=(0, box[0]))[0].astype(float) if K_ else np.zeros(NB)
    return np.concatenate([vib, atoms])


def bal_acc(Phi, y, ntr, lam=1.0):
    Xtr, Xte = Phi[:ntr], Phi[ntr:]; ytr, yte = y[:ntr], y[ntr:]
    mu = Xtr.mean(0); sd = Xtr.std(0) + 1e-6
    Xtr = (Xtr - mu) / sd; Xte = (Xte - mu) / sd
    Xtr = np.hstack([Xtr, np.ones((len(Xtr), 1))]); Xte = np.hstack([Xte, np.ones((len(Xte), 1))])
    W = np.linalg.solve(Xtr.T @ Xtr + lam * np.eye(Xtr.shape[1]), Xtr.T @ (ytr - 0.5))
    pred = Xte @ W; pos = yte > 0.5
    tpr = float(np.mean(pred[pos] > 0)) if pos.any() else 0.0
    tnr = float(np.mean(pred[~pos] <= 0)) if (~pos).any() else 0.0
    return 0.5 * (tpr + tnr)


def run(seed):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c); box = np.asarray(c.box_size)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    snap = snapshot(w)
    rng = np.random.default_rng(13400 + seed)
    P = rng.uniform(SPAN[0], SPAN[1], (N, KP))
    y = np.array([1.0 if np.min(np.abs(p[:, None] - p[None, :]) + np.eye(KP) * 999) < DTHRESH else 0.0 for p in P])
    Psort = np.sort(P, axis=1)   # raw features sorted (give linear its best shot)
    t0 = time.time()
    Phi_phys = np.array([phys_features(w, c, snap, P[i], box) for i in range(N)])
    Rm = rng.normal(0, 1.5 / np.sqrt(KP), (2 * NB, KP)); bm = rng.normal(0, 0.3, 2 * NB)
    Phi_elm = np.tanh(Psort @ Rm.T + bm)
    ntr = int(0.7 * N)
    return dict(pos=int(y.sum()), raw=bal_acc(Psort, y, ntr), elm=bal_acc(Phi_elm, y, ntr),
                phys=bal_acc(Phi_phys, y, ntr), secs=round(time.time() - t0, 1))


if __name__ == "__main__":
    print(f"=== G134: GEOMETRY (proximity detection) — does the physics earn its place? ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s} (pos={R[s]['pos']}/{N}): raw+linear={R[s]['raw']:.2f} | ELM={R[s]['elm']:.2f} | PHYSICAL={R[s]['phys']:.2f}  ({R[s]['secs']}s)", flush=True)
    phys_earns = all(R[s]['phys'] >= R[s]['raw'] + 0.10 for s in seeds)
    print("\n--- VERDICT ---", flush=True)
    print(f"PHYSICAL beats raw+linear by >=0.10 (both seeds): {phys_earns}", flush=True)
    if phys_earns:
        print("G134: PASS - on GEOMETRY the physical substrate EARNS its place: its proximity physics gives features that beat raw+linear (the physics computes the spatial relation natively)", flush=True)
    else:
        print("G134: NULL - even on a geometric proximity task the physical features do not beat raw+linear; the substrate does not earn its place here either", flush=True)
    print("DONE", flush=True)
