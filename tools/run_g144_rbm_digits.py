"""G144 — does the no-LLM physical stack help on REAL data? RBM (binary, CD-1) unsupervised feature
learning on real handwritten digits + a linear readout, vs a raw-pixel linear baseline. If RBM features
beat raw-linear, it's genuine representation learning (useful on real data); if not, it's toy-bound.
Established methods (RBM + linear/softmax), named as such. No LLM."""
import numpy as np
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

rng = np.random.default_rng(0)
d = load_digits()
X = (d.data > 6).astype(float)          # binarize 8x8 pixels
y = d.target
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)


class RBM:
    def __init__(s, nv, nh, seed=0):
        r = np.random.default_rng(seed); s.W = r.normal(0, 0.1, (nv, nh)); s.bv = np.zeros(nv); s.bh = np.zeros(nh)
    def ph(s, v): return 1 / (1 + np.exp(-(v @ s.W + s.bh)))
    def pv(s, h): return 1 / (1 + np.exp(-(h @ s.W.T + s.bv)))
    def train(s, data, epochs=300, lr=0.1, bs=64, seed=1):
        r = np.random.default_rng(seed)
        for e in range(epochs):
            idx = r.permutation(len(data))
            for b in range(0, len(data), bs):
                v0 = data[idx[b:b+bs]]
                p0 = s.ph(v0); h0 = (r.random(p0.shape) < p0).astype(float)
                v1 = (r.random(v0.shape) < s.pv(h0)).astype(float); p1 = s.ph(v1)
                s.W += lr * (v0.T @ p0 - v1.T @ p1) / len(v0)
                s.bv += lr * (v0 - v1).mean(0); s.bh += lr * (p0 - p1).mean(0)


if __name__ == "__main__":
    print("=== G144: RBM features on REAL digits vs raw-pixel linear ===", flush=True)
    # baseline: linear on raw pixels
    base = LogisticRegression(max_iter=2000, C=1.0).fit(Xtr, ytr)
    acc_raw = base.score(Xte, yte)
    # RBM unsupervised features + linear readout
    rbm = RBM(64, 128, seed=2); rbm.train(Xtr, epochs=300, lr=0.1, seed=3)
    Htr, Hte = rbm.ph(Xtr), rbm.ph(Xte)
    clf = LogisticRegression(max_iter=2000, C=1.0).fit(Htr, ytr)
    acc_rbm = clf.score(Hte, yte)
    print(f"  raw-pixel linear  test acc = {acc_raw:.3f}", flush=True)
    print(f"  RBM-features linear test acc = {acc_rbm:.3f}  (delta {acc_rbm-acc_raw:+.3f})", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if acc_rbm >= acc_raw + 0.02:
        print(f"G144: PASS - RBM unsupervised features BEAT raw-pixel linear on real digits (+{acc_rbm-acc_raw:.3f}); the no-LLM physical stack does useful representation learning on real data", flush=True)
    elif acc_rbm >= acc_raw - 0.02:
        print("G144: NULL(tie) - RBM features ~ raw-pixel linear; no representation-learning benefit here (the energy-based features don't add over raw pixels on this dataset)", flush=True)
    else:
        print("G144: NULL - RBM features WORSE than raw linear", flush=True)
    print("DONE", flush=True)
