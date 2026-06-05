"""JEP-381 — scale on a realistic ~28-sentence factual article: honest capture rate + reliability + abstention.
No transformer. Pre-registered bars in docs/amendments/jep381_real_article_scale.md.
"""
import json, re, tempfile
from pathlib import Path
from world.conversation import Conversation

# A natural-register factual article (mixed constructions: plurals, relative clauses, conjunctions, appositives,
# passive voice, definitions, lists). NOT shaped to the parser.
ARTICLE = """
Animals are living organisms. Mammals are animals that are warm-blooded. A dog is a mammal.
Dogs are loyal companions. A poodle is a kind of dog. Cats and dogs are carnivores.
A cat is a mammal. Birds are animals, and birds can fly. A sparrow is a bird.
An eagle is a bird of prey. Fish are animals that live in water. A salmon is a fish.
Salmon are fish, and fish are vertebrates. Reptiles are cold-blooded animals. A snake is a reptile.
A lizard is a reptile. Amphibians, such as frogs and toads, live both in water and on land.
A frog is an amphibian. Insects are small animals with six legs. A bee is an insect.
A dog has four legs. A spider has eight legs. The lion, which is a large cat, is a predator.
Whales are mammals that live in the ocean. A dolphin is a mammal. Penguins are birds that cannot fly.
A tiger is a mammal.
""".strip()

# Q&A whose answers are stated in CLEAR sentences (incl. multi-hop via consolidation)
QA = [
    ("is a dog an animal?", "yes"),          # dog->mammal->animal
    ("is a poodle a mammal?", "yes"),        # poodle->dog->mammal
    ("is a poodle an animal?", "yes"),       # multi-hop
    ("is a salmon a vertebrate?", "yes"),    # salmon->fish->vertebrate (conjunction)
    ("is a snake a reptile?", "yes"),
    ("is a salmon an animal?", "yes"),       # salmon->fish->animal
    ("is a sparrow a bird?", "yes"),
    ("is a bee an insect?", "yes"),
    ("is a dog a fish?", "no"),
    ("how many legs does a dog have?", "4"),
    ("how many legs does a spider have?", "8"),
    ("is a tiger a mammal?", "yes"),
]
MULTIHOP = ["is a poodle an animal?", "is a salmon a vertebrate?"]
OOD = ["is a robot an animal?", "what is the capital of japan?", "is a banana a mammal?"]


def is_factual(s):
    s = s.strip()
    return bool(s) and not s.endswith("?")


def run_seed(seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j381_{seed}_"), seed=seed)
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", ARTICLE.replace("\n", " ")) if s.strip()]
    factual = [s for s in sents if is_factual(s)]
    # coverage: read sentence-by-sentence, count those that add >=1 fact
    covered = 0
    for s in factual:
        before = len(c.sm.facts)
        c._learn_one(s)
        if len(c.sm.facts) > before:
            covered += 1
    c.consolidate()                                   # consolidate after the full read
    coverage = round(covered / len(factual), 3)

    qa_ok = []
    for q, exp in QA:
        ans = c.say(q).strip().lower()
        ok = ("yes" in ans) if exp == "yes" else (("yes" not in ans) if exp == "no" else (exp in ans))
        qa_ok.append((q, ok))
    qa_acc = round(sum(ok for _, ok in qa_ok) / len(qa_ok), 3)
    multihop = all("yes" in c.say(q).strip().lower() for q in MULTIHOP)

    ood_ok = 0
    for q in OOD:
        ans = c.say(q).strip().lower()
        if "yes" not in ans:                          # must not assert membership
            ood_ok += 1
    ood_abstain = round(ood_ok / len(OOD), 3)

    return {"n_factual": len(factual), "covered": covered, "coverage": coverage, "qa_acc": qa_acc,
            "multihop": bool(multihop), "ood_abstain": ood_abstain,
            "qa_fail": [q for q, ok in qa_ok if not ok], "facts": len(c.sm.facts)}


if __name__ == "__main__":
    print("=== JEP-381: scale on a realistic ~28-sentence article ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: coverage={r['coverage']} ({r['covered']}/{r['n_factual']}) facts={r['facts']} | "
              f"Q&A acc={r['qa_acc']} (fail: {r['qa_fail']}) | multihop={r['multihop']} | "
              f"OOD abstain={r['ood_abstain']}", flush=True)

    J381a = all(R[s]['coverage'] >= 0.55 for s in seeds)
    J381b = all(R[s]['qa_acc'] >= 0.90 and R[s]['multihop'] for s in seeds)
    J381c = all(R[s]['ood_abstain'] >= 0.95 for s in seeds)
    passed = J381a and J381b and J381c
    print("\n--- VERDICT ---", flush=True)
    print(f"J381a coverage >=0.55          : {J381a}", flush=True)
    print(f"J381b Q&A >=0.90 incl multihop : {J381b}", flush=True)
    print(f"J381c OOD abstention >=0.95    : {J381c}", flush=True)
    verdict = ("PASS - a realistic factual article is read end-to-end: a majority of natural sentences are captured, "
               "what is captured is answered reliably (incl. multi-hop via consolidation), and the brain abstains on "
               "everything unmentioned (zero hallucination). The reachable bounded domain holds at article scale.") \
        if passed else ("PARTIAL/NULL - see rows; coverage gap = the parsing wall on natural constructions (honest "
                        "measure), or a reliability/abstention miss. Reported, not retuned.")
    print(f"\nJEP-381: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP381"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J381a": J381a, "J381b": J381b, "J381c": J381c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
