"""JEP-326 — decisive diagnostic: does a single isa-gate ever drop a high-fan-out relation that the relation's own
gate captures? Sweep fan-out k and module load; report single-gate vs per-relation-gate recall. No transformer.
Pre-registered bars in docs/amendments/jep326_gate_near_capacity.md.
"""
import json
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory


def isa_gate(mem, seed):
    edges = [(a, b) for (a, r, b) in mem.facts if r == "isa"]
    rng = np.random.default_rng(seed)
    t = np.mean([mem.edge_sim(a, "isa", b) for (a, b) in edges]) if edges else 0.2
    u = np.mean([mem.query(f"n_{int(rng.integers(1e9))}", "isa")[1] for _ in range(30)])
    return float((t + u) / 2)


def rel_gate(mem, seed, role):
    edges = [(a, b) for (a, r, b) in mem.facts if r == role]
    rng = np.random.default_rng(seed + 1)
    t = np.mean([mem.edge_sim(a, role, b) for (a, b) in edges]) if edges else 0.2
    u = np.mean([mem.query(f"n_{int(rng.integers(1e9))}", role)[1] for _ in range(30)])
    return float((t + u) / 2)


def measure(k, load, seed, single_module):
    rng = np.random.default_rng(seed)
    cap = 10 ** 9 if single_module else None
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True, module_cap=cap)
    # `load` single-valued isa filler facts (fan-out 1 -> high per-value sim -> high isa gate)
    for i in range(load):
        mem.add_fact(f"a{i}", "isa", f"b{i}")
    # one high-fan-out relation: subj eats k objects
    objs = [f"food{j}" for j in range(k)]
    for o in objs:
        mem.add_fact("subj", "eats", o)
    gi = isa_gate(mem, seed); ge = rel_gate(mem, seed, "eats")
    single = {o for (o, _) in mem.query_all("subj", "eats", gi)}
    perrel = {o for (o, _) in mem.query_all("subj", "eats", ge)}
    return (len(single & set(objs)) / k, len(perrel & set(objs)) / k, gi, ge, len(mem.modules))


if __name__ == "__main__":
    print("=== JEP-326: single-gate vs per-relation-gate on high fan-out (sweep) ===", flush=True)
    seeds = [0, 7]
    grid = [(k, load, sm) for sm in [True] for load in [20, 110] for k in [10, 20, 30]]
    rows = {}
    max_gap = 0.0
    for (k, load, sm) in grid:
        sg = [measure(k, load, s, sm) for s in seeds]
        single = np.mean([r[0] for r in sg]); perrel = np.mean([r[1] for r in sg])
        gap = perrel - single
        max_gap = max(max_gap, gap)
        rows[f"k{k}_load{load}_single"] = {"single": round(single, 3), "perrel": round(perrel, 3),
                                           "gap": round(gap, 3), "isa_gate": round(sg[0][2], 3),
                                           "eats_gate": round(sg[0][3], 3)}
        print(f"  k={k} load={load} 1-module: single-gate recall={round(single,3)} | per-relation={round(perrel,3)} "
              f"| gap={round(gap,3)} (isa_gate={round(sg[0][2],3)} eats_gate={round(sg[0][3],3)})", flush=True)

    J326a = all(v["perrel"] >= 0.90 for v in rows.values())
    J326b = max_gap >= 0.15
    print("\n--- VERDICT ---", flush=True)
    print(f"J326a per-relation gate recall >=0.90 everywhere: {J326a}", flush=True)
    print(f"J326b a real contrast exists (max gap>=0.15)    : {J326b} (max gap={round(max_gap,3)})", flush=True)
    if J326a and J326b:
        verdict = "PASS - per-relation gating IS needed for high fan-out (single isa-gate over-rejects); refactor justified"
    elif J326a and not J326b:
        verdict = ("NULL - no contrast even near capacity: a single gate suffices; the per-relation refactor is "
                   "UNNECESSARY (recommend revert unless JEP-323's materialized case still needs it)")
    else:
        verdict = "NULL/partial - per-relation gate itself drops; deeper issue"
    print(f"\nJEP-326: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP326"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": rows, "J326a": J326a, "J326b": J326b,
                                                  "max_gap": max_gap, "verdict": verdict}, default=str))
    print("DONE", flush=True)
