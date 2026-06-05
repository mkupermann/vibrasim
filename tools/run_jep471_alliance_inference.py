"""JEP-471 — inferred alliances/enmities through signed chains (Heider transitivity). Pre-registered bars
in docs/amendments/jep471_alliance_inference.md.
"""
import json
from pathlib import Path
from world.conversation import Conversation


def run(seed):
    c = Conversation(seed=seed)
    for s in ["A villain is an enemy of a hero.", "A rebel is an enemy of a villain.",
              "A knight is a friend of a hero.", "A spy is a friend of a villain."]:
        c.say(s)
    return dict(
        rebel_ally=str(c.say("is a rebel an ally of a hero?")),
        spy_enemy=str(c.say("is a spy an enemy of a hero?")),
        knight_ally=str(c.say("is a knight an ally of a hero?")),
        table=str(c.say("is a table an ally of a hero?")),
    )


if __name__ == "__main__":
    print("=== JEP-471: inferred alliance/enmity (signed-path Heider transitivity) ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: rebel ally of hero={R[s]['rebel_ally']} | spy enemy of hero={R[s]['spy_enemy']} | "
              f"knight ally={R[s]['knight_ally']} | table ally={R[s]['table']}", flush=True)

    def yes(x): return x.lower().startswith("yes")
    def no(x): return x.lower().startswith("no")
    J471a = all(yes(R[s]['rebel_ally']) for s in seeds)
    J471b = all(yes(R[s]['spy_enemy']) and yes(R[s]['knight_ally']) for s in seeds)
    J471c = all(no(R[s]['table']) for s in seeds)
    passed = J471a and J471b and J471c

    print("\n--- VERDICT (suites = pytest separate) ---", flush=True)
    print(f"J471a enemy-of-enemy = ally (rebel)  : {J471a}", flush=True)
    print(f"J471b friend-of-enemy = enemy (spy)  : {J471b}", flush=True)
    print(f"J471c no spurious (table=no)         : {J471c}", flush=True)
    verdict = ("PASS - the brain infers alliances/enmities through signed chains (Heider transitivity)"
               if passed else "NULL/partial")
    print(f"\nJEP-471: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP471"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": R, "passed": passed,
                                                  "J471a": J471a, "J471b": J471b, "J471c": J471c}, indent=2, default=str))
    print("DONE", flush=True)
