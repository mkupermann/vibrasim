"""JEP-394 — 'is X <property>?' checks has_property. No transformer.
Pre-registered bars in docs/amendments/jep394_is_x_property.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation
from tools.run_jep393_integration_capstone import run_seed as j393_run


def run_seed(seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j394_{seed}_"), seed=seed)
    c.read_text("A dog is a mammal. Mammals are animals that are warm-blooded. A poodle is a kind of dog. "
                "A whale is not a fish.")
    prop = "yes" in c.say("is a dog warm-blooded?").strip().lower()
    isa = "yes" in c.say("is a poodle a dog?").strip().lower()
    neg = "yes" not in c.say("is a whale a fish?").strip().lower()
    nofp = "yes" not in c.say("is a dog purple?").strip().lower()
    j394a = bool(prop and isa and neg and nofp)

    r393 = j393_run(seed)
    j394b = r393["qa_acc"] >= 1.0
    return {"prop": bool(prop), "isa": bool(isa), "neg": bool(neg), "nofp": bool(nofp), "j394a": j394a,
            "j393_qa": r393["qa_acc"], "j393_fail": r393["qa_fail"], "j394b": bool(j394b)}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-394: 'is X property' -> has_property ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: J394a prop={r['prop']} isa={r['isa']} neg={r['neg']} no-fp={r['nofp']} | "
              f"J394b JEP-393 Q&A={r['j393_qa']} (fail {r['j393_fail']})", flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)

    J394a = all(R[s]['j394a'] for s in seeds)
    J394b = all(R[s]['j394b'] for s in seeds)
    J394c = gate_ok
    passed = J394a and J394b and J394c
    print("\n--- VERDICT ---", flush=True)
    print(f"J394a property+is-a+neg+no-fp : {J394a}", flush=True)
    print(f"J394b JEP-393 Q&A = 1.0       : {J394b}", flush=True)
    print(f"J394c suite green             : {J394c}", flush=True)
    verdict = ("PASS - 'is X Y?' now answers yes if X is-a Y OR X has property Y, so 'is a dog warm-blooded?' -> yes "
               "while is-a and negatives are unaffected (no false-positive on 'is a dog purple?'); JEP-393 Q&A rises to "
               "1.0; suite green.") if passed else "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-394: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP394"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J394a": J394a, "J394b": J394b,
                                                  "J394c": J394c, "passed": passed}, default=str))
    print("DONE", flush=True)
