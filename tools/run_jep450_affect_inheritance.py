"""JEP-450 — affect inherits through the taxonomy, with explanation. Teach affect on a parent class +
a taxonomy; a child inherits the affect and the brain explains why. A control branch with no valenced
ancestor must NOT inherit. Pre-registered bars in docs/amendments/jep450_affect_inheritance.md.
"""
import json
from pathlib import Path

from world.conversation import Conversation


def run(seed):
    c = Conversation()
    # affect on a PARENT class + taxonomy (scary branch)
    for s in ["Snakes are scary.", "A snake is a reptile.", "A cobra is a snake.",
              "A python is a snake.",
              # neutral control branch (no ancestor carries affect)
              "A table is furniture.", "A desk is a table."]:
        c.say(s)
    cobra_scary = c.say("is a cobra scary?")
    why = c.say("why is a cobra scary?")
    python_dark = c.say("what is the energy of a python?")
    desk_energy = c.say("what is the energy of a desk?")
    return dict(cobra_scary=str(cobra_scary), why=str(why),
                python_dark=str(python_dark), desk_energy=str(desk_energy))


if __name__ == "__main__":
    print("=== JEP-450: affect inherits through the taxonomy (explainable) ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: 'is a cobra scary?' -> {R[s]['cobra_scary']}", flush=True)
        print(f"           'why is a cobra scary?' -> {R[s]['why']}", flush=True)
        print(f"           energy(python) -> {R[s]['python_dark']} | energy(desk) -> {R[s]['desk_energy']}", flush=True)

    def _truthy(x): return x.lower() in ("true", "yes") or x.startswith("dark")
    J450a = all(_truthy(R[s]['cobra_scary']) or "dark" in R[s]['python_dark'] for s in seeds)
    J450b = all("reptile" in R[s]['why'] or "snake" in R[s]['why'] for s in seeds)
    J450c = all("dark" not in R[s]['desk_energy'] for s in seeds)   # desk has no valenced ancestor
    passed = J450a and J450b and J450c

    print("\n--- VERDICT ---", flush=True)
    print(f"J450a affect inherits to child            : {J450a}", flush=True)
    print(f"J450b inheritance is explained (cites anc): {J450b}", flush=True)
    print(f"J450c no spurious affect (desk neutral)   : {J450c}", flush=True)
    verdict = ("PASS - affect flows through is-a with an explanation; absent where no ancestor carries it"
               if passed else "NULL/partial")
    print(f"\nJEP-450: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP450"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "J450a": J450a, "J450b": J450b, "J450c": J450c}, indent=2, default=str))
    print("DONE", flush=True)
