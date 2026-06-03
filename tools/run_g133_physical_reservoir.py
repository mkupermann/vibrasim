"""G133 — DECISIVE: is the physical substrate a usable reservoir, or is the 'SubstrateReservoir' (a numpy
random matrix) the only thing that works? Feed input x into the REAL World physics, read the physical
state as features phi_phys(x), and test held-out generalization on a NONLINEAR task vs (a) the abstract
ELM matrix tanh(Rx) and (b) a linear baseline. If phi_phys generalizes ~ the ELM, the substrate genuinely
contributes to cognition. If phi_phys ~ linear (no nonlinear features), the substrate is decorative and
the cognition is purely classical ML (BET-143's worry, confirmed).
"""
import sys, time
from dataclasses import replace
import numpy as np
from world.state import World
from world.physics import tick
from tools.run_bet098 import inject_tight
from tools.run_g43_protocell import cfg as protocfg

SETTLE = 200
N = 90
D_IN = 6
XLOCS = np.linspace(6, 24, D_IN)
TICKS = 20
NB = 10


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


def phys_features(w, c, snap, x, box):
    restore(w, snap)
    for i, xv in enumerate(x):
        n = int(round(xv * 12))
        if n > 0:
            inject_tight(w, c, box, XLOCS[i], n=n)
    for _ in range(TICKS):
        tick(w, c.dt)
    n = w.s_pos.shape[0]
    al = w.s_alive[:n]
    sx = w.s_pos[:n, 0][al]
    vib = np.histogram(sx, bins=NB, range=(0, box[0]))[0].astype(float)
    K_ = w.k_count
    if K_:
        ka = w.k_alive[:K_]
        kx = w.k_pos[:K_, 0][ka]
        atoms = np.histogram(kx, bins=NB, range=(0, box[0]))[0].astype(float)
        ch = np.histogram(w.k_pos[:K_, 0][ka], bins=NB, range=(0, box[0]),
                          weights=np.abs(w.k_charge[:K_][ka]))[0]
    else:
        atoms = np.zeros(NB); ch = np.zeros(NB)
    return np.concatenate([vib, atoms, ch])


def ridge_r2(Phi, y, ntr, lam=1.0):
    Xtr, Xte = Phi[:ntr], Phi[ntr:]
    ytr, yte = y[:ntr], y[ntr:]
    mu = Xtr.mean(0); sd = Xtr.std(0) + 1e-6
    Xtr = (Xtr - mu) / sd; Xte = (Xte - mu) / sd
    Xtr = np.hstack([Xtr, np.ones((len(Xtr), 1))]); Xte = np.hstack([Xte, np.ones((len(Xte), 1))])
    W = np.linalg.solve(Xtr.T @ Xtr + lam * np.eye(Xtr.shape[1]), Xtr.T @ ytr)
    pred = Xte @ W
    ss_res = float(((yte - pred) ** 2).sum()); ss_tot = float(((yte - yte.mean()) ** 2).sum()) + 1e-9
    return 1.0 - ss_res / ss_tot


def run(seed):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c); box = np.asarray(c.box_size)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    snap = snapshot(w)
    rng = np.random.default_rng(13300 + seed)
    X = rng.uniform(0, 1, (N, D_IN))
    # NONLINEAR target: pairwise products (needs nonlinear features; linear baseline must fail)
    y = np.array([sum(xx[i] * xx[(i + 1) % D_IN] for i in range(D_IN)) for xx in X])
    t0 = time.time()
    Phi_phys = np.array([phys_features(w, c, snap, X[i], box) for i in range(N)])
    # abstract ELM
    R = rng.normal(0, 1.5 / np.sqrt(D_IN), (3 * NB, D_IN)); b = rng.normal(0, 0.3, 3 * NB)
    Phi_elm = np.tanh(X @ R.T + b)
    ntr = int(0.7 * N)
    return dict(lin=ridge_r2(X, y, ntr), elm=ridge_r2(Phi_elm, y, ntr),
                phys=ridge_r2(Phi_phys, y, ntr), secs=round(time.time() - t0, 1))


if __name__ == "__main__":
    print("=== G133: PHYSICAL substrate as reservoir vs abstract ELM (held-out R2 on a nonlinear task) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: linear R2={R[s]['lin']:.2f} | abstract-ELM R2={R[s]['elm']:.2f} | PHYSICAL-substrate R2={R[s]['phys']:.2f}  ({R[s]['secs']}s)", flush=True)
    phys_helps = all(R[s]['phys'] > R[s]['lin'] + 0.15 for s in seeds)
    elm_helps = all(R[s]['elm'] > R[s]['lin'] + 0.15 for s in seeds)
    print("\n--- VERDICT ---", flush=True)
    print(f"abstract ELM adds nonlinear features (R2>lin+0.15 both): {elm_helps}", flush=True)
    print(f"PHYSICAL substrate adds nonlinear features (both)       : {phys_helps}", flush=True)
    if phys_helps:
        print("G133: PASS - the PHYSICAL substrate is a genuine reservoir: its physics provides nonlinear features that generalize -> the substrate really contributes to cognition (not decorative)", flush=True)
    else:
        print("G133: NULL - the physical substrate does NOT provide usable nonlinear features (~linear baseline); the cognition stack's power is the abstract ELM, the physical substrate is DECORATIVE (confirms BET-143's worry)", flush=True)
    print("DONE", flush=True)
