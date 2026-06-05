"""JEP-357 — self-extending reading: the brain learns to read a new construction from the teacher. No transformer.
Pre-registered bars in docs/amendments/jep357_self_extending_reading.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation
from world.brain_query import BrainQuery


def run_seed(seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"selfext_{seed}_"), seed=seed)
    heldout = [("A cat was domesticated by farmers.", ("farmers", "domesticated", "cat")),
               ("A sheep was domesticated by herders.", ("herders", "domesticated", "sheep"))]

    # BEFORE teaching: the construction yields nothing
    before_parsed = 0
    for (s, _) in heldout:
        n0 = len(c.sm.facts); c._learn_one(s); before_parsed += (len(c.sm.facts) > n0)
    # reset by using a fresh conv (the above may have partially added nothing)
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"selfext2_{seed}_"), seed=seed)

    # TEACH 2 examples of the new construction
    c.teach_construction("The dog was domesticated by humans.", ("humans", "domesticated", "dog"))
    n_templates = c.teach_construction("The horse was domesticated by people.", ("people", "domesticated", "horse"))

    # NOW read held-out sentences normally -> they should parse via the learned construction
    after_parsed = 0; facts_ok = 0
    for (s, gold) in heldout:
        n0 = len(c.sm.facts); c._learn_one(s)
        after_parsed += (len(c.sm.facts) > n0)
        facts_ok += (tuple(x.lower() for x in gold) in set(c.sm.facts))

    # no false-fire on a normal unrelated sentence
    n0 = len(c.sm.facts); c._learn_one("The sky is blue today and very clear.")
    # (it's fine if a normal sentence parses via the engine; we only check the learned template didn't inject junk)
    junk = any(r == "domesticated" and o == "sky" for (s, r, o) in c.sm.facts)

    return {"before_parsed": before_parsed, "after_parsed": after_parsed, "facts_ok": facts_ok,
            "n_templates": n_templates, "no_junk": not junk}


def regression(repo):
    g = subprocess.run([sys.executable, "-m", "pytest", "tests/test_conversation.py", "-q"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    return "passed" in g.stdout and "failed" not in g.stdout


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-357: self-extending reading (learn to read a new construction from the teacher) ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: before-teach parsed={r['before_parsed']}/2 | learned {r['n_templates']} template(s) | "
              f"after-teach parsed={r['after_parsed']}/2 facts-correct={r['facts_ok']}/2 | no-junk={r['no_junk']}",
              flush=True)
    reg = regression(repo)
    print(f"  conversation gate: {'PASS' if reg else 'FAIL'}", flush=True)
    J357a = all(R[s]['facts_ok'] >= 2 for s in seeds)
    J357b = all(R[s]['before_parsed'] == 0 and R[s]['after_parsed'] == 2 for s in seeds)
    J357c = all(R[s]['no_junk'] for s in seeds) and reg
    passed = J357a and J357b and J357c
    print("\n--- VERDICT ---", flush=True)
    print(f"J357a learns to read held-out (facts correct): {J357a}", flush=True)
    print(f"J357b gap before -> parsed after              : {J357b}", flush=True)
    print(f"J357c no junk + gate green                     : {J357c}", flush=True)
    verdict = ("PASS - the brain EXTENDS ITS OWN READING: taught 2 examples of a new construction, it then reads "
               "unseen sentences of that form by itself (induction + the durable store)") if passed else "NULL/partial"
    print(f"\nJEP-357: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP357"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "reg": reg, "J357a": J357a, "J357b": J357b,
                                                  "J357c": J357c, "passed": passed}, default=str))
    print("DONE", flush=True)
