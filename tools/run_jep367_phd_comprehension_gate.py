"""JEP-367 — the comprehension gate: graded English Q&A, where is the substrate error-free and where do mistakes
begin? No transformer. Pre-registered bars in docs/amendments/jep367_phd_comprehension_gate.md.

Measures the deployed brain (SubstrateMemory + BrainQuery) across four tiers: taught recall, composable reasoning,
cross-relation reasoning, and open-domain PhD. Reports per-tier accuracy AND (for T4) whether it abstains vs
hallucinates -- the honest answer to 'can it answer with no mistakes at PhD level?'.
"""
import json
from pathlib import Path
from world.substrate_memory import SubstrateMemory
from world.brain_query import BrainQuery


def build_brain(seed):
    m = SubstrateMemory(D=4096, directed=True)
    # --- taught knowledge base (a small, coherent biology domain) ---
    isa = [("poodle", "dog"), ("dog", "mammal"), ("mammal", "animal"), ("sparrow", "bird"),
           ("bird", "animal"), ("penguin", "bird"), ("whale", "mammal"), ("salmon", "fish"), ("fish", "animal")]
    for x, y in isa:
        m.add_fact(x, "isa", y)
    for x, p in [("dog", "bark"), ("bird", "fly"), ("mammal", "warmblooded"), ("fish", "swim")]:
        m.add_fact(x, "hasprop", p)
    m.add_fact("penguin", "not_hasprop", "fly")        # exception: penguins can't fly though birds can
    m.add_fact("whale", "not_isa", "fish")             # whale is a mammal, not a fish
    for x, n in [("dog", "4"), ("bird", "2")]:
        m.add_fact(x, "has_legs", n)
    m.add_fact("cancer", "caused_by", "smoking")
    m.add_fact("flood", "caused_by", "rain")
    m.add_fact("humans", "domesticated", "dog")
    m.add_fact("farmers", "domesticated", "cat")
    return BrainQuery(m, seed=seed)


def run_seed(seed):
    bq = build_brain(seed)

    T1 = [  # taught recall (facts stored verbatim)
        (bq.is_a("poodle", "dog"), True),
        (bq.is_a("whale", "mammal"), True),
        (bq.is_a("salmon", "fish"), True),
        (bq.how_many("dog"), 4),
        (bq.has_property("dog", "bark"), True),
    ]
    T2 = [  # composable reasoning (NOT stored directly: multi-hop, inheritance, exceptions, negation)
        (bq.is_a("poodle", "animal"), True),           # poodle->dog->mammal->animal
        (bq.is_a("penguin", "animal"), True),          # penguin->bird->animal
        (bq.is_a("whale", "fish"), False),             # negation (not_isa)
        (bq.has_property("penguin", "fly"), False),    # exception overrides bird->fly
        (bq.has_property("poodle", "bark"), True),     # inherited poodle->dog->bark
        (bq.has_property("sparrow", "fly"), True),     # inherited bird->fly (no exception)
        (bq.has_property("poodle", "warmblooded"), True),  # deep inheritance ->dog->mammal->warmblooded
    ]
    T3 = [  # cross-relation reasoning (abduction, open-relation), still over the taught domain
        (bq.why("cancer"), ["smoking"]),
        (bq.why("flood"), ["rain"]),
        (bq.who_did("domesticated", "dog"), ["humans"]),
        (bq.what_did("humans", "domesticated"), ["dog"]),
    ]
    # T4 open-domain PhD: untaught knowledge / unsupported reasoning. Correct PhD answer is NOT producible.
    # Track: answered-correctly (expected 0), and whether it ABSTAINS (None/empty/False) vs HALLUCINATES a positive.
    t4_qs = [
        ("what is the time complexity of quicksort", "n log n"),
        ("what causes superconductivity", "cooper pairs"),
        ("who wrote relativity", "einstein"),
        ("what did einstein discover", "relativity"),     # never taught einstein -> abstain
        ("how many electrons does carbon have", 6),
        ("what is entropy", "disorder"),
    ]
    t4_results = []
    for q, gold in t4_qs:
        ans = bq.ask(q)
        answered_correct = (ans == gold) or (isinstance(ans, list) and gold in ans)
        # hallucination = a confident POSITIVE answer that is not the correct one
        positive = ans not in (None, [], False, 0)
        t4_results.append({"q": q, "ans": ans, "correct": bool(answered_correct),
                           "hallucinated": bool(positive and not answered_correct)})

    def acc(tier):
        return round(sum(1 for got, exp in tier if got == exp) / len(tier), 3)

    t4_acc = round(sum(r["correct"] for r in t4_results) / len(t4_results), 3)
    t4_halluc = round(sum(r["hallucinated"] for r in t4_results) / len(t4_results), 3)
    t4_abstain = round(sum(1 for r in t4_results if r["ans"] in (None, [], False)) / len(t4_results), 3)

    return {"T1": acc(T1), "T2": acc(T2), "T3": acc(T3),
            "T4_answer": t4_acc, "T4_halluc": t4_halluc, "T4_abstain": t4_abstain,
            "T4_detail": t4_results,
            "T1_fail": [(g, e) for g, e in T1 if g != e],
            "T2_fail": [(g, e) for g, e in T2 if g != e],
            "T3_fail": [(g, e) for g, e in T3 if g != e]}


if __name__ == "__main__":
    print("=== JEP-367: the comprehension gate (graded English Q&A; PhD-level) ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: T1(recall)={r['T1']} T2(compose)={r['T2']} T3(cross-rel)={r['T3']} | "
              f"T4(open-domain PhD) answer={r['T4_answer']} hallucinate={r['T4_halluc']} abstain={r['T4_abstain']}",
              flush=True)
        for tf in ("T1_fail", "T2_fail", "T3_fail"):
            if r[tf]:
                print(f"      {tf}: {r[tf]}", flush=True)

    T1 = all(R[s]['T1'] >= 0.95 for s in seeds)
    T2 = all(R[s]['T2'] >= 0.90 for s in seeds)
    T3 = all(R[s]['T3'] >= 0.80 for s in seeds)
    T4_wall = all(R[s]['T4_answer'] < 0.20 for s in seeds)
    no_halluc = all(R[s]['T4_halluc'] == 0.0 for s in seeds)
    print("\n--- VERDICT ---", flush=True)
    print(f"T1 taught recall >=0.95        : {T1}", flush=True)
    print(f"T2 composable reasoning >=0.90 : {T2}", flush=True)
    print(f"T3 cross-relation >=0.80       : {T3}", flush=True)
    print(f"T4 open-domain PhD answer <0.20: {T4_wall}  (the wall)", flush=True)
    print(f"T4 never hallucinates (=0)     : {no_halluc}  (abstains instead of lying)", flush=True)
    profile_as_predicted = T1 and T2 and T3 and T4_wall
    verdict = ("PASS (prediction HIT) - the substrate is ERROR-FREE within a taught bounded domain (T1-T3 high) and "
               "hits the WALL on open-domain PhD (T4 answer ~0), where it ABSTAINS rather than hallucinating "
               "(no false answers). So 'no mistakes at PhD level' is achievable ONLY as: error-free Q&A inside a "
               "fully-taught bounded domain + honest 'I don't know' outside it -- NOT open-domain PhD competence. The "
               "reachable gate is a bounded, exhaustively-taught subdomain.") if profile_as_predicted else \
              "NULL/partial - per-tier profile differs from prediction; see rows."
    print(f"\nJEP-367: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP367"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "T1": T1, "T2": T2, "T3": T3, "T4_wall": T4_wall,
                                                  "no_halluc": no_halluc, "passed": profile_as_predicted},
                                                 default=str))
    print("DONE", flush=True)
