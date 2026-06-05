"""JEP-468 — affective ambivalence detection (Heider imbalance): a concept reachable as both positive
and negative through signed relations is CONFLICTED. Pre-registered bars in
docs/amendments/jep468_affective_tension.md.
"""
import json
from pathlib import Path
from world.conversation import Conversation


def run(seed):
    c = Conversation(seed=seed)
    for s in ["Heroes are good.", "Villains are evil.",
              "A spy is a friend of a hero.", "A spy is a friend of a villain.",
              "A sidekick is a friend of a hero.", "A villain is an enemy of a hero."]:
        c.say(s)
    return dict(
        spy=str(c.say("is a spy conflicted?")),
        sidekick=str(c.say("is a sidekick conflicted?")),
        villain_amb=str(c.say("is a villain conflicted?")),
        villain_energy=str(c.say("what is the energy of a villain?")),
        sidekick_energy=str(c.say("what is the energy of a sidekick?")),
    )


if __name__ == "__main__":
    print("=== JEP-468: affective ambivalence (Heider imbalance) ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: spy conflicted={R[s]['spy']} | sidekick conflicted={R[s]['sidekick']} | "
              f"villain conflicted={R[s]['villain_amb']} | villain={R[s]['villain_energy']} | sidekick={R[s]['sidekick_energy']}",
              flush=True)

    def yes(x): return x.lower().startswith("yes")
    def no(x): return x.lower().startswith("no")
    J468a = all(yes(R[s]['spy']) for s in seeds)
    J468b = all(no(R[s]['sidekick']) and no(R[s]['villain_amb']) for s in seeds)
    J468c = all("dark" in R[s]['villain_energy'] and "bright" in R[s]['sidekick_energy'] for s in seeds)
    passed = J468a and J468b and J468c

    print("\n--- VERDICT (suites = pytest separate) ---", flush=True)
    print(f"J468a ambivalence detected (spy=yes)     : {J468a}", flush=True)
    print(f"J468b no false ambivalence (one-sided=no): {J468b}", flush=True)
    print(f"J468c propagation intact                 : {J468c}", flush=True)
    verdict = ("PASS - the brain detects conflicting energy (Heider imbalance) without over-firing"
               if passed else "NULL/partial")
    print(f"\nJEP-468: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP468"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": R, "passed": passed,
                                                  "J468a": J468a, "J468b": J468b, "J468c": J468c}, indent=2, default=str))
    print("DONE", flush=True)
