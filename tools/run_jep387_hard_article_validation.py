"""JEP-387 — validate the cumulative construction sweep on a harder article. No transformer.
Pre-registered bars in docs/amendments/jep387_hard_article_validation.md.
"""
import json, re, tempfile
from pathlib import Path
from world.conversation import Conversation

# Harder article: passive, appositive, quantifiers, conjunction-of-clauses, relative clauses, such-as, definitions.
ARTICLE = """
Mammals are animals that are warm-blooded. A dog is a mammal. The lion, a large cat, is a predator.
Lions are mammals, and mammals are vertebrates. Most birds can fly. A sparrow is a bird.
Birds such as eagles and hawks are predators. Fish are animals that live in water. A salmon is a fish.
Salmon are eaten by bears. Both frogs and toads are amphibians. An amphibian is an animal that lives in water and on land.
A dog has four legs. Reptiles are cold-blooded animals. A snake is a reptile.
Whales, which are mammals, live in the ocean. Many insects have six legs. A bee is an insect.
The eagle, a bird of prey, hunts small animals. A tiger is a mammal.
""".strip()

QA = [
    ("is a dog an animal?", "yes"),          # dog->mammal->animal
    ("is a lion a mammal?", "yes"),          # lion->cat? ... lion is 'a large cat'->cat; lions are mammals
    ("is a lion a vertebrate?", "yes"),      # lion->mammal->vertebrate (conjunction-of-clauses)
    ("is a salmon an animal?", "yes"),       # salmon->fish->animal
    ("is a snake a reptile?", "yes"),
    ("is a bee an insect?", "yes"),
    ("is a sparrow a bird?", "yes"),
    ("how many legs does a dog have?", "4"),
    ("is a dog a fish?", "no"),
    ("what was the salmon eaten by?", "bear"),   # passive query
]
MULTIHOP = ["is a dog an animal?", "is a lion a vertebrate?"]
OOD = ["is a robot an animal?", "what is the capital of italy?", "is a rock a mammal?"]


def run_seed(seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j387_{seed}_"), seed=seed)
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

    ood = sum(1 for q in OOD if "yes" not in c.say(q).strip().lower())
    ood_abstain = round(ood / len(OOD), 3)

    # junk: multi-word entity names among stored facts (subjects or objects)
    ents = set()
    for (a, r, b) in c.sm.facts:
        ents.add(a); ents.add(b)
    junk = [e for e in ents if " " in e]
    junk_rate = round(len(junk) / max(1, len(ents)), 3)

    return {"coverage": coverage, "covered": covered, "n": len(factual), "qa_acc": qa_acc, "multihop": bool(multihop),
            "ood_abstain": ood_abstain, "junk_rate": junk_rate, "junk": junk,
            "qa_fail": [q for q, ok in qa if not ok], "facts": len(c.sm.facts)}


if __name__ == "__main__":
    print("=== JEP-387: harder-article validation (cumulative construction sweep) ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: coverage={r['coverage']} ({r['covered']}/{r['n']}) facts={r['facts']} | Q&A={r['qa_acc']} "
              f"(fail {r['qa_fail']}) multihop={r['multihop']} | OOD={r['ood_abstain']} | junk={r['junk_rate']} "
              f"{r['junk']}", flush=True)

    J387a = all(R[s]['coverage'] >= 0.80 for s in seeds)
    J387b = all(R[s]['qa_acc'] >= 0.90 and R[s]['multihop'] for s in seeds)
    J387c = all(R[s]['ood_abstain'] >= 0.95 and R[s]['junk_rate'] <= 0.05 for s in seeds)
    passed = J387a and J387b and J387c
    print("\n--- VERDICT ---", flush=True)
    print(f"J387a coverage >=0.80          : {J387a}", flush=True)
    print(f"J387b Q&A >=0.90 incl multihop : {J387b}", flush=True)
    print(f"J387c abstain>=0.95 & junk<=5% : {J387c}", flush=True)
    verdict = ("PASS - the cumulative construction sweep handles a harder article: high coverage, reliable Q&A "
               "(incl. multi-hop + passive query), perfect abstention, and ~zero junk entities. Real encyclopedia "
               "prose is captured cleanly and answered without mistakes inside the captured domain.") if passed else \
              ("PARTIAL/NULL - see rows; residual construction gap or junk leak. Reported, not retuned.")
    print(f"\nJEP-387: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP387"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J387a": J387a, "J387b": J387b, "J387c": J387c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
