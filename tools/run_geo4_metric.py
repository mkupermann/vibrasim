"""GEO-4 — does a DISTANCE-PRESERVING embedding give clean geometry (strong analogy + composition)? Build a
graph distance matrix from the relational edges (shortest-path hops), embed with classical MDS (scipy/numpy
eigendecomposition) into 2D/3D, then re-test ANALOGY and relation COMPOSITION on the recovered geometry. If
the metric embedding recovers clean structure, geometric understanding is robust given the right method.
Established (MDS / spectral embedding); numpy/scipy."""
import numpy as np
GW = 6


def grid_graph():
    cells = [(x, y) for x in range(GW) for y in range(GW)]; idx = {c: i for i, c in enumerate(cells)}; n = len(cells)
    import numpy as np
    INF = 1e6; Dm = np.full((n, n), INF); np.fill_diagonal(Dm, 0)
    for (x, y) in cells:
        for (dx, dy) in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            if 0 <= x + dx < GW and 0 <= y + dy < GW:
                Dm[idx[(x, y)], idx[(x + dx, y + dy)]] = 1
    # Floyd-Warshall shortest paths
    for k in range(n):
        Dm = np.minimum(Dm, Dm[:, k:k+1] + Dm[k:k+1, :])
    return cells, idx, Dm


def mds(Dm, dim=2):
    n = Dm.shape[0]; J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (Dm ** 2) @ J
    w, V = np.linalg.eigh(B); order = np.argsort(w)[::-1]
    w = w[order][:dim]; V = V[:, order][:, :dim]
    return V * np.sqrt(np.maximum(w, 0))


def r1(E, q, t, ex):
    d = np.linalg.norm(E - q, axis=1); d[ex] = 1e9; return int(np.argmin(d) == t)


if __name__ == "__main__":
    print("=== GEO-4: metric (MDS) embedding -> clean geometry? ===", flush=True)
    cells, idx, Dm = grid_graph(); E = mds(Dm, dim=2); nE = len(cells)
    rng = np.random.default_rng(7)
    # analogy
    quads = []
    for _ in range(3000):
        ax, ay = rng.integers(0, GW), rng.integers(0, GW); dx, dy = rng.integers(-3, 4), rng.integers(-3, 4)
        bx, by = ax + dx, ay + dy; cx, cy = rng.integers(0, GW), rng.integers(0, GW); ex_, ey = cx + dx, cy + dy
        if all(0 <= v < GW for v in (bx, by, ex_, ey)) and (dx, dy) != (0, 0):
            quads.append((idx[(ax, ay)], idx[(bx, by)], idx[(cx, cy)], idx[(ex_, ey)]))
    quads = quads[:800]
    an = np.mean([r1(E, E[b] - E[a] + E[c], d, [a, b, c]) for a, b, c, d in quads])
    # composition: right+up via average offsets
    rights = [(idx[(x, y)], idx[(x + 1, y)]) for x in range(GW - 1) for y in range(GW)]
    ups = [(idx[(x, y)], idx[(x, y + 1)]) for x in range(GW) for y in range(GW - 1)]
    rvec = np.mean([E[t] - E[h] for h, t in rights], 0); uvec = np.mean([E[t] - E[h] for h, t in ups], 0)
    comp = [(idx[(x, y)], idx[(x + 1, y + 1)]) for x in range(GW - 1) for y in range(GW - 1)]
    cacc = np.mean([r1(E, E[h] + rvec + uvec, t, [h]) for h, t in comp])
    print(f"  analogy hits@1     = {an:.2f}", flush=True)
    print(f"  composition hits@1 = {cacc:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if an >= 0.7 and cacc >= 0.7:
        print("GEO-4: PASS - the distance-preserving (MDS) embedding recovers CLEAN geometry: analogy AND composition both strong. Geometric understanding is robust GIVEN the right embedding method (metric, not margin-TransE).", flush=True)
    elif an >= 0.5 or cacc >= 0.5:
        print(f"GEO-4: PARTIAL - cleaner than TransE (analogy {an:.2f}, comp {cacc:.2f}) but not both >=0.7", flush=True)
    else:
        print("GEO-4: NULL - metric embedding did not improve it", flush=True)
    print("DONE", flush=True)
