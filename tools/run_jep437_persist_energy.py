"""JEP-437 — the energy model survives save/load: generalized valence persists across a reload.
Teach valence (train the learner) -> predict held-out untaught -> save -> load -> predict the SAME
concepts; must be byte-identical and accuracy preserved. Pre-registered bars in
docs/amendments/jep437_persist_energy_model.md.
"""
import json, tempfile, os
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
    for nm, v in train:
        sm.learn_valence(nm, v)
    before = {nm: sm.predict_valence(nm) for nm, _ in test}

    with tempfile.TemporaryDirectory() as d:
        sm.save(d)
        sm2 = SubstrateMemory.load(d)
    after = {nm: sm2.predict_valence(nm) for nm, _ in test}

    max_diff = max(abs(before[nm] - after[nm]) for nm, _ in test)
    acc_after = sum(np.sign(after[nm]) == v for nm, v in test) / len(test)

    # no-energy store round-trips with energy None
    empty = SubstrateMemory(D=2048); empty.add_fact("a", "isa", "b")
    with tempfile.TemporaryDirectory() as d:
        empty.save(d); empty2 = SubstrateMemory.load(d)
    no_energy_ok = (empty2.energy is None and empty2.query("a", "isa")[0] == "b")

    return dict(max_diff=float(max_diff), acc_after=float(acc_after), no_energy_ok=bool(no_energy_ok))


if __name__ == "__main__":
    print("=== JEP-437: persist the energy model across save/load ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: round-trip max|diff|={R[s]['max_diff']:.2e} | acc_after_load={R[s]['acc_after']:.3f} | "
              f"no-energy store ok={R[s]['no_energy_ok']}", flush=True)

    J437a = all(R[s]['max_diff'] < 1e-6 for s in seeds)
    J437b = all(R[s]['acc_after'] >= 0.80 for s in seeds)
    J437c = all(R[s]['no_energy_ok'] for s in seeds)
    passed = J437a and J437b and J437c

    print("\n--- VERDICT ---", flush=True)
    print(f"J437a round-trip exact (<1e-6)      : {J437a}", flush=True)
    print(f"J437b accuracy preserved (>=0.80)   : {J437b}", flush=True)
    print(f"J437c no-energy store round-trips   : {J437c}", flush=True)
    verdict = ("PASS - the energy model persists across save/load; generalized valence survives a "
               "reload") if passed else "NULL/partial"
    print(f"\nJEP-437: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP437"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "J437a": J437a, "J437b": J437b, "J437c": J437c}, indent=2, default=str))
    print("DONE", flush=True)
