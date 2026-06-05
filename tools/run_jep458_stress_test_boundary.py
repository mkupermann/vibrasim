"""JEP-458 — stress-test JEP-457's surprise: push interaction order (k up to 10) and input size (P up
to 50) at FIXED compute to locate where fully-local node-perturbation learning actually breaks.
Pre-registered bars in docs/amendments/jep458_stress_test_boundary.md.
"""
import json
from pathlib import Path
import numpy as np

M = 64
N_TR, N_TE = 2500, 1000
EPOCHS = 5000
SIGMA = 0.1
LR = 0.05
CLIP = 1.0
ORDER_SWEEP = [(18, 5), (18, 6), (18, 8), (18, 10)]
WIDTH_SWEEP = [(30, 5), (50, 5)]


def _data(rng, n, P, k):
    X = rng.choice([-1.0, 1.0], size=(n, P))
    return X, np.prod(X[:, :k], axis=1)


def _clip(g):
    nrm = np.linalg.norm(g)
    return g * (CLIP / nrm) if nrm > CLIP else g


def _train(rng, Xtr, ytr, P):
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


def _eval(seed, P, k):
    rng = np.random.default_rng(seed * 1000 + P * 10 + k)
    Xtr, ytr = _data(rng, N_TR, P, k); Xte, yte = _data(rng, N_TE, P, k)
    return _acc(_train(rng, Xtr, ytr, P), Xte, yte)


def run(seed):
    order = {f"P{P}k{k}": _eval(seed, P, k) for (P, k) in ORDER_SWEEP}
    width = {f"P{P}k{k}": _eval(seed, P, k) for (P, k) in WIDTH_SWEEP}
    return dict(order=order, width=width)


if __name__ == "__main__":
    print(f"=== JEP-458: stress-test local high-order learning ({EPOCHS} epochs, M={M}) ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s} order: { {k: round(v,2) for k,v in R[s]['order'].items()} }", flush=True)
        print(f"  seed {s} width: { {k: round(v,2) for k,v in R[s]['width'].items()} }", flush=True)

    allvals = {s: {**R[s]['order'], **R[s]['width']} for s in seeds}
    J458a = all(any(v <= 0.75 for v in allvals[s].values()) for s in seeds)
    J458b = all(R[s]['order']['P18k5'] >= 0.90 for s in seeds)
    # boundary report
    boundary = {}
    for s in seeds:
        ob = next((f"P18k{k}" for (P, k) in ORDER_SWEEP if R[s]['order'][f"P{P}k{k}"] < 0.75), "none<=k10")
        wb = next((f"P{P}k5" for (P, k) in WIDTH_SWEEP if R[s]['width'][f"P{P}k{k}"] < 0.75), "none<=P50")
        boundary[s] = dict(order_break=ob, width_break=wb)
    passed = J458a and J458b

    print("\n--- VERDICT ---", flush=True)
    print(f"J458a a boundary exists (some setting <=0.75) : {J458a}", flush=True)
    print(f"J458b robust below (P18k5>=0.90)              : {J458b}", flush=True)
    print(f"J458c boundary: {boundary}", flush=True)
    verdict = ("PASS - located the real wall: local high-order learning breaks at high enough order/P "
               "at fixed compute") if passed else ("NULL/partial - no break observed (finding even more robust) "
                                                    "OR k5 not solid")
    print(f"\nJEP-458: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP458"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "J458a": J458a, "J458b": J458b, "boundary": {str(s): boundary[s] for s in seeds}},
                                                 indent=2, default=str))
    print("DONE", flush=True)
