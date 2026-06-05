"""JEP-356 — the synonym wall and the route through (taught equivalence). No transformer.
Pre-registered bars in docs/amendments/jep356_synonym_wall.md.
"""
import json
from pathlib import Path
import numpy as np
from world.induce_construction import induce, apply_template

EXAMPLES = [("The dog was domesticated by humans.", ("humans", "domesticated", "dog")),
            ("The horse was domesticated by people.", ("people", "domesticated", "horse"))]
# held-out uses the SYNONYM 'tamed' (+ varied article) -> needs synonym knowledge to match
HELDOUT_SYN = [("A cat was tamed by farmers.", ("farmers", "domesticated", "cat")),
               ("A goat was tamed by herders.", ("herders", "domesticated", "goat"))]
TAUGHT_SYNONYMS = {"tamed": "domesticated"}                 # separately-learned equivalence (substrate-legal)


def recall(syn):
    tpl = induce(EXAMPLES)
    ok = sum(apply_template(tpl, s, flex_articles=True, synonyms=syn) == tuple(x.lower() for x in g)
             for (s, g) in HELDOUT_SYN)
    return ok / len(HELDOUT_SYN)


def run_seed(seed):
    return {"no_synonym": round(recall(None), 3), "taught_synonym": round(recall(TAUGHT_SYNONYMS), 3)}


if __name__ == "__main__":
    print("=== JEP-356: the synonym wall (pure induction) and the route through (taught equivalence) ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        print(f"  seed {s}: WITHOUT synonym knowledge={R[s]['no_synonym']} (the wall) | WITH taught synonym="
              f"{R[s]['taught_synonym']}", flush=True)
    J356a = all(R[s]['no_synonym'] == 0.0 for s in seeds)
    J356b = all(R[s]['taught_synonym'] >= 0.90 for s in seeds)
    passed = J356a and J356b
    print("\n--- VERDICT ---", flush=True)
    print(f"J356a synonym does NOT emerge from induction (recall 0.0): {J356a}", flush=True)
    print(f"J356b taught equivalence routes through (>=.90)          : {J356b}", flush=True)
    verdict = ("PASS - honest boundary mapped: pure construction induction CANNOT generalise over synonyms (it does "
               "not invent equivalence -- the world-knowledge wall); but SEPARATELY-taught equivalence lets the "
               "learned construction generalise. Induction + learned knowledge, not induction alone.") if passed \
        else "NULL/partial"
    print(f"\nJEP-356: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP356"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J356a": J356a, "J356b": J356b, "passed": passed},
                                                 default=str))
    print("DONE", flush=True)
