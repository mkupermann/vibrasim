"""GEO-2 — robustness of geometric understanding: INVERSE relations (left = -right, never trained) and
MULTI-HOP composed paths (accuracy vs path length). Train TransE on right/up edges only; test inference of
left/down (via negated translations) and k-step random paths. Tests whether the learned geometry supports
inverses and deep composition = robust relational reasoning. Established (TransE); held-out generalization."""
import numpy as np

GW = 6; D = 16


def build():
    cells = [(x, y) for x in range(GW) for y in range(GW)]; idx = {c: i for i, c in enumerate(cells)}
    edges = []
    for (x, y) in cells:
        if x + 1 < GW: edges.append((idx[(x, y)], 0, idx[(x + 1, y)]))
        if y + 1 < GW: edges.append((idx[(x, y)], 1, idx[(x, y + 1)]))
    return cells, idx, edges


def train(edges, nE, epochs=5000, lr=0.05, margin=1.0, seed=1):
    r = np.random.default_rng(seed); E = r.normal(0, 0.3, (nE, D)); R = r.normal(0, 0.3, (2, D)); edges = np.array(edges)
    for ep in range(epochs):
        E /= np.linalg.norm(E, axis=1, keepdims=True) + 1e-9
        neg = edges.copy(); neg[:, 2] = r.integers(0, nE, len(edges))
        for (h, rel, t), (hn, reln, tn) in zip(edges, neg):
            dp = E[h] + R[rel] - E[t]; dn = E[hn] + R[reln] - E[tn]
            sp = np.linalg.norm(dp); sn = np.linalg.norm(dn)
            if margin + sp - sn > 0:
                gp = dp / (sp + 1e-9); gn = dn / (sn + 1e-9)
                E[h] -= lr * gp; E[t] += lr * gp; R[rel] -= lr * gp
                E[hn] += lr * gn; E[tn] -= lr * gn; R[reln] += lr * gn
    return E, R


def h1(E, q, t): return int(np.argmin(np.linalg.norm(E - q, axis=1)) == t)


if __name__ == "__main__":
    print("=== GEO-2: inverses + multi-hop geometric reasoning ===", flush=True)
    cells, idx, edges = build(); nE = len(cells); E, R = train(edges, nE)
    moves = {0: (R[0], (1, 0)), 1: (R[1], (0, 1)), 2: (-R[0], (-1, 0)), 3: (-R[1], (0, -1))}  # right/up/left/down

    # (a) INVERSES: left/down via -R, never trained as edges
    inv = []
    for (x, y) in cells:
        if x - 1 >= 0: inv.append(h1(E, E[idx[(x, y)]] - R[0], idx[(x - 1, y)]))
        if y - 1 >= 0: inv.append(h1(E, E[idx[(x, y)]] - R[1], idx[(x, y - 1)]))
    inv_acc = np.mean(inv)

    # (b) MULTI-HOP: random length-k paths staying in-grid; infer endpoint by summing translations
    rng = np.random.default_rng(5)
    print(f"  INVERSE (left/down via -R) hits@1 = {inv_acc:.2f}", flush=True)
    khit = {}
    for k in [1, 2, 3, 4, 5]:
        acc = []
        for _ in range(300):
            x, y = rng.integers(0, GW), rng.integers(0, GW); q = E[idx[(x, y)]].copy(); cx, cy = x, y; ok = True
            for _h in range(k):
                valid = [m for m in moves if 0 <= cx + moves[m][1][0] < GW and 0 <= cy + moves[m][1][1] < GW]
                m = rng.choice(valid); q = q + moves[m][0]; cx += moves[m][1][0]; cy += moves[m][1][1]
            acc.append(h1(E, q, idx[(cx, cy)]))
        khit[k] = np.mean(acc)
        print(f"  {k}-hop path hits@1 = {khit[k]:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    ok = inv_acc >= 0.5 and khit[1] >= 0.5 and khit[4] >= 0.3
    if ok:
        print("GEO-2: PASS - the geometry supports INVERSE relations (untrained) and MULTI-HOP composition; relational reasoning is robust over paths", flush=True)
    else:
        print("GEO-2: PARTIAL/NULL - inverses or long-path composition degrade (see numbers)", flush=True)
    print("DONE", flush=True)
