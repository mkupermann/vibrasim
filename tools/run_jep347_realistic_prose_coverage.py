"""JEP-347 — honest coverage on realistic encyclopedic prose. No transformer.
Pre-registered bars in docs/amendments/jep347_realistic_prose_coverage.md.
"""
import json, tempfile
from pathlib import Path
import numpy as np
from world.conversation import Conversation
from world.understanding import UnderstandingEngine

# realistic Wikipedia-style factual sentences (clear, but NOT all clean 'A is a B')
SENTS = [
    "A dog is a mammal.",
    "A mammal is an animal.",
    "Dogs are domesticated animals.",
    "A dog has four legs.",
    "A dog can bark.",
    "The poodle is a breed of dog.",
    "A poodle is a dog.",
    "Dogs are carnivores.",
    "A dog has a tail.",
    "A wolf is a wild animal.",
    "A dog can run.",
    "A puppy is a young dog.",
    "Smoking causes cancer.",
    "A heart is part of a dog.",
    "A poodle is a kind of dog.",
]


def run_seed(seed):
    d = tempfile.mkdtemp(prefix=f"prose_{seed}_")
    conv = Conversation(brain_dir=d, seed=seed)
    eng_ref = UnderstandingEngine(seed=seed)

    yielded = []; missed = []
    for s in SENTS:
        before = len(conv.sm.facts)
        conv.read_text(s)
        eng_ref.read(s)
        if len(conv.sm.facts) > before:
            yielded.append(s)
        else:
            missed.append(s)
    coverage = len(yielded) / len(SENTS)

    # Q&A drawn from content that COULD be extracted, vs the reference engine
    battery = [("is a poodle a dog?", eng_ref.is_a("poodle", "dog")),
               ("is a dog a mammal?", eng_ref.is_a("dog", "mammal")),
               ("is a poodle an animal?", eng_ref.is_a("poodle", "animal")),
               ("can a dog bark?", eng_ref.has_property("dog", "bark")),
               ("can a poodle bark?", eng_ref.has_property("poodle", "bark")),
               ("how many legs does a dog have?", None)]
    ok = 0; tot = 0
    for (q, exp) in battery:
        if exp is None:
            continue
        tot += 1
        ok += (conv.say(q).strip().lower() == ("yes." if exp else "no."))
    qa = ok / tot if tot else 1.0

    return {"coverage": round(coverage, 3), "n_yield": len(yielded), "n_total": len(SENTS),
            "qa": round(qa, 3), "missed": missed}


if __name__ == "__main__":
    print("=== JEP-347: honest coverage on realistic encyclopedic prose ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: parse coverage={r['coverage']} ({r['n_yield']}/{r['n_total']}) | Q&A={r['qa']}", flush=True)
        print(f"      MISSED forms: {r['missed']}", flush=True)
    J347a = all(R[s]['coverage'] >= 0.60 for s in seeds)
    J347b = all(R[s]['qa'] >= 0.80 for s in seeds)
    passed = J347a and J347b
    print("\n--- VERDICT ---", flush=True)
    print(f"J347a parse coverage >=60% : {J347a}", flush=True)
    print(f"J347b Q&A >=80%            : {J347b}", flush=True)
    print(f"J347c missed forms reported: True (see MISSED above)", flush=True)
    verdict = ("PASS - the brain extracts a useful majority of facts from realistic clear prose and answers content "
               "questions; missed forms named honestly") if passed else "NULL/partial - coverage/Q&A below bar (honest reach)"
    print(f"\nJEP-347: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP347"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J347a": J347a, "J347b": J347b, "passed": passed},
                                                 default=str))
    print("DONE", flush=True)
