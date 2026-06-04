"""GEO-12 — genuine learning of NEW structured knowledge (not from any LLM). Build a family KG where some
relations are DERIVED by rules (grandparent = parent∘parent; sibling shares a parent). Train a relational
embedding (TransE-style, from scratch) on BASE facts (parent) only; HOLD OUT all grandparent facts; test
whether the trained geometry INFERS grandparents by COMPOSING the learned parent relation. This is genuine
learning+understanding of new structure (vs GEO-10 arbitrary facts = no structure; vs frozen LLM = no new
knowledge). CPU, fast."""
import numpy as np
D = 24


def family(depth=4, branch=2):
    # build a tree: node 0 root; each node has `branch` children up to depth
    nodes = [0]; parent = {0: None}; children = {0: []}; nxt = 1; level = {0: 0}
    frontier = [0]
    for d in range(depth):
        new = []
        for p in frontier:
            for _ in range(branch):
                parent[nxt] = p; children.setdefault(p, []).append(nxt); children[nxt] = []
                level[nxt] = d + 1; nodes.append(nxt); new.append(nxt); nxt += 1
        frontier = new
    parent_edges = [(c, p) for c, p in parent.items() if p is not None]      # child -> parent
    grand = [(c, parent[p]) for c, p in parent.items() if p is not None and parent.get(p) is not None]  # child->grandparent
    return len(nodes), parent_edges, grand


def train_transe(edges, nE, epochs=6000, lr=0.05, margin=1.0, seed=1):
    r = np.random.default_rng(seed); E = r.normal(0, .3, (nE, D)); rp = r.normal(0, .3, D); ed = np.array(edges)
    for ep in range(epochs):
        E /= np.linalg.norm(E, axis=1, keepdims=True) + 1e-9
        neg = ed.copy(); neg[:, 1] = r.integers(0, nE, len(ed))
        for (h, t), (hn, tn) in zip(ed, neg):
            dp = E[h] + rp - E[t]; dn = E[hn] + rp - E[tn]; sp = np.linalg.norm(dp); sn = np.linalg.norm(dn)
            if margin + sp - sn > 0:
                gp = dp/(sp+1e-9); gn = dn/(sn+1e-9)
                E[h] -= lr*gp; E[t] += lr*gp; rp -= lr*gp; E[hn] += lr*gn; E[tn] -= lr*gn; rp += lr*gn
    return E, rp


def h1(E, q, t):
    return int(np.argmin(np.linalg.norm(E - q, axis=1)) == t)


if __name__ == "__main__":
    print("=== GEO-12: learn NEW structured knowledge from scratch + infer derived facts ===", flush=True)
    nE, parent_edges, grand = family(depth=5, branch=2)
    print(f"  family: {nE} people, {len(parent_edges)} parent-edges, {len(grand)} grandparent facts (HELD OUT)", flush=True)
    E, rp = train_transe(parent_edges, nE)              # train on PARENT only
    # held-out grandparent inference via composition: child + 2*parent_relation -> grandparent
    g2 = np.mean([h1(E, E[c] + 2*rp, gp) for c, gp in grand])
    # single parent (no composition) should hit the PARENT, not grandparent
    g1 = np.mean([h1(E, E[c] + rp, gp) for c, gp in grand])
    # known parent inference (sanity, held in)
    ptr = np.mean([h1(E, E[c] + rp, p) for c, p in parent_edges])
    print(f"  trained parent inference (sanity)            hits@1 = {ptr:.2f}", flush=True)
    print(f"  HELD-OUT grandparent via composition (2*rp)  hits@1 = {g2:.2f}", flush=True)
    print(f"  single-parent control (should miss grandpa)  hits@1 = {g1:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if g2 >= 0.5 and g1 < 0.2:
        print("GEO-12: PASS - trained-from-scratch geometry LEARNS new structure and INFERS held-out grandparent facts by COMPOSING the learned parent relation. Genuine learning+understanding of NEW knowledge (no LLM).", flush=True)
    elif g2 >= 0.3:
        print("GEO-12: PARTIAL - composition infers some grandparents (above the single-parent control) but < 0.5", flush=True)
    else:
        print("GEO-12: NULL - training did not yield compositional inference of held-out facts", flush=True)
    print("DONE", flush=True)
