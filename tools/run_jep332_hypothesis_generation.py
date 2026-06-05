"""JEP-332 — probe the creative-generation wall: sibling-majority PLAUSIBLE hypotheses vs novel invention. The
experiment is designed to find the boundary (a bounded result is the expected finding). No transformer.
Pre-registered bars in docs/amendments/jep332_hypothesis_generation.md.
"""
import json, tempfile
from collections import Counter
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory

# known dogs with properties; collie is NEW (class only) -> hypothesize its properties from siblings
DOGS = ["poodle", "beagle", "terrier", "boxer"]
PROPS = {"poodle": ["bark", "fetch"], "beagle": ["bark", "sniff"], "terrier": ["bark", "dig"], "boxer": ["bark"]}
TRUE_COLLIE = ["bark"]                       # ground-truth: a collie barks (the shared/majority property)
CALIB = [("z1", "isa", "w1"), ("z2", "isa", "w2"), ("z3", "isa", "w3")]


def gate(mem, seed, role="isa"):
    edges = [(a, b) for (a, r, b) in mem.facts if r == role]
    rng = np.random.default_rng(seed)
    t = np.mean([mem.edge_sim(a, role, b) for (a, b) in edges]) if edges else 0.2
    u = np.mean([mem.query(f"n_{int(rng.integers(1e9))}", role)[1] for _ in range(30)])
    return float((t + u) / 2)


def build():
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    for d in DOGS:
        mem.add_fact(d, "isa", "dog")
    mem.add_fact("collie", "isa", "dog")     # NEW entity, class only
    for d, ps in PROPS.items():
        for p in ps:
            mem.add_fact(d, "hasprop", p)
    for (c, r, p) in CALIB:
        mem.add_fact(c, r, p)
    return mem


def siblings(mem, x, g):
    parent, _ = mem.query(x, "isa")
    if parent is None:
        return []
    # who else is-a the same parent? (scan facts; small store)
    return [a for (a, r, b) in mem.facts if r == "isa" and b == parent and a != x]


def hypothesize(mem, x, g, threshold=0.5):
    """Sibling-majority properties as PLAUSIBLE hypotheses for x."""
    sibs = siblings(mem, x, g)
    cnt = Counter()
    for s in sibs:
        for (p, sc) in mem.query_all(s, "hasprop", g):
            cnt[p] += 1
    n = max(1, len(sibs))
    return [p for p, c in cnt.items() if c / n >= threshold]


def run_seed(seed):
    mem = build(); d = tempfile.mkdtemp(prefix=f"hyp_{seed}_"); mem.save(d)
    m = SubstrateMemory.load(d); g = gate(m, seed)

    hyp = set(hypothesize(m, "collie", g, threshold=0.6))
    # J332a plausibility: hypotheses match the true (majority) properties
    true = set(TRUE_COLLIE)
    # precision+recall vs true majority property set
    tp = len(hyp & true); fp = len(hyp - true); fn = len(true - hyp)
    plaus = tp / (tp + fp + fn) if (tp + fp + fn) else 1.0           # Jaccard

    # J332b boundary: every generated atom already exists in the store (no invented-novel atom)
    existing_props = {o for (s, r, o) in m.facts if r == "hasprop"}
    novel_invented = [p for p in hyp if p not in existing_props]

    return {"hypotheses": sorted(hyp), "plausibility": round(float(plaus), 3),
            "novel_atoms_invented": len(novel_invented), "true": sorted(true)}


if __name__ == "__main__":
    print("=== JEP-332: probe creative-generation wall (plausible hypotheses vs invention) ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: collie hypotheses={r['hypotheses']} (true {r['true']}) | plausibility={r['plausibility']} "
              f"| novel atoms invented={r['novel_atoms_invented']}", flush=True)
    J332a = all(R[s]['plausibility'] >= 0.90 for s in seeds)
    J332b = all(R[s]['novel_atoms_invented'] == 0 for s in seeds)
    passed = J332a and J332b
    print("\n--- VERDICT ---", flush=True)
    print(f"J332a plausible sibling-majority hypotheses (>=.90): {J332a}", flush=True)
    print(f"J332b honest wall: ZERO novel atoms invented       : {J332b}", flush=True)
    verdict = ("PASS (bounded) - the substrate generates PLAUSIBLE defeasible hypotheses by sibling majority, but "
               "invents NO novel property -- creative generation is the documented wall") if passed else "NULL/partial"
    print(f"\nJEP-332: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP332"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J332a": J332a, "J332b": J332b, "passed": passed}, default=str))
    print("DONE", flush=True)
