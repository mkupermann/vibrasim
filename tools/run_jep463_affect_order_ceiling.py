"""JEP-463 — the real energy model's affect-complexity ceiling over VSA energy-clouds. Balanced
order-k parity affect embedded in VSA clouds; measure ValenceReservoirLearner held-out accuracy vs k.
Pre-registered bars in docs/amendments/jep463_affect_order_ceiling.md.
"""
import json
from pathlib import Path
import numpy as np

from world.substrate_memory import atom_vector
from world.valence_reservoir import ValenceReservoirLearner

D = 4096
K_FILL = 4
N_FILL = 200
N_TR, N_TE = 1200, 600
KS = [2, 3, 4, 5]


def _slot_vecs(k):
    return [(atom_vector(f"slot{i}_0", D), atom_vector(f"slot{i}_1", D)) for i in range(k)]


def _fill_vecs():
    return np.stack([atom_vector(f"fill_{i}", D) for i in range(N_FILL)])


def _concept(rng, slots, FILL, seen):
    while True:
        f = frozenset(int(x) for x in rng.choice(N_FILL, size=K_FILL, replace=False))
        if f not in seen:
            break
    seen.add(f)
    choices = rng.integers(2, size=len(slots))
    v = sum(slots[i][choices[i]] for i in range(len(slots))) + FILL[list(f)].sum(axis=0)
    v = v / (np.linalg.norm(v) + 1e-9)
    val = 1.0 if (choices.sum() % 2 == 0) else -1.0       # parity of slot choices
    return v.astype(np.float64), val


def run(seed, k):
    rng = np.random.default_rng(seed * 100 + k)
    slots = _slot_vecs(k); FILL = _fill_vecs(); seen = set()
    res = ValenceReservoirLearner(n_inputs=D, n_features=600, seed=seed)
    for _ in range(N_TR):
        x, v = _concept(rng, slots, FILL, seen); res.experience(x, v)
    ok = 0
    for _ in range(N_TE):
        x, v = _concept(rng, slots, FILL, seen)
        ok += (np.sign(res.feel(x)) == v)
    return ok / N_TE


if __name__ == "__main__":
    print("=== JEP-463: affect-order ceiling of the energy model over VSA clouds ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = {k: run(s, k) for k in KS}
        print(f"  seed {s}: " + " ".join(f"k{k}={R[s][k]:.3f}" for k in KS), flush=True)

    J463a = all(R[s][2] >= 0.85 for s in seeds)
    J463b = all(R[s][5] <= R[s][2] - 0.15 for s in seeds)
    ceil = {s: next((k for k in KS if R[s][k] < 0.70), ">5") for s in seeds}
    passed = J463a and J463b

    print("\n--- VERDICT ---", flush=True)
    print(f"J463a low-order works (k2>=0.85)     : {J463a}", flush=True)
    print(f"J463b ceiling exists (k5<=k2-0.15)   : {J463b}", flush=True)
    print(f"J463c affect-order ceiling (first <0.70): {ceil}", flush=True)
    verdict = ("PASS - the real energy model has an affect-complexity ceiling over VSA clouds (located)"
               if passed else "NULL/partial - no clear ceiling through k=5 (clouds don't lower the boundary)")
    print(f"\nJEP-463: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP463"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): {str(k): R[s][k] for k in KS} for s in seeds},
                                                  "ceiling": {str(s): ceil[s] for s in seeds}, "passed": passed,
                                                  "J463a": J463a, "J463b": J463b}, indent=2, default=str))
    print("DONE", flush=True)
