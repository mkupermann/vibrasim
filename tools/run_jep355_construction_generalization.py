"""JEP-355 — construction induction attack C: structure vs slots (function-word abstraction). No transformer.
Pre-registered bars in docs/amendments/jep355_construction_generalization.md.
"""
import json
from pathlib import Path
import numpy as np
from world.induce_construction import induce, apply_template

# trained with 'The ...'; held-out uses 'A ...' (different article) -> tests generalisation, not memorisation
CASES = {
    "passive": {
        "examples": [("The dog was domesticated by humans.", ("humans", "domesticated", "dog")),
                     ("The horse was domesticated by people.", ("people", "domesticated", "horse"))],
        "heldout_varied": [("A cat was domesticated by farmers.", ("farmers", "domesticated", "cat")),
                           ("A sheep was domesticated by herders.", ("herders", "domesticated", "sheep"))],
        "other": "Paris is the capital of France.",
    },
    "lives_in": {
        "examples": [("The lion lives in Africa.", ("lion", "lives_in", "africa")),
                     ("The tiger lives in Asia.", ("tiger", "lives_in", "asia"))],
        "heldout_varied": [("A penguin lives in Antarctica.", ("penguin", "lives_in", "antarctica")),
                           ("A camel lives in Arabia.", ("camel", "lives_in", "arabia"))],
        "other": "The dog was domesticated by humans.",
    },
}


def recall(cases, flex):
    accs = []; false_fire = 0; ftot = 0
    for name, c in cases.items():
        tpl = induce(c["examples"])
        ok = sum(apply_template(tpl, s, flex_articles=flex) == tuple(x.lower() for x in g)
                 for (s, g) in c["heldout_varied"])
        accs.append(ok / len(c["heldout_varied"]))
        ftot += 1
        if apply_template(tpl, c["other"], flex_articles=flex) is not None:
            false_fire += 1
    return float(np.mean(accs)), false_fire / ftot


def run_seed(seed):
    naive_acc, naive_ff = recall(CASES, flex=False)
    flex_acc, flex_ff = recall(CASES, flex=True)
    return {"naive_acc": round(naive_acc, 3), "flex_acc": round(flex_acc, 3),
            "naive_false_fire": round(naive_ff, 3), "flex_false_fire": round(flex_ff, 3)}


if __name__ == "__main__":
    print("=== JEP-355: construction generalisation (structure vs slots) ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: naive exact-match on article-varied held-out={r['naive_acc']} | with function-word "
              f"abstraction={r['flex_acc']} | flex false-fire={r['flex_false_fire']}", flush=True)
    J355a = all(R[s]['naive_acc'] < 0.5 for s in seeds)
    J355b = all(R[s]['flex_acc'] >= 0.90 and R[s]['flex_false_fire'] == 0.0 for s in seeds)
    passed = J355a and J355b
    print("\n--- VERDICT ---", flush=True)
    print(f"J355a naive exact-match is BRITTLE (<.5 on varied): {J355a}", flush=True)
    print(f"J355b function-word abstraction GENERALISES (>=.90): {J355b}", flush=True)
    verdict = ("PASS - naive induction memorised literal words (brittle to article change); abstracting function "
               "words lets the LEARNED construction generalise to unseen variants -- a real step from slots toward "
               "structure") if passed else "NULL/partial"
    print(f"\nJEP-355: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP355"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J355a": J355a, "J355b": J355b, "passed": passed},
                                                 default=str))
    print("DONE", flush=True)
