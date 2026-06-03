"""G143 — does DEPTH help the no-LLM physical paradigm? 1-layer RBM vs 2-layer DBN (stacked RBMs, greedy
layer-wise) on a harder generative task (bars-and-stripes 5x5). Tests headroom: if the deeper model
generates more valid+novel patterns, the no-LLM path scales via depth (the pre-transformer route). If not,
the shallow ceiling is the limit. Established methods (RBM/DBN), named as such. No LLM."""
import numpy as np

G = 5; N = G * G


def all_bs():
    pats = set()
    for m in range(1 << G):
        rows = np.array([[1.0 if (m >> r) & 1 else -1.0] * G for r in range(G)]).reshape(-1)
        cols = np.array([[1.0 if (m >> c) & 1 else -1.0 for c in range(G)] for _ in range(G)]).reshape(-1)
        pats.add(tuple(rows)); pats.add(tuple(cols))
    return [np.array(p) for p in pats]


def is_valid(x):
    g = x.reshape(G, G)
    return all(len(set(g[r])) == 1 for r in range(G)) or all(len(set(g[:, c])) == 1 for c in range(G))


class RBM:
    def __init__(s, nv, nh, seed=0):
        r = np.random.default_rng(seed); s.W = r.normal(0, 0.1, (nv, nh)); s.bv = np.zeros(nv); s.bh = np.zeros(nh)
    def ph(s, v): return 1 / (1 + np.exp(-2 * (v @ s.W + s.bh)))
    def pv(s, h): return 1 / (1 + np.exp(-2 * (h @ s.W.T + s.bv)))
    def sm(s, p, r): return np.where(r.random(p.shape) < p, 1.0, -1.0)
    def train(s, data, epochs, lr, seed):
        r = np.random.default_rng(seed)
        for e in range(epochs):
            v0 = data; h0 = s.sm(s.ph(v0), r); v1 = s.sm(s.pv(h0), r); h1 = s.ph(v1)
            s.W += lr * (v0.T @ s.ph(v0) - v1.T @ h1) / len(data)
            s.bv += lr * (v0.mean(0) - v1.mean(0)); s.bh += lr * (s.ph(v0).mean(0) - h1.mean(0))
    def up(s, v, r): return s.sm(s.ph(v), r)
    def gen_top(s, n, r, steps=300):
        v = s.sm(np.full((n, len(s.bv)), .5), r)
        for _ in range(steps): v = s.sm(s.pv(s.sm(s.ph(v), r)), r)
        return v


def evalgen(samps, train_set):
    valid = [g for g in samps if is_valid(g)]
    fv = len(valid) / len(samps)
    novel = set(tuple(g) for g in valid) - train_set
    return fv, len(novel)


if __name__ == "__main__":
    print("=== G143: depth test — 1-layer RBM vs 2-layer DBN (bars-and-stripes 5x5) ===", flush=True)
    allp = all_bs(); rng = np.random.default_rng(5)
    idx = rng.permutation(len(allp)); tr = [allp[i] for i in idx[:int(0.6 * len(allp))]]
    tset = set(tuple(p) for p in tr); data = np.array(tr)

    rbm1 = RBM(N, 25, seed=2); rbm1.train(data, 4000, 0.08, 3)
    fv1, nv1 = evalgen(rbm1.gen_top(800, np.random.default_rng(7)), tset)

    # DBN: layer1 RBM, then layer2 RBM on hidden activations; generate top-down
    l1 = RBM(N, 25, seed=2); l1.train(data, 4000, 0.08, 3)
    r = np.random.default_rng(11); h1 = l1.up(data, r)
    l2 = RBM(25, 25, seed=4); l2.train(h1, 4000, 0.08, 5)
    top = l2.gen_top(800, np.random.default_rng(13))      # sample top layer
    vis = l1.sm(l1.pv(top), np.random.default_rng(14))     # propagate down to visible
    fv2, nv2 = evalgen(vis, tset)

    print(f"  1-layer RBM: valid={fv1:.2f}  novel-valid={nv1}", flush=True)
    print(f"  2-layer DBN: valid={fv2:.2f}  novel-valid={nv2}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if fv2 >= fv1 + 0.10 or nv2 >= nv1 + 3:
        print("G143: PASS - depth HELPS: the deeper model generates more valid/novel patterns -> the no-LLM path has headroom via depth (the pre-transformer route)", flush=True)
    else:
        print("G143: NULL - depth does NOT clearly help on this task; the shallow result is ~ the ceiling here (honest: DBNs are hard to train and were superseded by transformers)", flush=True)
    print("DONE", flush=True)
