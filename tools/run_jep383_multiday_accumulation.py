"""JEP-383 — 'read a book over 3 days': multi-session accumulation + cross-day reasoning. No transformer.
Pre-registered bars in docs/amendments/jep383_multiday_accumulation.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation


def run_seed(seed):
    brain = tempfile.mkdtemp(prefix=f"j383_{seed}_")

    # Day 1
    d1 = Conversation(brain_dir=brain, seed=seed)
    d1.read_text("A poodle is a kind of dog. Dogs are mammals.")
    d1.save()
    facts_d1 = len(d1.sm.facts)

    # Day 2 — fresh process loads day-1 brain
    d2 = Conversation(brain_dir=brain, seed=seed)
    loaded_d1 = ("poodle", "isa", "dog") in set(d2.sm.facts)        # persisted from day 1
    d2.read_text("Mammals are animals that are warm-blooded. A dog can bark.")
    d2.save()

    # Day 3 — fresh process loads day-2 brain
    d3 = Conversation(brain_dir=brain, seed=seed)
    d3.read_text("A dog has four legs.")

    # J383a: accumulation, no forgetting (day-1 and day-2 facts answerable on day 3)
    poodle_dog = "yes" in d3.say("is a poodle a dog?").strip().lower()         # day 1
    dog_bark = "yes" in d3.say("can a dog bark?").strip().lower()              # day 2
    dog_legs = "4" in d3.say("how many legs does a dog have?").strip().lower() # day 3
    j383a = bool(poodle_dog and dog_bark)

    # J383b: cross-day multi-hop
    poodle_animal = "yes" in d3.say("is a poodle an animal?").strip().lower()
    j383b = bool(poodle_animal)

    # J383c: consolidation persisted + abstention
    closed_persisted = "isa" in d3.sm.closed_relations
    abstain = "yes" not in d3.say("is a poodle a robot?").strip().lower()
    j383c_local = bool(closed_persisted and abstain)

    return {"facts_d1": facts_d1, "loaded_d1": bool(loaded_d1), "facts_d3": len(d3.sm.facts),
            "poodle_dog": bool(poodle_dog), "dog_bark": bool(dog_bark), "dog_legs": bool(dog_legs),
            "j383a": j383a, "poodle_animal": bool(poodle_animal), "j383b": j383b,
            "closed_persisted": bool(closed_persisted), "abstain": bool(abstain), "j383c_local": j383c_local}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-383: read over 3 days (multi-session accumulation) ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: loaded_d1={r['loaded_d1']} facts d1={r['facts_d1']}->d3={r['facts_d3']} | "
              f"day1 poodle-dog={r['poodle_dog']} day2 dog-bark={r['dog_bark']} day3 legs={r['dog_legs']} | "
              f"cross-day poodle->animal={r['poodle_animal']} | closed_persisted={r['closed_persisted']} "
              f"abstain={r['abstain']}", flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)

    J383a = all(R[s]['j383a'] for s in seeds)
    J383b = all(R[s]['j383b'] for s in seeds)
    J383c = all(R[s]['j383c_local'] for s in seeds) and gate_ok
    passed = J383a and J383b and J383c
    print("\n--- VERDICT ---", flush=True)
    print(f"J383a accumulation, no forgetting : {J383a}", flush=True)
    print(f"J383b cross-day multi-hop         : {J383b}", flush=True)
    print(f"J383c consolidation persists+abstain: {J383c}", flush=True)
    verdict = ("PASS - the substrate reads across 3 separate save/load sessions, accumulates knowledge without "
               "forgetting, resolves a multi-hop chain whose links were learned on DIFFERENT days, keeps consolidation "
               "across sessions, and abstains on the unmentioned. Michael's 'read a book over days' capability holds "
               "end-to-end.") if passed else \
              "NULL/partial - see rows (a bar missed; report the persistence-vs-consolidation diagnosis, do not retune)."
    print(f"\nJEP-383: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP383"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J383a": J383a, "J383b": J383b,
                                                  "J383c": J383c, "passed": passed}, default=str))
    print("DONE", flush=True)
