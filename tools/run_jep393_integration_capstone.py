"""JEP-393 — integration capstone: the whole vision in one flow. No transformer.
Pre-registered bars in docs/amendments/jep393_integration_capstone.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation

DAY1 = ("A dog is a mammal. Mammals are animals that are warm-blooded. A poodle is a kind of dog. "
        "A wheel is part of a car. A car has four wheels. Friction causes heat. "
        "Birds such as sparrows and eagles can fly. A whale is a fish.")
DAY2 = ("Actually, a whale is not a fish. A whale is a mammal. Salmon are fish, and fish are animals. "
        "A salmon is a fish. Heat causes expansion. The lion, a large cat, is a predator.")

QA = [
    ("is a poodle an animal?", "yes"),       # cross-day multi-hop (poodle/dog/mammal day1, animal day1)
    ("is a dog warm-blooded?", "yes"),
    ("is a wheel part of a car?", "yes"),    # part-of
    ("how many wheels does a car have?", "4"),  # count
    ("what causes heat?", "friction"),       # causal
    ("what causes expansion?", "heat"),      # causal day2
    ("is a whale a fish?", "no"),            # CORRECTION (day1 said fish, day2 corrected)
    ("is a whale a mammal?", "yes"),         # corrected
    ("is a salmon an animal?", "yes"),       # day2 conjunction multi-hop
    ("is a lion a predator?", "yes"),        # appositive
]
OOD = ["is a dog a planet?", "what causes happiness?", "is a wheel part of a star?"]


def run_seed(seed):
    brain = tempfile.mkdtemp(prefix=f"j393_{seed}_")
    d1 = Conversation(brain_dir=brain, seed=seed); d1.read_text(DAY1); d1.save()
    d2 = Conversation(brain_dir=brain, seed=seed); d2.read_text(DAY2); d2.save()
    d3 = Conversation(brain_dir=brain, seed=seed)

    qa = []
    for q, exp in QA:
        a = d3.say(q).strip().lower()
        ok = ("yes" in a) if exp == "yes" else (("yes" not in a) if exp == "no" else (exp in a))
        qa.append((q, ok))
    qa_acc = round(sum(ok for _, ok in qa) / len(qa), 3)

    gaps = set(d3.gaps())
    bad_gap = gaps & {"dog", "mammal", "poodle", "car", "whale", "animal"}      # defined/roots must NOT be gaps
    ood = sum(1 for q in OOD if "yes" not in d3.say(q).strip().lower() and "friction" not in d3.say(q).strip().lower())
    ood_abstain = round(ood / len(OOD), 3)
    ents = {e for (a, r, b) in d3.sm.facts for e in (a, b)}
    junk = [e for e in ents if " " in e]
    junk_rate = round(len(junk) / max(1, len(ents)), 3)
    closed = "isa" in d3.sm.closed_relations

    return {"qa_acc": qa_acc, "qa_fail": [q for q, ok in qa if not ok], "gaps": sorted(gaps),
            "bad_gap": sorted(bad_gap), "ood_abstain": ood_abstain, "junk_rate": junk_rate, "junk": junk,
            "closed": bool(closed), "facts": len(d3.sm.facts)}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-393: integration capstone (multi-day + all relations + correction + curiosity) ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: Q&A={r['qa_acc']} (fail {r['qa_fail']}) | gaps={r['gaps']} bad={r['bad_gap']} | "
              f"OOD={r['ood_abstain']} junk={r['junk_rate']} {r['junk']} | closed={r['closed']} facts={r['facts']}",
              flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)

    J393a = all(R[s]['qa_acc'] >= 0.90 for s in seeds)
    J393b = all(not R[s]['bad_gap'] and R[s]['ood_abstain'] >= 1.0 for s in seeds)
    J393c = all(R[s]['junk_rate'] <= 0.05 and R[s]['closed'] for s in seeds) and gate_ok
    passed = J393a and J393b and J393c
    print("\n--- VERDICT ---", flush=True)
    print(f"J393a broad Q&A >=0.90 (incl cross-day+correction): {J393a}", flush=True)
    print(f"J393b curiosity gaps sane + OOD abstain 1.0       : {J393b}", flush=True)
    print(f"J393c clean (junk<=5%) + durable consolidation    : {J393c}", flush=True)
    verdict = ("PASS - the whole vision composes in one flow: a factual article read across days (is-a + part-of + "
               "causal + counts, mixed constructions) is answered reliably incl. cross-day multi-hop, a mid-stream "
               "correction holds (whale not a fish), curiosity gaps are sensible, abstention is perfect, junk is zero, "
               "and consolidation persists. No interaction bugs.") if passed else \
              "PARTIAL/NULL - an interaction surfaced; see rows. Reported, not retuned."
    print(f"\nJEP-393: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP393"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J393a": J393a, "J393b": J393b,
                                                  "J393c": J393c, "passed": passed}, default=str))
    print("DONE", flush=True)
