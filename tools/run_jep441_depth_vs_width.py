"""JEP-441 — depth vs width for high-order feature discovery (order-3 parity, P=18). Flat 1-layer
random tanh features vs deep 2-layer (features-of-features), matched total unit budget. No backprop,
no enumeration. Pre-registered bars in docs/amendments/jep441_depth_vs_width.md.
"""
import json
from pathlib import Path
import numpy as np

P = 18
N_TR, N_TE = 2500, 1000
BUDGETS = [1200, 2400]


def _data(rng, n):
    X = rng.choice([-1.0, 1.0], size=(n, P))
    y = X[:, 0] * X[:, 1] * X[:, 2]
    return X, y


def _ridge_acc(Phi_tr, y_tr, Phi_te, y_te, ridge=1.0):
    A = Phi_tr.T @ Phi_tr + ridge * np.eye(Phi_tr.shape[1])
    w = np.linalg.solve(A, Phi_tr.T @ y_tr)
    return float((np.sign(Phi_te @ w) == y_te).mean())


def flat(rng, Xtr, ytr, Xte, yte, M):
    R = rng.standard_normal((P, M)); b = rng.standard_normal(M)
    return _ridge_acc(np.tanh(Xtr @ R + b), ytr, np.tanh(Xte @ R + b), yte)


def deep(rng, Xtr, ytr, Xte, yte, m1, m2):
    R1 = rng.standard_normal((P, m1)); b1 = rng.standard_normal(m1)
    h1_tr = np.tanh(Xtr @ R1 + b1); h1_te = np.tanh(Xte @ R1 + b1)
    R2 = rng.standard_normal((m1, m2)) / np.sqrt(m1); b2 = rng.standard_normal(m2)
    h2_tr = np.tanh(h1_tr @ R2 + b2); h2_te = np.tanh(h1_te @ R2 + b2)
    return _ridge_acc(h2_tr, ytr, h2_te, yte)


def run(seed):
    rng = np.random.default_rng(seed)
    Xtr, ytr = _data(rng, N_TR); Xte, yte = _data(rng, N_TE)
    out = {}
    for T in BUDGETS:
        out[T] = dict(flat=flat(rng, Xtr, ytr, Xte, yte, T),
                      deep=deep(rng, Xtr, ytr, Xte, yte, T // 2, T // 2))
    return out


if __name__ == "__main__":
    print("=== JEP-441: depth vs width for order-3 discovery (P=18 parity) ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        for T in BUDGETS:
            print(f"  seed {s} T={T}: flat={R[s][T]['flat']:.3f} | deep(2-layer)={R[s][T]['deep']:.3f}", flush=True)

    J441a = all(R[s][2400]['deep'] >= R[s][2400]['flat'] + 0.10 for s in seeds)
    J441b = all(any(R[s][T]['deep'] >= 0.85 for T in BUDGETS) for s in seeds)
    J441c = all(R[s][2400]['flat'] <= 0.80 for s in seeds)
    passed = J441a and J441b and J441c

    print("\n--- VERDICT ---", flush=True)
    print(f"J441a depth helps (deep>=flat+0.10 @T=2400) : {J441a}", flush=True)
    print(f"J441b depth reaches >=0.85 (T<=2400)        : {J441b}", flush=True)
    print(f"J441c flat baseline shortfall (<=0.80)      : {J441c}", flush=True)
    verdict = ("PASS - depth (composition) beats width: deep random features are a backprop-free, "
               "cheaper-than-flat partial route to high-order discovery") if passed else "NULL/partial"
    print(f"\nJEP-441: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP441"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): {str(T): R[s][T] for T in BUDGETS} for s in seeds},
                                                  "passed": passed, "J441a": J441a, "J441b": J441b, "J441c": J441c},
                                                 indent=2, default=str))
    print("DONE", flush=True)
