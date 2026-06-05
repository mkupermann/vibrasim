"""JEP-457 — measure the high-order cost of fully-local node perturbation: sweep interaction order k
of a parity rule at fixed compute. Pre-registered bars in docs/amendments/jep457_order_scaling.md.
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
KS = [2, 3, 4, 5]


def _data(rng, n, k):
    X = rng.choice([-1.0, 1.0], size=(n, P))
    y = np.prod(X[:, :k], axis=1)
    return X, y


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


def _predict(net, X):
    W1, b1, w2, b2 = net
    return np.sign(np.tanh(X @ W1 + b1) @ w2 + b2)


def _perm(net, Xte, yte, rng, k):
    base = float((_predict(net, Xte) == yte).mean())
    drops = []
    for i in range(P):
        Xp = Xte.copy(); Xp[:, i] = rng.permutation(Xp[:, i])
        drops.append(base - float((_predict(net, Xp) == yte).mean()))
    return sorted(sorted(range(P), key=lambda i: drops[i], reverse=True)[:k]) == list(range(k))


def run(seed):
    out = {}
    for k in KS:
        rng = np.random.default_rng(seed * 100 + k)
        Xtr, ytr = _data(rng, N_TR, k); Xte, yte = _data(rng, N_TE, k)
        net = _train(rng, Xtr, ytr)
        out[k] = dict(acc=float((_predict(net, Xte) == yte).mean()), found=_perm(net, Xte, yte, rng, k))
    return out


if __name__ == "__main__":
    print(f"=== JEP-457: high-order cost of local node perturbation ({EPOCHS} epochs) ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        curve = " ".join(f"k{k}={R[s][k]['acc']:.2f}({'T' if R[s][k]['found'] else 'F'})" for k in KS)
        print(f"  seed {s}: {curve}", flush=True)

    J457a = all(R[s][5]['acc'] <= R[s][2]['acc'] - 0.15 for s in seeds)
    J457b = all(R[s][2]['acc'] >= 0.90 and R[s][3]['acc'] >= 0.90 for s in seeds)
    J457c = all(all(R[s][KS[i + 1]]['acc'] <= R[s][KS[i]]['acc'] + 0.05 for i in range(len(KS) - 1)) for s in seeds)
    passed = J457a and J457b and J457c

    print("\n--- VERDICT ---", flush=True)
    print(f"J457a high-order cost (k5 <= k2-0.15) : {J457a}", flush=True)
    print(f"J457b low order solid (k2,k3 >=0.90)  : {J457b}", flush=True)
    print(f"J457c non-increasing in k             : {J457c}", flush=True)
    verdict = ("PASS - the high-order cost is real and quantified: local discovery degrades with "
               "interaction order at fixed compute") if passed else "NULL/partial"
    print(f"\nJEP-457: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP457"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): {str(k): R[s][k] for k in KS} for s in seeds},
                                                  "passed": passed, "J457a": J457a, "J457b": J457b, "J457c": J457c},
                                                 indent=2, default=str))
    print("DONE", flush=True)
