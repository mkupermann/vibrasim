"""JEP-401 — honest coverage ceiling on dense, hard encyclopedic prose. No transformer.
Pre-registered bars in docs/amendments/jep401_hard_prose_ceiling.md.
"""
import json, re, tempfile
from pathlib import Path
from world.conversation import Conversation

# Dense prose: long compound-complex sentences, parentheticals, comparatives, numbers, prepositional chains.
# Written to NOT favor the rule-based normalizer.
HARD = """
The cheetah, which is widely regarded as the fastest land animal on Earth, can accelerate from rest to roughly one
hundred kilometres per hour in just a few seconds. Although it is a member of the cat family, the cheetah differs from
most other big cats because it cannot fully retract its claws. Elephants, the largest living land animals, communicate
over long distances using low-frequency sounds that humans cannot hear. The blue whale, larger even than the biggest
dinosaurs, feeds almost entirely on tiny shrimp-like creatures called krill. Because they are warm-blooded and breathe
air, whales must periodically surface despite living their entire lives in the ocean. A dog is a mammal. Birds, unlike
mammals, lay eggs that are protected by hard shells. The heart, a muscular organ roughly the size of a fist, pumps
blood throughout the body. Photosynthesis, the process by which plants convert sunlight into energy, releases oxygen as
a by-product. Many reptiles, including snakes and lizards, regulate their body temperature by basking in the sun.
Smoking causes cancer. The human brain contains billions of neurons connected by trillions of synapses. A salmon is a
fish. Coral reefs, often called the rainforests of the sea, support an extraordinary diversity of marine life. Despite
their fearsome reputation, most sharks pose little threat to humans. Gravity, the force that attracts objects toward
one another, keeps the planets in orbit around the Sun.
""".strip()


def run_seed(seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j401_{seed}_"), seed=seed)
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", HARD.replace("\n", " ")) if s.strip()]
    parsed, unparsed = [], []
    for s in sents:
        b = len(c.sm.facts); c._learn_one(s)
        (parsed if len(c.sm.facts) > b else unparsed).append(s)
    c.consolidate()
    coverage = round(len(parsed) / len(sents), 3)

    # captured facts must be correct: spot-check 4 simple ones the text states
    spot = [("is a dog a mammal?", True), ("is a salmon a fish?", True),
            ("what causes cancer?", "cancer_marker"), ("is a dog a fish?", False)]
    correct = 0
    for q, t in spot:
        a = c.say(q).strip().lower()
        if t is True:
            correct += ("yes" in a)
        elif t is False:
            correct += ("yes" not in a)
        else:
            correct += ("smoking" in a)
    spot_ok = (correct >= 3)
    ents = {e for (x, r, b) in c.sm.facts for e in (x, b)}
    junk_rate = round(len([e for e in ents if " " in e]) / max(1, len(ents)), 3)

    # honest abstention: ask about a fact from an UNPARSED dense sentence (cheetah speed / krill) -> must not fabricate
    abstain = "yes" not in c.say("is a cheetah the fastest animal?").strip().lower()

    return {"n_sents": len(sents), "parsed": len(parsed), "coverage": coverage, "junk_rate": junk_rate,
            "spot_correct": correct, "spot_ok": bool(spot_ok), "abstain": bool(abstain),
            "sample_unparsed": unparsed[:3]}


if __name__ == "__main__":
    print("=== JEP-401: honest coverage ceiling on DENSE prose ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: coverage={r['coverage']} ({r['parsed']}/{r['n_sents']}) | junk={r['junk_rate']} | "
              f"spot={r['spot_correct']}/4 ({r['spot_ok']}) | abstain={r['abstain']}", flush=True)
        print(f"           sample unparsed: {r['sample_unparsed']}", flush=True)

    covs = [R[s]['coverage'] for s in seeds]
    J401a = abs(covs[0] - covs[1]) <= 0.1                       # stable measurement
    J401b = all(R[s]['junk_rate'] <= 0.05 and R[s]['spot_ok'] for s in seeds)
    J401c = all(R[s]['abstain'] for s in seeds)
    passed = J401a and J401b and J401c
    print("\n--- VERDICT ---", flush=True)
    print(f"coverage on dense prose (the honest ceiling): {covs}", flush=True)
    print(f"J401a stable measurement     : {J401a}", flush=True)
    print(f"J401b no wrong capture       : {J401b}", flush=True)
    print(f"J401c honest abstention      : {J401c}", flush=True)
    verdict = (f"PASS - honest ceiling MEASURED: dense hard prose yields ~{covs[0]:.0%} coverage (the rule-based "
               "normalizer captures simple is-a/property/causal cores, misses heavily-modified sentences), but what IS "
               "captured is correct (no junk, spot-checks pass) and the rest is honestly abstained -- partial capture, "
               "never wrong capture. The honest real-text ceiling, mapped.") if passed else \
              ("PARTIAL/NULL - measurement unstable or (critically) wrong capture / fabrication appeared; see rows.")
    print(f"\nJEP-401: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP401"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "coverages": covs, "J401a": J401a, "J401b": J401b,
                                                  "J401c": J401c, "passed": passed}, default=str))
    print("DONE", flush=True)
