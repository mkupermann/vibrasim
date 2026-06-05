"""JEP-369 — is dimension the lever to restore within-domain 'no mistakes' at scale? No transformer.
Pre-registered bars in docs/amendments/jep369_dimension_restores_within_domain.md.

Re-runs the JEP-368 stress at ~360 facts for D in {4096, 8192, 16384}, focusing on the difficulties that failed
(D1 deep is-a, D3 distractors, D4 adversarial composition).
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


def run(n_nodes, seed, D):
    rng = np.random.default_rng(seed)
    parent, depth = build_tree(n_nodes, rng)
    m = SubstrateMemory(D=D, directed=True)
    for i in range(1, n_nodes):
        m.add_fact(f"n{i}", "isa", f"n{parent[i]}")
    internal = [k for k in range(n_nodes) if depth[k] in (1, 2)]
    prop_of = {}
    for j, a in enumerate(internal[:12]):
        m.add_fact(f"n{a}", "hasprop", f"prop{j}"); prop_of[a] = f"prop{j}"
    exceptions = {}
    deep_nodes = [k for k in range(n_nodes) if depth[k] >= 4]; rng.shuffle(deep_nodes)
    for d in deep_nodes[:8]:
        carrier = next((a for a in ancestors(parent, d) if a in prop_of), None)
        if carrier is not None:
            m.add_fact(f"n{d}", "not_hasprop", prop_of[carrier]); exceptions[d] = prop_of[carrier]

    bq = BrainQuery(m, seed=seed)
    leaves = [k for k in range(n_nodes) if k not in set(parent.values())]; rng.shuffle(leaves)
    sample = leaves[:40] if len(leaves) >= 40 else leaves
    allnodes = list(range(n_nodes))

    d1 = []
    for x in sample:
        anc = ancestors(parent, x)
        if anc:
            z = anc[min(len(anc) - 1, int(rng.integers(0, len(anc))))]
            d1.append(bq.is_a(f"n{x}", f"n{z}") is True)
    d3 = []
    for x in sample:
        anc = set(ancestors(parent, x))
        non = [y for y in allnodes if y != x and y not in anc]
        if non:
            d3.append(bq.is_a(f"n{x}", f"n{int(rng.choice(non))}") is False)
    d4 = []
    for d, p in exceptions.items():
        root_ok = bq.is_a(f"n{d}", "n0") is True
        exc_ok = bq.has_property(f"n{d}", p) is False
        anc = ancestors(parent, d); non = [y for y in allnodes if y not in anc and y != d]
        dist_ok = bq.is_a(f"n{d}", f"n{int(rng.choice(non))}") is False if non else True
        d4.append(root_ok and exc_ok and dist_ok)

    def acc(l):
        return round(sum(l) / len(l), 3) if l else None
    return {"facts": len(m.facts), "n_modules": len(m.modules), "D1": acc(d1), "D3": acc(d3), "D4": acc(d4)}


if __name__ == "__main__":
    print("=== JEP-369: dimension as the lever to restore within-domain accuracy (~360 facts) ===", flush=True)
    N = 360; seeds = [0, 7]; Ds = [4096, 8192, 16384]
    R = {s: {D: run(N, s, D) for D in Ds} for s in seeds}
    for s in seeds:
        for D in Ds:
            r = R[s][D]
            print(f"  seed {s} | D={D:>5} | {r['facts']} facts, {r['n_modules']} modules: "
                  f"D1={r['D1']} D3={r['D3']} D4={r['D4']}", flush=True)

    J369a = all(R[s][16384]["D1"] >= 0.95 and R[s][16384]["D1"] >= R[s][4096]["D1"] for s in seeds)
    J369b = all(R[s][16384]["D4"] >= 0.85 and R[s][16384]["D4"] > R[s][4096]["D4"] for s in seeds)
    def nondec(metric):
        return all(R[s][4096][metric] <= R[s][8192][metric] <= R[s][16384][metric] for s in seeds)
    J369c = nondec("D1") and nondec("D4")
    passed = J369a and J369b
    print("\n--- VERDICT ---", flush=True)
    print(f"J369a deep is-a restored >=0.95 at D=16384      : {J369a}", flush=True)
    print(f"J369b adversarial compose restored >=0.85       : {J369b}", flush=True)
    print(f"J369c monotonic in D (lever works as predicted) : {J369c}", flush=True)
    if passed:
        verdict = ("PASS - DIMENSION is the lever: raising D shrinks the auto-grown module count and per-hop cleanup "
                   "error, restoring within-domain accuracy at ~360 facts (deep is-a >=0.95, adversarial composition "
                   ">=0.85) where D=4096 collapsed. The 'no mistakes' taught domain is bounded by a TUNABLE knob (D), "
                   "not a hard wall -- a larger, deeper error-free domain is reachable by paying memory.")
    else:
        verdict = ("NULL/partial - higher D did not fully restore within-domain accuracy; the ceiling is at least "
                   "partly STRUCTURAL (routing/compounding), not pure cleanup noise. See rows. Reported, not retuned.")
    print(f"\nJEP-369: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP369"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J369a": J369a, "J369b": J369b, "J369c": J369c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
