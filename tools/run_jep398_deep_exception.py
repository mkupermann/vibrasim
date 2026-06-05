"""JEP-398 — does a DEEP (mid-chain) exception still win after consolidation? No transformer.
Pre-registered bars in docs/amendments/jep398_deep_exception_after_consolidation.md.
"""
import json, tempfile
from pathlib import Path
from world.substrate_memory import SubstrateMemory
from world.brain_query import BrainQuery


def build(seed):
    m = SubstrateMemory(D=4096, directed=True)
    # taxonomy: baby_penguin -> penguin -> bird ; sparrow -> bird
    for a, b in [("babypenguin", "penguin"), ("penguin", "bird"), ("sparrow", "bird"), ("bird", "animal")]:
        m.add_fact(a, "isa", b)
    m.add_fact("bird", "hasprop", "fly")              # general property
    m.add_fact("penguin", "not_hasprop", "fly")       # exception on a MID ancestor (not the leaf babypenguin)
    return m.consolidate_closure(("isa",), auto_scale=True)   # consolidate (flattens ancestor order)


def run_seed(seed):
    m = build(seed)
    bq = BrainQuery(m, seed=seed)
    leaf = bq.has_property("penguin", "fly")          # leaf exception: should be False
    deep = bq.has_property("babypenguin", "fly")      # mid exception: should be False (penguin overrides bird)
    pos = bq.has_property("sparrow", "fly")           # inheritance: should be True
    return {"penguin_fly": leaf, "babypenguin_fly": deep, "sparrow_fly": pos}


if __name__ == "__main__":
    print("=== JEP-398: deep exception after consolidation ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: penguin_fly={r['penguin_fly']} (want False) | babypenguin_fly={r['babypenguin_fly']} "
              f"(want False) | sparrow_fly={r['sparrow_fly']} (want True)", flush=True)
    J398a = all(R[s]['penguin_fly'] is False for s in seeds)
    J398b = all(R[s]['babypenguin_fly'] is False for s in seeds)
    J398c = all(R[s]['sparrow_fly'] is True for s in seeds)
    passed = J398a and J398b and J398c
    print("\n--- VERDICT ---", flush=True)
    print(f"J398a leaf exception = False     : {J398a}", flush=True)
    print(f"J398b DEEP/mid exception = False : {J398b}", flush=True)
    print(f"J398c positive inheritance = True: {J398c}", flush=True)
    if passed:
        verdict = ("PASS - deep/mid exceptions still resolve correctly after consolidation: a baby_penguin cannot fly "
                   "(penguin's exception overrides bird's property) despite the flattened ancestor order. Most-specific-"
                   "wins is robust to consolidation.")
    elif not J398b:
        verdict = ("NULL - consolidation BREAKS deep-exception resolution: has_property scans the flattened ancestors "
                   "in scrambled order and returns the general property before the mid-level exception. Fix: order "
                   "ancestors by specificity (depth) in has_property. Important honest finding.")
    else:
        verdict = "NULL/partial - see rows."
    print(f"\nJEP-398: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP398"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J398a": J398a, "J398b": J398b, "J398c": J398c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
