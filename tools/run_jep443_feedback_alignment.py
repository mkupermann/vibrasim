"""JEP-443 — feedback alignment (Lillicrap 2016): backprop WITHOUT weight transport (fixed random
feedback B replaces w2 in the backward pass). Does it still crack order-3 parity with M=64, finding
the true triple? Reference probe toward locality; substrate stays backprop-free. Pure numpy.
Pre-registered bars in docs/amendments/jep443_feedback_alignment.md.
"""
import json
from pathlib import Path
import numpy as np

P = 18
M = 64
N_TR, N_TE = 2500, 1000
EPOCHS = 6000
LR = 0.5


def _data(rng, n):
    X = rng.choice([-1.0, 1.0], size=(n, P))
    y = X[:, 0] * X[:, 1] * X[:, 2]
    return X, y


def train_fa(rng, Xtr, ytr, M=M, epochs=EPOCHS, lr=LR):
    W1 = rng.standard_normal((P, M)) * (1.0 / np.sqrt(P)); b1 = np.zeros(M)
    w2 = rng.standard_normal(M) * (1.0 / np.sqrt(M)); b2 = 0.0
    B = rng.standard_normal(M)                     # FIXED random feedback (no weight transport)
    N = Xtr.shape[0]
    for _ in range(epochs):
        h = np.tanh(Xtr @ W1 + b1)
        o = h @ w2 + b2
        do = 2.0 * (o - ytr) / N
        dw2 = h.T @ do; db2 = do.sum()
        dh = np.outer(do, B) * (1.0 - h ** 2)      # FA: use B, not w2
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
    drops = [base - float((_predict(net, np.column_stack([rng.permutation(Xte[:, i]) if j == i else Xte[:, j]
                                                          for j in range(P)])) == yte).mean()) for i in range(P)]
    return sorted(sorted(range(P), key=lambda i: drops[i], reverse=True)[:3])


def run(seed):
    rng = np.random.default_rng(seed)
    Xtr, ytr = _data(rng, N_TR); Xte, yte = _data(rng, N_TE)
    net = train_fa(rng, Xtr, ytr)
    acc_fa = float((_predict(net, Xte) == yte).mean())
    acc_rand = random_matched(rng, Xtr, ytr, Xte, yte)
    top3 = perm_importance(net, Xte, yte, rng)
    return dict(acc_fa=acc_fa, acc_rand=acc_rand, top3=top3, found=(top3 == [0, 1, 2]))


if __name__ == "__main__":
    print("=== JEP-443: feedback alignment (no weight transport) on order-3 parity ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: FA(M=64) held-out={R[s]['acc_fa']:.3f} | matched-random={R[s]['acc_rand']:.3f} | "
              f"top-3={R[s]['top3']} (found triple={R[s]['found']})", flush=True)

    J443a = all(R[s]['acc_fa'] >= 0.90 for s in seeds)
    J443b = all(R[s]['found'] for s in seeds)
    J443c = all(R[s]['acc_fa'] >= R[s]['acc_rand'] + 0.20 for s in seeds)
    passed = J443a and J443b and J443c

    print("\n--- VERDICT ---", flush=True)
    print(f"J443a FA escapes wall (>=0.90, M=64)     : {J443a}", flush=True)
    print(f"J443b FA found the triple {{0,1,2}}        : {J443b}", flush=True)
    print(f"J443c gap is learning (FA>=rand+0.20)    : {J443c}", flush=True)
    verdict = ("PASS - feedback alignment (no weight transport) still escapes the order-3 wall and "
               "finds the interaction: a more-local rule discovers high-order structure") if passed else "NULL/partial"
    print(f"\nJEP-443: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP443"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "J443a": J443a, "J443b": J443b, "J443c": J443c}, indent=2, default=str))
    print("DONE", flush=True)
