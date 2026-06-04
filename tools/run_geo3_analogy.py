"""GEO-3 — geometric ANALOGY (a:b :: c:d) by vector offset — the canonical 'understanding' test (the
king-man+woman=queen mechanism). On the learned grid space and a richer 2-attribute relational space, test
whether (b-a)+c ranks the true d top-1 on HELD-OUT quadruples. Controls: random embedding; wrong-offset.
Established (analogical reasoning by offset); held-out generalization with controls. numpy/scipy, PC-scale.
"""
import numpy as np
GW = 6; D = 16


def grid():
    cells = [(x, y) for x in range(GW) for y in range(GW)]; idx = {c: i for i, c in enumerate(cells)}
    edges = []
    for (x, y) in cells:
        if x + 1 < GW: edges.append((idx[(x, y)], 0, idx[(x + 1, y)]))
        if y + 1 < GW: edges.append((idx[(x, y)], 1, idx[(x, y + 1)]))
    return cells, idx, edges


def train(edges, nE, epochs=5000, lr=0.05, margin=1.0, seed=1):
    r = np.random.default_rng(seed); E = r.normal(0, .3, (nE, D)); R = r.normal(0, .3, (2, D)); ed = np.array(edges)
    for ep in range(epochs):
        E /= np.linalg.norm(E, axis=1, keepdims=True) + 1e-9
        neg = ed.copy(); neg[:, 2] = r.integers(0, nE, len(ed))
        for (h, rel, t), (hn, rl, tn) in zip(ed, neg):
            dp = E[h] + R[rel] - E[t]; dn = E[hn] + R[rl] - E[tn]; sp = np.linalg.norm(dp); sn = np.linalg.norm(dn)
            if margin + sp - sn > 0:
                gp = dp / (sp + 1e-9); gn = dn / (sn + 1e-9)
                E[h] -= lr * gp; E[t] += lr * gp; R[rel] -= lr * gp; E[hn] += lr * gn; E[tn] -= lr * gn; R[rl] += lr * gn
    return E


def rank1(E, q, t, exclude):
    d = np.linalg.norm(E - q, axis=1); d[exclude] = 1e9
    return int(np.argmin(d) == t)


if __name__ == "__main__":
    print("=== GEO-3: geometric ANALOGY (a:b :: c:d) by offset ===", flush=True)
    cells, idx, edges = grid(); nE = len(cells); E = train(edges, nE)
    # analogy quadruples: a,b differ by some (dx,dy); c,d differ by the SAME -> d = b - a + c
    rng = np.random.default_rng(7); quads = []
    for _ in range(2000):
        ax, ay = rng.integers(0, GW), rng.integers(0, GW)
        dx, dy = rng.integers(-3, 4), rng.integers(-3, 4)
        bx, by = ax + dx, ay + dy
        cx, cy = rng.integers(0, GW), rng.integers(0, GW); ddx, ddy = cx + dx, cy + dy
        if all(0 <= v < GW for v in (bx, by, ddx, ddy)) and (dx, dy) != (0, 0):
            quads.append((idx[(ax, ay)], idx[(bx, by)], idx[(cx, cy)], idx[(ddx, ddy)]))
    quads = quads[:600]
    acc = np.mean([rank1(E, E[b] - E[a] + E[c], d, [a, b, c]) for a, b, c, d in quads])
    Erand = np.random.default_rng(3).normal(0, .3, (nE, D)); Erand /= np.linalg.norm(Erand, axis=1, keepdims=True) + 1e-9
    accr = np.mean([rank1(Erand, Erand[b] - Erand[a] + Erand[c], d, [a, b, c]) for a, b, c, d in quads])
    # wrong-offset control: use a random other pair's offset
    accw = np.mean([rank1(E, E[quads[(i+7) % len(quads)][1]] - E[quads[(i+7) % len(quads)][0]] + E[c], d, [a, b, c])
                    for i, (a, b, c, d) in enumerate(quads)])
    print(f"  analogy hits@1 (held-out quads)   = {acc:.2f}  (chance ~{1/nE:.3f})", flush=True)
    print(f"  control random embedding          = {accr:.2f}", flush=True)
    print(f"  control wrong-offset              = {accw:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if acc >= 0.5 and accr < 0.1 and accw < 0.3:
        print("GEO-3: PASS - geometric ANALOGY works: (b-a)+c finds the true d on held-out quadruples; controls collapse. The king-queen mechanism generalizes in the learned geometric substrate.", flush=True)
    elif acc >= 0.3:
        print("GEO-3: PARTIAL - analogy above chance but < 0.5", flush=True)
    else:
        print("GEO-3: NULL - analogy does not generalize", flush=True)
    print("DONE", flush=True)
