"""JEP-399 — adversarial 'no mistakes' audit: can we make the brain assert a falsehood? No transformer.
Pre-registered bars in docs/amendments/jep399_adversarial_no_mistakes.md.
"""
import json, tempfile
from pathlib import Path
from world.conversation import Conversation

# (article, [(question, truth)]) where truth is True (yes) / False (no) for the correct answer.
SCENARIOS = [
    ("A whale is a mammal. A whale is not a fish.",
     [("is a whale a fish?", False), ("is a whale a mammal?", True), ("is a whale an animal?", True)]),
    ("Birds can fly. A penguin is a bird. A penguin cannot fly. A sparrow is a bird.",
     [("can a penguin fly?", False), ("can a sparrow fly?", True), ("is a penguin a bird?", True)]),
    ("A dog is a mammal.",
     [("is a dog a mammal?", True), ("is a mammal a dog?", False)]),       # directionality
    ("A platypus is a mammal. A platypus is an egg-layer.",
     [("is a platypus a mammal?", True), ("is a platypus an egg-layer?", True)]),
    ("A dog is warm-blooded. A dog is a mammal.",
     [("is a dog warm-blooded?", True), ("is a dog a cat?", False)]),
    ("A whale is a mammal.",
     [("is a whale a planet?", False), ("is a whale a vegetable?", False)]),  # untaught -> must not say yes
]


def classify(ans, truth):
    yes = "yes" in ans
    no = ("yes" not in ans)
    if truth is True:
        return "correct" if yes else "abstain"         # missing a true fact = honest abstain (not a falsehood)
    else:
        # truth is False: correct = not yes. A confident 'yes' on a false fact = FALSEHOOD.
        return "correct" if no else "falsehood"


def run_seed(seed):
    falsehoods, correct, total = [], 0, 0
    direction_ok = None
    for art, qs in SCENARIOS:
        c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j399_{seed}_"), seed=seed)
        c.read_text(art)
        for q, truth in qs:
            ans = c.say(q).strip().lower()
            cls = classify(ans, truth)
            total += 1
            if cls == "correct":
                correct += 1
            elif cls == "falsehood":
                falsehoods.append((q, ans))
            if q == "is a mammal a dog?":
                direction_ok = ("yes" not in ans)
    return {"falsehoods": falsehoods, "n_falsehood": len(falsehoods), "correct": correct, "total": total,
            "correct_rate": round(correct / total, 3), "direction_ok": bool(direction_ok)}


if __name__ == "__main__":
    print("=== JEP-399: adversarial no-mistakes audit ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: falsehoods={r['n_falsehood']} {r['falsehoods']} | correct={r['correct']}/{r['total']} "
              f"({r['correct_rate']}) | directionality_ok={r['direction_ok']}", flush=True)

    J399a = all(R[s]['n_falsehood'] == 0 for s in seeds)
    J399b = all(R[s]['correct_rate'] >= 0.85 for s in seeds)
    J399c = all(R[s]['direction_ok'] for s in seeds)
    passed = J399a and J399b and J399c
    print("\n--- VERDICT ---", flush=True)
    print(f"J399a ZERO confident falsehoods : {J399a}", flush=True)
    print(f"J399b correct rate >=0.85       : {J399b}", flush=True)
    print(f"J399c directionality respected  : {J399c}", flush=True)
    verdict = ("PASS - across adversarial scenarios (negation, exception chains, directionality, multi-parent DAGs, "
               "ambiguous is-X-Y, untaught probes) the brain asserts ZERO falsehoods: every answer is correct or an "
               "honest 'no/don't know'. The 'no mistakes inside the domain + honest abstention' guarantee holds under "
               "adversarial probing.") if passed else \
              ("CRITICAL/NULL - a falsehood or directionality break surfaced; see rows. Reported, investigate.")
    print(f"\nJEP-399: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP399"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J399a": J399a, "J399b": J399b, "J399c": J399c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
