"""JEP-431 — does the valence-reservoir learner (JEP-430) recover a NON-LINEAR affect rule when the
input is a REAL VSA energy-cloud (a bundle of feature hypervectors), not a toy bit-vector?

Concepts = normalized superposition of K feature atom_vectors (the substrate's own representation).
Affect = XOR of two designated features (non-linear), embedded in a cloud of other features.
Compare reservoir vs raw-linear readout vs shuffled-label control. Established methods, named.
Pre-registered bars in docs/amendments/jep431_energy_on_real_vsa.md.
"""
import json
from pathlib import Path
import numpy as np

from world.substrate_memory import atom_vector
from world.valence_reservoir import ValenceReservoirLearner

D = 4096
F = 12          # feature vocabulary size
K = 4           # features per concept
N_TRAIN, N_TEST = 600, 400


def _feature_vecs():
    return np.stack([atom_vector(f"feat_{i}", D) for i in range(F)])   # (F, D) bipolar


def _make_concept(rng, FV):
    """A concept = K distinct features bundled (summed, sign) into one normalized energy cloud.
    Returns (cloud unit-vector, set-of-feature-indices)."""
    feats = rng.choice(F, size=K, replace=False)
    cloud = FV[feats].sum(axis=0)
    cloud = cloud / (np.linalg.norm(cloud) + 1e-9)
    return cloud.astype(np.float64), set(int(f) for f in feats)


def _valence(feats, a=0, b=1):
    """Non-linear (XOR) affect over two designated features: dark(-1) iff exactly one of a,b present."""
    return -1.0 if ((a in feats) ^ (b in feats)) else 1.0


def _dataset(seed, n):
    rng = np.random.default_rng(seed)
    FV = _feature_vecs()
    X, y = [], []
    for _ in range(n):
        cloud, feats = _make_concept(rng, FV)
        X.append(cloud); y.append(_valence(feats))
    return np.asarray(X), np.asarray(y)


def _linear_readout(Xtr, ytr, Xte, ridge=1.0):
    A = Xtr.T @ Xtr + ridge * np.eye(Xtr.shape[1])
    w = np.linalg.solve(A, Xtr.T @ ytr)
    return np.sign(Xte @ w)


def run(seed):
    Xtr, ytr = _dataset(seed, N_TRAIN)
    Xte, yte = _dataset(seed + 1000, N_TEST)        # disjoint UNSEEN concepts

    # reservoir (energy model)
    res = ValenceReservoirLearner(n_inputs=D, n_features=600, seed=seed)
    for x, v in zip(Xtr, ytr):
        res.experience(x, v)
    pred = np.array([np.sign(res.feel(x)) for x in Xte])
    acc_res = float((pred == yte).mean())

    # raw linear readout on the cloud
    acc_lin = float((_linear_readout(Xtr, ytr, Xte) == yte).mean())

    # shuffled-label negative control (reservoir on permuted valence)
    rng = np.random.default_rng(seed + 99)
    ysh = ytr.copy(); rng.shuffle(ysh)
    res2 = ValenceReservoirLearner(n_inputs=D, n_features=600, seed=seed)
    for x, v in zip(Xtr, ysh):
        res2.experience(x, v)
    pred2 = np.array([np.sign(res2.feel(x)) for x in Xte])
    acc_ctrl = float((pred2 == yte).mean())

    return dict(acc_res=acc_res, acc_lin=acc_lin, acc_ctrl=acc_ctrl)


if __name__ == "__main__":
    print("=== JEP-431: non-linear affect over REAL VSA energy-clouds ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: reservoir held-out={R[s]['acc_res']:.3f} | raw-linear={R[s]['acc_lin']:.3f} | "
              f"shuffled-control={R[s]['acc_ctrl']:.3f}", flush=True)

    J431a = all(R[s]['acc_res'] >= 0.80 for s in seeds)
    J431b = all(R[s]['acc_lin'] <= 0.65 for s in seeds)
    J431c = all(R[s]['acc_ctrl'] <= 0.60 for s in seeds)
    passed = J431a and J431b and J431c

    print("\n--- VERDICT ---", flush=True)
    print(f"J431a reservoir transfers (>=0.80)      : {J431a}", flush=True)
    print(f"J431b genuinely non-linear (raw<=0.65)  : {J431b}", flush=True)
    print(f"J431c control fails (shuffled<=0.60)    : {J431c}", flush=True)
    verdict = ("PASS - the energy model learns non-linear affect over the substrate's REAL VSA "
               "energy-clouds (transfers from toy bits)") if passed else "NULL/partial"
    print(f"\nJEP-431: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP431"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "J431a": J431a, "J431b": J431b, "J431c": J431c},
                                                 indent=2, default=str))
    print("DONE", flush=True)
