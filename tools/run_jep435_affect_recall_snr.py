"""JEP-435 — JEP-434 with SNR-controlled probe noise (norm = r * signal norm; primary r=0.5). Tests
whether the energy model's learned valence disambiguates confusable bright/dark twins where noisy
cosine fails. Established methods. Pre-registered bars in docs/amendments/jep435_affect_recall_snr.md.
"""
import json
from pathlib import Path
import numpy as np

from world.substrate_memory import atom_vector
from world.valence_reservoir import ValenceReservoirLearner

D = 4096
S = 100
K = 6
N_TRAIN, N_TEST = 300, 100
R_PRIMARY = 0.5

SHARED = np.stack([atom_vector(f"sem_{i}", D) for i in range(S)])
P_BRIGHT = atom_vector("polarity_bright", D)
P_DARK = atom_vector("polarity_dark", D)


def _twin(rng):
    feats = rng.choice(S, size=K, replace=False)
    base = SHARED[feats].sum(axis=0)
    b = base + P_BRIGHT; d = base + P_DARK
    b = b / (np.linalg.norm(b) + 1e-9); d = d / (np.linalg.norm(d) + 1e-9)
    return b.astype(np.float64), d.astype(np.float64), frozenset(int(x) for x in feats)


def _cos(a, b):
    return float(a @ b / ((np.linalg.norm(a) + 1e-9) * (np.linalg.norm(b) + 1e-9)))


def _train_energy(rng, n, shuffle, seed):
    X, y, seen = [], [], set()
    while len(X) < 2 * n:
        b, d, k = _twin(rng)
        if k in seen:
            continue
        seen.add(k); X += [b, d]; y += [1.0, -1.0]
    y = np.array(y)
    if shuffle:
        np.random.default_rng(seed + 99).shuffle(y)
    res = ValenceReservoirLearner(n_inputs=D, n_features=600, seed=seed)
    for x, v in zip(X, y):
        res.experience(x, v)
    return res, seen


def _eval(seed, r):
    rng = np.random.default_rng(seed)
    energy, train_keys = _train_energy(rng, N_TRAIN, False, seed)
    energy_sh, _ = _train_energy(np.random.default_rng(seed), N_TRAIN, True, seed)
    nrng = np.random.default_rng(seed + 7)
    sem = aff = ctrl = 0; n = 0; seen = set(train_keys)
    while n < N_TEST:
        b, d, k = _twin(rng)
        if k in seen:
            continue
        seen.add(k); n += 1
        nz = nrng.standard_normal(D)
        nz = nz * (r / (np.linalg.norm(nz) + 1e-9))   # ||nz|| = r (signal norm = 1)
        probe = b + nz; probe = probe / (np.linalg.norm(probe) + 1e-9)
        cands = [(b, 1.0), (d, -1.0)]
        sem += (max(cands, key=lambda c: _cos(probe, c[0]))[1] == 1.0)
        pv = 1.0 if energy.feel(probe) >= 0 else -1.0
        sub = [c for c in cands if c[1] == pv] or cands
        aff += (max(sub, key=lambda c: _cos(probe, c[0]))[1] == 1.0)
        pvs = 1.0 if energy_sh.feel(probe) >= 0 else -1.0
        subs = [c for c in cands if c[1] == pvs] or cands
        ctrl += (max(subs, key=lambda c: _cos(probe, c[0]))[1] == 1.0)
    return dict(sem=sem / N_TEST, aff=aff / N_TEST, ctrl=ctrl / N_TEST)


if __name__ == "__main__":
    print("=== JEP-435: affect-biased recall, SNR-controlled noise ===", flush=True)
    seeds = [0, 7]
    R = {s: _eval(s, R_PRIMARY) for s in seeds}
    for s in seeds:
        print(f"  seed {s} (r={R_PRIMARY}): semantics-only={R[s]['sem']:.3f} | affect={R[s]['aff']:.3f} | "
              f"shuffled-control={R[s]['ctrl']:.3f}", flush=True)
    print("  -- descriptive sweep --", flush=True)
    for r in (0.3, 0.7):
        for s in seeds:
            e = _eval(s, r)
            print(f"    r={r} seed {s}: sem={e['sem']:.3f} aff={e['aff']:.3f} ctrl={e['ctrl']:.3f}", flush=True)

    J435a = all(0.55 <= R[s]['sem'] <= 0.85 for s in seeds)
    J435b = all(R[s]['aff'] >= R[s]['sem'] + 0.10 and R[s]['aff'] >= 0.80 for s in seeds)
    J435c = all(R[s]['ctrl'] <= R[s]['sem'] + 0.05 for s in seeds)
    passed = J435a and J435b and J435c
    print("\n--- VERDICT (r=0.5) ---", flush=True)
    print(f"J435a confusion real, signal present : {J435a}", flush=True)
    print(f"J435b affect helps (>=sem+0.10,>=0.80): {J435b}", flush=True)
    print(f"J435c learned valence (ctrl<=sem+.05): {J435c}", flush=True)
    verdict = ("PASS - learned valence disambiguates confusable twins noisy cosine loses; affect "
               "feeds back into recall") if passed else "NULL/partial"
    print(f"\nJEP-435: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP435"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "J435a": J435a, "J435b": J435b, "J435c": J435c},
                                                 indent=2, default=str))
    print("DONE", flush=True)
