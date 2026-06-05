"""JEP-439 — quantitative capstone: random-feature threshold M* (to reach 0.85 on order-3 parity)
tracks C(P,3), the same combinatorial quantity order-3 OMP enumerates. Confirms the JEP-438
feature-cost == search-cost equivalence. Pure numpy. Pre-registered bars in
docs/amendments/jep439_cost_equivalence.md.
"""
import json
from math import comb
from pathlib import Path
import numpy as np

PS = [12, 15, 18]
M_GRID = [100, 200, 400, 800, 1600, 2400]
N_TR, N_TE = 2500, 1000


def _data(rng, n, P):
    X = rng.choice([-1.0, 1.0], size=(n, P))
    y = X[:, 0] * X[:, 1] * X[:, 2]
    return X, y


def _fit_acc(Phi_tr, y_tr, Phi_te, y_te, ridge=1.0):
    A = Phi_tr.T @ Phi_tr + ridge * np.eye(Phi_tr.shape[1])
    w = np.linalg.solve(A, Phi_tr.T @ y_tr)
    return float((np.sign(Phi_te @ w) == y_te).mean())


def mstar_for_P(rng, P):
    Xtr, ytr = _data(rng, N_TR, P); Xte, yte = _data(rng, N_TE, P)
    accs = {}
    for M in M_GRID:
        R = rng.standard_normal((P, M)); b = rng.standard_normal(M)
        accs[M] = _fit_acc(np.tanh(Xtr @ R + b), ytr, np.tanh(Xte @ R + b), yte)
    mstar = next((M for M in M_GRID if accs[M] >= 0.85), None)
    return mstar, accs


def run(seed):
    rng = np.random.default_rng(seed)
    out = {}
    for P in PS:
        mstar, accs = mstar_for_P(rng, P)
        c3 = comb(P, 3)
        out[P] = dict(mstar=mstar, c3=c3, ratio=(mstar / c3 if mstar else None),
                      accs={M: round(a, 2) for M, a in accs.items()})
    return out


if __name__ == "__main__":
    print("=== JEP-439: random-feature cost M* vs C(P,3) (order-3 parity) ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        for P in PS:
            d = R[s][P]
            print(f"  seed {s} P={P}: C(P,3)={d['c3']:4d} | M*={d['mstar']} | ratio M*/C={d['ratio']} | accs={d['accs']}",
                  flush=True)

    J439a = all(R[s][P]['mstar'] is not None for s in seeds for P in PS)
    J439b = all(R[s][PS[0]]['mstar'] <= R[s][PS[1]]['mstar'] <= R[s][PS[2]]['mstar']
                for s in seeds) if J439a else False
    J439c = all(0.25 <= R[s][P]['ratio'] <= 4.0 for s in seeds for P in PS) if J439a else False
    passed = J439a and J439b and J439c

    print("\n--- VERDICT ---", flush=True)
    print(f"J439a random eventually works (M* finite all P): {J439a}", flush=True)
    print(f"J439b M* non-decreasing in P                   : {J439b}", flush=True)
    print(f"J439c M*/C(P,3) in [0.25, 4] (equivalence)      : {J439c}", flush=True)
    verdict = ("PASS - random-feature cost M* tracks C(P,3) within a constant factor = the OMP "
               "enumeration cost; feature-cost and search-cost are the SAME quantity") if passed else "NULL/partial"
    print(f"\nJEP-439: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP439"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): {str(P): R[s][P] for P in PS} for s in seeds},
                                                  "passed": passed, "J439a": J439a, "J439b": J439b, "J439c": J439c},
                                                 indent=2, default=str))
    print("DONE", flush=True)
