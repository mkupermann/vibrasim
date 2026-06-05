"""JEP-470 — sparse signed affect: 2 camps (strong balance) or many factions (weak balance)? Sparse
signed graph + greedy de-frustration; count +subgraph components (clusters). Pre-registered bars in
docs/amendments/jep470_sparse_factions.md.
"""
import json
from itertools import combinations
from pathlib import Path
import numpy as np

N = 18
P_EDGE = 0.45
GRAPHS = 5
MAX_STEPS = 3000


def imbalanced(S, E):
    c = 0
    for i, j, k in combinations(range(N), 3):
        if E[i, j] and E[j, k] and E[i, k] and S[i, j] * S[j, k] * S[i, k] < 0:
            c += 1
    return c


def pos_components(S, E):
    """Connected components of the +edge subgraph."""
    seen = [-1] * N; comp = 0
    for start in range(N):
        if seen[start] != -1:
            continue
        stack = [start]; seen[start] = comp
        while stack:
            u = stack.pop()
            for v in range(N):
                if E[u, v] and S[u, v] > 0 and seen[v] == -1:
                    seen[v] = comp; stack.append(v)
        comp += 1
    return comp


def run(seed):
    res = []
    for g in range(GRAPHS):
        rng = np.random.default_rng(seed * 100 + g)
        E = (np.triu(rng.random((N, N)), 1) < P_EDGE)
        E = E | E.T
        S = rng.choice([-1, 1], size=(N, N)).astype(int)
        S = np.triu(S, 1); S = S + S.T
        it0 = imbalanced(S, E)
        cur = it0
        for _ in range(MAX_STEPS):
            if cur == 0:
                break
            edges = [(i, j) for i, j in combinations(range(N), 2) if E[i, j]]
            rng.shuffle(edges)
            best_gain, best_e = 0, None
            for (i, j) in edges:
                S[i, j] *= -1; S[j, i] *= -1
                g2 = cur - imbalanced(S, E)
                S[i, j] *= -1; S[j, i] *= -1
                if g2 > best_gain:
                    best_gain, best_e = g2, (i, j)
            if best_e is None:
                break
            i, j = best_e; S[i, j] *= -1; S[j, i] *= -1; cur = imbalanced(S, E)
        res.append(dict(it0=it0, it1=cur, clusters=pos_components(S, E)))
    return res


if __name__ == "__main__":
    print("=== JEP-470: sparse signed affect — 2 camps or many factions? ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        it0 = np.mean([r['it0'] for r in R[s]]); it1 = np.mean([r['it1'] for r in R[s]])
        cl = np.mean([r['clusters'] for r in R[s]])
        print(f"  seed {s}: imbal {it0:.0f}->{it1:.1f} | mean clusters={cl:.1f} "
              f"(per-graph={[r['clusters'] for r in R[s]]})", flush=True)

    J470a = all(np.mean([r['it1'] for r in R[s]]) <= 0.25 * max(np.mean([r['it0'] for r in R[s]]), 1) for s in seeds)
    J470b = all(np.mean([r['clusters'] for r in R[s]]) > 2.5 for s in seeds)
    passed = J470a and J470b

    print("\n--- VERDICT ---", flush=True)
    print(f"J470a de-frustration works (final<=0.25 init): {J470a}", flush=True)
    print(f"J470b sparse -> >2.5 factions (weak balance) : {J470b}", flush=True)
    verdict = ("PASS - sparse affect fragments into MULTIPLE factions (weak balance), not a clean binary"
               if passed else "NULL/partial - sparse still reaches ~2 camps (strong balance holds)")
    print(f"\nJEP-470: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP470"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "J470a": J470a, "J470b": J470b}, indent=2, default=str))
    print("DONE", flush=True)
