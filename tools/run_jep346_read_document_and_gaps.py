"""JEP-346 — read a document into the brain, discuss it, report gaps ('what is not clear to you?'). No transformer.
Pre-registered bars in docs/amendments/jep346_read_document_and_gaps.md.
"""
import json, tempfile, os, importlib
from pathlib import Path
import numpy as np
from world.conversation import Conversation
from world.understanding import UnderstandingEngine

DOC = (
    "A poodle is a dog. A beagle is a dog. A dog is a mammal. A cat is a mammal. A mammal is an animal. "
    "A salmon is a fish. A fish is an animal. A dog can bark. A bird can fly. A heart is part of a mammal. "
    "Smoking causes cancer."
)
# 'bird' is referenced (a bird can fly) but never defined -> a genuine gap; 'animal' is a root (not a gap)
DOC2 = "A bird is an animal. A sparrow is a bird."   # next-day reading: defines 'bird' -> closes that gap


def run_seed(seed):
    d = tempfile.mkdtemp(prefix=f"doc_{seed}_")
    conv = Conversation(brain_dir=d, seed=seed)
    r = conv.read_text(DOC)
    learned_ok = r["facts_learned"] >= 8

    # discuss: answer questions about the document, vs engine ground truth
    eng = UnderstandingEngine(seed=seed); eng.read(DOC)
    qs = [("is a poodle an animal?", eng.is_a("poodle", "animal")),
          ("can a poodle bark?", eng.has_property("poodle", "bark")),
          ("is a salmon a mammal?", eng.is_a("salmon", "mammal")),
          ("what causes cancer?", None)]
    disc_ok = sum((conv.say(q).strip().lower() == ("yes." if exp else "no.")) for (q, exp) in qs[:3]) / 3

    # gaps: 'bird' should be flagged (referenced, undefined); after reading DOC2, 'bird' is defined -> gap gone
    gaps_before = conv.gaps()
    bird_flagged = "bird" in gaps_before
    resp_unclear = conv.say("what is not clear to you?")
    unclear_reports = ("bird" in resp_unclear.lower())

    conv.save()
    # NEXT DAY: reload (persisted) + read more -> accumulates + closes the 'bird' gap
    conv2 = Conversation(brain_dir=d, seed=seed)
    persisted = conv2.n_facts == conv.n_facts
    before2 = conv2.n_facts
    conv2.read_text(DOC2)
    grew_next_day = conv2.n_facts > before2
    bird_gap_closed = "bird" not in conv2.gaps()

    return {"facts_learned": r["facts_learned"], "learned_ok": bool(learned_ok), "discuss_acc": round(disc_ok, 3),
            "bird_flagged": bool(bird_flagged), "unclear_reports_bird": bool(unclear_reports),
            "persisted": bool(persisted), "grew_next_day": bool(grew_next_day),
            "bird_gap_closed": bool(bird_gap_closed), "unclear_response": resp_unclear}


if __name__ == "__main__":
    print("=== JEP-346: read a document, discuss, report gaps ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: learned={r['facts_learned']} discuss={r['discuss_acc']} | bird-gap-flagged="
              f"{r['bird_flagged']} | persists={r['persisted']} grew-next-day={r['grew_next_day']} "
              f"bird-gap-closed={r['bird_gap_closed']}", flush=True)
        print(f"      'what is not clear to you?' -> {r['unclear_response']}", flush=True)
    try:
        importlib.import_module("tools.read_to_brain"); tool_ok = True
    except Exception as ex:
        tool_ok = False; print("  read_to_brain:", ex, flush=True)

    J346a = all(R[s]['learned_ok'] and R[s]['discuss_acc'] >= 0.90 and R[s]['persisted'] for s in seeds)
    J346b = all(R[s]['bird_flagged'] and R[s]['unclear_reports_bird'] and R[s]['bird_gap_closed'] for s in seeds)
    J346c = all(R[s]['grew_next_day'] for s in seeds) and tool_ok
    passed = J346a and J346b and J346c
    print("\n--- VERDICT ---", flush=True)
    print(f"J346a read+discuss+persist (>=.90)            : {J346a}", flush=True)
    print(f"J346b 'what is not clear' reports real gaps    : {J346b}", flush=True)
    print(f"J346c next-day accumulation + tool             : {J346c}", flush=True)
    verdict = ("PASS - the brain reads a document (memory grows + persists across days), discusses it, and reports "
               "honest knowledge gaps when asked 'what is not clear to you?'") if passed else "NULL/partial"
    print(f"\nJEP-346: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP346"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J346a": J346a, "J346b": J346b, "J346c": J346c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
