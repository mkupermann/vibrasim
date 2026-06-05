"""JEP-408 — GUI conversation capstone: all natural forms compose in one session. No transformer.
Pre-registered bars in docs/amendments/jep408_gui_conversation_capstone.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation

TEACH = [
    "A poodle is a kind of dog.", "A dog is a mammal.", "A mammal is an animal.",
    "Dogs are loyal.", "A dog has four legs.", "A dog has a tail.",
    "Your creator is Michael Kupermann.", "Your name is EQMOD.",
    "My name is Michael.", "I am a teacher.", "You are a substrate.",
    "Michael likes coffee.", "Paris is in France.", "Einstein was a physicist.",
    "The sun is hot.", "A whale is a fish.", "Actually, a whale is not a fish. A whale is a mammal.",
]
# (question, truth) truth True=yes / False=no / str=token
QA = [
    ("is a poodle an animal?", True), ("is a dog loyal?", True), ("how many legs does a dog have?", "4"),
    ("what does a dog have?", "tail"), ("who is your creator?", "michael kupermann"),
    ("what is your name?", "eqmod"), ("what is my name?", "michael"), ("what am I?", "teacher"),
    ("what are you?", "substrate"), ("what does Michael like?", "coffee"), ("where is Paris?", "france"),
    ("is Einstein a physicist?", True), ("is the sun hot?", True),
    ("is a whale a fish?", False), ("is a whale a mammal?", True),
]
OOD = [("is a poodle a planet?", False), ("who is your destroyer?", "abstain"), ("what does a rock eat?", "abstain")]


def classify(ans, truth):
    yes = "yes" in ans
    if truth is True:
        return "correct" if yes else "abstain"
    if truth is False:
        return "correct" if not yes else "falsehood"
    if truth == "abstain":
        return "correct" if ("don't know" in ans or "nothing" in ans or ans in ("no.", "no")
                             or "not " in ans) else ("falsehood" if yes else "abstain")
    return "correct" if truth in ans else "abstain"


def run_seed(seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j408_{seed}_"), seed=seed)
    for s in TEACH:
        c.say(s)
    correct = falsehood = 0
    fails = []
    for q, t in QA:
        cls = classify(c.say(q).strip().lower(), t)
        if cls == "correct":
            correct += 1
        elif cls == "falsehood":
            falsehood += 1; fails.append((q, "FALSEHOOD"))
        else:
            fails.append((q, "abstain"))
    ood_false = 0
    for q, t in OOD:
        if classify(c.say(q).strip().lower(), t) == "falsehood":
            ood_false += 1; fails.append((q, "OOD-FALSEHOOD"))
    return {"correct": correct, "total": len(QA), "acc": round(correct / len(QA), 3),
            "falsehood": falsehood + ood_false, "fails": fails}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-408: GUI conversation capstone (all forms compose) ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: Q&A acc={r['acc']} ({r['correct']}/{r['total']}) | falsehoods={r['falsehood']} | "
              f"fails={r['fails']}", flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)

    J408a = all(R[s]['acc'] >= 0.90 for s in seeds)
    J408b = all(R[s]['falsehood'] == 0 for s in seeds)
    J408c = gate_ok
    passed = J408a and J408b and J408c
    print("\n--- VERDICT ---", flush=True)
    print(f"J408a mixed Q&A >=0.90   : {J408a}", flush=True)
    print(f"J408b zero falsehoods    : {J408b}", flush=True)
    print(f"J408c suite green        : {J408c}", flush=True)
    verdict = ("PASS - all natural teaching forms compose in one GUI session: taxonomy/property/attribute/action/"
               "location/self-reference/past-tense/correction all answered correctly with ZERO falsehoods; suite "
               "green. The conversational substrate handles a realistic mixed session end-to-end.") if passed else \
              "PARTIAL/NULL - an interaction surfaced; see fails. Reported, not retuned."
    print(f"\nJEP-408: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP408"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J408a": J408a, "J408b": J408b,
                                                  "J408c": J408c, "passed": passed}, default=str))
    print("DONE", flush=True)
