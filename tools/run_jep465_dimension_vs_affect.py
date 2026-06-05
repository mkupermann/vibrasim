"""JEP-465 — does cloud dimension D raise the energy model's affect ceiling? Order-3 affect over VSA
clouds, ValenceReservoirLearner, sweep D. Pre-registered bars in docs/amendments/jep465_dimension_vs_affect.md.
"""
import json
from pathlib import Path
import numpy as np

from world.substrate_memory import atom_vector
from world.valence_reservoir import ValenceReservoirLearner

K = 3
K_FILL = 4
N_FILL = 200
N_TR, N_TE = 1000, 600
DS = [4096, 8192, 16384]


def run(seed, D):
    rng = np.random.default_rng(seed * 100 + D)
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

    res = ValenceReservoirLearner(n_inputs=D, n_features=600, seed=seed)
    for _ in range(N_TR):
        x, val = concept(); res.experience(x, val)
    ok = 0
    for _ in range(N_TE):
        x, val = concept(); ok += (np.sign(res.feel(x)) == val)
    return ok / N_TE


if __name__ == "__main__":
    print("=== JEP-465: does cloud dimension D raise the order-3 affect ceiling? ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = {D: run(s, D) for D in DS}
        print(f"  seed {s}: " + " ".join(f"D{D}={R[s][D]:.3f}" for D in DS), flush=True)

    J465a = all(0.55 <= R[s][4096] <= 0.72 for s in seeds)
    J465b = all(R[s][16384] >= R[s][4096] + 0.10 for s in seeds)
    J465c_cross = all(R[s][16384] >= 0.80 for s in seeds)
    passed = J465b

    print("\n--- VERDICT ---", flush=True)
    print(f"J465a baseline D=4096 ~0.63 (0.55-0.72): {J465a}", flush=True)
    print(f"J465b D helps (D16384 >= D4096+0.10)   : {J465b}", flush=True)
    print(f"J465c D=16384 crosses 0.80             : {J465c_cross}", flush=True)
    verdict = ("PASS - cloud dimension D is a usable lever: bigger clouds raise the affect ceiling"
               if passed else "NULL/partial - D is NOT the lever (ceiling is the reservoir's order-3 limit, D-independent)")
    print(f"\nJEP-465: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP465"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): {str(D): R[s][D] for D in DS} for s in seeds},
                                                  "passed": passed, "J465a": J465a, "J465b": J465b,
                                                  "J465c_cross": J465c_cross}, indent=2, default=str))
    print("DONE", flush=True)
