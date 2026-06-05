"""JEP-300 — bridge ALL the engine's relation types (is-a, part-of, causal, property) into the persistent substrate
and reason over them after a reload, matching the engine. No transformer, no pretrained model.

Pre-registered bars in docs/amendments/jep300_multirelational_bridge.md.
"""
import json, tempfile, itertools, subprocess, sys, os
from pathlib import Path
import numpy as np
from world.understanding import UnderstandingEngine
from world.substrate_memory import SubstrateMemory

CORPUS = (
    "A poodle is a dog. A beagle is a dog. A dog is a mammal. A cat is a mammal. A mammal is an animal. "
    "A salmon is a fish. A fish is an animal. An animal is an organism. "
    "A cell is part of a heart. A heart is part of a dog. A wheel is part of a car. An engine is part of a car. "
    "Smoking causes cancer. A virus causes infection. Stress causes headache. "
    "A dog can bark. A bird can fly. A fish can swim."
)
CALIB = [("c1", "isa", "k1"), ("c2", "isa", "k2"), ("c3", "isa", "k3"), ("c4", "isa", "k4")]


def closure(graph):
    pairs = set()
    for node in graph:
        seen, stack = set(), list(graph.get(node, []))
        while stack:
            p = stack.pop()
            if p in seen:
                continue
            seen.add(p); pairs.add((node, p)); stack.extend(graph.get(p, []))
    return pairs


def gate_threshold(mem, seed):
    taught = np.mean([mem.query(c, "isa")[1] for (c, _, _) in CALIB])
    rng = np.random.default_rng(seed + 321)
    untaught = np.mean([mem.query(f"none_{int(rng.integers(1e9))}", "isa")[1] for _ in range(32)])
    return float((taught + untaught) / 2.0)


def climb(mem, x, y, role, gate, max_hops=10):
    cur, seen = x, {x}
    for _ in range(max_hops):
        p, s = mem.query(cur, role)
        if p is None or s < gate or p in seen:
            return False
        if p == y:
            return True
        seen.add(p); cur = p
    return False


def run_seed(seed):
    eng = UnderstandingEngine(seed=seed)
    eng.read(CORPUS)
    parents = {k: set(v) for k, v in eng.parents.items()}
    parts = {k: set(v) for k, v in eng.part_of_g.items()}
    causes = {k: set(v) for k, v in eng.causes.items()}
    props = {k: set(v) for k, v in dict(eng.properties).items()}

    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    for g, role in [(parents, "isa"), (parts, "partof"), (causes, "causes"), (props, "hasprop")]:
        for a, bs in g.items():
            for b in bs:
                mem.add_fact(a, role, b)
    for (c, r, p) in CALIB:
        mem.add_fact(c, r, p)

    d = tempfile.mkdtemp(prefix=f"multi_{seed}_")
    mem.save(d)
    mem2 = SubstrateMemory.load(d)
    gate = gate_threshold(mem2, seed)

    rng = np.random.default_rng(seed)
    nodes = sorted(set(parents) | {p for v in parents.values() for p in v})
    pnodes = sorted(set(parts) | {p for v in parts.values() for p in v})

    # ----- build query sets per relation, ground truth = the engine -----
    def sample_neg(cands, k):
        return [cands[i] for i in rng.choice(len(cands), min(k, len(cands)), replace=False)] if cands else []

    isa_pos = sorted(closure(parents))
    isa_neg = sample_neg([pr for pr in itertools.permutations(nodes, 2) if pr not in set(isa_pos)], len(isa_pos))
    part_pos = sorted(closure(parts))
    part_neg = sample_neg([pr for pr in itertools.permutations(pnodes, 2) if pr not in set(part_pos)], len(part_pos))
    cause_pos = [(a, b) for a, bs in causes.items() for b in bs]
    cause_neg = sample_neg([(a, b) for a in causes for b in {x for v in causes.values() for x in v}
                            if b not in causes[a]], len(cause_pos))
    prop_pos = [(a, b) for a, bs in props.items() for b in bs]
    prop_neg = sample_neg([(a, b) for a in props for b in {x for v in props.values() for x in v}
                           if b not in props[a]], len(prop_pos))

    per = {}
    def score(name, pos, neg, fn_sub, fn_eng):
        ok = 0; tot = 0
        for (a, b) in pos + neg:
            tot += 1; ok += (fn_sub(a, b) == fn_eng(a, b))
        per[name] = round(ok / tot, 3) if tot else None
        return ok, tot

    tot_ok = tot_n = 0
    for name, pos, neg, fs, fe in [
        ("isa", isa_pos, isa_neg, lambda a, b: climb(mem2, a, b, "isa", gate), lambda a, b: eng.is_a(a, b)),
        ("partof", part_pos, part_neg, lambda a, b: climb(mem2, a, b, "partof", gate), lambda a, b: eng.part_of(a, b)),
        ("causes", cause_pos, cause_neg, lambda a, b: mem2.contains(a, "causes", b, gate),
         lambda a, b: eng.causes_effect(a, b)),
        ("hasprop", prop_pos, prop_neg, lambda a, b: mem2.contains(a, "hasprop", b, gate),
         lambda a, b: eng.has_property(a, b)),
    ]:
        o, t = score(name, pos, neg, fs, fe); tot_ok += o; tot_n += t
    acc = tot_ok / tot_n

    # coverage: every stored edge recovered (transitive: 1-hop query; multi-valued: contains)
    edges = [(a, "isa", b) for a, v in parents.items() for b in v] + \
            [(a, "partof", b) for a, v in parts.items() for b in v]
    cov_t = sum(mem2.query(a, r)[0] == b for (a, r, b) in edges) / len(edges)
    medges = [(a, "causes", b) for a, v in causes.items() for b in v] + \
             [(a, "hasprop", b) for a, v in props.items() for b in v]
    cov_m = sum(mem2.contains(a, r, b, gate) for (a, r, b) in medges) / len(medges)
    coverage = (cov_t * len(edges) + cov_m * len(medges)) / (len(edges) + len(medges))

    # persistence: reload twice -> identical
    mem3 = SubstrateMemory.load(d); gate3 = gate_threshold(mem3, seed)
    persist = all(climb(mem3, a, b, "isa", gate3) == climb(mem2, a, b, "isa", gate) for (a, b) in isa_pos + isa_neg)

    return {"acc_vs_engine": round(acc, 3), "per_relation": per, "coverage": round(coverage, 3),
            "persist_ok": bool(persist), "n_q": tot_n}


def regression(repo):
    r296 = subprocess.run([sys.executable, "tools/run_jep296_unbounded_growth.py"], capture_output=True,
                          text=True, env={**os.environ, "PYTHONPATH": repo})
    r298 = subprocess.run([sys.executable, "tools/run_jep298_directed_binding.py"], capture_output=True,
                          text=True, env={**os.environ, "PYTHONPATH": repo})
    return ("JEP-296: PASS" in r296.stdout), ("JEP-298: PASS" in r298.stdout)


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-300: multi-relational knowledge through the persistent substrate ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: vs-engine acc={r['acc_vs_engine']} ({r['n_q']} queries) per-relation={r['per_relation']} "
              f"| coverage={r['coverage']} | persists={r['persist_ok']}", flush=True)
    reg296, reg298 = regression(repo)
    print(f"  regression: JEP-296={'PASS' if reg296 else 'FAIL'} JEP-298={'PASS' if reg298 else 'FAIL'}", flush=True)

    J300a = all(R[s]['acc_vs_engine'] >= 0.90 for s in seeds)
    J300b = all(R[s]['coverage'] >= 0.95 for s in seeds)
    J300c = all(R[s]['persist_ok'] for s in seeds)
    passed = J300a and J300b and J300c and reg296 and reg298
    print("\n--- VERDICT ---", flush=True)
    print(f"J300a multi-relational reasoning matches engine (>=.90): {J300a}", flush=True)
    print(f"J300b coverage of all relations (>=.95)                : {J300b}", flush=True)
    print(f"J300c persists across reload                           : {J300c}", flush=True)
    print(f"no-regression: JEP-296 & JEP-298 still PASS            : {reg296 and reg298}", flush=True)
    verdict = ("PASS - is-a, part-of, causal and property knowledge all live in the durable substrate and are "
               "reasoned over after reload, matching the engine") if passed else "NULL/partial - see per-relation"
    print(f"\nJEP-300: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP300"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "reg296": reg296,
                                                  "reg298": reg298, "J300a": J300a, "J300b": J300b, "J300c": J300c,
                                                  "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
