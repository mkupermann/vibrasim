"""HYB-04 — noise tolerance of the algebraic discovery module (the LPN boundary). Flip a fraction of
parity labels; test exact GF(2) vs robust (subset-voting) GF(2) for set recovery. Pre-registered bars in
docs/amendments/hyb04_noise_tolerance.md.
"""
import json
from pathlib import Path
import numpy as np

P = 18
K = 8
EPS = [0.0, 0.02, 0.05, 0.10]
N_EXACT = 40
N_SUBSETS, SUB = 200, P + 2
N_TE = 2000


def _samples(rng, n, eps):
    X = rng.choice([-1.0, 1.0], size=(n, P))
    yb = (np.prod(X[:, :K], axis=1) < 0).astype(np.int64)
    flip = rng.random(n) < eps
    yb = yb ^ flip.astype(np.int64)
    return (X < 0).astype(np.int64), yb


def gf2_solve(Xb, yb):
    N = Xb.shape[0]
    M = np.concatenate([Xb % 2, (yb % 2)[:, None]], axis=1)
    rank = 0; piv = []
    for col in range(P):
        rows = np.where(M[rank:, col] == 1)[0]
        if len(rows) == 0:
            continue
        pr = rank + rows[0]; M[[rank, pr]] = M[[pr, rank]]
        for r in range(N):
            if r != rank and M[r, col] == 1:
                M[r] = (M[r] + M[rank]) % 2
        piv.append(col); rank += 1
        if rank == N:
            break
    s = np.zeros(P, dtype=np.int64)
    for i, col in enumerate(piv):
        s[col] = M[i, -1]
    return s


def robust_solve(rng, Xb, yb):
    N = Xb.shape[0]
    votes = np.zeros(P)
    for _ in range(N_SUBSETS):
        idx = rng.choice(N, SUB, replace=False)
        votes += gf2_solve(Xb[idx], yb[idx])
    return (votes > N_SUBSETS / 2).astype(np.int64)


def acc(s, rng):
    Xte = rng.choice([-1.0, 1.0], size=(N_TE, P))
    yte = (np.prod(Xte[:, :K], axis=1) < 0).astype(np.int64)
    pred = ((Xte < 0).astype(np.int64) @ s) % 2
    return float((pred == yte).mean())


def run(seed):
    out = {}
    for eps in EPS:
        rng = np.random.default_rng(seed * 100 + int(eps * 1000))
        Xb, yb = _samples(rng, max(N_EXACT, 400), eps)
        s_ex = gf2_solve(Xb[:N_EXACT], yb[:N_EXACT])
        s_rb = robust_solve(np.random.default_rng(seed + 1), Xb, yb)
        out[eps] = dict(exact_ok=(set(np.where(s_ex == 1)[0].tolist()) == set(range(K))),
                        robust_ok=(set(np.where(s_rb == 1)[0].tolist()) == set(range(K))),
                        exact_acc=round(acc(s_ex, np.random.default_rng(seed + 2)), 3),
                        robust_acc=round(acc(s_rb, np.random.default_rng(seed + 3)), 3))
    return out


if __name__ == "__main__":
    print("=== HYB-04: noise tolerance of algebraic discovery (LPN boundary) ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        for eps in EPS:
            d = R[s][eps]
            print(f"  seed {s} eps={eps}: exact set_ok={d['exact_ok']} (acc {d['exact_acc']}) | "
                  f"robust set_ok={d['robust_ok']} (acc {d['robust_acc']})", flush=True)

    HYB04a = all(R[s][0.0]['exact_ok'] and R[s][0.0]['robust_ok'] for s in seeds)
    HYB04b = all(not R[s][0.02]['exact_ok'] for s in seeds)
    HYB04c = all(R[s][0.05]['robust_ok'] and not R[s][0.10]['robust_ok'] for s in seeds)
    passed = HYB04a and HYB04b and HYB04c

    print("\n--- VERDICT ---", flush=True)
    print(f"HYB04a clean baseline recovers (eps=0)        : {HYB04a}", flush=True)
    print(f"HYB04b exact GF(2) fragile (fails eps=0.02)   : {HYB04b}", flush=True)
    print(f"HYB04c robust extends to 0.05, fails 0.10(LPN): {HYB04c}", flush=True)
    verdict = ("PASS - algebraic module's noise tolerance characterized: exact brittle, robust extends to "
               "moderate noise, LPN barrier ends it") if passed else "NULL/partial - noise pattern differs from prediction"
    print(f"\nHYB-04: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "HYB04"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): {str(e): R[s][e] for e in EPS} for s in seeds},
                                                  "passed": passed, "HYB04a": HYB04a, "HYB04b": HYB04b, "HYB04c": HYB04c},
                                                 indent=2, default=str))
    print("DONE", flush=True)
