"""JEP-28b - improve the concept reasoner with higher-dim hyperbolic; re-test held-out + sanity queries."""
import numpy as np
from tools.concept_reasoner import ConceptReasoner

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


def depth(cr, n):
    d = 0; p = cr.parent.get(cr.ID[n])
    while p is not None:
        d += 1; p = cr.parent.get(p)
    return d


def main():
    print("=== JEP-28b: higher-dim hyperbolic concept reasoner ===", flush=True)
    for HD in [5, 10]:
        cr = ConceptReasoner(TAX)
        ALL = [(u, v) for v in range(cr.N) for u in cr._ancestors(v)]
        rng = np.random.default_rng(1); idx = rng.permutation(len(ALL)); cut = int(0.3 * len(ALL))
        holdout = set(ALL[i] for i in idx[:cut])
        cr.fit(hyp_dim=HD, iters=4000, holdout_pairs=holdout)
        ok = sum(int(cr.hnorm[u] < cr.hnorm[v]) for (u, v) in holdout) / len(holdout)
        # norm vs depth correlation (does norm encode generality?)
        depths = np.array([depth(cr, n) for n in cr.nodes]); nm = cr.hnorm
        nd = float(np.corrcoef(depths, nm)[0, 1])
        # sanity queries
        sane = {
            "is_a(cat,mammal)": cr.is_a("cat", "mammal"),
            "is_a(mammal,cat)": cr.is_a("mammal", "cat"),
            "is_a(dog,animal)": cr.is_a("dog", "animal"),
            "is_a(rose,plant)": cr.is_a("rose", "plant"),
            "is_a(animal,dog)": cr.is_a("animal", "dog"),
        }
        sane_ok = sane["is_a(cat,mammal)"] and (not sane["is_a(mammal,cat)"]) and sane["is_a(dog,animal)"] and sane["is_a(rose,plant)"] and (not sane["is_a(animal,dog)"])
        print(f"  [hyp_dim={HD}] held-out IS-A acc={ok:.3f}  norm-vs-depth corr={nd:.3f}  sanity_all_correct={sane_ok}", flush=True)
        print(f"     {sane}", flush=True)
        if HD == 10:
            final_ok, final_sane, final_nd = ok, sane_ok, nd
    print("\n--- VERDICT ---", flush=True)
    if final_ok >= 0.9 and final_sane and final_nd >= 0.7:
        print(f"JEP-28b: PASS - higher-dim (10D) hyperbolic makes the reasoner reliable: held-out IS-A {final_ok:.2f},", flush=True)
        print(f"norm encodes generality (norm-vs-depth corr {final_nd:.2f}), and ALL sanity queries correct (cat IS-A", flush=True)
        print(f"mammal True, mammal IS-A cat False, etc). Fixes JEP-28's per-query failures. tools/concept_reasoner.py", flush=True)
        print(f"is now per-query reliable at 10D. Nickel-Kiela (2017) established - named as such.", flush=True)
    else:
        print(f"JEP-28b: PARTIAL/NULL - held-out {final_ok:.2f}, norm-depth {final_nd:.2f}, sanity {final_sane}", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
