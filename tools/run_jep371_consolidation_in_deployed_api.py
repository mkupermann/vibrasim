"""JEP-371 — prove the DEPLOYED BrainQuery.is_a benefits from SubstrateMemory.consolidate_closure(). No transformer.
Pre-registered bars in docs/amendments/jep371_consolidation_in_deployed_api.md.
"""
import json, subprocess, sys, os
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


def deep_neg_acc(mem, parent, n_nodes, seed):
    rng = np.random.default_rng(seed + 100)
    bq = BrainQuery(mem, seed=seed)
    leaves = [k for k in range(n_nodes) if k not in set(parent.values())]; rng.shuffle(leaves)
    sample = leaves[:40]
    allnodes = list(range(n_nodes))
    deep, neg = [], []
    for x in sample:
        anc = ancestors(parent, x)
        if anc:
            z = anc[min(len(anc) - 1, int(rng.integers(0, len(anc))))]
            deep.append(bq.is_a(f"n{x}", f"n{z}") is True)
        nonanc = [y for y in allnodes if y != x and y not in set(anc)]
        if nonanc:
            neg.append(bq.is_a(f"n{x}", f"n{int(rng.choice(nonanc))}") is False)
    return round(sum(deep) / len(deep), 3), round(sum(neg) / len(neg), 3)


def run_seed(seed, N=360, D=8192):
    rng = np.random.default_rng(seed)
    parent, depth = build_tree(N, rng)
    mem = SubstrateMemory(D=D, directed=True)
    for i in range(1, N):
        mem.add_fact(f"n{i}", "isa", f"n{parent[i]}")
    # a couple of exceptions to confirm closure respects not_isa
    for d in [k for k in range(N) if depth[k] >= 4][:4]:
        anc = ancestors(parent, d)
        if len(anc) >= 2:
            mem.add_fact(f"n{d}", "not_isa", f"n{anc[-1]}")     # deny the root-most ancestor

    before_deep, before_neg = deep_neg_acc(mem, parent, N, seed)
    cons = mem.consolidate_closure(("isa",))
    after_deep, after_neg = deep_neg_acc(cons, parent, N, seed)

    # idempotency: consolidate again -> same fact set
    cons2 = cons.consolidate_closure(("isa",))
    idempotent = set(cons.facts) == set(cons2.facts)
    # negation respected: denied ancestor edges must NOT have been materialized
    denied = {(s, o) for (s, r, o) in mem.facts if r == "not_isa"}
    no_bridge = all((s, o) not in {(a, b) for (a, rr, b) in cons.facts if rr == "isa"} for (s, o) in denied)

    return {"facts_before": len(mem.facts), "facts_after": len(cons.facts),
            "before_deep": before_deep, "after_deep": after_deep,
            "before_neg": before_neg, "after_neg": after_neg,
            "idempotent": bool(idempotent), "no_bridge_through_exception": bool(no_bridge)}


def regression(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow",
                        "tests/test_substrate_memory.py", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    return ("failed" not in r.stdout) and ("error" not in r.stdout.lower().split("warnings")[0]), r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-371: closure consolidation in the deployed API ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: deep is-a {r['before_deep']} -> {r['after_deep']} | neg {r['before_neg']} -> "
              f"{r['after_neg']} | facts {r['facts_before']}->{r['facts_after']} | idempotent={r['idempotent']} | "
              f"no-bridge-through-exception={r['no_bridge_through_exception']}", flush=True)
    gate_ok, gate_line = regression(repo)
    print(f"  test suite: {gate_ok}  ({gate_line})", flush=True)

    J371a = all(R[s]['after_deep'] >= 0.95 and R[s]['after_deep'] > R[s]['before_deep'] for s in seeds)
    J371b = all(R[s]['after_neg'] >= 0.95 and R[s]['no_bridge_through_exception'] for s in seeds)
    J371c = all(R[s]['idempotent'] for s in seeds) and gate_ok
    passed = J371a and J371b and J371c
    print("\n--- VERDICT ---", flush=True)
    print(f"J371a live is_a deep restored >=0.95 & > before : {J371a}", flush=True)
    print(f"J371b negations respected (>=0.95, no bad bridge): {J371b}", flush=True)
    print(f"J371c idempotent + no test regression           : {J371c}", flush=True)
    verdict = ("PASS - SubstrateMemory.consolidate_closure() makes the DEPLOYED BrainQuery.is_a reliable on deep "
               "chains (single-hop after materialization), respects not_isa exceptions, is idempotent, and breaks no "
               "tests. The within-domain reliability fix is now a real, reusable capability of the durable store.") \
        if passed else "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-371: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP371"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J371a": J371a, "J371b": J371b,
                                                  "J371c": J371c, "passed": passed}, default=str))
    print("DONE", flush=True)
