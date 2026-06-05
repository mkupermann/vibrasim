"""JEP-345 — conversational robustness on messier phrasings. No transformer.
Pre-registered bars in docs/amendments/jep345_conversational_robustness.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation


def run_seed(seed):
    d = tempfile.mkdtemp(prefix=f"rob_{seed}_")
    c = Conversation(brain_dir=d, seed=seed)
    for s in ["A poodle is a dog.", "A dog is a mammal.", "A mammal is an animal.", "A dog can bark.",
              "A cat is a mammal."]:
        c.say(s)

    checks = []
    # negated/contracted question
    checks.append(("isn't a poodle a dog?", c.say("isn't a poodle a dog?").strip().lower() == "yes."))
    # plural subject
    checks.append(("do poodles bark?", c.say("do poodles bark?").strip().lower() == "yes."))
    # leading filler
    checks.append(("so, is a poodle an animal?", c.say("so, is a poodle an animal?").strip().lower() == "yes."))
    # multi-sentence turn mixing teach + ask
    r = c.say("A beagle is a dog. Is it a mammal?")
    checks.append(("mixed turn", "learned" in r.lower() and "yes" in r.lower()))
    # "what about X?" follow-up after a yes/no question
    c.say("is a dog a mammal?")
    wa = c.say("what about a cat?")
    checks.append(("what about a cat?", wa.strip().lower() == "yes."))

    acc = sum(v for _, v in checks) / len(checks)
    return {"acc": round(acc, 3), "checks": {k: bool(v) for k, v in checks}}


def regression(repo):
    outs = {}
    for name in ["run_jep340_conversation", "run_jep342_make_connections", "run_jep344_open_ended_questions"]:
        r = subprocess.run([sys.executable, f"tools/{name}.py"], capture_output=True, text=True,
                           env={**os.environ, "PYTHONPATH": repo})
        num = name.split("jep")[1][:3]
        outs[num] = f"JEP-{num}: PASS" in r.stdout
    return outs


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-345: conversational robustness on messier phrasings ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        print(f"  seed {s}: acc={R[s]['acc']} | {R[s]['checks']}", flush=True)
    reg = regression(repo)
    print(f"  regression: {reg}", flush=True)
    J345a = all(R[s]['acc'] >= 0.90 for s in seeds)
    J345b = all(reg.values())
    passed = J345a and J345b
    print("\n--- VERDICT ---", flush=True)
    print(f"J345a messy phrasings answered (>=.90): {J345a}", flush=True)
    print(f"J345b no regression (340, 342, 344)    : {J345b}", flush=True)
    verdict = ("PASS - the conversation tolerates negated/contracted forms, plurals, filler, multi-sentence turns, "
               "and 'what about X?' follow-ups") if passed else "NULL/partial"
    print(f"\nJEP-345: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP345"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "reg": reg, "J345a": J345a, "J345b": J345b,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
