"""JEP-444 — feedback alignment with a STABLE optimizer (fixes JEP-443 divergence). LR=0.02 +
per-block gradient-norm clipping. Does FA (no weight transport) escape order-3 parity and find the
triple? Reference probe; substrate stays backprop-free. Pre-registered bars in
docs/amendments/jep444_feedback_alignment_stable.md.
"""
import json
from pathlib import Path
import numpy as np

P = 18
M = 64
N_TR, N_TE = 2500, 1000
EPOCHS = 12000
LR = 0.02
CLIP = 1.0


def _data(rng, n):
    X = rng.choice([-1.0, 1.0], size=(n, P))
    return X, X[:, 0] * X[:, 1] * X[:, 2]


def _clip(g):
    n = np.linalg.norm(g)
    return g * (CLIP / n) if n > CLIP else g


def train_fa(rng, Xtr, ytr):
    W1 = rng.standard_normal((P, M)) / np.sqrt(P); b1 = np.zeros(M)
    w2 = rng.standard_normal(M) / np.sqrt(M); b2 = 0.0
    B = rng.standard_normal(M)
    N = Xtr.shape[0]
    for _ in range(EPOCHS):
        h = np.tanh(Xtr @ W1 + b1)
        o = h @ w2 + b2
        do = 2.0 * (o - ytr) / N
        dw2 = _clip(h.T @ do); db2 = do.sum()
        dh = np.outer(do, B) * (1.0 - h ** 2)
        dW1 = _clip(Xtr.T @ dh); db1 = dh.sum(axis=0)
        W1 -= LR * dW1; b1 -= LR * db1; w2 -= LR * dw2; b2 -= LR * db2
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
    net = train_fa(rng, Xtr, ytr)
    acc_fa = float((_predict(net, Xte) == yte).mean())
    acc_rand = random_matched(rng, Xtr, ytr, Xte, yte)
    top3 = perm_importance(net, Xte, yte, rng)
    return dict(acc_fa=acc_fa, acc_rand=acc_rand, top3=top3, found=(top3 == [0, 1, 2]))


if __name__ == "__main__":
    print("=== JEP-444: feedback alignment (stable optimizer) on order-3 parity ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: FA(M=64) held-out={R[s]['acc_fa']:.3f} | matched-random={R[s]['acc_rand']:.3f} | "
              f"top-3={R[s]['top3']} (found triple={R[s]['found']})", flush=True)

    J444a = all(R[s]['acc_fa'] >= 0.90 for s in seeds)
    J444b = all(R[s]['found'] for s in seeds)
    J444c = all(R[s]['acc_fa'] >= R[s]['acc_rand'] + 0.20 for s in seeds)
    passed = J444a and J444b and J444c

    print("\n--- VERDICT ---", flush=True)
    print(f"J444a FA escapes wall (>=0.90)        : {J444a}", flush=True)
    print(f"J444b FA found the triple {{0,1,2}}     : {J444b}", flush=True)
    print(f"J444c gap is learning (FA>=rand+0.20) : {J444c}", flush=True)
    verdict = ("PASS - feedback alignment (no weight transport) escapes the order-3 wall and finds "
               "the interaction: a more-local rule discovers high-order structure") if passed else "NULL/partial"
    print(f"\nJEP-444: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP444"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "J444a": J444a, "J444b": J444b, "J444c": J444c}, indent=2, default=str))
    print("DONE", flush=True)
