"""JEP-451 — affect inheritance with the gated statistical fallback (JEP-450 fixed). Lexicon affect
word sets valence; cobra/python inherit dark via the is-a ancestor + explanation; an unrelated desk
is neutral (the gated fallback abstains on sparse valence data). Pre-registered bars in
docs/amendments/jep451_affect_inheritance_gated.md.
"""
import json
from pathlib import Path

import tempfile
from world.conversation import Conversation


def run(seed):
    c = Conversation(brain_dir=tempfile.mkdtemp())  # clean-room (lesson #16)
    for s in ["Snakes are evil.", "A snake is a reptile.", "A cobra is a snake.",
              "A python is a snake.", "A desk is a table.", "A table is furniture."]:
        c.say(s)
    return dict(
        cobra=c.say("what is the energy of a cobra?"),
        python=c.say("what is the energy of a python?"),
        why=c.say("why is a cobra evil?"),
        desk=c.say("what is the energy of a desk?"),
    )


if __name__ == "__main__":
    print("=== JEP-451: affect inheritance (gated fallback) ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = {k: str(v) for k, v in run(s).items()}
        print(f"  seed {s}: cobra={R[s]['cobra']} | python={R[s]['python']}", flush=True)
        print(f"           why={R[s]['why']} | desk={R[s]['desk']}", flush=True)

    J451a = all("dark" in R[s]['cobra'] and "dark" in R[s]['python'] for s in seeds)
    J451b = all("snake" in R[s]['why'] for s in seeds)
    J451c = all("dark" not in R[s]['desk'] for s in seeds)
    passed = J451a and J451b and J451c

    print("\n--- VERDICT ---", flush=True)
    print(f"J451a affect inherits (cobra,python dark) : {J451a}", flush=True)
    print(f"J451b explained (cites snake)             : {J451b}", flush=True)
    print(f"J451c no hallucination (desk neutral)     : {J451c}", flush=True)
    verdict = ("PASS - affect inherits through is-a with an explanation; the gated fallback abstains on "
               "sparse data so unrelated concepts stay neutral") if passed else "NULL/partial"
    print(f"\nJEP-451: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP451"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": R, "passed": passed,
                                                  "J451a": J451a, "J451b": J451b, "J451c": J451c}, indent=2, default=str))
    print("DONE", flush=True)
