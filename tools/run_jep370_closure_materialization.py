"""JEP-370 — materialize the transitive closure to remove compounding hops. No transformer.
Pre-registered bars in docs/amendments/jep370_closure_materialization.md.

BASE: is_a via multi-hop walk (reproduces JEP-368/369 failure).
CLOSURE: store every ancestor edge directly -> is_a is a single-hop membership probe that does not compound.
"""
import json
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory
from world.brain_query import BrainQuery


def build_tree(n_nodes, rng, max_depth=8):
    depth = {0: 0}; parent = {0: None}
    for i in range(1, n_nodes):
        cands = [k for k in depth if depth[k] < max_depth]
        w = np.array([depth[k] + 1 for k in cands], float)
        p = int(rng.choice(cands, p=w / w.sum()))
        parent[i] = p; depth[i] = depth[p] + 1
    return parent, depth


def ancestors(parent, x):
    out = []
    while parent[x] is not None:
        out.append(parent[x]); x = parent[x]
    return out


def make_kb(n_nodes, seed, D, closure):
    rng = np.random.default_rng(seed)
    parent, depth = build_tree(n_nodes, rng)
    m = SubstrateMemory(D=D, directed=True)
    for i in range(1, n_nodes):
        m.add_fact(f"n{i}", "isa", f"n{parent[i]}")
        if closure:                                            # materialize all ancestor edges (consolidation)
            for a in ancestors(parent, i)[1:]:                 # skip direct parent (already stored)
                m.add_fact(f"n{i}", "isa", f"n{a}")
    internal = [k for k in range(n_nodes) if depth[k] in (1, 2)]
    prop_of = {}
    for j, a in enumerate(internal[:12]):
        m.add_fact(f"n{a}", "hasprop", f"prop{j}"); prop_of[a] = f"prop{j}"
    exceptions = {}
    deep = [k for k in range(n_nodes) if depth[k] >= 4]; rng.shuffle(deep)
    for d in deep[:8]:
        carrier = next((a for a in ancestors(parent, d) if a in prop_of), None)
        if carrier is not None:
            m.add_fact(f"n{d}", "not_hasprop", prop_of[carrier]); exceptions[d] = prop_of[carrier]
    return m, parent, depth, prop_of, exceptions, rng


def evaluate(n_nodes, seed, D, closure):
    m, parent, depth, prop_of, exceptions, rng = make_kb(n_nodes, seed, D, closure)
    bq = BrainQuery(m, seed=seed)
    g = bq.gate
    leaves = [k for k in range(n_nodes) if k not in set(parent.values())]; rng.shuffle(leaves)
    sample = leaves[:40] if len(leaves) >= 40 else leaves
    allnodes = list(range(n_nodes))

    def isa(x, z):                                             # single-hop probe in CLOSURE, walk in BASE
        return m.contains(f"n{x}", "isa", f"n{z}", g) if closure else (bq.is_a(f"n{x}", f"n{z}") is True)

    d1 = []
    for x in sample:
        anc = ancestors(parent, x)
        if anc:
            z = anc[min(len(anc) - 1, int(rng.integers(0, len(anc))))]
            d1.append(isa(x, z) is True)
    d3 = []
    for x in sample:
        anc = set(ancestors(parent, x))
        non = [y for y in allnodes if y != x and y not in anc]
        if non:
            d3.append(isa(x, int(rng.choice(non))) is False)
    d4 = []
    for d, p in exceptions.items():
        root_ok = isa(d, 0) is True
        exc_ok = bq.has_property(f"n{d}", p) is False
        anc = ancestors(parent, d); non = [y for y in allnodes if y not in anc and y != d]
        dist_ok = (isa(d, int(rng.choice(non))) is False) if non else True
        d4.append(bool(root_ok and exc_ok and dist_ok))

    def acc(l):
        return round(sum(l) / len(l), 3) if l else None
    return {"facts": len(m.facts), "modules": len(m.modules), "D1": acc(d1), "D3": acc(d3), "D4": acc(d4)}


if __name__ == "__main__":
    print("=== JEP-370: transitive-closure materialization (single-hop is-a, no compounding) ===", flush=True)
    N = 360; seeds = [0, 7]; Ds = [4096, 8192]
    R = {}
    for s in seeds:
        for D in Ds:
            R[(s, D, "BASE")] = evaluate(N, s, D, closure=False)
            R[(s, D, "CLOSURE")] = evaluate(N, s, D, closure=True)
            b, c = R[(s, D, "BASE")], R[(s, D, "CLOSURE")]
            print(f"  seed {s} D={D}: BASE   {b['facts']}f/{b['modules']}m D1={b['D1']} D3={b['D3']} D4={b['D4']}",
                  flush=True)
            print(f"  seed {s} D={D}: CLOSURE {c['facts']}f/{c['modules']}m D1={c['D1']} D3={c['D3']} D4={c['D4']}",
                  flush=True)

    # bars evaluated at D=8192 (the predicted-restored setting); require improvement over BASE at same D
    def clo(s, D):
        return R[(s, D, "CLOSURE")]
    def bas(s, D):
        return R[(s, D, "BASE")]
    J370a = all(clo(s, 8192)["D1"] >= 0.95 and clo(s, 8192)["D1"] > bas(s, 8192)["D1"] for s in seeds)
    J370b = all(clo(s, 8192)["D4"] >= 0.85 and clo(s, 8192)["D4"] > bas(s, 8192)["D4"] for s in seeds)
    J370c = all(clo(s, 8192)["D3"] >= 0.95 for s in seeds)
    passed = J370a and J370b and J370c
    print("\n--- VERDICT ---", flush=True)
    print(f"J370a deep is-a restored >=0.95 & > BASE   : {J370a}", flush=True)
    print(f"J370b adversarial restored >=0.85 & > BASE : {J370b}", flush=True)
    print(f"J370c no distractor false-positive (>=0.95): {J370c}", flush=True)
    verdict = ("PASS - materializing the transitive closure turns deep is-a into a single-hop lookup that does NOT "
               "compound, restoring within-domain deep reasoning (D1>=0.95) and adversarial composition (D4>=0.85) at "
               "~360 facts where the multi-hop walk collapsed -- without inflating distractor false-positives. The "
               "within-domain 'no mistakes' domain IS reachable at scale by paying storage (consolidation), the "
               "correct lever (not dimension).") if passed else \
              ("NULL/partial - closure did not fully restore accuracy (or inflated false-positives). See rows; the "
               "within-domain ceiling is tighter than storage alone can fix. Reported, not retuned.")
    print(f"\nJEP-370: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP370"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {f"{s}|{D}|{c}": R[(s, D, c)] for (s, D, c) in R},
                                                  "J370a": J370a, "J370b": J370b, "J370c": J370c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
