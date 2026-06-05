"""JEP-402 — correctness guards: miss rather than capture wrong. No transformer.
Pre-registered bars in docs/amendments/jep402_wrong_capture_guards.md.
"""
import json, re, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation
from tools.run_jep401_hard_prose_ceiling import HARD


def facts_of(text, seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j402_{seed}_"), seed=seed)
    c.read_text(text)
    return set(c.sm.facts)


def run_seed(seed):
    f1 = facts_of("The heart, a muscular organ roughly the size of a fist, pumps blood throughout the body.", seed)
    j402a = not any(b == "fist" for (a, r, b) in f1)            # no X->fist falsehood

    f2 = facts_of("Because they are warm-blooded and breathe air, whales must surface.", seed)
    j402b = not any(("because" in a or a == "they" or "they" in a.split()) for (a, r, b) in f2)

    # clean appositive still works
    fc = facts_of("The lion, a large cat, is a predator.", seed)
    clean_appos = ("lion", "isa", "cat") in fc and ("lion", "isa", "predator") in fc

    # re-run JEP-401: junk must be 0, coverage still reasonable
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j402h_{seed}_"), seed=seed)
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", HARD.replace("\n", " ")) if s.strip()]
    covered = 0
    for s in sents:
        b = len(c.sm.facts); c._learn_one(s)
        if len(c.sm.facts) > b:
            covered += 1
    coverage = round(covered / len(sents), 3)
    ents = {e for (a, r, b) in c.sm.facts for e in (a, b)}
    junk = [e for e in ents if " " in e]
    junk_rate = round(len(junk) / max(1, len(ents)), 3)
    bad = [f for f in c.sm.facts if f[2] == "fist" or "because" in f[0] or " " in f[0] or " " in f[2]]

    return {"j402a": bool(j402a), "f1": sorted(f1), "j402b": bool(j402b), "f2": sorted(f2),
            "clean_appos": bool(clean_appos), "coverage": coverage, "junk_rate": junk_rate, "junk": junk,
            "bad_facts": [list(f) for f in bad]}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-402: correctness guards (miss > wrong) ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: J402a no-heart-fist={r['j402a']} ({r['f1']}) | J402b no-because={r['j402b']} ({r['f2']}) | "
              f"clean-appos={r['clean_appos']} | dense coverage={r['coverage']} junk={r['junk_rate']} "
              f"bad={r['bad_facts']}", flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)

    J402a = all(R[s]['j402a'] for s in seeds)
    J402b = all(R[s]['j402b'] for s in seeds)
    J402c = all(R[s]['clean_appos'] and R[s]['junk_rate'] == 0.0 and R[s]['coverage'] >= 0.25 for s in seeds) and gate_ok
    passed = J402a and J402b and J402c
    print("\n--- VERDICT ---", flush=True)
    print(f"J402a no heart->fist falsehood : {J402a}", flush=True)
    print(f"J402b no subordinate-subject   : {J402b}", flush=True)
    print(f"J402c clean appos + dense junk=0 + suite: {J402c}", flush=True)
    verdict = ("PASS - correctness guards reject the wrong captures (no heart->fist, no 'because they' subject) while "
               "clean appositives still work; dense-prose junk rate is now 0.0 with good facts kept; suite green. "
               "'Never wrong capture' restored even on dense prose -- miss > wrong.") if passed else \
              "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-402: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP402"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J402a": J402a, "J402b": J402b,
                                                  "J402c": J402c, "passed": passed}, default=str))
    print("DONE", flush=True)
