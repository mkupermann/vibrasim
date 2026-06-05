"""JEP-469 — does balance-seeking on signed affect produce emergent us-vs-them camps (Cartwright-Harary
structure theorem)? Complete signed graph + greedy de-frustration dynamic; measure imbalanced triads and
2-clusterability before/after. Pre-registered bars in docs/amendments/jep469_emergent_camps.md.
"""
import json
from itertools import combinations
from pathlib import Path
import numpy as np

N = 12
GRAPHS = 5
MAX_STEPS = 2000


def imbalanced_triads(S):
    c = 0
    for i, j, k in combinations(range(N), 3):
        if S[i, j] * S[j, k] * S[i, k] < 0:
            c += 1
    return c


def two_color_violations(S):
    """Greedy BFS 2-coloring (+ edge -> same color, - edge -> different); count edges inconsistent with it."""
    best = None
    color = -np.ones(N, dtype=int)
    color[0] = 0
    from collections import deque
    q = deque([0])
    while q:
        u = q.popleft()
        for v in range(N):
            if v == u:
                continue
            want = color[u] if S[u, v] > 0 else 1 - color[u]
            if color[v] == -1:
                color[v] = want; q.append(v)
    viol = 0; tot = 0
    for i, j in combinations(range(N), 2):
        tot += 1
        same = (color[i] == color[j])
        if (S[i, j] > 0) != same:
            viol += 1
    return viol / tot


def balance_dynamic(S, rng):
    series = [imbalanced_triads(S)]
    for _ in range(MAX_STEPS):
        if imbalanced_triads(S) == 0:
            break
        # find the edge whose flip removes the most imbalanced triads
        best_gain, best_e = 0, None
        cur = imbalanced_triads(S)
        edges = list(combinations(range(N), 2))
        rng.shuffle(edges)
        for (i, j) in edges:
            S[i, j] *= -1; S[j, i] *= -1
            gain = cur - imbalanced_triads(S)
            S[i, j] *= -1; S[j, i] *= -1
            if gain > best_gain:
                best_gain, best_e = gain, (i, j)
        if best_e is None:
            break
        i, j = best_e; S[i, j] *= -1; S[j, i] *= -1
        series.append(imbalanced_triads(S))
    return series


def run(seed):
    res = []
    for g in range(GRAPHS):
        rng = np.random.default_rng(seed * 100 + g)
        S = rng.choice([-1, 1], size=(N, N)).astype(int)
        S = np.triu(S, 1); S = S + S.T
        np.fill_diagonal(S, 0)
        it0, v0 = imbalanced_triads(S), two_color_violations(S)
        series = balance_dynamic(S, rng)
        it1, v1 = imbalanced_triads(S), two_color_violations(S)
        monotone = all(series[i + 1] <= series[i] for i in range(len(series) - 1))
        res.append(dict(it0=it0, v0=v0, it1=it1, v1=v1, monotone=monotone))
    return res


if __name__ == "__main__":
    print("=== JEP-469: emergent us-vs-them camps from balance-seeking signed affect ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        it0 = np.mean([r['it0'] for r in R[s]]); v0 = np.mean([r['v0'] for r in R[s]])
        it1 = np.mean([r['it1'] for r in R[s]]); v1 = np.mean([r['v1'] for r in R[s]])
        mono = all(r['monotone'] for r in R[s])
        print(f"  seed {s}: BEFORE imbal_triads={it0:.0f} 2color_viol={v0:.2f} | "
              f"AFTER imbal_triads={it1:.1f} 2color_viol={v1:.3f} | monotone={mono}", flush=True)

    J469a = all(np.mean([r['it0'] for r in R[s]]) > 0 and np.mean([r['v0'] for r in R[s]]) > 0.10 for s in seeds)
    J469b = all(all(r['it1'] == 0 for r in R[s]) and np.mean([r['v1'] for r in R[s]]) <= 0.02 for s in seeds)
    J469c = all(all(r['monotone'] for r in R[s]) for s in seeds)
    passed = J469a and J469b and J469c

    print("\n--- VERDICT ---", flush=True)
    print(f"J469a random start frustrated         : {J469a}", flush=True)
    print(f"J469b balance -> 2 camps (0 imbal, clean): {J469b}", flush=True)
    print(f"J469c monotone de-frustration         : {J469c}", flush=True)
    verdict = ("PASS - signed affect self-organizes into two antagonistic camps (Cartwright-Harary) in our "
               "representation") if passed else "NULL/partial"
    print(f"\nJEP-469: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP469"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "J469a": J469a, "J469b": J469b, "J469c": J469c}, indent=2, default=str))
    print("DONE", flush=True)
