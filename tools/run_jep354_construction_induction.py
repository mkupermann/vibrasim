"""JEP-354 — construction induction (breakthrough attack A): learn a sentence pattern from 2 examples, apply to
held-out. No transformer. Pre-registered bars in docs/amendments/jep354_construction_induction.md.
"""
import json
from pathlib import Path
import numpy as np
from world.induce_construction import induce, apply_template

CONSTRUCTIONS = {
    "passive_domesticated": {
        "examples": [("The dog was domesticated by humans.", ("humans", "domesticated", "dog")),
                     ("The horse was domesticated by people.", ("people", "domesticated", "horse"))],
        "heldout": [("The cat was domesticated by farmers.", ("farmers", "domesticated", "cat")),
                    ("The sheep was domesticated by herders.", ("herders", "domesticated", "sheep"))],
        "other": ("Paris is the capital of France.",),
    },
    "lives_in": {
        "examples": [("A lion lives in Africa.", ("lion", "lives_in", "africa")),
                     ("A tiger lives in Asia.", ("tiger", "lives_in", "asia"))],
        "heldout": [("A penguin lives in Antarctica.", ("penguin", "lives_in", "antarctica")),
                    ("A camel lives in Arabia.", ("camel", "lives_in", "arabia"))],
        "other": ("The dog was domesticated by humans.",),
    },
    "capital_of": {
        "examples": [("Paris is the capital of France.", ("paris", "capital_of", "france")),
                     ("Berlin is the capital of Germany.", ("berlin", "capital_of", "germany"))],
        "heldout": [("Rome is the capital of Italy.", ("rome", "capital_of", "italy")),
                    ("Madrid is the capital of Spain.", ("madrid", "capital_of", "spain"))],
        "other": ("A lion lives in Africa.",),
    },
}


def run_seed(seed):
    per = {}; false_fire = 0; false_tot = 0
    for name, c in CONSTRUCTIONS.items():
        tpl = induce(c["examples"])
        ok = 0
        for (sent, gold) in c["heldout"]:
            got = apply_template(tpl, sent)
            ok += (got == tuple(x.lower() for x in gold))
        per[name] = ok / len(c["heldout"])
        # J354b: this template must NOT fire on a different construction
        false_tot += 1
        if apply_template(tpl, c["other"][0]) is not None:
            false_fire += 1
    apply_acc = float(np.mean(list(per.values())))
    return {"per_construction": {k: round(v, 3) for k, v in per.items()}, "apply_acc": round(apply_acc, 3),
            "false_fire_rate": round(false_fire / false_tot, 3)}


if __name__ == "__main__":
    print("=== JEP-354: construction induction (learn a sentence pattern from 2 examples) ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        print(f"  seed {s}: per-construction={R[s]['per_construction']} | held-out apply acc={R[s]['apply_acc']} "
              f"| false-fire on other construction={R[s]['false_fire_rate']}", flush=True)
    J354a = all(all(v >= 0.90 for v in R[s]['per_construction'].values()) for s in seeds)
    J354b = all(R[s]['false_fire_rate'] == 0.0 for s in seeds)
    passed = J354a and J354b
    print("\n--- VERDICT ---", flush=True)
    print(f"J354a induce from 2 examples + apply to held-out (>=.90): {J354a}", flush=True)
    print(f"J354b no false-fire across different constructions       : {J354b}", flush=True)
    verdict = ("PASS - the system LEARNS a new sentence construction from 2 examples and applies it to unseen "
               "sentences of that pattern (few-shot template induction); honest boundary: needs matching fixed "
               "words, no cross-template generalisation yet (attack C)") if passed else "NULL/partial"
    print(f"\nJEP-354: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP354"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J354a": J354a, "J354b": J354b, "passed": passed},
                                                 default=str))
    print("DONE", flush=True)
