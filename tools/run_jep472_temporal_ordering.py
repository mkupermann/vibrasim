"""JEP-472 — temporal/event ordering (before/after, forward/backward/transitive). Pre-registered bars in
docs/amendments/jep472_temporal_ordering.md.
"""
import json
from pathlib import Path
from world.conversation import Conversation


def run(seed):
    c = Conversation(seed=seed)
    for s in ["Breakfast happens before lunch.", "Lunch happens before dinner.",
              "The egg comes before the chicken."]:
        c.say(s)
    return dict(
        after_breakfast=str(c.say("what comes after breakfast?")),
        before_dinner=str(c.say("what comes before dinner?")),
        after_egg=str(c.say("what comes after the egg?")),
        bf_lt_dinner=str(c.say("is breakfast before dinner?")),
        dinner_lt_bf=str(c.say("is dinner before breakfast?")),
        bf_lt_egg=str(c.say("is breakfast before the egg?")),
    )


if __name__ == "__main__":
    print("=== JEP-472: temporal/event ordering ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: after_bf={R[s]['after_breakfast']} before_dinner={R[s]['before_dinner']} "
              f"after_egg={R[s]['after_egg']} | bf<dinner={R[s]['bf_lt_dinner']} dinner<bf={R[s]['dinner_lt_bf']} "
              f"bf<egg={R[s]['bf_lt_egg']}", flush=True)

    def has(x, w): return w in x.lower()
    J472a = all(has(R[s]['after_breakfast'], "lunch") and has(R[s]['before_dinner'], "lunch")
                and has(R[s]['after_egg'], "chicken") for s in seeds)
    J472b = all(R[s]['bf_lt_dinner'].lower().startswith("yes") and R[s]['dinner_lt_bf'].lower().startswith("no")
                for s in seeds)
    J472c = all(R[s]['bf_lt_egg'].lower().startswith("no") for s in seeds)
    passed = J472a and J472b and J472c

    print("\n--- VERDICT (suites = pytest separate) ---", flush=True)
    print(f"J472a forward/backward correct  : {J472a}", flush=True)
    print(f"J472b multi-hop transitive      : {J472b}", flush=True)
    print(f"J472c no spurious cross-chain   : {J472c}", flush=True)
    verdict = ("PASS - the brain reasons about event order forward, backward, and transitively"
               if passed else "NULL/partial")
    print(f"\nJEP-472: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP472"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": R, "passed": passed,
                                                  "J472a": J472a, "J472b": J472b, "J472c": J472c}, indent=2, default=str))
    print("DONE", flush=True)
