"""JEP-384 — strip leading quantifiers so subjects aren't polluted. No transformer.
Pre-registered bars in docs/amendments/jep384_quantifier_stripping.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation


def facts_of(text, seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j384_{seed}_"), seed=seed)
    c.read_text(text)
    return set(c.sm.facts)


def run_seed(seed):
    f1 = facts_of("Both frogs and toads are amphibians.", seed)
    j384a = (("frog", "isa", "amphibian") in f1 and ("toad", "isa", "amphibian") in f1
             and not any(a.startswith("both") for (a, r, b) in f1))

    f2 = facts_of("Most birds can fly.", seed)
    f3 = facts_of("Many fish are predators.", seed)
    junk2 = any(a.startswith("most") for (a, r, b) in f2)
    junk3 = any(a.startswith("many") for (a, r, b) in f3)
    j384b = (("bird", "hasprop", "fly") in f2 and not junk2
             and ("fish", "isa", "predator") in f3 and not junk3)

    f4 = facts_of("A dog is a mammal.", seed)
    f5 = facts_of("Dogs are carnivores.", seed)
    f6 = facts_of("A whale is not a fish.", seed)
    j384c_local = (("dog", "isa", "mammal") in f4 and ("dog", "isa", "carnivore") in f5
                   and ("whale", "not_isa", "fish") in f6)
    return {"j384a": bool(j384a), "f1": sorted(f1), "j384b": bool(j384b), "f2": sorted(f2), "f3": sorted(f3),
            "j384c_local": bool(j384c_local)}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-384: strip leading quantifiers ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: J384a both-conj={r['j384a']} ({r['f1']}) | J384b quant={r['j384b']} (most-birds={r['f2']}, "
              f"many-fish={r['f3']}) | J384c reg={r['j384c_local']}", flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)

    J384a = all(R[s]['j384a'] for s in seeds)
    J384b = all(R[s]['j384b'] for s in seeds)
    J384c = all(R[s]['j384c_local'] for s in seeds) and gate_ok
    passed = J384a and J384b and J384c
    print("\n--- VERDICT ---", flush=True)
    print(f"J384a Both X and Y (no junk)      : {J384a}", flush=True)
    print(f"J384b Most/Many quantifier (clean): {J384b}", flush=True)
    print(f"J384c no regression               : {J384c}", flush=True)
    verdict = ("PASS - stripping leading quantifiers removes junk-entity facts ('both frog', 'most bird') and yields "
               "clean-subject facts (frog/toad->amphibian, bird can fly, fish->predator) without harming a/an/the "
               "forms; suite green. A correctness fix that stops polluting the store with wrong facts.") if passed \
              else "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-384: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP384"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J384a": J384a, "J384b": J384b,
                                                  "J384c": J384c, "passed": passed}, default=str))
    print("DONE", flush=True)
