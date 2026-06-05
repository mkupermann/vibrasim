"""JEP-380 — conjunction-of-clauses + irregular plurals close the JEP-379 gap. No transformer.
Pre-registered bars in docs/amendments/jep380_conjunction_clauses.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation

PARA = ("Dogs are mammals. Mammals are animals that are warm-blooded. A poodle is a kind of dog. "
        "Dogs and cats are carnivores. A dog has four legs. Salmon are fish, and fish are animals. "
        "Birds such as sparrows can fly. The dog, which is a domesticated animal, can bark.")


def learn(text, seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j380_{seed}_"), seed=seed)
    c.read_text(text)
    return c


def has(c, a, r, b):
    return (a, r, b) in set(c.sm.facts)


def run_seed(seed):
    # J380a: conjunction-of-clauses extracts both edges (two examples)
    c1 = learn("Salmon are fish, and fish are animals.", seed)
    a1 = has(c1, "salmon", "isa", "fish") and has(c1, "fish", "isa", "animal")
    c2 = learn("Sharks are fish, and fish are vertebrates.", seed)
    a2 = has(c2, "shark", "isa", "fish") and has(c2, "fish", "isa", "vertebrate")
    j380a = bool(a1 and a2)

    # J380b: end-to-end gap closed in the real paragraph
    c = learn(PARA, seed)
    salmon_animal = "yes" in c.say("is a salmon an animal?").strip().lower()
    j380b = bool(salmon_animal)

    # J380c: conjunction-SUBJECT still works + JEP-379 invariants hold
    cs = learn("Dogs and cats are carnivores.", seed)
    subj_ok = has(cs, "dog", "isa", "carnivore") and has(cs, "cat", "isa", "carnivore")
    poodle_animal = "yes" in c.say("is a poodle an animal?").strip().lower()
    ood_abstain = ("yes" not in c.say("is a tiger an animal?").strip().lower())
    j380c_local = bool(subj_ok and poodle_animal and ood_abstain)
    return {"j380a": j380a, "a1": bool(a1), "a2": bool(a2), "j380b": j380b,
            "subj_ok": bool(subj_ok), "poodle_animal": bool(poodle_animal), "ood_abstain": bool(ood_abstain),
            "j380c_local": j380c_local, "facts": len(c.sm.facts)}


def regression(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-380: conjunction-of-clauses + irregular plurals ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: J380a conj-extract={r['j380a']} (salmon/fish={r['a1']}, sharks={r['a2']}) | "
              f"J380b salmon->animal={r['j380b']} | J380c subj={r['subj_ok']} poodle->animal={r['poodle_animal']} "
              f"ood-abstain={r['ood_abstain']}", flush=True)
    gate_ok, line = regression(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)

    J380a = all(R[s]['j380a'] for s in seeds)
    J380b = all(R[s]['j380b'] for s in seeds)
    J380c = all(R[s]['j380c_local'] for s in seeds) and gate_ok
    passed = J380a and J380b and J380c
    print("\n--- VERDICT ---", flush=True)
    print(f"J380a conjunction extracts both edges : {J380a}", flush=True)
    print(f"J380b salmon->animal end-to-end       : {J380b}", flush=True)
    print(f"J380c no regression (subj/poodle/ood/suite): {J380c}", flush=True)
    verdict = ("PASS - the conjunction-of-clauses splitter + general 'X are Y' rule (incl. irregular plurals) close the "
               "JEP-379 gap: 'Salmon are fish, and fish are animals' now yields both edges and 'is a salmon an "
               "animal?' answers yes end-to-end, with the conjunction-subject form and all JEP-379 invariants intact "
               "and the suite green. More real prose is now reliably captured.") if passed else \
              "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-380: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP380"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J380a": J380a, "J380b": J380b,
                                                  "J380c": J380c, "passed": passed}, default=str))
    print("DONE", flush=True)
