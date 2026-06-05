"""JEP-391 — strip leading discourse markers so corrections in prose parse. No transformer.
Pre-registered bars in docs/amendments/jep391_discourse_markers.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation


def conv(seed):
    return Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j391_{seed}_"), seed=seed)


def run_seed(seed):
    c1 = conv(seed); c1.read_text("Actually, a whale is not a fish.")
    c2 = conv(seed); c2.read_text("However, a dog is a mammal.")
    j391a = (("whale", "not_isa", "fish") in set(c1.sm.facts)
             and ("dog", "isa", "mammal") in set(c2.sm.facts))

    # correction overrides end-to-end
    c = conv(seed)
    c.read_text("A whale is a fish.")
    before = "yes" in c.say("is a whale a fish?").strip().lower()
    c.read_text("Actually, a whale is not a fish. A whale is a mammal.")
    after_fish = "yes" not in c.say("is a whale a fish?").strip().lower()
    after_mammal = "yes" in c.say("is a whale a mammal?").strip().lower()
    j391b = bool(before and after_fish and after_mammal)

    # regression
    cr = conv(seed); cr.read_text("A dog is a mammal.")
    j391c_local = ("dog", "isa", "mammal") in set(cr.sm.facts)
    return {"j391a": bool(j391a), "before_fish": bool(before), "after_fish": bool(after_fish),
            "after_mammal": bool(after_mammal), "j391b": j391b, "j391c_local": bool(j391c_local)}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-391: discourse markers + corrections ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: J391a marker-stripped={r['j391a']} | J391b correction (before-fish={r['before_fish']} "
              f"after-fish-no={r['after_fish']} after-mammal-yes={r['after_mammal']})={r['j391b']} | "
              f"J391c reg={r['j391c_local']}", flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)

    J391a = all(R[s]['j391a'] for s in seeds)
    J391b = all(R[s]['j391b'] for s in seeds)
    J391c = all(R[s]['j391c_local'] for s in seeds) and gate_ok
    passed = J391a and J391b and J391c
    print("\n--- VERDICT ---", flush=True)
    print(f"J391a marker stripped (not_isa) : {J391a}", flush=True)
    print(f"J391b correction overrides      : {J391b}", flush=True)
    print(f"J391c no regression             : {J391c}", flush=True)
    verdict = ("PASS - stripping leading discourse markers lets corrections in flowing prose parse: 'Actually, a whale "
               "is not a fish' now stores not_isa and overrides the earlier 'whale is a fish' (defeasible is_a), so "
               "after the correction 'is a whale a fish?' -> no and 'is a whale a mammal?' -> yes; suite green. The "
               "substrate now updates from corrections in real text (Michael's request).") if passed else \
              "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-391: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP391"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J391a": J391a, "J391b": J391b,
                                                  "J391c": J391c, "passed": passed}, default=str))
    print("DONE", flush=True)
