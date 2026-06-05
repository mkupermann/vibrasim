"""JEP-460 — is the order-8 hard wall the known exponential parity-width law? Sweep hidden width M at
fixed order-8 parity with fully-local node perturbation. If solving crosses near M~2^8=256, the wall
is representational width (explained, not new science). Pre-registered bars in
docs/amendments/jep460_width_wall.md.
"""
import json
from pathlib import Path
import numpy as np

P = 18
K = 8
N_TR, N_TE = 3000, 1000
EPOCHS = 8000
SIGMA = 0.1
LR = 0.05
CLIP = 1.0
MS = [128, 256, 384, 512]


def _data(rng, n):
    X = rng.choice([-1.0, 1.0], size=(n, P))
    return X, np.prod(X[:, :K], axis=1)


def _clip(g):
    nrm = np.linalg.norm(g)
    return g * (CLIP / nrm) if nrm > CLIP else g


def _train(rng, Xtr, ytr, M):
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


def run(seed):
    out = {}
    for M in MS:
        rng = np.random.default_rng(seed * 1000 + M)
        Xtr, ytr = _data(rng, N_TR); Xte, yte = _data(rng, N_TE)
        out[M] = _acc(_train(rng, Xtr, ytr, M), Xte, yte)
    return out


if __name__ == "__main__":
    print(f"=== JEP-460: order-{K} parity vs width M ({EPOCHS} ep) — testing the 2^k width law ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: " + " ".join(f"M{M}={R[s][M]:.2f}" for M in MS) + f"  (2^{K}={2**K})", flush=True)

    J460a = all(R[s][128] <= 0.65 for s in seeds)
    J460b = all(R[s][512] >= 0.85 for s in seeds)
    J460c = all(R[s][256] > R[s][128] + 0.15 for s in seeds)
    passed = J460a and J460b and J460c

    print("\n--- VERDICT ---", flush=True)
    print(f"J460a M=128 fails (<2^8)        : {J460a}", flush=True)
    print(f"J460b M=512 solves (>=0.85)     : {J460b}", flush=True)
    print(f"J460c crossing near 2^8=256     : {J460c}", flush=True)
    if passed:
        verdict = "PASS - the order-8 wall is the KNOWN exponential parity-width law (explained, NOT new science)"
    elif all(R[s][512] < 0.7 for s in seeds):
        verdict = "NULL - M=512 also fails: the wall is NOT mere width (deeper limit, chase it)"
    else:
        verdict = "PARTIAL - width helps but crossing not as predicted"
    print(f"\nJEP-460: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP460"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): {str(M): R[s][M] for M in MS} for s in seeds},
                                                  "passed": passed, "J460a": J460a, "J460b": J460b, "J460c": J460c},
                                                 indent=2, default=str))
    print("DONE", flush=True)
