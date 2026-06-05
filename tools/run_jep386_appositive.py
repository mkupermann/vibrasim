"""JEP-386 — appositive handling. No transformer.
Pre-registered bars in docs/amendments/jep386_appositive.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation


def facts_of(text, seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j386_{seed}_"), seed=seed)
    c.read_text(text)
    return set(c.sm.facts)


def run_seed(seed):
    f1 = facts_of("The lion, a large cat, is a predator.", seed)
    junk = any(" " in a for (a, r, b) in f1)
    j386a = (("lion", "isa", "cat") in f1 and ("lion", "isa", "predator") in f1 and not junk)

    f2 = facts_of("A robin, a small bird, eats worms.", seed)
    j386b = (("robin", "isa", "bird") in f2 and not any(" " in a for (a, r, b) in f2))

    # no false-fire: relative-clause + such-as still correct
    fr = facts_of("The lion, which is a large cat, is a predator.", seed)
    rel_ok = ("lion", "isa", "cat") in fr and ("lion", "isa", "predator") in fr
    fs = facts_of("Amphibians, such as frogs and toads, live in water.", seed)
    such_ok = ("frog", "isa", "amphibian") in fs and ("toad", "isa", "amphibian") in fs \
        and not any(" " in a for (a, r, b) in fs)
    return {"j386a": bool(j386a), "f1": sorted(f1), "j386b": bool(j386b), "f2": sorted(f2),
            "rel_ok": bool(rel_ok), "such_ok": bool(such_ok)}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-386: appositive handling ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: J386a lion={r['j386a']} ({r['f1']}) | J386b robin={r['j386b']} ({r['f2']}) | "
              f"J386c rel_ok={r['rel_ok']} such_ok={r['such_ok']}", flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)

    J386a = all(R[s]['j386a'] for s in seeds)
    J386b = all(R[s]['j386b'] for s in seeds)
    J386c = all(R[s]['rel_ok'] and R[s]['such_ok'] for s in seeds) and gate_ok
    passed = J386a and J386b and J386c
    print("\n--- VERDICT ---", flush=True)
    print(f"J386a appositive both facts, no junk : {J386a}", flush=True)
    print(f"J386b generalizes                    : {J386b}", flush=True)
    print(f"J386c no false-fire + suite          : {J386c}", flush=True)
    verdict = ("PASS - appositive 'X, a Y, <rest>' now yields both is-a facts (X->Y and X-><rest>) with no 'large cat' "
               "junk entity, generalizes, and does not disturb the relative-clause or such-as handlers; suite green. "
               "Another real-prose construction captured correctly.") if passed else \
              "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-386: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP386"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J386a": J386a, "J386b": J386b,
                                                  "J386c": J386c, "passed": passed}, default=str))
    print("DONE", flush=True)
