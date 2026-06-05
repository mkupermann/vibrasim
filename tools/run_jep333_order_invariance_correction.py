"""JEP-333 — order-invariance of answers + correction-by-negation over the durable store. No transformer.
Pre-registered bars in docs/amendments/jep333_order_invariance_correction.md.
"""
import json, tempfile, itertools
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory
from world.brain_query import BrainQuery

# enough facts to cross a small module boundary so teach order changes the split
ISA = [("poodle", "dog"), ("beagle", "dog"), ("dog", "mammal"), ("cat", "mammal"), ("mammal", "animal"),
       ("salmon", "fish"), ("fish", "animal"), ("sparrow", "bird"), ("bird", "animal"),
       ("penguin", "bird"), ("penguin", "swimmer"), ("swimmer", "animal")]


def gate(mem, seed, role="isa"):
    edges = [(a, b) for (a, r, b) in mem.facts if r == role]
    rng = np.random.default_rng(seed)
    t = np.mean([mem.edge_sim(a, role, b) for (a, b) in edges]) if edges else 0.2
    u = np.mean([mem.query(f"n_{int(rng.integers(1e9))}", role)[1] for _ in range(30)])
    return float((t + u) / 2)


def climb(mem, x, y, g, mx=20):
    from collections import deque
    q, seen, n = deque([x]), {x}, 0
    while q and n < mx:
        cur = q.popleft(); n += 1
        for (p, _) in mem.query_all(cur, "isa", g):
            if p == y:
                return True
            if p not in seen:
                seen.add(p); q.append(p)
    return False


def build_order(facts, seed, cap):
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True, module_cap=cap)
    for (a, b) in facts:
        mem.add_fact(a, "isa", b)
    return mem


def run_seed(seed):
    nodes = sorted({x for e in ISA for x in e})
    queries = [(a, b) for (a, b) in itertools.permutations(nodes, 2)]

    # J333a: 5 random orders, small cap so splits differ; answers must agree
    answers = []
    for k in range(5):
        rng = np.random.default_rng(seed * 10 + k)
        order = list(ISA); rng.shuffle(order)
        mem = build_order(order, seed, cap=5)         # cap 5 -> ~3 modules, split depends on order
        g = gate(mem, seed)
        answers.append(tuple(climb(mem, a, b, g) for (a, b) in queries))
    agree = np.mean([answers[i] == answers[0] for i in range(5)])
    n_modules = len(build_order(list(reversed(ISA)), seed, cap=5).modules)

    # J333b: correction by negation
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    mem.add_fact("whale", "isa", "fish")              # taught wrong
    mem.add_fact("whale", "isa", "mammal")
    mem.add_fact("mammal", "isa", "animal")
    mem.add_fact("bird", "hasprop", "fly"); mem.add_fact("penguin", "isa", "bird")
    d = tempfile.mkdtemp(prefix=f"corr_{seed}_");
    mem.add_fact("whale", "not_isa", "fish")          # CORRECTION
    mem.add_fact("penguin", "not_hasprop", "fly")     # exception/correction
    mem.save(d); m = SubstrateMemory.load(d)
    bq = BrainQuery(m, seed=seed)
    corr_isa = (bq.is_a("whale", "fish") is False) and (bq.is_a("whale", "animal") is True)
    corr_prop = (bq.has_property("penguin", "fly") is False)

    # J333c persists (reload again)
    m2 = SubstrateMemory.load(d); bq2 = BrainQuery(m2, seed=seed)
    persist = (bq2.is_a("whale", "fish") is False) and (bq2.has_property("penguin", "fly") is False)

    return {"order_agreement": round(float(agree), 3), "n_modules": n_modules,
            "correction_isa": bool(corr_isa), "correction_prop": bool(corr_prop), "persist": bool(persist)}


if __name__ == "__main__":
    print("=== JEP-333: order-invariance + correction-by-negation ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: order-agreement={r['order_agreement']} ({r['n_modules']} modules) | "
              f"correction is-a={r['correction_isa']} prop={r['correction_prop']} | persists={r['persist']}", flush=True)
    J333a = all(R[s]['order_agreement'] >= 1.0 for s in seeds)
    J333b = all(R[s]['correction_isa'] and R[s]['correction_prop'] for s in seeds)
    J333c = all(R[s]['persist'] for s in seeds)
    passed = J333a and J333b and J333c
    print("\n--- VERDICT ---", flush=True)
    print(f"J333a answers identical across 5 teach orders: {J333a}", flush=True)
    print(f"J333b correction-by-negation flips the answer : {J333b}", flush=True)
    print(f"J333c corrected answers persist               : {J333c}", flush=True)
    verdict = ("PASS - answers are invariant to teach order (routing finds all holding modules), and a later "
               "negation correctly overrides an earlier fact, durably") if passed else "NULL/partial"
    print(f"\nJEP-333: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP333"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J333a": J333a, "J333b": J333b, "J333c": J333c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
