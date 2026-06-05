"""JEP-456 — efficient local discovery: antithetic node perturbation (variance-reduced, still fully
local) vs plain node perturbation on order-3 parity at a REDUCED epoch budget. No backprop, no weight
transport. Pre-registered bars in docs/amendments/jep456_variance_reduced_local.md.
"""
import json
from pathlib import Path
import numpy as np

P = 18
M = 64
N_TR, N_TE = 2500, 1000
EPOCHS = 5000
SIGMA = 0.1
LR = 0.05
CLIP = 1.0


def _data(rng, n):
    X = rng.choice([-1.0, 1.0], size=(n, P))
    return X, X[:, 0] * X[:, 1] * X[:, 2]


def _clip(g):
    nrm = np.linalg.norm(g)
    return g * (CLIP / nrm) if nrm > CLIP else g


def _train(rng, Xtr, ytr, antithetic):
    W1 = rng.standard_normal((P, M)) / np.sqrt(P); b1 = np.zeros(M)
    w2 = rng.standard_normal(M) / np.sqrt(M); b2 = 0.0
    N = Xtr.shape[0]
    for _ in range(EPOCHS):
        pre = Xtr @ W1 + b1
        h = np.tanh(pre)
        o = h @ w2 + b2
        err = o - ytr
        w2 -= LR * _clip(h.T @ (2.0 * err / N)); b2 -= LR * (2.0 * err / N).sum()
        xi = rng.standard_normal((N, M))
        if antithetic:
            hp = np.tanh(pre + SIGMA * xi); hm = np.tanh(pre - SIGMA * xi)
            Lp = (hp @ w2 + b2 - ytr) ** 2; Lm = (hm @ w2 + b2 - ytr) ** 2
            mod = xi * ((Lp - Lm) / (2.0 * SIGMA ** 2))[:, None]
        else:
            hpert = np.tanh(pre + SIGMA * xi)
            dL = (hpert @ w2 + b2 - ytr) ** 2 - (o - ytr) ** 2
            mod = (xi * dL[:, None]) / (SIGMA ** 2)
        W1 -= LR * _clip(Xtr.T @ mod / N); b1 -= LR * mod.mean(axis=0)
    return (W1, b1, w2, b2)


def _predict(net, X):
    W1, b1, w2, b2 = net
    return np.sign(np.tanh(X @ W1 + b1) @ w2 + b2)


def _perm(net, Xte, yte, rng):
    base = float((_predict(net, Xte) == yte).mean())
    drops = []
    for i in range(P):
        Xp = Xte.copy(); Xp[:, i] = rng.permutation(Xp[:, i])
        drops.append(base - float((_predict(net, Xp) == yte).mean()))
    return sorted(sorted(range(P), key=lambda i: drops[i], reverse=True)[:3])


def run(seed):
    rng = np.random.default_rng(seed)
    Xtr, ytr = _data(rng, N_TR); Xte, yte = _data(rng, N_TE)
    plain = _train(rng, Xtr, ytr, antithetic=False)
    anti = _train(rng, Xtr, ytr, antithetic=True)
    return dict(plain=float((_predict(plain, Xte) == yte).mean()),
                anti=float((_predict(anti, Xte) == yte).mean()),
                anti_top3=_perm(anti, Xte, yte, rng))


if __name__ == "__main__":
    print(f"=== JEP-456: variance-reduced local discovery ({EPOCHS} epochs) ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: plain node-pert={R[s]['plain']:.3f} | antithetic={R[s]['anti']:.3f} | "
              f"anti top-3={R[s]['anti_top3']}", flush=True)

    J456a = all(R[s]['anti'] >= 0.90 and R[s]['anti'] >= R[s]['plain'] + 0.10 for s in seeds)
    J456b = all(R[s]['anti_top3'] == [0, 1, 2] for s in seeds)
    passed = J456a and J456b

    print("\n--- VERDICT ---", flush=True)
    print(f"J456a antithetic faster (>=0.90, >=plain+0.10): {J456a}", flush=True)
    print(f"J456b antithetic finds the triple             : {J456b}", flush=True)
    print(f"J456c (honest): still needs {EPOCHS} epochs — constant-factor speedup, not asymptotic fix", flush=True)
    verdict = ("PASS - antithetic variance reduction materially speeds up fully-local high-order "
               "discovery") if passed else "NULL/partial"
    print(f"\nJEP-456: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP456"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "J456a": J456a, "J456b": J456b, "epochs": EPOCHS}, indent=2, default=str))
    print("DONE", flush=True)
