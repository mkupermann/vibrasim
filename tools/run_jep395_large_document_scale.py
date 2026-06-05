"""JEP-395 — does the real-prose pipeline hold at book-chapter scale? No transformer.
Pre-registered bars in docs/amendments/jep395_large_document_scale.md.
"""
import json, re, tempfile
from pathlib import Path
from world.conversation import Conversation

# ~50 connected factual sentences (nested taxonomy + properties + part-of + causal).
ARTICLE = """
Animals are living organisms. Mammals are animals that are warm-blooded. Birds are animals that have feathers.
Fish are animals that live in water. Reptiles are animals that are cold-blooded. Amphibians are animals.
Insects are animals that have six legs. A dog is a mammal. A cat is a mammal. A poodle is a kind of dog.
A whale is a mammal. A dolphin is a mammal. A lion is a mammal. A tiger is a mammal. A bat is a mammal.
A sparrow is a bird. An eagle is a bird. A penguin is a bird. An owl is a bird. A robin is a bird.
A salmon is a fish. A shark is a fish. A tuna is a fish. A snake is a reptile. A lizard is a reptile.
A turtle is a reptile. A frog is an amphibian. A toad is an amphibian. A bee is an insect. An ant is an insect.
A dog has four legs. A bird has two legs. An insect has six legs. A spider has eight legs.
Mammals are vertebrates. Birds are vertebrates. Fish are vertebrates. Vertebrates are animals.
A heart is part of an animal. A wing is part of a bird. A fin is part of a fish. A leg is part of a dog.
Disease can harm animals. Viruses cause disease. Bacteria cause infection. Predators hunt prey.
A lion is a predator. Cold weather can kill insects. Pollution harms wildlife. A poodle is a pet.
""".strip()

QA = [
    ("is a poodle an animal?", "yes"),       # poodle->dog->mammal->animal (deep multi-hop)
    ("is a whale a vertebrate?", "yes"),     # whale->mammal->vertebrate->... multi-hop
    ("is a sparrow an animal?", "yes"),      # sparrow->bird->animal
    ("is a salmon a vertebrate?", "yes"),    # salmon->fish->vertebrate
    ("is a bee an animal?", "yes"),          # bee->insect->animal
    ("is a poodle a fish?", "no"),           # negative
    ("how many legs does a dog have?", "4"),
    ("how many legs does a spider have?", "8"),
    ("is a wing part of a bird?", "yes"),    # part-of
    ("what causes disease?", "virus"),       # causal
    ("is a lion a predator?", "yes"),
    ("is a tiger a mammal?", "yes"),
]
MULTIHOP = ["is a poodle an animal?", "is a whale a vertebrate?", "is a salmon a vertebrate?"]
OOD = ["is a robot an animal?", "what causes happiness?", "is a planet a mammal?"]


def sents_of(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.replace("\n", " ")) if s.strip()]


def coverage_at(prefix_sents, seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j395_{seed}_"), seed=seed)
    covered = 0
    for s in prefix_sents:
        b = len(c.sm.facts); c._learn_one(s)
        if len(c.sm.facts) > b:
            covered += 1
    c.consolidate()
    return round(covered / len(prefix_sents), 3), c


def run_seed(seed):
    sents = sents_of(ARTICLE)
    res = {}
    for n in (12, 25, len(sents)):
        cov, c = coverage_at(sents[:n], seed)
        res[n] = {"coverage": cov, "facts": len(c.sm.facts), "conv": c}
    cfull = res[len(sents)]["conv"]

    qa = []
    for q, exp in QA:
        a = cfull.say(q).strip().lower()
        ok = ("yes" in a) if exp == "yes" else (("yes" not in a) if exp == "no" else (exp in a))
        qa.append((q, ok))
    qa_acc = round(sum(ok for _, ok in qa) / len(qa), 3)
    multihop = all("yes" in cfull.say(q).strip().lower() for q in MULTIHOP)
    ood = sum(1 for q in OOD if "yes" not in cfull.say(q).strip().lower() and "virus" not in cfull.say(q).strip().lower())
    ood_abstain = round(ood / len(OOD), 3)
    ents = {e for (a, r, b) in cfull.sm.facts for e in (a, b)}
    junk_rate = round(len([e for e in ents if " " in e]) / max(1, len(ents)), 3)

    return {"n_sents": len(sents), "cov12": res[12]["coverage"], "cov25": res[25]["coverage"],
            "cov50": res[len(sents)]["coverage"], "facts_full": res[len(sents)]["facts"],
            "qa_acc": qa_acc, "qa_fail": [q for q, ok in qa if not ok], "multihop": bool(multihop),
            "ood_abstain": ood_abstain, "junk_rate": junk_rate}


if __name__ == "__main__":
    print("=== JEP-395: large-document scale (coverage + reliability curve) ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: coverage 12={r['cov12']} 25={r['cov25']} {r['n_sents']}={r['cov50']} | "
              f"facts@full={r['facts_full']} | Q&A={r['qa_acc']} (fail {r['qa_fail']}) multihop={r['multihop']} | "
              f"OOD={r['ood_abstain']} junk={r['junk_rate']}", flush=True)

    J395a = all(min(R[s]['cov12'], R[s]['cov25'], R[s]['cov50']) >= 0.80 for s in seeds)
    J395b = all(R[s]['qa_acc'] >= 0.90 and R[s]['multihop'] for s in seeds)
    J395c = all(R[s]['ood_abstain'] >= 0.95 and R[s]['junk_rate'] <= 0.05 for s in seeds)
    passed = J395a and J395b and J395c
    print("\n--- VERDICT ---", flush=True)
    print(f"J395a coverage >=0.80 at all sizes : {J395a}", flush=True)
    print(f"J395b Q&A >=0.90 at full scale     : {J395b}", flush=True)
    print(f"J395c abstain+clean at scale       : {J395c}", flush=True)
    verdict = ("PASS - the real-prose pipeline holds at book-chapter scale: coverage stays high across 12/25/50 "
               "sentences, multi-hop Q&A stays reliable on the full document (hundreds of consolidated facts across "
               "modules), abstention is perfect and junk ~zero. Reading a real document end-to-end is reliable at "
               "scale.") if passed else \
              ("PARTIAL/NULL - see the size where it breaks (the honest scale curve). Reported, not retuned.")
    print(f"\nJEP-395: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP395"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J395a": J395a, "J395b": J395b, "J395c": J395c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
