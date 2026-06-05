"""JEP-390 — generalize how_many to any counted part. No transformer.
Pre-registered bars in docs/amendments/jep390_how_many_generalize.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation
from tools.run_jep389_relational_article import run_seed as j389_run


def conv(text, seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j390_{seed}_"), seed=seed)
    c.read_text(text)
    return c


def run_seed(seed):
    cw = conv("A car has four wheels.", seed)
    wheels = "4" in cw.say("how many wheels does a car have?").strip().lower()
    cl = conv("A dog has four legs.", seed)
    legs = "4" in cl.say("how many legs does a dog have?").strip().lower()
    have_legs = "yes" in cl.say("does a dog have legs?").strip().lower()
    j390a = bool(wheels and legs)

    r389 = j389_run(seed)
    j390b = r389["qa_acc"] >= 0.90
    return {"wheels": bool(wheels), "legs": bool(legs), "have_legs": bool(have_legs), "j390a": j390a,
            "qa_acc": r389["qa_acc"], "qa_fail": r389["qa_fail"], "j390b": bool(j390b)}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-390: generalize how_many ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: J390a wheels={r['wheels']} legs={r['legs']} have-legs={r['have_legs']} | "
              f"J390b JEP-389 Q&A={r['qa_acc']} (fail {r['qa_fail']})", flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)

    J390a = all(R[s]['j390a'] and R[s]['have_legs'] for s in seeds)
    J390b = all(R[s]['j390b'] for s in seeds)
    J390c = gate_ok
    passed = J390a and J390b and J390c
    print("\n--- VERDICT ---", flush=True)
    print(f"J390a any part (wheels+legs)   : {J390a}", flush=True)
    print(f"J390b JEP-389 Q&A >=0.90       : {J390b}", flush=True)
    print(f"J390c suite green              : {J390c}", flush=True)
    verdict = ("PASS - how_many now answers any counted part ('how many wheels does a car have?' -> 4) while legs still "
               "work; JEP-389 Q&A rises to >=0.90 (the stored-but-unreachable wheels count is now queryable); suite "
               "green. Another stored-but-unreachable gap closed.") if passed else \
              "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-390: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP390"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J390a": J390a, "J390b": J390b,
                                                  "J390c": J390c, "passed": passed}, default=str))
    print("DONE", flush=True)
