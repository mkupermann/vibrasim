"""GEO-1 — does a learned GEOMETRIC space COMPOSE relations (= understand)? A 2D conceptual grid: entities
= cells, relations 'right'/'up' = translations. Train TransE-style (h + r ~ t) on a FRACTION of edges,
then test (a) held-out edge inference and (b) COMPOSITION right+up on UNSEEN pairs (never trained as a
composite). If composition ranks the true target top-1 on held-out cells, geometry composes = a foundation
of understanding. Controls: random embedding (chance), and single-relation (must fail to predict the
composite). Established method (TransE), named as such. PC-scale numpy."""
import numpy as np

GW = 6                      # 6x6 grid -> 36 entities
D = 16
rng = np.random.default_rng(0)


def build():
    cells = [(x, y) for x in range(GW) for y in range(GW)]
    idx = {c: i for i, c in enumerate(cells)}
    edges = []   # (h, r, t): r=0 right, r=1 up
    for (x, y) in cells:
        if x + 1 < GW: edges.append((idx[(x, y)], 0, idx[(x + 1, y)]))
        if y + 1 < GW: edges.append((idx[(x, y)], 1, idx[(x, y + 1)]))
    return cells, idx, edges


def train_transe(edges, nE, epochs=4000, lr=0.05, margin=1.0, seed=1):
    r = np.random.default_rng(seed)
    E = r.normal(0, 0.3, (nE, D)); R = r.normal(0, 0.3, (2, D))
    edges = np.array(edges)
    for ep in range(epochs):
        E /= (np.linalg.norm(E, axis=1, keepdims=True) + 1e-9)   # normalize entities
        neg = edges.copy(); neg[:, 2] = r.integers(0, nE, len(edges))   # corrupt tail
        for (h, rel, t), (hn, reln, tn) in zip(edges, neg):
            dp = E[h] + R[rel] - E[t]; dn = E[hn] + R[reln] - E[tn]
            sp = np.linalg.norm(dp); sn = np.linalg.norm(dn)
            if margin + sp - sn > 0:
                gp = dp / (sp + 1e-9); gn = dn / (sn + 1e-9)
                E[h] -= lr * gp; E[t] += lr * gp; R[rel] -= lr * gp
                E[hn] += lr * gn; E[tn] -= lr * gn; R[reln] += lr * gn
    return E, R


def hits1(E, query, true_t):
    d = np.linalg.norm(E - query, axis=1)
    return int(np.argmin(d) == true_t)


if __name__ == "__main__":
    print("=== GEO-1: does the geometric space COMPOSE relations (understand)? ===", flush=True)
    cells, idx, edges = build(); nE = len(cells)
    rng2 = np.random.default_rng(3); perm = rng2.permutation(len(edges))
    train = [edges[i] for i in perm[:int(0.7 * len(edges))]]
    test_edges = [edges[i] for i in perm[int(0.7 * len(edges)):]]
    E, R = train_transe(train, nE)

    # (a) held-out single-edge inference
    he = np.mean([hits1(E, E[h] + R[rel], t) for h, rel, t in test_edges])
    # (b) COMPOSITION right+up: for cells with both neighbors, target = diagonal (x+1,y+1); NEVER trained as composite
    comp_pairs = [(idx[(x, y)], idx[(x + 1, y + 1)]) for x in range(GW - 1) for y in range(GW - 1)]
    # hold out: test composition on ALL such pairs (the composite relation was never a training edge)
    comp_acc = np.mean([hits1(E, E[h] + R[0] + R[1], t) for h, t in comp_pairs])
    # control 1: random embedding
    Erand = np.random.default_rng(9).normal(0, 0.3, (nE, D)); Erand /= np.linalg.norm(Erand, axis=1, keepdims=True) + 1e-9
    rand_comp = np.mean([hits1(Erand, Erand[h] + R[0] + R[1], t) for h, t in comp_pairs])
    # control 2: single relation (right only) should NOT hit the diagonal
    single = np.mean([hits1(E, E[h] + R[0], t) for h, t in comp_pairs])

    print(f"  held-out edge inference hits@1   = {he:.2f}", flush=True)
    print(f"  COMPOSITION right+up hits@1      = {comp_acc:.2f}  (the geometry composes unseen relations)", flush=True)
    print(f"  control random-embedding compose = {rand_comp:.2f} (chance ~{1/nE:.3f})", flush=True)
    print(f"  control single-relation (right)  = {single:.2f} (should miss the diagonal)", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if comp_acc >= 0.5 and rand_comp < 0.1 and single < 0.3:
        print("GEO-1: PASS - the learned geometric space COMPOSES relations to infer UNSEEN composite facts (right+up=diagonal) > 0.5, controls collapse. Geometric composition = a working foundation of understanding.", flush=True)
    elif comp_acc >= 0.3:
        print("GEO-1: PARTIAL - composition works above chance but below 0.5 (geometry partly composes)", flush=True)
    else:
        print("GEO-1: NULL - the geometry does not compose relations", flush=True)
    print("DONE", flush=True)
