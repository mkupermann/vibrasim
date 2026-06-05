"""JEP-434 — affect feeds back into cognition: does the energy model's learned valence disambiguate
two concepts that are near-identical in VSA space but opposite in affect (bright vs dark twin)?
Compare semantics-only recall vs affect-augmented vs shuffled-energy control. Established methods.
Pre-registered bars in docs/amendments/jep434_affect_biased_recall.md.
"""
import json
from pathlib import Path
import numpy as np

from world.substrate_memory import atom_vector
from world.valence_reservoir import ValenceReservoirLearner

D = 4096
S = 100            # shared semantic feature pool
K = 6              # shared features per concept
N_TRAIN, N_TEST = 300, 100
SIGMA = 1.0        # probe noise (fixed pre-run)

SHARED = np.stack([atom_vector(f"sem_{i}", D) for i in range(S)])
P_BRIGHT = atom_vector("polarity_bright", D)
P_DARK = atom_vector("polarity_dark", D)


def _twin(rng):
    """Return (bright_cloud, dark_cloud, shared-key). Twins share K semantic features, differ in polarity."""
    feats = rng.choice(S, size=K, replace=False)
    base = SHARED[feats].sum(axis=0)
    b = base + P_BRIGHT
    d = base + P_DARK
    b = b / (np.linalg.norm(b) + 1e-9)
    d = d / (np.linalg.norm(d) + 1e-9)
    return b.astype(np.float64), d.astype(np.float64), frozenset(int(x) for x in feats)


def _cos(a, b):
    return float(a @ b / ((np.linalg.norm(a) + 1e-9) * (np.linalg.norm(b) + 1e-9)))


def _train_energy(rng, n, shuffle=False, seed=0):
    X, y, seen = [], [], set()
    while len(X) < n:
        b, d, k = _twin(rng)
        if k in seen:
            continue
        seen.add(k)
        X.append(b); y.append(1.0)
        X.append(d); y.append(-1.0)
    y = np.array(y)
    if shuffle:
        np.random.default_rng(seed + 99).shuffle(y)
    res = ValenceReservoirLearner(n_inputs=D, n_features=600, seed=seed)
    for x, v in zip(X, y):
        res.experience(x, v)
    return res, seen


def run(seed):
    rng = np.random.default_rng(seed)
    energy, train_keys = _train_energy(rng, N_TRAIN, shuffle=False, seed=seed)
    rng_sh = np.random.default_rng(seed)
    energy_sh, _ = _train_energy(rng_sh, N_TRAIN, shuffle=True, seed=seed)

    nrng = np.random.default_rng(seed + 7)
    sem_ok = aff_ok = ctrl_ok = 0
    n = 0
    seen = set(train_keys)
    while n < N_TEST:
        b, d, k = _twin(rng)
        if k in seen:
            continue
        seen.add(k); n += 1
        noise = nrng.standard_normal(D) * SIGMA
        probe = b + noise
        probe = probe / (np.linalg.norm(probe) + 1e-9)
        cands = [(b, 1.0), (d, -1.0)]   # (cloud, known valence); target = bright (b)

        # semantics-only: nearest by cosine
        sem_pick = max(cands, key=lambda c: _cos(probe, c[0]))
        sem_ok += (sem_pick[1] == 1.0)

        # affect-augmented: restrict to predicted-valence subset, then cosine
        pv = 1.0 if energy.feel(probe) >= 0 else -1.0
        sub = [c for c in cands if c[1] == pv] or cands
        aff_pick = max(sub, key=lambda c: _cos(probe, c[0]))
        aff_ok += (aff_pick[1] == 1.0)

        # shuffled-energy control
        pv_s = 1.0 if energy_sh.feel(probe) >= 0 else -1.0
        sub_s = [c for c in cands if c[1] == pv_s] or cands
        ctrl_pick = max(sub_s, key=lambda c: _cos(probe, c[0]))
        ctrl_ok += (ctrl_pick[1] == 1.0)

    return dict(sem=sem_ok / N_TEST, aff=aff_ok / N_TEST, ctrl=ctrl_ok / N_TEST)


if __name__ == "__main__":
    print("=== JEP-434: affect-biased recall (learned valence disambiguates confusable twins) ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: semantics-only={R[s]['sem']:.3f} | affect-augmented={R[s]['aff']:.3f} | "
              f"shuffled-control={R[s]['ctrl']:.3f}", flush=True)

    J434a = all(R[s]['sem'] <= 0.80 for s in seeds)
    J434b = all(R[s]['aff'] >= R[s]['sem'] + 0.15 and R[s]['aff'] >= 0.85 for s in seeds)
    J434c = all(R[s]['ctrl'] <= R[s]['sem'] + 0.05 for s in seeds)
    passed = J434a and J434b and J434c

    print("\n--- VERDICT ---", flush=True)
    print(f"J434a confusion real (semantics<=0.80)        : {J434a}", flush=True)
    print(f"J434b affect helps (aff>=sem+0.15 & >=0.85)   : {J434b}", flush=True)
    print(f"J434c it's the learned valence (ctrl<=sem+.05): {J434c}", flush=True)
    verdict = ("PASS - learned valence gives the substrate a disambiguation channel raw VSA "
               "similarity lacks; affect feeds back into recall") if passed else "NULL/partial"
    print(f"\nJEP-434: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP434"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "J434a": J434a, "J434b": J434b, "J434c": J434c},
                                                 indent=2, default=str))
    print("DONE", flush=True)
