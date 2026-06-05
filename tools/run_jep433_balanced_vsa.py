"""JEP-433 — decisive test: balanced (50/50) PARITY affect over real VSA energy-clouds. Two binary
feature-slots (A0/A1, B0/B1) + filler noise; valence = (whichA == whichB). Parity is provably NOT
linearly separable, so a linear readout must be at chance; if the valence-reservoir energy model
carries it on real clouds, the non-linear transfer is genuine. Established methods, named.
Pre-registered bars in docs/amendments/jep433_balanced_parity_vsa.md.
"""
import json
from pathlib import Path
import numpy as np

from world.substrate_memory import atom_vector
from world.valence_reservoir import ValenceReservoirLearner

D = 4096
N_FILL = 200       # filler vocabulary
K_FILL = 4
N_TRAIN, N_TEST = 800, 400

A0, A1 = atom_vector("slotA_0", D), atom_vector("slotA_1", D)
B0, B1 = atom_vector("slotB_0", D), atom_vector("slotB_1", D)
FILL = np.stack([atom_vector(f"fill_{i}", D) for i in range(N_FILL)])


def _concept(rng, exclude):
    """Return (cloud, valence, filler-key). whichA,whichB in {0,1}; valence=+1 iff equal."""
    while True:
        fills = frozenset(int(x) for x in rng.choice(N_FILL, size=K_FILL, replace=False))
        if fills not in exclude:
            break
    wa, wb = int(rng.integers(2)), int(rng.integers(2))
    va = A0 if wa == 0 else A1
    vb = B0 if wb == 0 else B1
    cloud = va + vb + FILL[list(fills)].sum(axis=0)
    cloud = (cloud / (np.linalg.norm(cloud) + 1e-9)).astype(np.float64)
    val = 1.0 if wa == wb else -1.0
    return cloud, val, fills


def _split(seed):
    rng = np.random.default_rng(seed)
    seen = set()
    Xtr, ytr, Xte, yte = [], [], [], []
    for _ in range(N_TRAIN):
        c, v, f = _concept(rng, seen); seen.add(f); Xtr.append(c); ytr.append(v)
    for _ in range(N_TEST):
        c, v, f = _concept(rng, seen); seen.add(f); Xte.append(c); yte.append(v)
    return (np.asarray(Xtr), np.asarray(ytr), np.asarray(Xte), np.asarray(yte))


def _linear_readout(Xtr, ytr, Xte, ridge=1.0):
    A = Xtr.T @ Xtr + ridge * np.eye(Xtr.shape[1])
    w = np.linalg.solve(A, Xtr.T @ ytr)
    return np.sign(Xte @ w)


def run(seed):
    Xtr, ytr, Xte, yte = _split(seed)
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
    print("=== JEP-433: balanced PARITY affect over real VSA clouds ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: reservoir held-out={R[s]['acc_res']:.3f} | raw-linear={R[s]['acc_lin']:.3f} | "
              f"shuffled-control={R[s]['acc_ctrl']:.3f} | base_rate={R[s]['base_rate']:.3f}", flush=True)

    J433a = all(R[s]['acc_res'] >= 0.85 for s in seeds)
    J433b = all(R[s]['acc_lin'] <= 0.65 for s in seeds)
    J433c = all(R[s]['acc_ctrl'] <= 0.60 for s in seeds)
    passed = J433a and J433b and J433c

    print("\n--- VERDICT ---", flush=True)
    print(f"J433a reservoir learns parity (>=0.85)  : {J433a}", flush=True)
    print(f"J433b raw-linear at chance (<=0.65)     : {J433b}", flush=True)
    print(f"J433c control fails (shuffled<=0.60)    : {J433c}", flush=True)
    verdict = ("PASS - the energy model learns BALANCED non-linear (parity) affect over UNSEEN real "
               "VSA energy-clouds; a linear readout cannot") if passed else "NULL/partial"
    print(f"\nJEP-433: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP433"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "J433a": J433a, "J433b": J433b, "J433c": J433c},
                                                 indent=2, default=str))
    print("DONE", flush=True)
