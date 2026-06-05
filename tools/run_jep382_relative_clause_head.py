"""JEP-382 — fix the relative-clause head bug in plural is-a. No transformer.
Pre-registered bars in docs/amendments/jep382_relative_clause_head.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation
from tools.run_jep381_real_article_scale import run_seed as j381_run_seed


def learn(text, seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j382_{seed}_"), seed=seed)
    c.read_text(text)
    return c


def has(c, a, r, b):
    return (a, r, b) in set(c.sm.facts)


def run_seed(seed):
    # J382a: head fixed
    c = learn("Mammals are animals that are warm-blooded.", seed)
    head_ok = has(c, "mammal", "isa", "animal") and not has(c, "mammal", "isa", "warm-blooded")
    # J382c: simple plural is-a + conjunction still work
    c2 = learn("Dogs are mammals. Cats and dogs are carnivores.", seed)
    reg_ok = has(c2, "dog", "isa", "mammal") and has(c2, "cat", "isa", "carnivore") and has(c2, "dog", "isa", "carnivore")
    # J382b: full JEP-381 re-run
    r381 = j381_run_seed(seed)
    return {"head_ok": bool(head_ok), "reg_ok": bool(reg_ok),
            "coverage": r381["coverage"], "qa_acc": r381["qa_acc"], "multihop": r381["multihop"],
            "ood_abstain": r381["ood_abstain"], "qa_fail": r381["qa_fail"]}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-382: relative-clause head fix ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: head_ok={r['head_ok']} reg_ok={r['reg_ok']} | JEP-381 re-run: coverage={r['coverage']} "
              f"Q&A={r['qa_acc']} multihop={r['multihop']} OOD={r['ood_abstain']} (fail: {r['qa_fail']})", flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)

    J382a = all(R[s]['head_ok'] for s in seeds)
    J382b = all(R[s]['qa_acc'] >= 0.90 and R[s]['multihop'] and R[s]['coverage'] >= 0.90 and R[s]['ood_abstain'] >= 1.0
                for s in seeds)
    J382c = all(R[s]['reg_ok'] for s in seeds) and gate_ok
    passed = J382a and J382b and J382c
    print("\n--- VERDICT ---", flush=True)
    print(f"J382a relative-clause head fixed       : {J382a}", flush=True)
    print(f"J382b JEP-381 Q&A restored >=0.90      : {J382b}", flush=True)
    print(f"J382c no regression (simple/conj/suite): {J382c}", flush=True)
    verdict = ("PASS - stripping the trailing relative clause before taking the head fixes 'X are Y that ...' "
               "(mammal->animal, not mammal->warm-blooded), restoring dog/poodle->animal multi-hop: JEP-381 Q&A rises "
               "to >=0.90 with coverage and abstention intact, simple/conjunction handlers unaffected, suite green. "
               "Real-prose capture is now reliable end-to-end at article scale.") if passed else \
              "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-382: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP382"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J382a": J382a, "J382b": J382b,
                                                  "J382c": J382c, "passed": passed}, default=str))
    print("DONE", flush=True)
