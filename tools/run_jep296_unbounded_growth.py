"""JEP-296 — unbounded growth past the capacity cliff via auto module-add (neurogenesis).

Stores 3*K* facts. A SINGLE bundle must black out (<0.90); the auto-module SubstrateMemory must hold them
(>=0.90), survive a save/load, and keep untaught queries separable. Established modular-VSA route, named as such.
No transformer, no pretrained model. Pre-registered bars in docs/amendments/jep296_unbounded_growth.md.
"""
import json, tempfile
from pathlib import Path
import numpy as np
from world.vsa import rand_hv, bind, unbind, sim, CleanupMemory
from world.substrate_memory import SubstrateMemory, atom_vector

D = 4096
KSTAR = D // 32           # 128
NFACTS = 3 * KSTAR        # 384


def make_facts(n, seed):
    rng = np.random.default_rng(seed)
    # distinct (entity, role, value) triples; value drawn from a vocabulary of size n (each fact its own value)
    return [(f"e{seed}_{i}", "rel", f"v{seed}_{i}") for i in range(n)], rng


def single_bundle_acc(facts, seed):
    """Baseline: ALL facts in ONE bundle (no modules) -> expected to black out."""
    ROLE = atom_vector("rel", D)
    accum = np.zeros(D)
    cm = CleanupMemory()
    for (e, r, v) in facts:
        accum = accum + bind(bind(atom_vector(e, D), ROLE), atom_vector(v, D))
        cm.add(v, atom_vector(v, D))
    mem = np.sign(accum); mem[mem == 0] = 1.0
    ok = 0
    for (e, r, v) in facts:
        key = bind(atom_vector(e, D), ROLE)
        ok += (cm.cleanup(unbind(mem, key))[0] == v)
    return ok / len(facts)


def multi_module_acc(mem, facts):
    ok = sum(mem.query(e, r)[0] == v for (e, r, v) in facts)
    return ok / len(facts)


def untaught_gap(mem, facts, seed):
    taught = np.mean([mem.query(e, r)[1] for (e, r, v) in facts[:64]])
    rng = np.random.default_rng(seed + 555)
    unt = [mem.query(f"zzz_{int(rng.integers(1e9))}", "rel")[1] for _ in range(64)]
    return float(taught - np.mean(unt)), float(taught), float(np.mean(unt))


def run_seed(seed):
    facts, _ = make_facts(NFACTS, seed)
    single = single_bundle_acc(facts, seed)

    mem = SubstrateMemory(D=D, tau=0.12)
    for (e, r, v) in facts:
        mem.add_fact(e, r, v)
    multi = multi_module_acc(mem, facts)
    n_modules = len(mem.modules)
    gap, taught, unt = untaught_gap(mem, facts, seed)

    # persistence of the grown store
    d = tempfile.mkdtemp(prefix=f"grow_{seed}_")
    mem.save(d);
    mem2 = SubstrateMemory.load(d)
    multi_reload = multi_module_acc(mem2, facts)

    return {"single": single, "multi": multi, "multi_reload": multi_reload, "n_modules": n_modules,
            "gap": gap, "taught": taught, "untaught": unt}


def run_jep295_regression():
    """No-regression: single-module persistence still works (subset of JEP-295 A bar)."""
    F = [("germany", "has", "politics"), ("poodle", "isa", "dog"), ("paris", "capitalof", "france"),
         ("salmon", "isa", "fish"), ("sun", "isa", "star")]
    d = tempfile.mkdtemp(prefix="reg_")
    m = SubstrateMemory(D=D); [m.add_fact(*t) for t in F]; m.save(d)
    m2 = SubstrateMemory.load(d)
    return sum(m2.query(e, r)[0] == v for (e, r, v) in F) / len(F)


if __name__ == "__main__":
    print("=== JEP-296: unbounded growth past the capacity cliff ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: {NFACTS} facts | SINGLE bundle={r['single']:.2f} (cliff) | "
              f"MULTI({r['n_modules']} modules)={r['multi']:.2f} | reload={r['multi_reload']:.2f} | "
              f"untaught gap={r['gap']:+.3f}", flush=True)
    reg = run_jep295_regression()
    print(f"  JEP-295 regression (single-module persist): {reg:.2f}", flush=True)

    J296a = all(R[s]['single'] < 0.90 and R[s]['multi'] >= 0.90 for s in seeds)
    J296b = all(R[s]['gap'] > 0 for s in seeds)
    J296c = all(R[s]['multi_reload'] >= 0.90 for s in seeds)
    J296reg = reg >= 0.95
    passed = J296a and J296b and J296c and J296reg
    print("\n--- VERDICT ---", flush=True)
    print(f"J296a single blacks out (<.90) AND multi holds (>=.90): {J296a}", flush=True)
    print(f"J296b untaught entity separable (gap>0)               : {J296b}", flush=True)
    print(f"J296c grown store persists (reload >=.90)             : {J296c}", flush=True)
    print(f"no-regression: single-module persistence (>=.95)      : {J296reg}", flush=True)
    verdict = ("PASS - growth is unbounded: when a module saturates a new one is added, recall stays >=0.90 across "
               "modules where a single bundle blacks out, and the grown brain persists") if passed else "NULL/partial"
    print(f"\nJEP-296: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP296"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "reg": reg,
                                                  "J296a": J296a, "J296b": J296b, "J296c": J296c,
                                                  "J296reg": J296reg, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
