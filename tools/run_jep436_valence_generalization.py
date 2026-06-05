"""JEP-436 — the integrated energy model predicts the valence of UNTAUGHT concepts in the live
SubstrateMemory. Teach valence on train entities via sm.learn_valence; predict held-out untaught
entities via sm.predict_valence (generalizes from the entity feature-cloud). Established methods.
Pre-registered bars in docs/amendments/jep436_valence_generalization.md.
"""
import json
from pathlib import Path
import numpy as np

from world.substrate_memory import SubstrateMemory

DARK = [f"dk_{i}" for i in range(5)]
BRIGHT = [f"br_{i}" for i in range(5)]
POOL = DARK + BRIGHT
K = 5
N_TRAIN, N_TEST = 200, 100


def _entity_features(rng):
    idx = rng.choice(len(POOL), size=K, replace=False)
    feats = [POOL[i] for i in idx]
    n_dark = sum(1 for f in feats if f in DARK)
    val = -1.0 if n_dark > K - n_dark else 1.0     # majority dark -> dark; ties -> bright
    return feats, val


def _populate(sm, names, rng):
    out = []
    for name in names:
        feats, val = _entity_features(rng)
        for f in feats:
            sm.add_fact(name, "has", f)
        out.append((name, val))
    return out


def run(seed, shuffle=False):
    rng = np.random.default_rng(seed)
    sm = SubstrateMemory(D=4096)
    sm.energy_seed = seed
    train = _populate(sm, [f"train_{i}" for i in range(N_TRAIN)], rng)
    test = _populate(sm, [f"test_{i}" for i in range(N_TEST)], rng)   # facts stored, valence NOT taught

    train_vals = [v for (_, v) in train]
    if shuffle:
        sv = list(train_vals); np.random.default_rng(seed + 99).shuffle(sv)
        train_vals = sv
    for (name, _), v in zip(train, train_vals):
        sm.learn_valence(name, v)

    # held-out untaught: predict_valence must GENERALIZE
    held_ok = sum(1 for (name, val) in test if np.sign(sm.predict_valence(name)) == val)
    # taught: must return exact taught value (use the ACTUAL taught labels, even if shuffled)
    taught_ok = sum(1 for (name, _), v in zip(train, train_vals) if sm.predict_valence(name) == v)
    return dict(held=held_ok / N_TEST, taught=taught_ok / N_TRAIN)


if __name__ == "__main__":
    print("=== JEP-436: energy model predicts valence of UNTAUGHT concepts (live store) ===", flush=True)
    seeds = [0, 7]
    R, C = {}, {}
    for s in seeds:
        R[s] = run(s, shuffle=False)
        C[s] = run(s, shuffle=True)
        print(f"  seed {s}: held-out untaught acc={R[s]['held']:.3f} | taught exact={R[s]['taught']:.3f} | "
              f"shuffled-control held-out={C[s]['held']:.3f}", flush=True)

    J436a = all(R[s]['held'] >= 0.80 for s in seeds)
    J436b = all(R[s]['taught'] >= 0.999 for s in seeds)
    J436c = all(C[s]['held'] <= 0.60 for s in seeds)
    passed = J436a and J436b and J436c

    print("\n--- VERDICT ---", flush=True)
    print(f"J436a valence generalizes to untaught (>=0.80): {J436a}", flush=True)
    print(f"J436b no regression on taught (==1.0)         : {J436b}", flush=True)
    print(f"J436c learned rule (shuffled<=0.60)           : {J436c}", flush=True)
    verdict = ("PASS - the integrated energy model predicts the affect of UNTAUGHT concepts from their "
               "feature-cloud in the live store; taught values exact; shuffled control fails") if passed else "NULL/partial"
    print(f"\nJEP-436: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP436"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds},
                                                  "control": {str(s): C[s] for s in seeds}, "passed": passed,
                                                  "J436a": J436a, "J436b": J436b, "J436c": J436c}, indent=2, default=str))
    print("DONE", flush=True)
