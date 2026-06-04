"""JEP-30 - compositional query: lowest-common-ancestor ("what includes both X and Y") from the hyperbolic embedding."""
import numpy as np, torch
from tools.concept_reasoner import ConceptReasoner, _poin_dc

TAX = {
 "living_thing": ["animal", "plant"], "animal": ["vertebrate", "invertebrate"],
 "vertebrate": ["mammal", "bird", "reptile", "fish"], "mammal": ["carnivore", "primate", "rodent", "ungulate"],
 "carnivore": ["feline", "canine"], "feline": ["cat", "lion", "tiger"], "canine": ["dog", "wolf", "fox"],
 "primate": ["human", "chimp", "gorilla"], "rodent": ["mouse", "rat", "squirrel"], "ungulate": ["horse", "cow", "deer"],
 "bird": ["raptor", "waterfowl", "songbird"], "raptor": ["eagle", "hawk", "owl"], "waterfowl": ["duck", "goose", "swan"],
 "songbird": ["sparrow", "robin", "finch"], "reptile": ["snake", "lizard", "turtle", "crocodile"],
 "fish": ["salmon", "shark", "tuna", "trout"], "invertebrate": ["insect", "arachnid", "mollusk"],
 "insect": ["ant", "bee", "butterfly", "beetle"], "arachnid": ["spider", "scorpion", "tick"], "mollusk": ["snail", "octopus", "clam"],
 "plant": ["tree", "flower", "grass"], "tree": ["oak", "pine", "maple", "birch"], "flower": ["rose", "tulip", "daisy", "lily"], "grass": ["wheat", "corn", "bamboo"],
}


def true_lca(cr, a, b):
    aa = [cr.ID[a]] + cr._ancestors(cr.ID[a]); bb = set([cr.ID[b]] + cr._ancestors(cr.ID[b]))
    for x in aa:  # aa is ordered self->root; first in bb is the deepest common ancestor
        if x in bb:
            return x
    return None


def main():
    print("=== JEP-30: compositional LCA query from hyperbolic embedding (77-concept toy) ===", flush=True)
    cr = ConceptReasoner(TAX); cr.fit(euc_dim=4, hyp_dim=10, iters=5000)
    X = cr.Xh; nm = cr.hnorm
    # geometric LCA readout: among nodes more general than BOTH (smaller norm), pick the one minimizing
    # total hyperbolic distance to A and B (deepest common ancestor = closest general node to both)
    def pred_lca(ia, ib):
        cap = min(nm[ia], nm[ib])
        cands = [c for c in range(cr.N) if nm[c] <= cap + 1e-9]
        if not cands:
            return None
        dists = [(float(_poin_dc(X[c:c + 1], X[ia:ia + 1]) + _poin_dc(X[c:c + 1], X[ib:ib + 1])), c) for c in cands]
        return min(dists)[1]
    rng = np.random.default_rng(0)
    exact = 0; common_anc = 0; tot = 0
    examples = []
    for _ in range(400):
        ia, ib = rng.integers(cr.N), rng.integers(cr.N)
        if ia == ib:
            continue
        a, b = cr.nodes[ia], cr.nodes[ib]
        tl = true_lca(cr, a, b); pl = pred_lca(ia, ib)
        if tl is None or pl is None:
            continue
        tot += 1
        exact += int(pl == tl)
        # is predicted a common ancestor of both?
        anc_a = set([ia] + cr._ancestors(ia)); anc_b = set([ib] + cr._ancestors(ib))
        common_anc += int(pl in anc_a and pl in anc_b)
        if len(examples) < 5:
            examples.append((a, b, cr.nodes[tl], cr.nodes[pl]))
    print(f"  pairs tested: {tot}", flush=True)
    print(f"  exact-LCA accuracy        = {exact / tot:.3f}", flush=True)
    print(f"  predicted-is-common-ancestor = {common_anc / tot:.3f}", flush=True)
    print("  examples (A, B -> true LCA / predicted):", flush=True)
    for a, b, t, p in examples:
        print(f"    {a}, {b} -> {t} / {p}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    ea = exact / tot; ca = common_anc / tot
    if ea >= 0.6 and ca >= 0.85:
        print(f"JEP-30: PASS - the hyperbolic embedding supports COMPOSITIONAL category queries: lowest-common-", flush=True)
        print(f"ancestor read geometrically (closest more-general node to both) matches the true LCA {ea:.2f} of the", flush=True)
        print(f"time and is a valid common ancestor {ca:.2f} of the time - 'what category includes both X and Y' from", flush=True)
        print(f"geometry, combining two concepts. A step beyond pairwise IS-A toward compositional reasoning. SR/", flush=True)
        print(f"hyperbolic (Stachenfeld 2017; Nickel-Kiela 2017) established - named as such.", flush=True)
    else:
        print(f"JEP-30: PARTIAL/NULL - exact-LCA {ea:.2f}, common-ancestor {ca:.2f}", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
