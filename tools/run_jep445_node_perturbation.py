"""JEP-445 — node perturbation (3-factor Hebbian, fully local: no backprop, no weight transport, no
derivative through the hidden layer) on order-3 parity. Hidden weights update from pre-synaptic
activity x perturbation x a single global scalar error modulator. Reference probe; substrate path
unchanged. Pure numpy. Pre-registered bars in docs/amendments/jep445_local_node_perturbation.md.
"""
import json
from pathlib import Path
import numpy as np

P = 18
M = 64
N_TR, N_TE = 2500, 1000
EPOCHS = 20000
SIGMA = 0.1
LR = 0.05
CLIP = 1.0


def _data(rng, n):
    X = rng.choice([-1.0, 1.0], size=(n, P))
    return X, X[:, 0] * X[:, 1] * X[:, 2]


def _clip(g):
    nrm = np.linalg.norm(g)
    return g * (CLIP / nrm) if nrm > CLIP else g


def train_nodepert(rng, Xtr, ytr):
    W1 = rng.standard_normal((P, M)) / np.sqrt(P); b1 = np.zeros(M)
    w2 = rng.standard_normal(M) / np.sqrt(M); b2 = 0.0
    N = Xtr.shape[0]
    for _ in range(EPOCHS):
        pre = Xtr @ W1 + b1
        h = np.tanh(pre)
        o = h @ w2 + b2
        err = o - ytr
        # output weights: local delta rule
        w2 -= LR * _clip(h.T @ (2.0 * err / N)); b2 -= LR * (2.0 * err / N).sum()
        # hidden weights: node perturbation with a global scalar modulator
        xi = rng.standard_normal((N, M))
        h_pert = np.tanh(pre + SIGMA * xi)
        o_pert = h_pert @ w2 + b2
        dL = (o_pert - ytr) ** 2 - (o - ytr) ** 2          # per-sample global scalar
        mod = (xi * dL[:, None]) / (SIGMA ** 2)            # 3rd factor x perturbation
        dW1 = _clip(Xtr.T @ mod / N); db1 = mod.mean(axis=0)
        W1 -= LR * dW1; b1 -= LR * db1
    return (W1, b1, w2, b2)


def _predict(net, X):
    W1, b1, w2, b2 = net
    return np.sign(np.tanh(X @ W1 + b1) @ w2 + b2)


def random_matched(rng, Xtr, ytr, Xte, yte, ridge=1.0):
    R = rng.standard_normal((P, M)); b = rng.standard_normal(M)
    Ptr = np.tanh(Xtr @ R + b); Pte = np.tanh(Xte @ R + b)
    A = Ptr.T @ Ptr + ridge * np.eye(M); w = np.linalg.solve(A, Ptr.T @ ytr)
    return float((np.sign(Pte @ w) == yte).mean())


def perm_importance(net, Xte, yte, rng):
    base = float((_predict(net, Xte) == yte).mean())
    drops = []
    for i in range(P):
        Xp = Xte.copy(); Xp[:, i] = rng.permutation(Xp[:, i])
        drops.append(base - float((_predict(net, Xp) == yte).mean()))
    return sorted(sorted(range(P), key=lambda i: drops[i], reverse=True)[:3])


def run(seed):
    rng = np.random.default_rng(seed)
    Xtr, ytr = _data(rng, N_TR); Xte, yte = _data(rng, N_TE)
    net = train_nodepert(rng, Xtr, ytr)
    acc = float((_predict(net, Xte) == yte).mean())
    acc_rand = random_matched(rng, Xtr, ytr, Xte, yte)
    top3 = perm_importance(net, Xte, yte, rng)
    return dict(acc=acc, acc_rand=acc_rand, top3=top3, found=(top3 == [0, 1, 2]))


if __name__ == "__main__":
    print("=== JEP-445: node perturbation (fully-local 3-factor) on order-3 parity ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: node-pert(M=64) held-out={R[s]['acc']:.3f} | matched-random={R[s]['acc_rand']:.3f} | "
              f"top-3={R[s]['top3']} (found triple={R[s]['found']})", flush=True)

    J445a = all(R[s]['acc'] >= 0.90 for s in seeds)
    J445b = all(R[s]['found'] for s in seeds)
    J445c = all(R[s]['acc'] >= R[s]['acc_rand'] + 0.20 for s in seeds)
    passed = J445a and J445b and J445c

    print("\n--- VERDICT ---", flush=True)
    print(f"J445a fully-local escapes wall (>=0.90)  : {J445a}", flush=True)
    print(f"J445b found the triple {{0,1,2}}           : {J445b}", flush=True)
    print(f"J445c gap is learning (>=rand+0.20)      : {J445c}", flush=True)
    verdict = ("PASS - a fully-local 3-factor rule discovers the order-3 interaction: the substrate's "
               "own local primitives could in principle do targeted high-order discovery") if passed else "NULL/partial"
    print(f"\nJEP-445: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP445"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "J445a": J445a, "J445b": J445b, "J445c": J445c}, indent=2, default=str))
    print("DONE", flush=True)
