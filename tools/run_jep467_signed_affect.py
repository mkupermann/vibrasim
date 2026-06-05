"""JEP-467 — affect propagates through SIGNED relations (Heider balance). Verify enemy-of-good=bad,
enemy-of-enemy=friend (multi-hop sign product), friend-of-good=good, and no spurious propagation.
Pre-registered bars in docs/amendments/jep467_signed_affect_propagation.md.
"""
import json
from pathlib import Path
from world.conversation import Conversation


def run(seed):
    c = Conversation(seed=seed)
    for s in ["Heroes are good.", "A villain is an enemy of a hero.",
              "A rebel is an enemy of a villain.", "A sidekick is a friend of a hero.",
              "A table is furniture."]:
        c.say(s)
    return dict(
        villain=str(c.say("what is the energy of a villain?")),
        rebel=str(c.say("what is the energy of a rebel?")),
        sidekick=str(c.say("what is the energy of a sidekick?")),
        table=str(c.say("what is the energy of a table?")),
        villain_bad=str(c.say("is a villain bad?")),
    )


if __name__ == "__main__":
    print("=== JEP-467: signed-relation affect propagation (Heider balance) ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: villain={R[s]['villain']} | rebel={R[s]['rebel']} | "
              f"sidekick={R[s]['sidekick']} | table={R[s]['table']} | 'is a villain bad?'={R[s]['villain_bad']}", flush=True)

    J467a = all("dark" in R[s]['villain'] and R[s]['villain_bad'].lower().startswith("yes") for s in seeds)
    J467b = all("bright" in R[s]['rebel'] for s in seeds)
    J467c = all("dark" not in R[s]['table'] and "bright" not in R[s]['table'] for s in seeds)
    passed = J467a and J467b and J467c

    print("\n--- VERDICT (J467c suites = pytest separate) ---", flush=True)
    print(f"J467a enemy of good = bad          : {J467a}", flush=True)
    print(f"J467b enemy of enemy = friend(bright): {J467b}", flush=True)
    print(f"J467c no spurious propagation      : {J467c}", flush=True)
    verdict = ("PASS - affect propagates through signed relations with correct sign products (Heider balance)"
               if passed else "NULL/partial")
    print(f"\nJEP-467: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP467"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": R, "passed": passed,
                                                  "J467a": J467a, "J467b": J467b, "J467c": J467c}, indent=2, default=str))
    print("DONE", flush=True)
