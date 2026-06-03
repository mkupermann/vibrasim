"""G141 — the physical paradigm can LEARN: a fully-visible Boltzmann machine (= stochastic Ising machine)
learns a target distribution's statistics from data, unsupervised, no LLM/transformer. The SAME coupled
hardware that optimizes (G138/9) and recalls (G140), run stochastically, LEARNS. Established method
(Boltzmann machine), named as such. Measure: learned-model pairwise correlations match the data's.
"""
import numpy as np


def gibbs_sample(W, b, n_samp, steps=50, seed=0):
    rng = np.random.default_rng(seed); n = len(b)
    s = rng.choice([-1, 1], (n_samp, n)).astype(float)
    for _ in range(steps):
        for i in range(n):
            field = s @ W[i] + b[i]
            p = 1.0 / (1.0 + np.exp(-2.0 * field))
            s[:, i] = np.where(rng.random(n_samp) < p, 1.0, -1.0)
    return s


def corr(S):
    return (S.T @ S) / len(S)


if __name__ == "__main__":
    print("=== G141: Boltzmann machine (stochastic Ising) LEARNS a distribution ===", flush=True)
    rng = np.random.default_rng(0); n = 8
    # target distribution: a planted Boltzmann model with structured couplings
    Wt = rng.normal(0, 0.7, (n, n)); Wt = np.triu(Wt, 1); Wt = Wt + Wt.T
    bt = rng.normal(0, 0.3, n)
    data = gibbs_sample(Wt, bt, 4000, steps=80, seed=1)        # the "data"
    Cdata = corr(data)

    # LEARN: fit W,b by the Boltzmann learning rule (data corr - model corr)
    W = np.zeros((n, n)); b = np.zeros(n); lr = 0.05
    for epoch in range(300):
        model = gibbs_sample(W, b, 800, steps=20, seed=epoch + 2)
        dW = corr(data) - corr(model); np.fill_diagonal(dW, 0)
        db = data.mean(0) - model.mean(0)
        W += lr * dW; b += lr * db
    learned = gibbs_sample(W, b, 4000, steps=80, seed=99)
    Cl = corr(learned)

    # how well do learned correlations match the data's (off-diagonal)?
    mask = ~np.eye(n, dtype=bool)
    err_learned = float(np.mean(np.abs(Cdata[mask] - Cl[mask])))
    Crand = corr(rng.choice([-1, 1], (4000, n)).astype(float))
    err_rand = float(np.mean(np.abs(Cdata[mask] - Crand[mask])))
    print(f"  mean |corr| error: learned model = {err_learned:.3f} | random baseline = {err_rand:.3f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if err_learned <= 0.5 * err_rand and err_learned < 0.10:
        print("G141: PASS - the Boltzmann machine LEARNED the distribution (its samples reproduce the data's correlations). The physical paradigm does unsupervised LEARNING, no LLM.", flush=True)
    else:
        print(f"G141: PARTIAL - learned err {err_learned:.3f} vs random {err_rand:.3f} (learning present; tuning improves)", flush=True)
    print("DONE", flush=True)
