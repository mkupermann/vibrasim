"""JEP-405 — GUI teaching robustness: past tense, copular adjectives, first-person. No transformer.
Pre-registered bars in docs/amendments/jep405_copular_robustness.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation


def trial(stmts, q, seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j405_{seed}_"), seed=seed)
    for s in stmts:
        c.read_text(s)
    return c.say(q).strip().lower()


def run_seed(seed):
    a1 = "yes" in trial(["Einstein was a physicist."], "is Einstein a physicist?", seed)
    a2 = "physicist" in trial(["Einstein was a physicist."], "what was Einstein?", seed)
    j405a = a1 and a2

    b1 = "yes" in trial(["The sun is hot."], "is the sun hot?", seed)
    b2 = "yes" in trial(["Dogs are loyal."], "are dogs loyal?", seed)
    b3 = "yes" in trial(["A dog is a mammal."], "is a dog a mammal?", seed)
    j405b = b1 and b2 and b3

    c1 = "michael" in trial(["My name is Michael."], "what is my name?", seed)
    c2 = "yes" in trial(["A poodle is a dog.", "A dog is a mammal."], "is a poodle a mammal?", seed)
    j405c_local = c1 and c2
    return {"j405a": bool(j405a), "a1": bool(a1), "a2": bool(a2), "j405b": bool(j405b),
            "b1": bool(b1), "b2": bool(b2), "b3": bool(b3), "c1": bool(c1), "c2": bool(c2),
            "j405c_local": bool(j405c_local)}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-405: copular robustness (past tense, adjectives, first-person) ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: J405a past-tense={r['j405a']} (isa={r['a1']},what-was={r['a2']}) | J405b adjective="
              f"{r['j405b']} (sun-hot={r['b1']},dogs-loyal={r['b2']},dog-mammal={r['b3']}) | J405c first-person="
              f"{r['c1']} multihop={r['c2']}", flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)

    J405a = all(R[s]['j405a'] for s in seeds)
    J405b = all(R[s]['j405b'] for s in seeds)
    J405c = all(R[s]['j405c_local'] for s in seeds) and gate_ok
    passed = J405a and J405b and J405c
    print("\n--- VERDICT ---", flush=True)
    print(f"J405a past-tense is-a       : {J405a}", flush=True)
    print(f"J405b copular adjective     : {J405b}", flush=True)
    print(f"J405c first-person + suite  : {J405c}", flush=True)
    verdict = ("PASS - natural GUI teaching forms now work: past tense ('Einstein was a physicist' -> is/what-was), "
               "copular adjectives ('The sun is hot', 'Dogs are loyal' -> yes) with is-a still distinguished by the "
               "article, and first-person ('My name is Michael' -> 'what is my name?' -> Michael); suite green.") \
        if passed else "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-405: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP405"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J405a": J405a, "J405b": J405b,
                                                  "J405c": J405c, "passed": passed}, default=str))
    print("DONE", flush=True)
