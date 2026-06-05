"""JEP-438 — principled (greedy OMP over interaction terms) vs random features for HIGH-order
feature discovery, on a pure order-3 parity rule (the JEP-428/429 residual). Pins down where the
cost lives: random pays in feature count, order-3 OMP pays in combinatorial enumeration, and greedy
order<=2 gets nothing because parity has no low-order signal. Established methods. Pure numpy.
Pre-registered bars in docs/amendments/jep438_principled_vs_random_discovery.md.
"""
import json
from itertools import combinations
from pathlib import Path
import numpy as np

P = 24
TRIPLE = (0, 1, 2)
N_TR, N_TE = 3000, 1000
M_GRID = [50, 100, 200, 400, 800, 1600]


def _data(rng, n):
    X = rng.choice([-1.0, 1.0], size=(n, P))
    y = X[:, TRIPLE[0]] * X[:, TRIPLE[1]] * X[:, TRIPLE[2]]
    return X, y


def _ridge_fit_predict(Phi_tr, y_tr, Phi_te, ridge=1.0):
    A = Phi_tr.T @ Phi_tr + ridge * np.eye(Phi_tr.shape[1])
    w = np.linalg.solve(A, Phi_tr.T @ y_tr)
    return np.sign(Phi_te @ w)


def random_features(rng, Xtr, ytr, Xte, yte):
    out = {}
    for M in M_GRID:
        R = rng.standard_normal((P, M)); b = rng.standard_normal(M)
        Ptr = np.tanh(Xtr @ R + b); Pte = np.tanh(Xte @ R + b)
        acc = float((_ridge_fit_predict(Ptr, ytr, Pte) == yte).mean())
        out[M] = acc
    mstar = next((M for M in M_GRID if out[M] >= 0.85), None)
    return out, mstar


def _candidates(max_order):
    terms = [(i,) for i in range(P)]
    if max_order >= 2:
        terms += list(combinations(range(P), 2))
    if max_order >= 3:
        terms += list(combinations(range(P), 3))
    return terms


def _term_col(X, t):
    c = np.ones(X.shape[0])
    for i in t:
        c = c * X[:, i]
    return c


def greedy_omp(Xtr, ytr, Xte, yte, max_order, steps=30):
    cands = _candidates(max_order)
    cols_tr = {t: _term_col(Xtr, t) for t in cands}
    selected, resid = [], ytr - ytr.mean()
    evals = 0
    for _ in range(steps):
        best_t, best_c = None, -1.0
        for t in cands:
            if t in selected:
                continue
            ct = cols_tr[t]
            corr = abs(float(ct @ resid) / (np.linalg.norm(ct) * np.linalg.norm(resid) + 1e-12))
            evals += 1
            if corr > best_c:
                best_c, best_t = corr, t
        if best_t is None:
            break
        selected.append(best_t)
        Ptr = np.stack([cols_tr[t] for t in selected], axis=1)
        A = Ptr.T @ Ptr + 1e-6 * np.eye(len(selected))
        w = np.linalg.solve(A, Ptr.T @ ytr)
        resid = ytr - Ptr @ w
        if np.linalg.norm(resid) < 1e-6:
            break
    Pte = np.stack([_term_col(Xte, t) for t in selected], axis=1)
    Ptr = np.stack([cols_tr[t] for t in selected], axis=1)
    A = Ptr.T @ Ptr + 1e-6 * np.eye(len(selected)); w = np.linalg.solve(A, Ptr.T @ ytr)
    acc = float((np.sign(Pte @ w) == yte).mean())
    return dict(acc=acc, n_terms=len(selected), evals=evals,
                found_triple=tuple(TRIPLE) in selected, n_candidates=len(cands))


def run(seed):
    rng = np.random.default_rng(seed)
    Xtr, ytr = _data(rng, N_TR); Xte, yte = _data(rng, N_TE)
    rf, mstar = random_features(rng, Xtr, ytr, Xte, yte)
    p2 = greedy_omp(Xtr, ytr, Xte, yte, max_order=2)
    p3 = greedy_omp(Xtr, ytr, Xte, yte, max_order=3)
    return dict(rf=rf, mstar=mstar, p2=p2, p3=p3)


if __name__ == "__main__":
    print("=== JEP-438: principled vs random high-order feature discovery (order-3 parity) ===", flush=True)
    seeds = [0, 7]
    R = {}
    C3 = 2024  # C(24,3)
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: random M*={R[s]['mstar']} (accs={ {M: round(a,2) for M,a in R[s]['rf'].items()} })", flush=True)
        print(f"           greedy P2(order<=2) acc={R[s]['p2']['acc']:.3f} (terms={R[s]['p2']['n_terms']}, "
              f"evals={R[s]['p2']['evals']}) | P3(order<=3) acc={R[s]['p3']['acc']:.3f} "
              f"(found_triple={R[s]['p3']['found_triple']}, evals={R[s]['p3']['evals']}, cands={R[s]['p3']['n_candidates']})",
              flush=True)

    J438a = all(R[s]['p2']['acc'] <= 0.65 for s in seeds)
    J438b = all(R[s]['p3']['acc'] >= 0.95 and R[s]['p3']['n_candidates'] >= C3 for s in seeds)
    J438c = all(R[s]['mstar'] is not None and R[s]['mstar'] >= 400 for s in seeds)
    passed = J438a and J438b and J438c

    print("\n--- VERDICT ---", flush=True)
    print(f"J438a greedy order<=2 fails (<=0.65)            : {J438a}", flush=True)
    print(f"J438b order-3 OMP works but enumerates C(P,3)   : {J438b}", flush=True)
    print(f"J438c random needs many features (M*>=400)      : {J438c}", flush=True)
    verdict = ("PASS - no free lunch for high-order discovery without low-order signal: pay in "
               "features (random) OR order-k enumeration (OMP); greedy climbing gets nothing") if passed else "NULL/partial"
    print(f"\nJEP-438: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP438"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "J438a": J438a, "J438b": J438b, "J438c": J438c}, indent=2, default=str))
    print("DONE", flush=True)
