"""JEP-325 — per-relation gating in BrainQuery: robust on high-fan-out relations where a single isa-gate drops
members. No transformer. Pre-registered bars in docs/amendments/jep325_per_relation_gate.md.
"""
import json, tempfile
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory
from world.brain_query import BrainQuery


CAUSES = [f"cause{i}" for i in range(15)]          # HIGH FAN-OUT: cancer has 15 causes
EATS = [f"food{i}" for i in range(15)]             # cat eats 15 things


def build():
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    for c, p in [("poodle", "dog"), ("dog", "mammal"), ("mammal", "animal")]:
        mem.add_fact(c, "isa", p)
    for c in CAUSES:
        mem.add_fact(c, "causes", "cancer"); mem.add_fact("cancer", "caused_by", c)
    for o in EATS:
        mem.add_fact("cat", "eats", o)
    return mem


def single_gate_answers(mem, seed):
    """Baseline: force the isa-calibrated gate for everything (what BrainQuery did before JEP-325)."""
    edges = [(a, b) for (a, r, b) in mem.facts if r == "isa"]
    rng = np.random.default_rng(seed)
    t = np.mean([mem.edge_sim(a, "isa", b) for (a, b) in edges])
    u = np.mean([mem.query(f"none_{int(rng.integers(1e9))}", "isa")[1] for _ in range(30)])
    g = float((t + u) / 2)
    why = {c for (c, _) in mem.query_all("cancer", "caused_by", g)}
    what = {o for (o, _) in mem.query_all("cat", "eats", g)}
    return why, what


def run_seed(seed):
    mem = build(); d = tempfile.mkdtemp(prefix=f"prg_{seed}_"); mem.save(d); m = SubstrateMemory.load(d)
    bq = BrainQuery(m, seed=seed)

    why = set(bq.why("cancer")); what = set(bq.what("cat", "eat"))
    why_true = set(CAUSES); what_true = set(EATS)
    why_acc = len(why & why_true) / len(why_true)
    what_acc = len(what & what_true) / len(what_true)

    sg_why, sg_what = single_gate_answers(m, seed)
    sg_why_acc = len(sg_why & why_true) / len(why_true)
    sg_what_acc = len(sg_what & what_true) / len(what_true)

    # J325b simple cases unaffected
    simple = (bq.is_a("poodle", "animal") is True) and (bq.is_a("poodle", "fish") is False)
    return {"why_acc": round(why_acc, 3), "what_acc": round(what_acc, 3),
            "single_gate_why": round(sg_why_acc, 3), "single_gate_what": round(sg_what_acc, 3),
            "simple_ok": bool(simple)}


if __name__ == "__main__":
    print("=== JEP-325: per-relation gating in BrainQuery ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: per-relation why={r['why_acc']} what={r['what_acc']} | "
              f"single-gate baseline why={r['single_gate_why']} what={r['single_gate_what']} | "
              f"simple={r['simple_ok']}", flush=True)
    J325a = all(R[s]['why_acc'] >= 0.95 and R[s]['what_acc'] >= 0.95 for s in seeds)
    J325b = all(R[s]['simple_ok'] for s in seeds)
    passed = J325a and J325b
    print("\n--- VERDICT ---", flush=True)
    print(f"J325a per-relation gate full set on high fan-out (>=.95): {J325a}", flush=True)
    print(f"J325b simple cases unaffected                           : {J325b}", flush=True)
    verdict = ("PASS - per-relation gating recovers the full set on high-fan-out relations where a single isa-gate "
               "drops members") if passed else "NULL/partial"
    print(f"\nJEP-325: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP325"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J325a": J325a, "J325b": J325b, "passed": passed}, default=str))
    print("DONE", flush=True)
