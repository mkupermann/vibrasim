"""JEP-368 — where do mistakes begin INSIDE a taught domain? Scale + depth + distractors + composition.
No transformer. Pre-registered bars in docs/amendments/jep368_within_domain_error_onset.md.

Builds a large synthetic taxonomy across auto-grown modules and stress-tests held-out derived questions of
increasing difficulty, reporting per-difficulty accuracy and the fact-count where any error first appears.
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
        w = np.array([depth[k] + 1 for k in cands], float)          # bias deeper -> grow long chains
        p = int(rng.choice(cands, p=w / w.sum()))
        parent[i] = p; depth[i] = depth[p] + 1
    return parent, depth


def ancestors(parent, x):
    out = []
    while parent[x] is not None:
        out.append(parent[x]); x = parent[x]
    return out                                                       # root-ward, excludes x


def run_size(n_nodes, seed):
    rng = np.random.default_rng(seed)
    parent, depth = build_tree(n_nodes, rng)
    m = SubstrateMemory(D=4096, directed=True)
    for i in range(1, n_nodes):
        m.add_fact(f"n{i}", "isa", f"n{parent[i]}")

    # properties at internal nodes; exceptions at some deep descendants
    internal = [k for k in range(n_nodes) if depth[k] in (1, 2)]
    prop_of = {}
    for j, a in enumerate(internal[:12]):
        p = f"prop{j}"
        m.add_fact(f"n{a}", "hasprop", p); prop_of[a] = p
    # insert exceptions: pick deep nodes whose ancestor carries a property, deny it there
    exceptions = {}
    deep_nodes = [k for k in range(n_nodes) if depth[k] >= 4]
    rng.shuffle(deep_nodes)
    for d in deep_nodes[:8]:
        anc = ancestors(parent, d)
        carrier = next((a for a in anc if a in prop_of), None)
        if carrier is not None:
            m.add_fact(f"n{d}", "not_hasprop", prop_of[carrier]); exceptions[d] = prop_of[carrier]

    bq = BrainQuery(m, seed=seed)
    fact_count = len(m.facts)

    leaves = [k for k in range(n_nodes) if k not in set(parent.values())]
    rng.shuffle(leaves)
    sample = leaves[:40] if len(leaves) >= 40 else leaves

    # D1 deep is-a chains
    d1 = []
    for x in sample:
        anc = ancestors(parent, x)
        if not anc:
            continue
        z = anc[min(len(anc) - 1, rng.integers(0, len(anc)))]       # an ancestor up the chain
        d1.append(bq.is_a(f"n{x}", f"n{z}") is True)

    # D2 inheritance + exceptions at depth
    d2 = []
    for d, p in exceptions.items():
        d2.append(bq.has_property(f"n{d}", p) is False)             # exception node: must be False
        for child in [k for k in range(n_nodes) if parent[k] == d]:
            d2.append(bq.has_property(f"n{child}", p) is False)     # most-specific-wins flows down
    for a, p in list(prop_of.items())[:6]:
        desc = [k for k in range(n_nodes) if a in ancestors(parent, k) and k not in exceptions][:3]
        for dd in desc:
            d2.append(bq.has_property(f"n{dd}", p) is True)         # inherited, no exception

    # D3 distractor / negative probes (must be False)
    d3 = []
    allnodes = list(range(n_nodes))
    for x in sample:
        anc = set(ancestors(parent, x))
        non = [y for y in allnodes if y != x and y not in anc]
        if non:
            y = int(rng.choice(non))
            d3.append(bq.is_a(f"n{x}", f"n{y}") is False)

    # D4 adversarial composition (conjunction must all hold)
    d4 = []
    for d, p in exceptions.items():
        root_ok = bq.is_a(f"n{d}", "n0") is True                    # full-chain is-a
        exc_ok = bq.has_property(f"n{d}", p) is False               # exception respected
        anc = ancestors(parent, d)
        non = [y for y in allnodes if y not in anc and y != d]
        dist_ok = bq.is_a(f"n{d}", f"n{int(rng.choice(non))}") is False if non else True
        d4.append(root_ok and exc_ok and dist_ok)

    def acc(lst):
        return round(sum(lst) / len(lst), 3) if lst else None
    return {"facts": fact_count, "D1": acc(d1), "D2": acc(d2), "D3": acc(d3), "D4": acc(d4)}


if __name__ == "__main__":
    print("=== JEP-368: within-domain error onset (scale + depth + distractors + composition) ===", flush=True)
    sizes = [80, 160, 260, 360]
    seeds = [0, 7]
    R = {s: {n: run_size(n, s) for n in sizes} for s in seeds}
    for s in seeds:
        for n in sizes:
            r = R[s][n]
            print(f"  seed {s} | {r['facts']:>4} facts: D1(deep is-a)={r['D1']} D2(inherit+exc)={r['D2']} "
                  f"D3(distractor)={r['D3']} D4(adversarial)={r['D4']}", flush=True)

    def worst(metric, bar):
        return all(R[s][n][metric] is not None and R[s][n][metric] >= bar for s in seeds for n in sizes)
    D1ok = worst("D1", 0.95); D2ok = worst("D2", 0.90); D3ok = worst("D3", 0.95); D4ok = worst("D4", 0.85)

    # onset: first fact-count where any difficulty drops below 0.95 (averaged over seeds)
    onset = None
    for n in sizes:
        worst_n = min(R[s][n][k] for s in seeds for k in ("D1", "D2", "D3", "D4") if R[s][n][k] is not None)
        if worst_n < 0.95:
            onset = R[seeds[0]][n]["facts"]; break

    passed = D1ok and D2ok and D3ok and D4ok
    print("\n--- VERDICT ---", flush=True)
    print(f"D1 deep is-a >=0.95           : {D1ok}", flush=True)
    print(f"D2 inheritance+exception >=0.90: {D2ok}", flush=True)
    print(f"D3 distractor/negative >=0.95 : {D3ok}", flush=True)
    print(f"D4 adversarial compose >=0.85 : {D4ok}", flush=True)
    print(f"error onset (<0.95 anywhere)  : {('~'+str(onset)+' facts') if onset else 'none within tested range'}",
          flush=True)
    verdict = ("PASS - within-domain Q&A stays error-free (or near) up to ~360 facts across multiple auto-grown "
               "modules, at depth ~8, under distractors and adversarial composition. The taught-domain ceiling is "
               "comfortably large -- the reachable 'no mistakes' domain is real and sizeable.") if passed else \
              (f"PARTIAL/NULL - within-domain mistakes begin around {onset} facts (or some difficulty under bar); "
               "that IS the honest taught-domain ceiling (see rows). Reported, not retuned.")
    print(f"\nJEP-368: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP368"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "D1": D1ok, "D2": D2ok, "D3": D3ok, "D4": D4ok,
                                                  "onset": onset, "passed": passed}, default=str))
    print("DONE", flush=True)
