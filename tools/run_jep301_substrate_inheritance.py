"""JEP-301 — substrate-native cross-relation INHERITANCE: compose the is-a climb with a target relation, over the
persistent VSA store, matching the engine. Closes the boundary named in JEP-300. No transformer.

Pre-registered bars in docs/amendments/jep301_substrate_inheritance.md.
"""
import json, tempfile, itertools, subprocess, sys, os
from pathlib import Path
import numpy as np
from world.understanding import UnderstandingEngine
from world.substrate_memory import SubstrateMemory

CORPUS = (
    "A poodle is a dog. A beagle is a dog. A dog is a mammal. A cat is a mammal. A mammal is an animal. "
    "A salmon is a fish. A fish is an animal. "
    "A dog can bark. A mammal can breathe. An animal can move. A fish can swim. "
    "A cell is part of a heart. A heart is part of a dog. A nucleus is part of a cell. "
    "A wheel is part of a car."
)
CALIB = [("c1", "isa", "k1"), ("c2", "isa", "k2"), ("c3", "isa", "k3"), ("c4", "isa", "k4")]


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


def partof_proper_ancestors(mem, y, gate, max_hops=10):
    """Holders reachable from y by >=1 real part-of edge (excludes y itself)."""
    out, cur, seen = [], y, {y}
    for _ in range(max_hops):
        p, s = mem.query(cur, "partof")
        if p is None or s < gate or p in seen:
            break
        out.append(p); seen.add(p); cur = p
    return out


def has_property_inh(mem, x, p, gate):
    return any(mem.contains(a, "hasprop", p, gate) for a in isa_ancestors(mem, x, gate))


def part_of_inh(mem, y, x, gate):
    """y is part of x iff y is a PROPER part of some holder z, and z is in x's is-a chain in EITHER direction
    (z is a supertype of x -> x inherits the part; or z is a subtype of x -> the part rolls up to x). Matches the
    engine's part-of semantics; needs a real part edge (so an is-a ancestor of x that merely equals y doesn't count)."""
    holders = partof_proper_ancestors(mem, y, gate)
    if not holders:
        return False
    x_anc = set(isa_ancestors(mem, x, gate))            # x and its supertypes
    for z in holders:
        if z == x or z in x_anc or x in set(isa_ancestors(mem, z, gate)):
            return True
    return False


def build_store(eng, seed):
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    for g, role in [({k: set(v) for k, v in eng.parents.items()}, "isa"),
                    ({k: set(v) for k, v in eng.part_of_g.items()}, "partof"),
                    ({k: set(v) for k, v in dict(eng.properties).items()}, "hasprop")]:
        for a, bs in g.items():
            for b in bs:
                mem.add_fact(a, role, b)
    for (c, r, p) in CALIB:
        mem.add_fact(c, r, p)
    return mem


def balanced(cands, truth_fn, rng, cap=40):
    pos = [c for c in cands if truth_fn(*c)]
    neg = [c for c in cands if not truth_fn(*c)]
    k = min(len(pos), len(neg), cap)
    if k == 0:
        return pos[:cap] + neg[:cap]
    pos = [pos[i] for i in rng.choice(len(pos), k, replace=False)]
    neg = [neg[i] for i in rng.choice(len(neg), k, replace=False)]
    return pos + neg


def run_seed(seed):
    eng = UnderstandingEngine(seed=seed)
    eng.read(CORPUS)
    nodes = sorted(set(eng.parents) | {p for v in eng.parents.values() for p in v}
                   | set(eng.part_of_g) | {p for v in eng.part_of_g.values() for p in v})
    allprops = sorted({p for v in dict(eng.properties).values() for p in v})

    mem = build_store(eng, seed)
    d = tempfile.mkdtemp(prefix=f"inh_{seed}_")
    mem.save(d)
    mem2 = SubstrateMemory.load(d)
    gate = gate_threshold(mem2, seed)
    rng = np.random.default_rng(seed)

    prop_q = balanced(list(itertools.product(nodes, allprops)), eng.has_property, rng)
    part_q = balanced(list(itertools.permutations(nodes, 2)), eng.part_of, rng)

    prop_ok = sum(has_property_inh(mem2, x, p, gate) == eng.has_property(x, p) for (x, p) in prop_q) / len(prop_q)
    part_ok = sum(part_of_inh(mem2, y, x, gate) == eng.part_of(y, x) for (y, x) in part_q) / len(part_q)

    # persistence: reload again, identical
    mem3 = SubstrateMemory.load(d); gate3 = gate_threshold(mem3, seed)
    persist = all(has_property_inh(mem3, x, p, gate3) == has_property_inh(mem2, x, p, gate) for (x, p) in prop_q)

    # concrete inherited demos (never stored directly)
    demos = {"poodle_can_bark": has_property_inh(mem2, "poodle", "bark", gate),
             "poodle_can_breathe": has_property_inh(mem2, "poodle", "breathe", gate),
             "heart_part_of_poodle": part_of_inh(mem2, "heart", "poodle", gate),
             "cell_part_of_poodle": part_of_inh(mem2, "cell", "poodle", gate)}
    return {"prop_acc": round(prop_ok, 3), "part_acc": round(part_ok, 3), "persist_ok": bool(persist),
            "n_prop": len(prop_q), "n_part": len(part_q), "demos": demos}


def regression(repo):
    r = subprocess.run([sys.executable, "tools/run_jep300_multirelational_bridge.py"], capture_output=True,
                       text=True, env={**os.environ, "PYTHONPATH": repo})
    return "JEP-300: PASS" in r.stdout


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-301: substrate-native cross-relation inheritance ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: property-inherit acc={r['prop_acc']} ({r['n_prop']}q) | part-inherit acc={r['part_acc']} "
              f"({r['n_part']}q) | persists={r['persist_ok']} | demos={r['demos']}", flush=True)
    reg = regression(repo)
    print(f"  regression: JEP-300={'PASS' if reg else 'FAIL'}", flush=True)

    J301a = all(R[s]['prop_acc'] >= 0.90 for s in seeds)
    J301b = all(R[s]['part_acc'] >= 0.90 for s in seeds)
    J301c = all(R[s]['persist_ok'] for s in seeds)
    passed = J301a and J301b and J301c and reg
    print("\n--- VERDICT ---", flush=True)
    print(f"J301a property inheritance matches engine (>=.90): {J301a}", flush=True)
    print(f"J301b part inheritance matches engine (>=.90)    : {J301b}", flush=True)
    print(f"J301c persists across reload                     : {J301c}", flush=True)
    print(f"no-regression: JEP-300 still PASS                : {reg}", flush=True)
    verdict = ("PASS - the substrate composes its is-a climb with a target relation to do inheritance natively, "
               "matching the engine, over the persistent store") if passed else "NULL/partial"
    print(f"\nJEP-301: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP301"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "reg": reg,
                                                  "J301a": J301a, "J301b": J301b, "J301c": J301c,
                                                  "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
