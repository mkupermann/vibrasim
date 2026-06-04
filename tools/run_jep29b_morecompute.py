"""JEP-29b - does more compute (more dims + iters) recover concept-reasoner scaling on WordNet carnivore (366)?"""
import numpy as np
from nltk.corpus import wordnet as wn
from tools.concept_reasoner import ConceptReasoner


def build_tax(root_name):
    root = wn.synset(root_name); seen = set()

    def closure(s):
        seen.add(s)
        for h in s.hyponyms():
            if h not in seen:
                closure(h)
    closure(root)
    tax = {}
    for s in seen:
        for c in s.hyponyms():
            if c in seen:
                tax.setdefault(s.name(), []).append(c.name())
    return tax


def main():
    print("=== JEP-29b: more compute on WordNet carnivore (366 concepts) ===", flush=True)
    TAX = build_tax("carnivore.n.01")
    cr = ConceptReasoner(TAX)
    ALL = [(u, v) for v in range(cr.N) for u in cr._ancestors(v)]
    rng = np.random.default_rng(1); idx = rng.permutation(len(ALL)); cut = int(0.3 * len(ALL))
    holdout = set(ALL[i] for i in idx[:cut])
    # more dims + more iters
    cr.fit(euc_dim=8, hyp_dim=20, iters=12000, holdout_pairs=holdout)
    ok = sum(int(cr.hnorm[u] < cr.hnorm[v]) for (u, v) in holdout) / len(holdout)
    # relatedness sanity: nearest of dog should be other canines, not alphabetical
    near = cr.nearest("dog.n.01", k=6)
    print(f"  held-out IS-A direction acc = {ok:.3f}  (was 0.68 at 10D/4000 iters)", flush=True)
    print(f"  nearest(dog.n.01) = {near}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if ok >= 0.85:
        print(f"JEP-29b: PASS - more compute (20D, 12000 iters) RECOVERS scaling: held-out IS-A {ok:.2f} on 366 real", flush=True)
        print(f"concepts. The JEP-29 failure was UNDER-TRAINING, not a fundamental limit - the reasoning result holds", flush=True)
        print(f"at real scale given adequate embedding dim + iterations. Nickel-Kiela (2017) established - named.", flush=True)
    else:
        print(f"JEP-29b: NULL - even with 20D/12000 iters, held-out IS-A only {ok:.2f}. The simple norm-direction", flush=True)
        print(f"readout + ranking loss has a real scaling cost on deep real taxonomies; proper reconstruction (MAP/", flush=True)
        print(f"mean-rank with the Nickel-Kiela is-a score) and larger budgets are needed. Honest scaling limit.", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
