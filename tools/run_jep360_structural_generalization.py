"""JEP-360 — deep-structure boundary: passive vs active. No transformer.
Pre-registered bars in docs/amendments/jep360_structural_generalization.md.
"""
import json
from pathlib import Path
import numpy as np
from world.induce_construction import induce, apply_template

PASSIVE = [("The dog was domesticated by humans.", ("humans", "domesticated", "dog")),
           ("The horse was domesticated by people.", ("people", "domesticated", "horse"))]
ACTIVE = [("Humans domesticated the dog.", ("humans", "domesticated", "dog")),
          ("People domesticated the horse.", ("people", "domesticated", "horse"))]
HELD_PASSIVE = ("A cat was domesticated by farmers.", ("farmers", "domesticated", "cat"))
HELD_ACTIVE = ("Farmers domesticated the sheep.", ("farmers", "domesticated", "sheep"))


def fire(tpls, sent, gold):
    for t in tpls:
        f = apply_template(t, sent, flex_articles=True)
        if f == tuple(x.lower() for x in gold):
            return 1
    return 0


def run_seed(seed):
    tp = induce(PASSIVE); ta = induce(ACTIVE)
    # J360a: passive-only on an ACTIVE sentence (the wall)
    wall = fire([tp], HELD_ACTIVE[0], HELD_ACTIVE[1])
    # J360b: both templates -> both surface forms parse to the same relation
    both_passive = fire([tp, ta], HELD_PASSIVE[0], HELD_PASSIVE[1])
    both_active = fire([tp, ta], HELD_ACTIVE[0], HELD_ACTIVE[1])
    return {"passive_only_on_active": wall, "both_passive": both_passive, "both_active": both_active}


if __name__ == "__main__":
    print("=== JEP-360: deep-structure boundary (passive vs active) ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: passive-only fires on ACTIVE sentence={r['passive_only_on_active']} (the wall) | "
              f"both-templates: passive={r['both_passive']} active={r['both_active']}", flush=True)
    J360a = all(R[s]['passive_only_on_active'] == 0 for s in seeds)
    J360b = all(R[s]['both_passive'] == 1 and R[s]['both_active'] == 1 for s in seeds)
    passed = J360a and J360b
    print("\n--- VERDICT ---", flush=True)
    print(f"J360a deep-structure WALL (passive-only can't read active): {J360a}", flush=True)
    print(f"J360b route = learn each form (both templates -> both work): {J360b}", flush=True)
    verdict = ("PASS - honest deep-structure boundary: construction induction does NOT infer active from passive "
               "(no structural generalisation without an LLM); the substrate handles surface-form variety by "
               "LEARNING EACH FORM (composable, teacher-coupled). The ceiling, precisely mapped.") if passed \
        else "NULL/partial"
    print(f"\nJEP-360: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP360b"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J360a": J360a, "J360b": J360b, "passed": passed},
                                                 default=str))
    print("DONE", flush=True)
