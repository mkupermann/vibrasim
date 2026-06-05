"""JEP-299 — bridge the Understanding Engine's learned taxonomy into the PERSISTENT substrate store, then reason
over it after a reload (engine gone). Shows the reading brain's knowledge survives close+reopen and is reasoned
through the substrate itself. No transformer, no pretrained model.

Pre-registered bars in docs/amendments/jep299_engine_substrate_bridge.md.
"""
import json, tempfile, itertools
from pathlib import Path
import numpy as np
from world.understanding import UnderstandingEngine
from world.substrate_memory import SubstrateMemory

CORPUS = (
    "A poodle is a dog. A beagle is a dog. A dog is a mammal. A cat is a mammal. "
    "A mammal is an animal. A salmon is a fish. A fish is an animal. A sparrow is a bird. "
    "A bird is an animal. An animal is an organism. An oak is a tree. A tree is a plant. "
    "A plant is an organism. A rose is a plant."
)
CALIB = [("c1", "isa", "k1"), ("c2", "isa", "k2"), ("c3", "isa", "k3"), ("c4", "isa", "k4")]


def transitive_closure(parents):
    """All (descendant, ancestor) true pairs from the is-a DAG."""
    pairs = set()
    for node in parents:
        seen, stack = set(), list(parents.get(node, []))
        while stack:
            p = stack.pop()
            if p in seen:
                continue
            seen.add(p); pairs.add((node, p)); stack.extend(parents.get(p, []))
    return pairs


def gate_threshold(mem, seed):
    taught = np.mean([mem.query(c, "isa")[1] for (c, _, _) in CALIB])
    rng = np.random.default_rng(seed + 321)
    untaught = np.mean([mem.query(f"none_{int(rng.integers(1e9))}", "isa")[1] for _ in range(32)])
    return float((taught + untaught) / 2.0)


def is_a(mem, x, y, gate, max_hops=10):
    cur, seen = x, {x}
    for _ in range(max_hops):
        p, s = mem.query(cur, "isa")
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
    nodes = sorted(set(parents) | {p for ps in parents.values() for p in ps})

    # bridge engine taxonomy -> directed substrate store
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    for child, ps in parents.items():
        for p in ps:
            mem.add_fact(child, "isa", p)
    for (c, r, p) in CALIB:
        mem.add_fact(c, r, p)

    # build query set: all true closure pairs (positives) + matched random non-pairs (negatives)
    pos = sorted(transitive_closure(parents))
    rng = np.random.default_rng(seed)
    allpairs = [(a, b) for a, b in itertools.permutations(nodes, 2)]
    negcand = [pr for pr in allpairs if pr not in set(pos)]
    neg = [negcand[i] for i in rng.choice(len(negcand), min(len(pos), len(negcand)), replace=False)]
    queries = [(a, b, True) for (a, b) in pos] + [(a, b, False) for (a, b) in neg]

    # pre-save answers (sanity) + ground truth from the engine
    gate = gate_threshold(mem, seed)
    pre = {(a, b): is_a(mem, a, b, gate) for (a, b, _) in queries}

    # SAVE -> reload into a FRESH store (engine discarded) -> answer from the substrate alone
    d = tempfile.mkdtemp(prefix=f"bridge_{seed}_")
    mem.save(d)
    mem2 = SubstrateMemory.load(d)
    gate2 = gate_threshold(mem2, seed)

    correct = depth_ok = 0
    for (a, b, truth) in queries:
        ans = is_a(mem2, a, b, gate2)
        correct += (ans == (eng.is_a(a, b)))          # match the ENGINE's ground truth
    j299a = correct / len(queries)

    # J299b: 1-hop coverage of every is-a edge from the reloaded store
    edges = [(c, p) for c, ps in parents.items() for p in ps]
    cov = sum(mem2.query(c, "isa")[0] == p for (c, p) in edges) / len(edges)

    # J299c: reloaded answers identical to pre-save
    persist_ok = all(is_a(mem2, a, b, gate2) == pre[(a, b)] for (a, b, _) in queries)

    # a concrete multi-hop demo the engine was never told directly
    demo = ("poodle", "organism", is_a(mem2, "poodle", "organism", gate2))
    return {"acc_vs_engine": round(j299a, 3), "coverage_1hop": round(cov, 3), "persist_ok": bool(persist_ok),
            "n_pos": len(pos), "n_queries": len(queries), "n_edges": len(edges), "demo": demo}


if __name__ == "__main__":
    print("=== JEP-299: engine taxonomy -> persistent substrate -> reason after reload ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: vs-engine acc={r['acc_vs_engine']} ({r['n_queries']} queries, {r['n_pos']} multi-hop "
              f"positives) | 1-hop coverage={r['coverage_1hop']} ({r['n_edges']} edges) | persists={r['persist_ok']} "
              f"| demo poodle->organism={r['demo'][2]}", flush=True)

    J299a = all(R[s]['acc_vs_engine'] >= 0.90 for s in seeds)
    J299b = all(R[s]['coverage_1hop'] >= 0.95 for s in seeds)
    J299c = all(R[s]['persist_ok'] for s in seeds)
    passed = J299a and J299b and J299c
    print("\n--- VERDICT ---", flush=True)
    print(f"J299a substrate matches engine reasoning after reload (>=.90): {J299a}", flush=True)
    print(f"J299b 1-hop bridge coverage (>=.95)                          : {J299b}", flush=True)
    print(f"J299c answers persist across save/load                       : {J299c}", flush=True)
    verdict = ("PASS - the reading brain's taxonomy lives in the durable substrate; after close+reopen the "
               "substrate alone answers multi-hop questions, matching the engine") if passed else "NULL/partial"
    print(f"\nJEP-299: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP299"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds},
                                                  "J299a": J299a, "J299b": J299b, "J299c": J299c,
                                                  "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
