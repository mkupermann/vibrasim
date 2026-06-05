"""JEP-358 — interactive construction teaching: brain asks when it can't parse, learns the form live. No transformer.
Pre-registered bars in docs/amendments/jep358_interactive_construction_teaching.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation
from world.brain_query import BrainQuery


def run_seed(seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"int_{seed}_"), seed=seed)

    # J358b: a normal statement does NOT trigger the ask
    r_norm = c.say("A poodle is a dog.")
    norm_no_ask = "couldn't" not in r_norm.lower()
    r_restate = c.say("A poodle is a dog.")            # re-stated known fact -> no ask
    restate_no_ask = "couldn't" not in r_restate.lower()

    # J358a: an unparseable statement -> ask -> teach -> after 2, learns the construction
    r1 = c.say("The dog was domesticated by humans.")
    asked1 = "couldn't" in r1.lower()
    ack1 = c.say("humans domesticated dog")            # teacher answers with the fact
    r2 = c.say("The horse was domesticated by people.")
    asked2 = "couldn't" in r2.lower()
    ack2 = c.say("people domesticated horse")
    learned = "pattern" in ack2.lower()

    # held-out: read a NEW sentence of that form -> now parses, answerable
    c.say("A cat was domesticated by farmers.")
    got = ("farmers", "domesticated", "cat") in set(c.sm.facts)

    return {"norm_no_ask": bool(norm_no_ask), "restate_no_ask": bool(restate_no_ask),
            "asked1": bool(asked1), "asked2": bool(asked2), "learned_announced": bool(learned),
            "heldout_parsed": bool(got), "ack1": ack1}


def regression(repo):
    g = subprocess.run([sys.executable, "-m", "pytest", "tests/test_conversation.py", "-q"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    s = subprocess.run([sys.executable, "tools/run_jep357_self_extending_reading.py"], capture_output=True,
                       text=True, env={**os.environ, "PYTHONPATH": repo})
    return ("passed" in g.stdout and "failed" not in g.stdout), ("JEP-357: PASS" in s.stdout)


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-358: interactive construction teaching ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: normal-no-ask={r['norm_no_ask']} restate-no-ask={r['restate_no_ask']} | "
              f"asked={r['asked1']}&{r['asked2']} learned={r['learned_announced']} held-out-parsed={r['heldout_parsed']}",
              flush=True)
        print(f"      ack: {r['ack1']}", flush=True)
    gate, j357 = regression(repo)
    print(f"  conversation gate: {gate} | JEP-357: {j357}", flush=True)

    J358a = all(R[s]['asked1'] and R[s]['learned_announced'] and R[s]['heldout_parsed'] for s in seeds)
    J358b = all(R[s]['norm_no_ask'] and R[s]['restate_no_ask'] for s in seeds)
    J358c = gate and j357
    passed = J358a and J358b and J358c
    print("\n--- VERDICT ---", flush=True)
    print(f"J358a asks + learns the form live: {J358a}", flush=True)
    print(f"J358b no false ask on parseable   : {J358b}", flush=True)
    print(f"J358c no regression               : {J358c}", flush=True)
    verdict = ("PASS - when the brain can't parse a sentence it ASKS the teacher, learns the construction from 2 "
               "answers, and then reads that form by itself -- human-in-the-loop self-extension, live") if passed \
        else "NULL/partial"
    print(f"\nJEP-358: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP358"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate, "j357": j357, "J358a": J358a,
                                                  "J358b": J358b, "J358c": J358c, "passed": passed}, default=str))
    print("DONE", flush=True)
