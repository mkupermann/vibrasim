"""JEP-29 - scale the concept reasoner to a REAL WordNet subtree (carnivore, 366 concepts); held-out IS-A."""
import numpy as np
from nltk.corpus import wordnet as wn
from tools.concept_reasoner import ConceptReasoner


def build_tax(root_name):
    root = wn.synset(root_name)
    seen = set()

    def closure(s):
        seen.add(s)
        for h in s.hyponyms():
            if h not in seen:
                closure(h)
    closure(root)
    # parent = the hypernym that is inside the subtree (primary path); build parent->children
    tax = {}
    for s in seen:
        for c in s.hyponyms():
            if c in seen:
                tax.setdefault(s.name(), []).append(c.name())
    return tax, root.name()


def main():
    print("=== JEP-29: concept reasoner on REAL WordNet carnivore subtree ===", flush=True)
    TAX, root = build_tax("carnivore.n.01")
    cr = ConceptReasoner(TAX)
    print(f"  concepts={cr.N}, root={root}", flush=True)
    ALL = [(u, v) for v in range(cr.N) for u in cr._ancestors(v)]
    print(f"  ancestor pairs={len(ALL)}", flush=True)
    rng = np.random.default_rng(1); idx = rng.permutation(len(ALL)); cut = int(0.3 * len(ALL))
    holdout = set(ALL[i] for i in idx[:cut])
    cr.fit(euc_dim=4, hyp_dim=10, iters=4000, holdout_pairs=holdout)
    ok = sum(int(cr.hnorm[u] < cr.hnorm[v]) for (u, v) in holdout) / len(holdout)
    tr = sum(int(cr.hnorm[u] < cr.hnorm[v]) for (u, v) in (ALL[i] for i in idx[cut:])) / (len(ALL) - cut)
    print(f"  trained IS-A direction acc  = {tr:.3f}", flush=True)
    print(f"  HELD-OUT IS-A direction acc = {ok:.3f}  (random 0.5)", flush=True)
    # sanity with real synsets
    def sid(name):
        return name if name in cr.ID else None
    pairs = [("dog.n.01", "carnivore.n.01"), ("domestic_cat.n.01", "feline.n.01"),
             ("carnivore.n.01", "dog.n.01"), ("wolf.n.01", "canine.n.02")]
    print("  sanity (real synsets):", flush=True)
    sane = []
    for a, b in pairs:
        if sid(a) and sid(b):
            r = cr.is_a(a, b); print(f"    is_a({a},{b}) = {r}", flush=True); sane.append((a, b, r))
    # expected: dog is-a carnivore True; cat is-a feline True; carnivore is-a dog False; wolf is-a canine True
    exp = {("dog.n.01", "carnivore.n.01"): True, ("domestic_cat.n.01", "feline.n.01"): True,
           ("carnivore.n.01", "dog.n.01"): False, ("wolf.n.01", "canine.n.02"): True}
    sane_ok = all(r == exp[(a, b)] for a, b, r in sane) if sane else False
    print(f"    nearest(dog.n.01) = {cr.nearest('dog.n.01') if sid('dog.n.01') else 'n/a'}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if ok >= 0.85 and sane_ok:
        print(f"JEP-29: PASS - the concept reasoner SCALES to a REAL {cr.N}-concept WordNet taxonomy: held-out IS-A", flush=True)
        print(f"direction accuracy {ok:.2f} on real hypernym relations never trained on, and sanity queries correct", flush=True)
        print(f"on real synsets (dog is-a carnivore, etc). The mixed-curvature reasoning result holds at ~5x scale on", flush=True)
        print(f"REAL data, not just the curated toy. Nickel-Kiela (2017) established - named as such.", flush=True)
    else:
        print(f"JEP-29: PARTIAL/NULL - held-out {ok:.2f}, sanity_ok {sane_ok}", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
