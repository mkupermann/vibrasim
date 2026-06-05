"""JEP-440 — backfill the energy model from stored valence: a brain taught BEFORE the energy model
existed (valence dict set directly, no learner) gains affect generalization on first predict_valence,
with no re-teaching. Pre-registered bars in docs/amendments/jep440_energy_backfill.md.
"""
import json, tempfile
from pathlib import Path
import numpy as np

from world.substrate_memory import SubstrateMemory

DARK = [f"dk_{i}" for i in range(5)]; BRIGHT = [f"br_{i}" for i in range(5)]; POOL = DARK + BRIGHT


def _populate(sm, names, rng):
    out = []
    for nm in names:
        feats = [POOL[i] for i in rng.choice(len(POOL), size=5, replace=False)]
        for f in feats:
            sm.add_fact(nm, "has", f)
        nd = sum(f in DARK for f in feats)
        out.append((nm, -1.0 if nd > 5 - nd else 1.0))
    return out


def run(seed):
    rng = np.random.default_rng(seed)
    sm = SubstrateMemory(D=4096); sm.energy_seed = seed
    train = _populate(sm, [f"tr_{i}" for i in range(200)], rng)
    test = _populate(sm, [f"te_{i}" for i in range(100)], rng)
    # OLD WAY: set valence directly, NO learner trained (simulates a pre-JEP-436 brain)
    for nm, v in train:
        sm.valence[nm] = v
    assert sm.energy is None

    with tempfile.TemporaryDirectory() as d:
        sm.save(d)                        # legacy-format save (energy present=False)
        sm2 = SubstrateMemory.load(d)
    assert sm2.energy is None             # loaded brain has no learner yet

    # first predict triggers backfill
    held = sum(np.sign(sm2.predict_valence(nm)) == v for nm, v in test) / len(test)
    backfilled = sm2.energy is not None
    taught_ok = all(sm2.predict_valence(nm) == v for nm, v in train)

    empty = SubstrateMemory(D=2048)
    empty_none = (empty.predict_valence("xyz") is None and empty.energy is None)

    return dict(held=float(held), backfilled=bool(backfilled), taught_ok=bool(taught_ok),
                empty_none=bool(empty_none))


if __name__ == "__main__":
    print("=== JEP-440: backfill energy model from stored valence ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: backfilled={R[s]['backfilled']} | held-out untaught acc={R[s]['held']:.3f} | "
              f"taught exact={R[s]['taught_ok']} | empty->None={R[s]['empty_none']}", flush=True)

    J440a = all(R[s]['held'] >= 0.80 and R[s]['backfilled'] for s in seeds)
    J440b = all(R[s]['taught_ok'] for s in seeds)
    J440c = all(R[s]['empty_none'] for s in seeds)
    passed = J440a and J440b and J440c

    print("\n--- VERDICT ---", flush=True)
    print(f"J440a backfill generalizes (>=0.80)   : {J440a}", flush=True)
    print(f"J440b taught values intact            : {J440b}", flush=True)
    print(f"J440c empty store -> None, no learner : {J440c}", flush=True)
    verdict = ("PASS - existing brains gain affect generalization via backfill, no re-teaching; "
               "taught values intact; empty stays empty") if passed else "NULL/partial"
    print(f"\nJEP-440: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP440"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "J440a": J440a, "J440b": J440b, "J440c": J440c}, indent=2, default=str))
    print("DONE", flush=True)
