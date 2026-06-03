"""G139 — how does the recommended hardware path (oscillator-Ising) SCALE? Approximation ratio vs problem
size on MAX-CUT, vs the Goemans-Williamson ~0.878 guarantee and a greedy baseline. Tells the user what an
oscillator machine can actually do at scale. Established method; numpy reference (hardware would be parallel)."""
import numpy as np


def cut(W, s):
    return 0.25 * float(np.sum(W * (1 - np.outer(s, s))))


def osc(W, steps=600, dt=0.04, seed=0):
    n = W.shape[0]; rng = np.random.default_rng(seed)
    th = rng.uniform(0, 2 * np.pi, n)
    for t in range(steps):
        diff = th[:, None] - th[None, :]
        th = (th + dt * (np.sum(W * np.sin(diff), axis=1) - np.sin(2 * th) * (t / steps))) % (2 * np.pi)
    return np.where(np.cos(th) >= 0, 1, -1)


def greedy(W):
    n = W.shape[0]; s = np.ones(n, int)
    for _ in range(3):
        for i in range(n):
            s[i] = 1; a = cut(W, s); s[i] = -1; b = cut(W, s); s[i] = 1 if a >= b else -1
    return cut(W, s)


if __name__ == "__main__":
    print("=== G139: oscillator-Ising MAX-CUT scaling (approx vs problem size) ===", flush=True)
    rng = np.random.default_rng(3)
    for n in [10, 20, 40, 80]:
        oratios, gratios = [], []
        for _ in range(3):
            A = (rng.random((n, n)) < 0.3).astype(float); W = np.triu(A, 1); W = W + W.T
            ub = float(np.sum(W) / 2.0)            # cut <= total edge weight; loose upper bound
            o = max(cut(W, osc(W, seed=s)) for s in range(8))
            g = greedy(W)
            oratios.append(o / ub); gratios.append(g / ub)
        print(f"  n={n:>3}: oscillator/UB={np.mean(oratios):.2f}  greedy/UB={np.mean(gratios):.2f}", flush=True)
    print("\n  (UB = total edge weight, a loose upper bound; ratios near each other = oscillator ~ greedy.)", flush=True)
    print("DONE", flush=True)
