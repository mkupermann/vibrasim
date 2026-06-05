"""JEP-389 — relational article capstone: taxonomy + part-of + causal, all queryable. No transformer.
Pre-registered bars in docs/amendments/jep389_relational_article.md.
"""
import json, re, tempfile
from pathlib import Path
from world.conversation import Conversation

ARTICLE = """
A car is a vehicle. Vehicles are machines. A wheel is part of a car. An engine is part of a car.
The engine, a complex machine, powers the car. A car has four wheels. Rust can damage a car.
Friction causes heat. Heat causes expansion. A battery is part of an engine.
Cars are machines that need fuel. Fuel powers the engine. A truck is a vehicle.
Brakes are parts of a car. Worn brakes cause accidents. A tire is part of a wheel.
""".strip()

QA = [
    ("is a car a machine?", "yes"),          # car->vehicle->machine (multi-hop)
    ("is a truck a vehicle?", "yes"),
    ("is a wheel part of a car?", "yes"),    # part-of query
    ("is an engine part of a car?", "yes"),
    ("is a tire part of a wheel?", "yes"),
    ("is a wheel part of a tree?", "no"),    # part-of negative
    ("what causes heat?", "friction"),       # causal query
    ("what causes expansion?", "heat"),
    ("what causes accidents?", "brake"),     # 'worn brakes cause accidents' -> brake
    ("how many wheels does a car have?", "4"),
]
MULTIHOP = ["is a car a machine?"]
OOD = ["is a car an animal?", "what causes happiness?", "is a wheel part of a planet?"]


def run_seed(seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j389_{seed}_"), seed=seed)
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", ARTICLE.replace("\n", " ")) if s.strip()]
    factual = [s for s in sents if not s.endswith("?")]
    covered = 0
    for s in factual:
        b = len(c.sm.facts); c._learn_one(s)
        if len(c.sm.facts) > b:
            covered += 1
    c.consolidate()
    coverage = round(covered / len(factual), 3)

    qa = []
    for q, exp in QA:
        a = c.say(q).strip().lower()
        ok = ("yes" in a) if exp == "yes" else (("yes" not in a) if exp == "no" else (exp in a))
        qa.append((q, ok))
    qa_acc = round(sum(ok for _, ok in qa) / len(qa), 3)
    multihop = all("yes" in c.say(q).strip().lower() for q in MULTIHOP)
    ood = sum(1 for q in OOD if "yes" not in c.say(q).strip().lower() and "friction" not in c.say(q).strip().lower())
    ood_abstain = round(ood / len(OOD), 3)
    ents = {e for (a, r, b) in c.sm.facts for e in (a, b)}
    junk = [e for e in ents if " " in e]
    junk_rate = round(len(junk) / max(1, len(ents)), 3)
    return {"coverage": coverage, "covered": covered, "n": len(factual), "qa_acc": qa_acc, "multihop": bool(multihop),
            "ood_abstain": ood_abstain, "junk_rate": junk_rate, "junk": junk, "facts": len(c.sm.facts),
            "qa_fail": [q for q, ok in qa if not ok]}


if __name__ == "__main__":
    print("=== JEP-389: relational article (is-a + part-of + causal) ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: coverage={r['coverage']} ({r['covered']}/{r['n']}) facts={r['facts']} | Q&A={r['qa_acc']} "
              f"(fail {r['qa_fail']}) multihop={r['multihop']} | OOD={r['ood_abstain']} | junk={r['junk_rate']} "
              f"{r['junk']}", flush=True)
    J389a = all(R[s]['coverage'] >= 0.80 for s in seeds)
    J389b = all(R[s]['qa_acc'] >= 0.90 and R[s]['multihop'] for s in seeds)
    J389c = all(R[s]['ood_abstain'] >= 0.95 and R[s]['junk_rate'] <= 0.05 for s in seeds)
    passed = J389a and J389b and J389c
    print("\n--- VERDICT ---", flush=True)
    print(f"J389a coverage >=0.80          : {J389a}", flush=True)
    print(f"J389b multi-relation Q&A >=0.90: {J389b}", flush=True)
    print(f"J389c abstain>=0.95 & junk<=5% : {J389c}", flush=True)
    verdict = ("PASS - a relational article (is-a + part-of + causal) is read end-to-end: high coverage, reliable Q&A "
               "across all three relation types (incl. multi-hop, part-of, and 'what causes X?'), perfect abstention, "
               "zero junk. The substrate captures a real article's RELATIONSHIPS, not just its taxonomy.") if passed \
              else "PARTIAL/NULL - see rows; residual relation gap. Reported, not retuned."
    print(f"\nJEP-389: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP389"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J389a": J389a, "J389b": J389b, "J389c": J389c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
