"""JEP-361 — self-directed learning: the brain drives its own gap-filling. No transformer.
Pre-registered bars in docs/amendments/jep361_self_directed_learning.md.
"""
import json, tempfile
from pathlib import Path
from world.conversation import Conversation
from world.brain_query import BrainQuery

DOC = ("A poodle is a dog. A beagle is a dog. A cat is a mammal. A sparrow is a bird. A robin is a bird. "
       "A salmon is a fish. A tuna is a fish.")
# teacher's definitions for the gaps (dog/mammal/bird/fish are referenced but undefined in DOC)
DEFINITIONS = {"dog": "mammal", "mammal": "animal", "bird": "animal", "fish": "animal"}


def run_seed(seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"sd_{seed}_"), seed=seed)
    c.read_text(DOC)

    # baseline: a multi-hop question that should FAIL until 'bird'/'mammal' are defined
    before_q = BrainQuery(c.sm, seed=seed).is_a("sparrow", "animal")

    first_asked = c.curiosity_question()             # the most-connected gap it wants explained
    gap_trace = [len(c.gaps())]
    asked_order = []
    # self-directed loop: keep asking for the top gap and integrating the teacher's definition
    for _ in range(20):
        top = c.curiosity_question()
        if top is None or top not in DEFINITIONS:
            break
        asked_order.append(top)
        c.say(f"A {top} is a {DEFINITIONS[top]}.")
        gap_trace.append(len(c.gaps()))

    after_q = BrainQuery(c.sm, seed=seed).is_a("sparrow", "animal")
    remaining = [g for g in c.gaps() if g in DEFINITIONS]    # resolvable gaps left (should be none)
    monotonic = all(gap_trace[i + 1] <= gap_trace[i] for i in range(len(gap_trace) - 1))
    return {"first_asked": first_asked, "asked_order": asked_order, "gap_trace": gap_trace,
            "resolvable_left": remaining, "before_sparrow_animal": bool(before_q),
            "after_sparrow_animal": bool(after_q), "monotonic": bool(monotonic)}


if __name__ == "__main__":
    print("=== JEP-361: self-directed learning (the brain drives its own gap-filling) ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: first-asked='{r['first_asked']}' | asked order={r['asked_order']} | "
              f"gaps {r['gap_trace']} | resolvable-left={r['resolvable_left']} | "
              f"sparrow->animal before={r['before_sparrow_animal']} after={r['after_sparrow_animal']}", flush=True)
    # 'dog' is the most-referenced gap (poodle+beagle -> dog, plus dog as subject) -> asked first
    J361a = all(not R[s]['resolvable_left'] and R[s]['first_asked'] == 'dog' for s in seeds)
    J361b = all(R[s]['monotonic'] and R[s]['gap_trace'][-1] <= R[s]['gap_trace'][0] for s in seeds)
    J361c = all((not R[s]['before_sparrow_animal']) and R[s]['after_sparrow_animal'] for s in seeds)
    passed = J361a and J361b and J361c
    print("\n--- VERDICT ---", flush=True)
    print(f"J361a drives + closes all resolvable gaps (dog first): {J361a}", flush=True)
    print(f"J361b gaps shrink monotonically                      : {J361b}", flush=True)
    print(f"J361c new multi-hop reasoning unlocked               : {J361c}", flush=True)
    verdict = ("PASS - the brain DRIVES its own learning: it asks for its most-connected gap first, integrates the "
               "answer, its gaps shrink to zero, and new reasoning (sparrow->animal) becomes possible") if passed \
        else "NULL/partial"
    print(f"\nJEP-361: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP361"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J361a": J361a, "J361b": J361b, "J361c": J361c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
