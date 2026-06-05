"""JEP-464 — would LEARNED local features (node perturbation) raise the energy model's affect ceiling
over VSA clouds vs fixed random features? Test at order-3 (the reservoir's break point). Pre-registered
bars in docs/amendments/jep464_learned_features_ceiling.md.
"""
import json
from pathlib import Path
import numpy as np

from world.substrate_memory import atom_vector
from world.valence_reservoir import ValenceReservoirLearner

D = 4096
K = 3
K_FILL = 4
N_FILL = 200
N_TR, N_TE = 1000, 600
M = 64
EPOCHS = 3000
SIGMA, LR, CLIP = 0.1, 0.05, 1.0


def _build(seed):
    rng = np.random.default_rng(seed * 100 + K)
    slots = [(atom_vector(f"slot{i}_0", D), atom_vector(f"slot{i}_1", D)) for i in range(K)]
    FILL = np.stack([atom_vector(f"fill_{i}", D) for i in range(N_FILL)])
    seen = set()

    def concept():
        while True:
            f = frozenset(int(x) for x in rng.choice(N_FILL, size=K_FILL, replace=False))
            if f not in seen:
                break
        seen.add(f)
        ch = rng.integers(2, size=K)
        v = sum(slots[i][ch[i]] for i in range(K)) + FILL[list(f)].sum(axis=0)
        v = v / (np.linalg.norm(v) + 1e-9)
        return v.astype(np.float64), (1.0 if ch.sum() % 2 == 0 else -1.0)

    Xtr = np.zeros((N_TR, D)); ytr = np.zeros(N_TR)
    for i in range(N_TR):
        Xtr[i], ytr[i] = concept()
    Xte = np.zeros((N_TE, D)); yte = np.zeros(N_TE)
    for i in range(N_TE):
        Xte[i], yte[i] = concept()
    return Xtr, ytr, Xte, yte


def _clip(g):
    n = np.linalg.norm(g)
    return g * (CLIP / n) if n > CLIP else g


def node_pert(Xtr, ytr, Xte, yte, seed):
    rng = np.random.default_rng(seed)
    W1 = rng.standard_normal((D, M)) / np.sqrt(D); b1 = np.zeros(M)
    w2 = rng.standard_normal(M) / np.sqrt(M); b2 = 0.0
    N = Xtr.shape[0]
    for _ in range(EPOCHS):
        pre = Xtr @ W1 + b1
        h = np.tanh(pre); o = h @ w2 + b2; err = o - ytr
        w2 -= LR * _clip(h.T @ (2.0 * err / N)); b2 -= LR * (2.0 * err / N).sum()
        xi = rng.standard_normal((N, M))
        dL = (np.tanh(pre + SIGMA * xi) @ w2 + b2 - ytr) ** 2 - (o - ytr) ** 2
        mod = (xi * dL[:, None]) / (SIGMA ** 2)
        W1 -= LR * _clip(Xtr.T @ mod / N); b1 -= LR * mod.mean(axis=0)
    return float((np.sign(np.tanh(Xte @ W1 + b1) @ w2 + b2) == yte).mean())


def reservoir(Xtr, ytr, Xte, yte, seed):
    L = ValenceReservoirLearner(n_inputs=D, n_features=600, seed=seed)
    for x, v in zip(Xtr, ytr):
        L.experience(x, v)
    return float((np.array([np.sign(L.feel(x)) for x in Xte]) == yte).mean())


def run(seed):
    Xtr, ytr, Xte, yte = _build(seed)
    return dict(reservoir=reservoir(Xtr, ytr, Xte, yte, seed),
                node_pert=node_pert(Xtr, ytr, Xte, yte, seed))


if __name__ == "__main__":
    print("=== JEP-464: learned features vs random reservoir, order-3 affect over VSA clouds ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: random-reservoir={R[s]['reservoir']:.3f} | learned(node-pert)={R[s]['node_pert']:.3f}", flush=True)

    J464a = all(R[s]['node_pert'] >= R[s]['reservoir'] + 0.15 for s in seeds)
    J464b = all(R[s]['node_pert'] >= 0.75 for s in seeds)
    passed = J464a and J464b

    print("\n--- VERDICT ---", flush=True)
    print(f"J464a learned helps (node>=res+0.15) : {J464a}", flush=True)
    print(f"J464b learned reaches usable (>=0.75): {J464b}", flush=True)
    verdict = ("PASS - learned local features RAISE the affect ceiling over clouds (a learning-rule upgrade "
               "is worth it)") if passed else "NULL/partial - cloud noise caps both (order-3 ceiling is not just the learner)"
    print(f"\nJEP-464: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP464"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "J464a": J464a, "J464b": J464b}, indent=2, default=str))
    print("DONE", flush=True)
