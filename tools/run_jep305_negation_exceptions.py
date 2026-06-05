"""JEP-305 — negation & defeasible exceptions in the durable substrate: most-specific-explicit-wins inheritance
over the persistent VSA store, matching the engine (penguin cannot fly; whale is not a fish). No transformer.

Pre-registered bars in docs/amendments/jep305_negation_exceptions.md.
"""
import json, tempfile, itertools, subprocess, sys, os
from pathlib import Path
import numpy as np
from world.understanding import UnderstandingEngine
from world.substrate_memory import SubstrateMemory

CORPUS = (
    "A bird can fly. A penguin is a bird. A penguin cannot fly. A robin is a bird. An eagle is a bird. "
    "A mammal cannot fly. A bat is a mammal. A bat can fly. A dog is a mammal. "
    "A whale is a mammal. A whale is not a fish. A salmon is a fish. A fish is an animal. "
    "A bird is an animal. A mammal is an animal."
)
CALIB = [("c1", "isa", "k1"), ("c2", "isa", "k2"), ("c3", "isa", "k3")]


def gate_threshold(mem, seed):
    taught = np.mean([mem.query(c, "isa")[1] for (c, _, _) in CALIB])
    rng = np.random.default_rng(seed + 321)
    untaught = np.mean([mem.query(f"none_{int(rng.integers(1e9))}", "isa")[1] for _ in range(32)])
    return float((taught + untaught) / 2.0)


def isa_ancestors(mem, x, gate, max_hops=10):
    chain, cur, seen = [x], x, {x}
    for _ in range(max_hops):
        p, s = mem.query(cur, "isa")
        if p is None or s < gate or p in seen:
            break
        chain.append(p); seen.add(p); cur = p
    return chain


def has_property_def(mem, x, p, gate):
    for a in isa_ancestors(mem, x, gate):           # most specific first
        if mem.contains(a, "not_hasprop", p, gate):
            return False
        if mem.contains(a, "hasprop", p, gate):
            return True
    return False


def is_a_def(mem, x, y, gate, max_hops=10):
    if mem.contains(x, "not_isa", y, gate):
        return False
    cur, seen = x, {x}
    for _ in range(max_hops):
        pp, s = mem.query(cur, "isa")
        if pp is None or s < gate or pp in seen:
            return False
        if pp == y:
            return True
        seen.add(pp); cur = pp
    return False


def build(eng):
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    for c, ps in eng.parents.items():
        for p in ps:
            mem.add_fact(c, "isa", p)
    for a, ps in dict(eng.properties).items():
        for p in ps:
            mem.add_fact(a, "hasprop", p)
    for a, ps in dict(getattr(eng, "not_properties", {})).items():
        for p in ps:
            mem.add_fact(a, "not_hasprop", p)
    for (a, b) in getattr(eng, "neg_isa", set()):
        mem.add_fact(a, "not_isa", b)
    for (c, r, p) in CALIB:
        mem.add_fact(c, r, p)
    return mem


def run_seed(seed):
    eng = UnderstandingEngine(seed=seed)
    eng.read(CORPUS)
    nodes = sorted(set(eng.parents) | {p for v in eng.parents.values() for p in v})
    props = ["fly", "swim", "bark"]

    mem = build(eng)
    d = tempfile.mkdtemp(prefix=f"neg_{seed}_")
    mem.save(d)
    mem2 = SubstrateMemory.load(d)
    gate = gate_threshold(mem2, seed)

    prop_q = [(n, p) for n in nodes for p in props]
    prop_acc = np.mean([has_property_def(mem2, n, p, gate) == eng.has_property(n, p) for (n, p) in prop_q])

    isa_q = list(itertools.permutations(nodes, 2))
    isa_acc = np.mean([is_a_def(mem2, a, b, gate) == eng.is_a(a, b) for (a, b) in isa_q])

    mem3 = SubstrateMemory.load(d); gate3 = gate_threshold(mem3, seed)
    persist = all(has_property_def(mem3, n, p, gate3) == has_property_def(mem2, n, p, gate) for (n, p) in prop_q)

    demo = {"penguin_can_fly": has_property_def(mem2, "penguin", "fly", gate),
            "robin_can_fly": has_property_def(mem2, "robin", "fly", gate),
            "bat_can_fly": has_property_def(mem2, "bat", "fly", gate),
            "dog_can_fly": has_property_def(mem2, "dog", "fly", gate),
            "whale_is_fish": is_a_def(mem2, "whale", "fish", gate),
            "whale_is_animal": is_a_def(mem2, "whale", "animal", gate)}
    return {"prop_acc": round(float(prop_acc), 3), "isa_acc": round(float(isa_acc), 3),
            "persist_ok": bool(persist), "demo": demo}


def regression(repo):
    r = subprocess.run([sys.executable, "tools/run_jep301_substrate_inheritance.py"], capture_output=True,
                       text=True, env={**os.environ, "PYTHONPATH": repo})
    return "JEP-301: PASS" in r.stdout


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-305: negation & defeasible exceptions in the durable substrate ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: defeasible-property acc={r['prop_acc']} | negative-is-a acc={r['isa_acc']} | "
              f"persists={r['persist_ok']}", flush=True)
        print(f"           demo={r['demo']}", flush=True)
    reg = regression(repo)
    print(f"  regression JEP-301: {'PASS' if reg else 'FAIL'}", flush=True)

    J305a = all(R[s]['prop_acc'] >= 0.90 for s in seeds)
    J305b = all(R[s]['isa_acc'] >= 0.95 for s in seeds)
    J305c = all(R[s]['persist_ok'] for s in seeds)
    passed = J305a and J305b and J305c and reg
    print("\n--- VERDICT ---", flush=True)
    print(f"J305a defeasible property w/ exceptions (>=.90): {J305a}", flush=True)
    print(f"J305b explicit negative is-a (>=.95)           : {J305b}", flush=True)
    print(f"J305c persists across reload                   : {J305c}", flush=True)
    print(f"no-regression: JEP-301 still PASS              : {reg}", flush=True)
    verdict = ("PASS - the substrate resolves negation and exceptions (most-specific-explicit-wins) over its "
               "persistent store, matching the engine: a penguin cannot fly, a whale is not a fish") if passed \
        else "NULL/partial"
    print(f"\nJEP-305: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP305"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "reg": reg,
                                                  "J305a": J305a, "J305b": J305b, "J305c": J305c,
                                                  "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
