"""HYB-02 — the energy+algebraic hybrid DECOMPOSES a mixed rule (low-order gate + SQ-hard parity) where
neither pure method works. The algebraic module runs GF(2) on the local learner's LOW-CONFIDENCE
residual (general boosting-style; not told which feature gates). Pre-registered bars in
docs/amendments/hyb02_mixed_rule.md.
"""
import json
from pathlib import Path
import numpy as np

from world.valence_reservoir import ValenceReservoirLearner

P = 18
K = 8
N_TR, N_TE = 2000, 2000


def _data(rng, n):
    X = rng.choice([-1.0, 1.0], size=(n, P))
    par = np.prod(X[:, 1:1 + K], axis=1)
    y = np.where(X[:, 0] > 0, 1.0, par)            # gated mixed rule
    return X, y


def _train(X, y, seed, nf=400):
    L = ValenceReservoirLearner(n_inputs=X.shape[1], n_features=nf, seed=seed)
    feels = []
    for x, v in zip(X, y):
        L.experience(x, v)
    return L


def _acc(L, X, y):
    return float((np.array([np.sign(L.feel(x)) for x in X]) == y).mean())


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


def run(seed):
    rng = np.random.default_rng(seed)
    Xtr, ytr = _data(rng, N_TR); Xte, yte = _data(rng, N_TE)

    # (a) raw energy
    L0 = _train(Xtr, ytr, seed)
    acc_raw = _acc(L0, Xte, yte)

    # (b) pure GF(2) linear on the whole target
    s_whole = gf2_solve((Xtr < 0).astype(np.int64), (ytr < 0).astype(np.int64))
    pred_gf2 = np.where(((Xte < 0).astype(np.int64) @ s_whole) % 2 == 1, -1.0, 1.0)
    acc_gf2 = float((pred_gf2 == yte).mean())

    # (c) hybrid: GF(2) on the local learner's MISCLASSIFIED residual (HYB-03: cleaner SQ-hard isolation)
    wrong = np.array([np.sign(L0.feel(x)) for x in Xtr]) != ytr
    s_res = gf2_solve((Xtr[wrong] < 0).astype(np.int64), (ytr[wrong] < 0).astype(np.int64))
    phi_tr = np.prod(Xtr[:, s_res == 1], axis=1, keepdims=True) if (s_res == 1).any() else np.zeros((N_TR, 1))
    phi_te = np.prod(Xte[:, s_res == 1], axis=1, keepdims=True) if (s_res == 1).any() else np.zeros((N_TE, 1))
    L1 = _train(np.concatenate([Xtr, phi_tr], axis=1), ytr, seed)
    acc_hyb = _acc(L1, np.concatenate([Xte, phi_te], axis=1), yte)

    return dict(acc_raw=acc_raw, acc_gf2=acc_gf2, acc_hyb=acc_hyb,
                res_set=sorted(np.where(s_res == 1)[0].tolist()))


if __name__ == "__main__":
    print("=== HYB-03: hybrid via MISCLASSIFIED residual (gate + SQ-hard parity) ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: raw-energy={R[s]['acc_raw']:.3f} | GF2-whole={R[s]['acc_gf2']:.3f} | "
              f"HYBRID={R[s]['acc_hyb']:.3f} | residual-set={R[s]['res_set']}", flush=True)

    HYB03a = all(0.65 <= R[s]['acc_raw'] <= 0.85 for s in seeds)
    HYB03b = all(R[s]['acc_gf2'] <= 0.80 for s in seeds)
    HYB03c = all(R[s]['acc_hyb'] >= 0.93 for s in seeds)
    passed = HYB03a and HYB03b and HYB03c

    print("\n--- VERDICT ---", flush=True)
    print(f"HYB03a raw local partial (0.65-0.85)   : {HYB03a}", flush=True)
    print(f"HYB03b pure GF(2) fails (<=0.80)       : {HYB03b}", flush=True)
    print(f"HYB03c hybrid decomposes both (>=0.93) : {HYB03c}", flush=True)
    verdict = ("PASS - the energy+algebraic hybrid DECOMPOSES a mixed rule (local gate + SQ-hard parity) "
               "where neither pure method can") if passed else "NULL/partial"
    print(f"\nHYB-03: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "HYB03"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "HYB03a": HYB03a, "HYB03b": HYB03b, "HYB03c": HYB03c}, indent=2, default=str))
    print("DONE", flush=True)
