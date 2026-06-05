"""JEP-461 — confirm the order-8 wall is SQ-hardness (algorithm-class, not problem): a NON-SQ algorithm
(Gaussian elimination over GF(2)) cracks parity of any order with O(P) samples, where local node
perturbation failed with thousands. Pre-registered bars in docs/amendments/jep461_sq_confirmation.md.
"""
import json
from pathlib import Path
import numpy as np

P = 18
N_TR, N_TE = 40, 2000
KS = [8, 10, 12]


def _data(rng, n, k):
    X = rng.choice([-1.0, 1.0], size=(n, P))
    y = np.prod(X[:, :k], axis=1)
    Xb = (X < 0).astype(np.int64)            # bit = 1 iff x = -1
    yb = (y < 0).astype(np.int64)            # parity bit
    return Xb, yb


def gf2_solve(Xb, yb):
    """Solve Xb · s = yb (mod 2) for s in {0,1}^P by Gaussian elimination over GF(2)."""
    N = Xb.shape[0]
    M = np.concatenate([Xb % 2, (yb % 2)[:, None]], axis=1)
    rank = 0; pivots = []
    for col in range(P):
        rows = np.where(M[rank:, col] == 1)[0]
        if len(rows) == 0:
            continue
        pr = rank + rows[0]
        M[[rank, pr]] = M[[pr, rank]]
        for r in range(N):
            if r != rank and M[r, col] == 1:
                M[r] = (M[r] + M[rank]) % 2
        pivots.append(col); rank += 1
        if rank == N:
            break
    s = np.zeros(P, dtype=np.int64)
    for i, col in enumerate(pivots):
        s[col] = M[i, -1]
    return s


def run(seed):
    out = {}
    for k in KS:
        rng = np.random.default_rng(seed * 100 + k)
        Xtr, ytr = _data(rng, N_TR, k); Xte, yte = _data(rng, N_TE, k)
        s = gf2_solve(Xtr, ytr)
        pred = (Xte @ s) % 2
        acc = float((pred == yte).mean())
        recovered = set(np.where(s == 1)[0].tolist())
        out[k] = dict(acc=acc, recovered_set=sorted(recovered), correct_set=(recovered == set(range(k))))
    return out


if __name__ == "__main__":
    print(f"=== JEP-461: GF(2) elimination cracks parity (N={N_TR}) — SQ-hardness confirmation ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: " + " ".join(f"k{k}: acc={R[s][k]['acc']:.2f} set_ok={R[s][k]['correct_set']}" for k in KS),
              flush=True)

    J461a = all(R[s][8]['acc'] == 1.0 and R[s][8]['correct_set'] for s in seeds)
    J461b = all(R[s][10]['acc'] == 1.0 and R[s][12]['acc'] == 1.0 for s in seeds)
    passed = J461a and J461b

    print("\n--- VERDICT ---", flush=True)
    print(f"J461a GF(2) cracks order-8 (acc=1.0, exact set) : {J461a}", flush=True)
    print(f"J461b GF(2) order-independent (k10,k12=1.0)     : {J461b}", flush=True)
    print(f"J461c contrast: node perturbation (JEP-460) was CHANCE on order-8 with N=3000, M<=512; "
          f"GF(2) solves it with N={N_TR}", flush=True)
    verdict = ("PASS - the order-8 wall is the SQ-hardness of parity (local/correlational algorithm class), "
               "NOT the problem: GF(2) elimination cracks any order with O(P) samples") if passed else "NULL - GF(2) setup wrong"
    print(f"\nJEP-461: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP461"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): {str(k): R[s][k] for k in KS} for s in seeds},
                                                  "passed": passed, "J461a": J461a, "J461b": J461b}, indent=2, default=str))
    print("DONE", flush=True)
