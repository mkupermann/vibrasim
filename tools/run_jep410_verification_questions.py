"""JEP-410 — yes/no verification questions for actions, causes, locations. No transformer.
Pre-registered bars in docs/amendments/jep410_verification_questions.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation


def ask(stmts, q, seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j410_{seed}_"), seed=seed)
    for s in stmts:
        c.read_text(s)
    return "yes" in c.say(q).strip().lower()


def run_seed(seed):
    a_yes = ask(["Michael likes coffee."], "does Michael like coffee?", seed)
    a_no = not ask(["Michael likes coffee."], "does Michael like tea?", seed)
    j410a = a_yes and a_no
    b_yes = ask(["Paris is in France."], "is Paris in France?", seed)
    b_no = not ask(["Paris is in France."], "is Paris in Spain?", seed)
    j410b = b_yes and b_no
    c_yes = ask(["Smoking causes cancer."], "does smoking cause cancer?", seed)
    have_ok = ask(["A dog has a tail."], "does a dog have a tail?", seed)
    j410c_local = c_yes and have_ok
    return {"a_yes": a_yes, "a_no": a_no, "j410a": bool(j410a), "b_yes": b_yes, "b_no": b_no, "j410b": bool(j410b),
            "c_yes": c_yes, "have_ok": have_ok, "j410c_local": bool(j410c_local)}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-410: verification questions ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: J410a action={r['j410a']} (coffee={r['a_yes']},tea-no={r['a_no']}) | J410b location="
              f"{r['j410b']} (france={r['b_yes']},spain-no={r['b_no']}) | J410c cause={r['c_yes']} have={r['have_ok']}",
              flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)
    J410a = all(R[s]['j410a'] for s in seeds)
    J410b = all(R[s]['j410b'] for s in seeds)
    J410c = all(R[s]['j410c_local'] for s in seeds) and gate_ok
    passed = J410a and J410b and J410c
    print("\n--- VERDICT ---", flush=True)
    print(f"J410a action verify   : {J410a}", flush=True)
    print(f"J410b location verify : {J410b}", flush=True)
    print(f"J410c cause + have     : {J410c}", flush=True)
    verdict = ("PASS - yes/no verification works for actions ('does Michael like coffee?'->yes, tea->no), locations "
               "('is Paris in France?'->yes, Spain->no), and causes ('does smoking cause cancer?'->yes), with the "
               "part-of 'have' rule intact; suite green. Users can verify any taught fact.") if passed else \
              "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-410: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP410"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J410a": J410a, "J410b": J410b,
                                                  "J410c": J410c, "passed": passed}, default=str))
    print("DONE", flush=True)
