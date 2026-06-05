"""HYB-01 — energy model + algebraic discovery escapes the SQ wall. The actual ValenceReservoirLearner
fails order-8 parity on raw inputs (SQ wall) but succeeds when augmented with a GF(2)-discovered parity
feature. Pre-registered bars in docs/amendments/hyb01_energy_plus_algebraic.md.
"""
import json
from pathlib import Path
import numpy as np

from world.valence_reservoir import ValenceReservoirLearner

P = 18
K = 8
N_DISCOVER = 40           # samples for the algebraic (GF2) discovery step
N_TR, N_TE = 1500, 2000


def _data(rng, n):
    X = rng.choice([-1.0, 1.0], size=(n, P))
    y = np.prod(X[:, :K], axis=1)
    return X, y


def gf2_discover(rng):
    """Discover the parity set s from a small sample via GF(2) Gaussian elimination."""
    X = rng.choice([-1.0, 1.0], size=(N_DISCOVER, P))
    yb = (np.prod(X[:, :K], axis=1) < 0).astype(np.int64)
    Xb = (X < 0).astype(np.int64)
    M = np.concatenate([Xb % 2, (yb % 2)[:, None]], axis=1)
    rank = 0; pivots = []
    for col in range(P):
        rows = np.where(M[rank:, col] == 1)[0]
        if len(rows) == 0:
            continue
        pr = rank + rows[0]; M[[rank, pr]] = M[[pr, rank]]
        for r in range(N_DISCOVER):
            if r != rank and M[r, col] == 1:
                M[r] = (M[r] + M[rank]) % 2
        pivots.append(col); rank += 1
        if rank == N_DISCOVER:
            break
    s = np.zeros(P, dtype=np.int64)
    for i, col in enumerate(pivots):
        s[col] = M[i, -1]
    return np.where(s == 1)[0]


def _parity_feature(X, s):
    return np.prod(X[:, s], axis=1, keepdims=True) if len(s) else np.zeros((X.shape[0], 1))


def train_energy(Xtr, ytr, Xte, yte, seed):
    learner = ValenceReservoirLearner(n_inputs=Xtr.shape[1], n_features=400, seed=seed)
    for x, v in zip(Xtr, ytr):
        learner.experience(x, v)
    return float((np.array([np.sign(learner.feel(x)) for x in Xte]) == yte).mean())


def run(seed):
    rng = np.random.default_rng(seed)
    Xtr, ytr = _data(rng, N_TR); Xte, yte = _data(rng, N_TE)
    acc_raw = train_energy(Xtr, ytr, Xte, yte, seed)

    s = gf2_discover(np.random.default_rng(seed + 1))
    Xtr_aug = np.concatenate([Xtr, _parity_feature(Xtr, s)], axis=1)
    Xte_aug = np.concatenate([Xte, _parity_feature(Xte, s)], axis=1)
    acc_hyb = train_energy(Xtr_aug, ytr, Xte_aug, yte, seed)

    # GF(2)-only reference
    phi_te = _parity_feature(Xte, s).ravel()
    acc_gf2 = float((np.sign(phi_te + 1e-9) == yte).mean())   # phi = parity over s = y if s correct
    return dict(acc_raw=acc_raw, acc_hyb=acc_hyb, acc_gf2=acc_gf2, set_ok=(set(s.tolist()) == set(range(K))))


if __name__ == "__main__":
    print("=== HYB-01: energy model + algebraic discovery vs the SQ wall (order-8) ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: raw-energy={R[s]['acc_raw']:.3f} | energy+algebraic={R[s]['acc_hyb']:.3f} | "
              f"GF2-only={R[s]['acc_gf2']:.3f} (set_ok={R[s]['set_ok']})", flush=True)

    HYB01a = all(R[s]['acc_raw'] <= 0.65 for s in seeds)
    HYB01b = all(R[s]['acc_hyb'] >= 0.95 for s in seeds)
    passed = HYB01a and HYB01b

    print("\n--- VERDICT ---", flush=True)
    print(f"HYB01a raw energy hits SQ wall (<=0.65)   : {HYB01a}", flush=True)
    print(f"HYB01b energy+algebraic escapes (>=0.95)  : {HYB01b}", flush=True)
    verdict = ("PASS - the energy model + a bolt-on algebraic discovery module escapes the SQ wall: a "
               "working architecture for the boundary JEP-461 identified") if passed else "NULL/partial"
    print(f"\nHYB-01: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "HYB01"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "HYB01a": HYB01a, "HYB01b": HYB01b}, indent=2, default=str))
    print("DONE", flush=True)
