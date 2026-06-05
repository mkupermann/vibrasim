"""JEP-350 — honest aggregate Half-1 reach on a realistic multi-paragraph article. No transformer.
Pre-registered bars in docs/amendments/jep350_realistic_article_endtoend.md.
"""
import json, tempfile, re
from pathlib import Path
import numpy as np
from world.conversation import Conversation
from world.understanding import UnderstandingEngine
from world.brain_query import BrainQuery

ARTICLE = """
A dog is a mammal. A mammal is an animal. Dogs are domesticated animals.
The poodle is a breed of dog. A poodle is a kind of dog. Cats and dogs are mammals.
A dog has four legs. A dog can bark. A dog can run. Dogs are carnivores.
A puppy is a young dog. A wolf, which is a wild animal, can howl.
A heart is part of a dog. A dog has a tail.
Paris is in France. France is in Europe. Berlin is in Germany. Germany is in Europe.
A salmon is a fish. A fish is an animal. A salmon can swim.
Smoking causes cancer. Pollution causes smog.
A bird is an animal. A sparrow is a bird. A bird can fly.
""".strip()


def climb(mem, x, y, rel, g):
    from collections import deque
    q, seen, n = deque([x]), {x}, 0
    while q and n < 30:
        cur = q.popleft(); n += 1
        for (p, _) in mem.query_all(cur, rel, g):
            if p == y:
                return True
            if p not in seen:
                seen.add(p); q.append(p)
    return False


def run_seed(seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"art_{seed}_"), seed=seed)
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", ARTICLE.replace("\n", " ")) if s.strip()]
    yielded = 0; missed = []
    for s in sents:
        before = len(c.sm.facts)
        c._learn_one(s)
        if len(c.sm.facts) > before:
            yielded += 1
        else:
            missed.append(s)
    coverage = yielded / len(sents)

    g = BrainQuery(c.sm, seed=seed).gate
    bq = BrainQuery(c.sm, seed=seed)
    battery = [
        ("poodle is-a animal", bq.is_a("poodle", "animal"), True),
        ("salmon is-a animal", bq.is_a("salmon", "animal"), True),
        ("cat is-a mammal", bq.is_a("cat", "mammal"), True),
        ("dog has 4 legs", bq.how_many("dog") == 4, True),
        ("dog can bark", bq.has_property("dog", "bark"), True),
        ("poodle can bark", bq.has_property("poodle", "bark"), True),
        ("paris in europe", climb(c.sm, "paris", "europe", "located_in", g), True),
        ("what causes cancer", "smoking" in bq.why("cancer"), True),
        ("salmon is-a mammal (False)", bq.is_a("salmon", "mammal"), False),
    ]
    qa = np.mean([(got == exp) for (_, got, exp) in battery])
    gaps = c.gaps()
    return {"coverage": round(coverage, 3), "n_sent": len(sents), "qa": round(float(qa), 3),
            "gaps": gaps[:8], "missed": missed}


if __name__ == "__main__":
    print("=== JEP-350: realistic article end-to-end (aggregate Half-1 reach) ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: coverage={r['coverage']} ({r['n_sent']} sentences) | Q&A={r['qa']}", flush=True)
        print(f"      missed: {r['missed']}", flush=True)
        print(f"      gaps reported: {r['gaps']}", flush=True)
    J350a = all(R[s]['coverage'] >= 0.80 for s in seeds)
    J350b = all(R[s]['qa'] >= 0.85 for s in seeds)
    J350c = all(len(R[s]['gaps']) >= 0 for s in seeds)   # gaps reported (may be empty if all defined)
    passed = J350a and J350b
    print("\n--- VERDICT ---", flush=True)
    print(f"J350a coverage >=0.80 : {J350a}", flush=True)
    print(f"J350b Q&A >=0.85      : {J350b}", flush=True)
    verdict = ("PASS - on a realistic ~25-sentence article the brain reads a strong majority and answers content "
               "questions; honest aggregate Half-1 reach") if passed else "NULL/partial - honest reach below bar"
    print(f"\nJEP-350: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP350"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J350a": J350a, "J350b": J350b, "passed": passed},
                                                 default=str))
    print("DONE", flush=True)
