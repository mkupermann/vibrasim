"""JEP-442 — REFERENCE BASELINE (not a substrate mechanism): does a LEARNED 2-layer net (full
backprop, non-local) crack order-3 parity with few units where local/cheap routes failed? Measures
the non-local upper bound to sharpen the open problem to local-vs-non-local. Pure numpy backprop.
Pre-registered bars in docs/amendments/jep442_backprop_reference.md.
"""
import json
from pathlib import Path
import numpy as np

P = 18
M = 64
N_TR, N_TE = 2500, 1000
EPOCHS = 2000
LR = 0.5


def _data(rng, n):
    X = rng.choice([-1.0, 1.0], size=(n, P))
    y = X[:, 0] * X[:, 1] * X[:, 2]
    return X, y


def train_backprop(rng, Xtr, ytr, Xte, M=M, epochs=EPOCHS, lr=LR):
    W1 = rng.standard_normal((P, M)) * (1.0 / np.sqrt(P)); b1 = np.zeros(M)
    w2 = rng.standard_normal(M) * (1.0 / np.sqrt(M)); b2 = 0.0
    N = Xtr.shape[0]
    for _ in range(epochs):
        h = np.tanh(Xtr @ W1 + b1)          # (N,M)
        o = h @ w2 + b2                     # (N,)
        do = 2.0 * (o - ytr) / N
        dw2 = h.T @ do; db2 = do.sum()
        dh = np.outer(do, w2) * (1.0 - h ** 2)
        dW1 = Xtr.T @ dh; db1 = dh.sum(axis=0)
        W1 -= lr * dW1; b1 -= lr * db1; w2 -= lr * dw2; b2 -= lr * db2
    return (W1, b1, w2, b2)


def _predict(net, X):
    W1, b1, w2, b2 = net
    return np.sign(np.tanh(X @ W1 + b1) @ w2 + b2)


def random_matched(rng, Xtr, ytr, Xte, yte, M=M, ridge=1.0):
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
    top3 = sorted(range(P), key=lambda i: drops[i], reverse=True)[:3]
    return sorted(top3)


def run(seed):
    rng = np.random.default_rng(seed)
    Xtr, ytr = _data(rng, N_TR); Xte, yte = _data(rng, N_TE)
    net = train_backprop(rng, Xtr, ytr, Xte)
    acc_bp = float((_predict(net, Xte) == yte).mean())
    acc_rand = random_matched(rng, Xtr, ytr, Xte, yte)
    top3 = perm_importance(net, Xte, yte, rng)
    return dict(acc_bp=acc_bp, acc_rand=acc_rand, top3=top3, found=(top3 == [0, 1, 2]))


if __name__ == "__main__":
    print("=== JEP-442: non-local upper bound — learned (backprop) vs matched random, order-3 parity ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: backprop(M=64) held-out={R[s]['acc_bp']:.3f} | matched-random={R[s]['acc_rand']:.3f} | "
              f"top-3 features={R[s]['top3']} (found triple={R[s]['found']})", flush=True)

    J442a = all(R[s]['acc_bp'] >= 0.95 for s in seeds)
    J442b = all(R[s]['acc_rand'] <= 0.70 for s in seeds)
    J442c = all(R[s]['found'] for s in seeds)
    passed = J442a and J442b and J442c

    print("\n--- VERDICT ---", flush=True)
    print(f"J442a learned escapes C(P,k) (bp>=0.95, M=64): {J442a}", flush=True)
    print(f"J442b gap is learning (random<=0.70)         : {J442b}", flush=True)
    print(f"J442c found the true triple {{0,1,2}}          : {J442c}", flush=True)
    verdict = ("PASS - learned features crack order-3 with M<<C(P,3) and concentrate on the true "
               "triple; matched random fails -> the escape is non-local LEARNING") if passed else "NULL/partial"
    print(f"\nJEP-442: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP442"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "J442a": J442a, "J442b": J442b, "J442c": J442c}, indent=2, default=str))
    print("DONE", flush=True)
