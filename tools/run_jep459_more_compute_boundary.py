"""JEP-459 — does MORE compute push the fully-local high-order learning boundary outward? Scale up
node perturbation (M=192, 20000 epochs, N=5000) on the orders that broke at modest compute (k=6,8,10).
Pre-registered bars in docs/amendments/jep459_more_compute_boundary.md.
"""
import json
from pathlib import Path
import numpy as np

P = 18
M = 192
N_TR, N_TE = 5000, 1000
EPOCHS = 20000
SIGMA = 0.1
LR = 0.05
CLIP = 1.0
KS = [6, 8, 10]


def _data(rng, n, k):
    X = rng.choice([-1.0, 1.0], size=(n, P))
    return X, np.prod(X[:, :k], axis=1)


def _clip(g):
    nrm = np.linalg.norm(g)
    return g * (CLIP / nrm) if nrm > CLIP else g


def _train(rng, Xtr, ytr):
    W1 = rng.standard_normal((P, M)) / np.sqrt(P); b1 = np.zeros(M)
    w2 = rng.standard_normal(M) / np.sqrt(M); b2 = 0.0
    N = Xtr.shape[0]
    for _ in range(EPOCHS):
        pre = Xtr @ W1 + b1
        h = np.tanh(pre); o = h @ w2 + b2; err = o - ytr
        w2 -= LR * _clip(h.T @ (2.0 * err / N)); b2 -= LR * (2.0 * err / N).sum()
        xi = rng.standard_normal((N, M))
        hpert = np.tanh(pre + SIGMA * xi)
        dL = (hpert @ w2 + b2 - ytr) ** 2 - (o - ytr) ** 2
        mod = (xi * dL[:, None]) / (SIGMA ** 2)
        W1 -= LR * _clip(Xtr.T @ mod / N); b1 -= LR * mod.mean(axis=0)
    return (W1, b1, w2, b2)


def _acc(net, X, y):
    W1, b1, w2, b2 = net
    return float((np.sign(np.tanh(X @ W1 + b1) @ w2 + b2) == y).mean())


def _found(net, Xte, yte, rng, k):
    W1, b1, w2, b2 = net
    base = _acc(net, Xte, yte); drops = []
    for i in range(P):
        Xp = Xte.copy(); Xp[:, i] = rng.permutation(Xp[:, i])
        drops.append(base - _acc(net, Xp, yte))
    return sorted(sorted(range(P), key=lambda i: drops[i], reverse=True)[:k]) == list(range(k))


def run(seed):
    out = {}
    for k in KS:
        rng = np.random.default_rng(seed * 100 + k)
        Xtr, ytr = _data(rng, N_TR, k); Xte, yte = _data(rng, N_TE, k)
        net = _train(rng, Xtr, ytr)
        out[k] = dict(acc=_acc(net, Xte, yte), found=_found(net, Xte, yte, rng, k))
    return out


if __name__ == "__main__":
    print(f"=== JEP-459: more compute (M={M}, {EPOCHS} ep, N={N_TR}) vs local high-order boundary ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: " + " ".join(f"k{k}={R[s][k]['acc']:.2f}({'T' if R[s][k]['found'] else 'F'})" for k in KS),
              flush=True)

    J459a = all(R[s][6]['acc'] >= 0.90 for s in seeds)
    J459b = all(R[s][8]['acc'] >= 0.85 for s in seeds)
    passed = J459a and J459b
    print("\n--- VERDICT ---", flush=True)
    print(f"J459a compute fixes k=6 (>=0.90)   : {J459a}", flush=True)
    print(f"J459b boundary moves: k=8 (>=0.85) : {J459b}", flush=True)
    print(f"J459c k=10: { {s: round(R[s][10]['acc'],2) for s in seeds} }", flush=True)
    verdict = ("PASS - the local-learning wall is COMPUTE-BOUND: more compute pushes it past order-8"
               if passed else "NULL/partial - compute alone does not move the boundary as predicted")
    print(f"\nJEP-459: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP459"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): {str(k): R[s][k] for k in KS} for s in seeds},
                                                  "passed": passed, "J459a": J459a, "J459b": J459b}, indent=2, default=str))
    print("DONE", flush=True)
