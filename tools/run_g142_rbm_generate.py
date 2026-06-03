"""G142 — the physical paradigm GENERATES with systematic generalization (RBM on bars-and-stripes).
An RBM (stochastic Ising, contrastive divergence) is trained on a SUBSET of bars-and-stripes patterns
(rows-all-equal OR cols-all-equal on a GxG grid). Test: does it generate VALID structured patterns, and
does it generate held-out valid patterns it never saw (generalization, not memorization)? Established
method (RBM, CD-1; bars-and-stripes is a standard generative benchmark), named as such. No LLM.
"""
import numpy as np

G = 4
N = G * G


def all_bs():
    pats = set()
    for m in range(1 << G):
        rows = np.array([[1.0 if (m >> r) & 1 else -1.0] * G for r in range(G)]).reshape(-1)
        cols = np.array([[1.0 if (m >> c) & 1 else -1.0 for c in range(G)] for _ in range(G)]).reshape(-1)
        pats.add(tuple(rows)); pats.add(tuple(cols))
    return [np.array(p) for p in pats]


def is_valid(x):
    g = x.reshape(G, G)
    rows_ok = all(len(set(g[r])) == 1 for r in range(G))
    cols_ok = all(len(set(g[:, c])) == 1 for c in range(G))
    return rows_ok or cols_ok


class RBM:
    def __init__(self, nv, nh, seed=0):
        rng = np.random.default_rng(seed)
        self.W = rng.normal(0, 0.1, (nv, nh)); self.bv = np.zeros(nv); self.bh = np.zeros(nh)
    def ph(self, v): return 1 / (1 + np.exp(-2 * (v @ self.W + self.bh)))
    def pv(self, h): return 1 / (1 + np.exp(-2 * (h @ self.W.T + self.bv)))
    def samp(self, p, rng): return np.where(rng.random(p.shape) < p, 1.0, -1.0)
    def train(self, data, epochs=2000, lr=0.05, seed=1):
        rng = np.random.default_rng(seed)
        for e in range(epochs):
            v0 = data
            h0 = self.samp(self.ph(v0), rng)
            v1 = self.samp(self.pv(h0), rng)
            h1p = self.ph(v1)
            self.W += lr * (v0.T @ self.ph(v0) - v1.T @ h1p) / len(data)
            self.bv += lr * (v0.mean(0) - v1.mean(0)); self.bh += lr * (self.ph(v0).mean(0) - h1p.mean(0))
    def gen(self, n, rng, steps=200):
        v = self.samp(np.full((n, len(self.bv)), 0.5), rng)
        for _ in range(steps):
            v = self.samp(self.pv(self.samp(self.ph(v), rng)), rng)
        return v


if __name__ == "__main__":
    print("=== G142: RBM (stochastic Ising) GENERATES bars-and-stripes (valid + novel) ===", flush=True)
    allp = all_bs(); rng = np.random.default_rng(5)
    idx = rng.permutation(len(allp)); tr = [allp[i] for i in idx[:int(0.6 * len(allp))]]
    train_set = set(tuple(p) for p in tr)
    data = np.array(tr)
    rbm = RBM(N, 16, seed=2); rbm.train(data, epochs=3000, lr=0.08, seed=3)
    gen = rbm.gen(500, np.random.default_rng(7))
    valid = [g for g in gen if is_valid(g)]
    frac_valid = len(valid) / len(gen)
    novel_valid = set(tuple(g) for g in valid) - train_set
    print(f"  trained on {len(tr)}/{len(allp)} BS patterns | generated 500 samples", flush=True)
    print(f"  fraction VALID (structured) = {frac_valid:.2f}  (random chance ~{2*(2**G)/(2**N):.4f})", flush=True)
    print(f"  distinct NOVEL valid patterns generated (held-out) = {len(novel_valid)}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if frac_valid >= 0.5 and len(novel_valid) >= 1:
        print("G142: PASS - the RBM GENERATES valid structured patterns AND novel held-out ones: systematic generative generalization, no LLM. The physical paradigm does generative AI (bounded).", flush=True)
    elif frac_valid >= 0.5:
        print("G142: PARTIAL - generates valid patterns but mostly memorized (few novel)", flush=True)
    else:
        print("G142: NULL - does not reliably generate valid structure", flush=True)
    print("DONE", flush=True)
