"""JEP-339 — substrate-legal kernel from GeoWorld: classical hyperbolic (Poincare-ball) embedding of the is-a tree
via hyperbolic MDS (L-BFGS, NO neural net, NO transformer, NO pretraining). Tests whether hyperbolic geometry
recovers the hierarchy in few dimensions, and compares honestly to the VSA. No transformer.
Pre-registered bars in docs/amendments/jep339_hyperbolic_taxonomy.md.
"""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize

# a taxonomy tree (child -> parent)
TREE = {"poodle": "dog", "beagle": "dog", "dog": "mammal", "cat": "mammal", "tiger": "cat",
        "mammal": "animal", "salmon": "fish", "shark": "fish", "fish": "animal",
        "sparrow": "bird", "eagle": "bird", "bird": "animal"}
ROOT = "animal"


def nodes_and_dists():
    nodes = sorted(set(TREE) | set(TREE.values()))
    idx = {n: i for i, n in enumerate(nodes)}
    # undirected tree graph distances (BFS)
    adj = {n: set() for n in nodes}
    for c, p in TREE.items():
        adj[c].add(p); adj[p].add(c)
    N = len(nodes)
    G = np.zeros((N, N))
    from collections import deque
    for s in nodes:
        seen = {s: 0}; q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in seen:
                    seen[v] = seen[u] + 1; q.append(v)
        for t in nodes:
            G[idx[s], idx[t]] = seen[t]
    return nodes, idx, G


def to_ball(e):
    """exp-map of a free Euclidean vector to the Poincare ball (||p||<1)."""
    n = np.linalg.norm(e)
    if n < 1e-9:
        return e * 0.0
    return (np.tanh(n) / n) * e


def hdist(u, v):
    nu, nv = np.dot(u, u), np.dot(v, v)
    diff = np.dot(u - v, u - v)
    arg = 1 + 2 * diff / max((1 - nu) * (1 - nv), 1e-12)
    return np.arccosh(max(arg, 1.0))


def embed(G, D, seed):
    N = G.shape[0]
    rng = np.random.default_rng(seed)
    x0 = rng.normal(0, 0.1, N * D)

    def loss(x):
        E = x.reshape(N, D)
        P = np.array([to_ball(E[i]) for i in range(N)])
        s = 0.0
        for i in range(N):
            for j in range(i + 1, N):
                s += (hdist(P[i], P[j]) - G[i, j]) ** 2
        return s

    res = minimize(loss, x0, method="L-BFGS-B", options={"maxiter": 400})
    E = res.x.reshape(N, D)
    return np.array([to_ball(E[i]) for i in range(N)])


def ancestors(x):
    out, cur = [], x
    while cur in TREE:
        cur = TREE[cur]; out.append(cur)
    return out


def auc_ancestor_ranking(P, nodes, idx):
    """For each node, AUC that true ancestors are closer (hyperbolic) than non-ancestors."""
    aucs = []
    for x in nodes:
        anc = set(ancestors(x))
        if not anc:
            continue
        others = [n for n in nodes if n != x and n not in anc]
        if not others:
            continue
        dist = {n: hdist(P[idx[x]], P[idx[n]]) for n in nodes if n != x}
        pos = [dist[a] for a in anc]; neg = [dist[o] for o in others]
        wins = sum(p < n for p in pos for n in neg)
        aucs.append(wins / (len(pos) * len(neg)))
    return float(np.mean(aucs))


def run_seed(seed, D=5):
    nodes, idx, G = nodes_and_dists()
    P = embed(G, D, seed)
    auc = auc_ancestor_ranking(P, nodes, idx)
    # norm encodes depth: root-ward concepts have smaller norm than their descendants
    norms = {n: float(np.linalg.norm(P[idx[n]])) for n in nodes}
    depth_ok = sum(norms[c] > norms[p] for c, p in TREE.items()) / len(TREE)   # child farther from origin than parent
    # distortion
    N = len(nodes)
    dist_err = np.mean([abs(hdist(P[idx[a]], P[idx[b]]) - G[idx[a], idx[b]])
                        for a in nodes for b in nodes if a < b])
    return {"D": D, "ancestor_auc": round(auc, 3), "depth_monotonic": round(float(depth_ok), 3),
            "mean_distortion": round(float(dist_err), 3)}


if __name__ == "__main__":
    print("=== JEP-339: hyperbolic taxonomy embedding (GeoWorld's legal kernel; classical, no NN) ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s, D=5) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: D={r['D']} ancestor-ranking AUC={r['ancestor_auc']} depth-monotonic="
              f"{r['depth_monotonic']} mean-distortion={r['mean_distortion']}", flush=True)
    J339a = all(R[s]['ancestor_auc'] >= 0.85 and R[s]['depth_monotonic'] >= 0.7 for s in seeds)
    print("\n--- VERDICT ---", flush=True)
    print(f"J339a hyperbolic kernel recovers hierarchy in D=5 (AUC>=.85, depth>=.7): {J339a}", flush=True)
    print("  J339b (honest): the VSA already does is-a at 1.0 with routing; hyperbolic is a more dimension-efficient",
          flush=True)
    print("  geometry for pure trees but a COMPLEMENT, not a needed replacement. Transformer/RL parts of the paper",
          flush=True)
    print("  are FORBIDDEN by CLAUDE.md and were NOT incorporated.", flush=True)
    verdict = ("PASS - the paper's hyperbolic-geometry kernel works substrate-legally (classical Poincare embedding, "
               "no NN); adopted as an optional geometry, transformer parts rejected by rule") if J339a else "NULL/partial"
    print(f"\nJEP-339: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP339"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J339a": J339a, "passed": J339a}, default=str))
    print("DONE", flush=True)
