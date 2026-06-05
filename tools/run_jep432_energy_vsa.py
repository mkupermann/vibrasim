"""JEP-432 — JEP-431 with the concept-space flaw fixed: F=64, K=6 (C(64,6)~7.4e7 concepts) and a
PROVABLY DISJOINT train/test partition, so "held-out" means genuinely unseen clouds. Re-tests
whether the valence-reservoir energy model recovers a NON-LINEAR (XOR) affect rule over real VSA
energy-clouds where a linear readout cannot. Established methods, named. No transformer.
Pre-registered bars in docs/amendments/jep432_energy_vsa_disjoint.md.
"""
import json
from pathlib import Path
import numpy as np

from world.substrate_memory import atom_vector
from world.valence_reservoir import ValenceReservoirLearner

D = 4096
F = 64
K = 6
N_TRAIN, N_TEST = 800, 400


def _feature_vecs():
    return np.stack([atom_vector(f"feat_{i}", D) for i in range(F)])


def _unique_concepts(rng, n, exclude):
    """n distinct frozenset feature-combos not in `exclude`."""
    out = []
    seen = set(exclude)
    while len(out) < n:
        feats = frozenset(int(x) for x in rng.choice(F, size=K, replace=False))
        if feats in seen:
            continue
        seen.add(feats); out.append(feats)
    return out


def _cloud(feats, FV):
    v = FV[list(feats)].sum(axis=0)
    return (v / (np.linalg.norm(v) + 1e-9)).astype(np.float64)


def _valence(feats, a=0, b=1):
    return -1.0 if ((a in feats) ^ (b in feats)) else 1.0


def _linear_readout(Xtr, ytr, Xte, ridge=1.0):
    A = Xtr.T @ Xtr + ridge * np.eye(Xtr.shape[1])
    w = np.linalg.solve(A, Xtr.T @ ytr)
    return np.sign(Xte @ w)


def run(seed):
    rng = np.random.default_rng(seed)
    FV = _feature_vecs()
    train_sets = _unique_concepts(rng, N_TRAIN, exclude=set())
    test_sets = _unique_concepts(rng, N_TEST, exclude=set(train_sets))
    assert set(train_sets).isdisjoint(set(test_sets)), "train/test overlap!"

    Xtr = np.stack([_cloud(f, FV) for f in train_sets]); ytr = np.array([_valence(f) for f in train_sets])
    Xte = np.stack([_cloud(f, FV) for f in test_sets]);  yte = np.array([_valence(f) for f in test_sets])

    res = ValenceReservoirLearner(n_inputs=D, n_features=600, seed=seed)
    for x, v in zip(Xtr, ytr):
        res.experience(x, v)
    acc_res = float((np.array([np.sign(res.feel(x)) for x in Xte]) == yte).mean())

    acc_lin = float((_linear_readout(Xtr, ytr, Xte) == yte).mean())

    ysh = ytr.copy(); np.random.default_rng(seed + 99).shuffle(ysh)
    res2 = ValenceReservoirLearner(n_inputs=D, n_features=600, seed=seed)
    for x, v in zip(Xtr, ysh):
        res2.experience(x, v)
    acc_ctrl = float((np.array([np.sign(res2.feel(x)) for x in Xte]) == yte).mean())

    return dict(acc_res=acc_res, acc_lin=acc_lin, acc_ctrl=acc_ctrl,
                base_rate=float(max((yte == 1).mean(), (yte == -1).mean())))


if __name__ == "__main__":
    print("=== JEP-432: non-linear affect over UNSEEN real VSA clouds (disjoint) ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: reservoir held-out={R[s]['acc_res']:.3f} | raw-linear={R[s]['acc_lin']:.3f} | "
              f"shuffled-control={R[s]['acc_ctrl']:.3f} | base_rate={R[s]['base_rate']:.3f}", flush=True)

    J432a = all(R[s]['acc_res'] >= 0.80 for s in seeds)
    J432b = all(R[s]['acc_lin'] <= 0.65 for s in seeds)
    J432c = all(R[s]['acc_ctrl'] <= 0.60 for s in seeds)
    passed = J432a and J432b and J432c

    print("\n--- VERDICT ---", flush=True)
    print(f"J432a reservoir generalizes (>=0.80)    : {J432a}", flush=True)
    print(f"J432b genuinely non-linear (raw<=0.65)  : {J432b}", flush=True)
    print(f"J432c control fails (shuffled<=0.60)    : {J432c}", flush=True)
    verdict = ("PASS - the energy model learns non-linear affect over UNSEEN real VSA energy-clouds; "
               "a linear readout cannot") if passed else "NULL/partial"
    print(f"\nJEP-432: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP432"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "J432a": J432a, "J432b": J432b, "J432c": J432c},
                                                 indent=2, default=str))
    print("DONE", flush=True)
