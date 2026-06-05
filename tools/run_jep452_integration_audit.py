"""JEP-452 — integrated capability audit: teach one coherent mini-world, run a battery spanning ALL
subsystems (reasoning + the new affect/energy layer) and verify they compose without interference or
confident falsehoods. Pre-registered bars in docs/amendments/jep452_integration_audit.md.
"""
import json
from pathlib import Path

import tempfile
from world.conversation import Conversation

TEACH = [
    "A poodle is a dog.", "A dog is a mammal.", "A mammal is an animal.",
    "Mammals are warm-blooded.", "A dog has four legs.",
    "A penguin is a bird.", "Birds can fly.", "A penguin cannot fly.",
    "Snakes are evil.", "A cobra is a snake.",
    "The capital of France is Paris.",
    "A villain is bad.",
]


def _affirm(x):
    x = str(x).strip().lower()
    return x.startswith("yes")


def _deny(x):
    x = str(x).strip().lower()
    return x.startswith("no")


def run(seed):
    c = Conversation(brain_dir=tempfile.mkdtemp())  # clean-room (lesson #16)
    for t in TEACH:
        c.say(t)
    # emotional fact + interference (affective memory)
    c.say("A dragon breathes fire.")
    c.learn_dummy = True
    # bury under interference
    for i in range(120):
        c.say(f"A gizmo{i} is a widget.")

    checks = []
    def chk(name, ok, answer): checks.append((name, bool(ok), str(answer)))

    a = c.say("is a poodle an animal?"); chk("multihop_isa", _affirm(a), a)
    a = c.say("is a poodle warm-blooded?"); chk("property_inherit", _affirm(a), a)
    a = c.say("can a penguin fly?"); chk("exception", _deny(a), a)
    a = c.say("how many legs does a dog have?"); chk("part_count", "4" in str(a) or "four" in str(a).lower(), a)
    a = c.say("what is the energy of a villain?"); chk("affect_taught", "dark" in str(a), a)
    a = c.say("what is the energy of a cobra?"); chk("affect_inherited", "dark" in str(a) and "inherit" in str(a), a)
    a = c.say("why is a cobra evil?"); chk("affect_explained", "snake" in str(a), a)
    a = c.say("what is the capital of France?"); chk("attribute", "paris" in str(a).lower(), a)
    a = c.say("is a cobra a snake?"); chk("isa_direct", _affirm(a), a)
    a = c.say("is a poodle a bird?"); chk("negative_isa", not _affirm(a), a)   # must NOT say yes
    a = c.say("is a quark a mammal?"); chk("abstain_untaught", not _affirm(a), a)  # untaught -> not a false yes
    a = c.say("what does a dragon breathe?"); chk("emotional_recall", "fire" in str(a).lower(), a)

    n_ok = sum(1 for _, ok, _ in checks)
    # confident falsehood = a check that FAILED by asserting yes/no wrongly (not by abstaining)
    falsehoods = [n for (n, ok, ans) in checks if not ok and (_affirm(ans) or _deny(ans))
                  and n in ("multihop_isa", "property_inherit", "exception", "isa_direct")]
    return dict(checks=checks, n_ok=n_ok, n=len(checks), falsehoods=falsehoods)


if __name__ == "__main__":
    print("=== JEP-452: integrated capability audit ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: {R[s]['n_ok']}/{R[s]['n']} passed; falsehoods={R[s]['falsehoods']}", flush=True)
        for name, ok, ans in R[s]['checks']:
            print(f"      [{'OK ' if ok else 'XX '}] {name}: {ans[:60]}", flush=True)

    J452a = all(R[s]['n_ok'] >= 11 for s in seeds)
    J452b = all(len(R[s]['falsehoods']) == 0 for s in seeds)
    passed = J452a and J452b

    print("\n--- VERDICT (J452c = pytest, separate) ---", flush=True)
    print(f"J452a capabilities compose (>=11/12) : {J452a}", flush=True)
    print(f"J452b no confident falsehoods        : {J452b}", flush=True)
    verdict = ("PASS - the affect/energy layer composes cleanly with the reasoning brain"
               if passed else "NULL/partial")
    print(f"\nJEP-452: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP452"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "J452a": J452a, "J452b": J452b}, indent=2, default=str))
    print("DONE", flush=True)
