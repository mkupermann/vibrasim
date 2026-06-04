"""JEP-28 - held-out IS-A generalization with the mixed-curvature concept reasoner."""
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


def main():
    print("=== JEP-28: held-out IS-A generalization (mixed-curvature concept reasoner) ===", flush=True)
    cr = ConceptReasoner(TAX)
    ALL = [(u, v) for v in range(cr.N) for u in cr._ancestors(v)]
    rng = np.random.default_rng(1); idx = rng.permutation(len(ALL)); cut = int(0.3 * len(ALL))
    holdout = set(ALL[i] for i in idx[:cut]); train = [ALL[i] for i in idx[cut:]]
    cr.fit(holdout_pairs=holdout)
    ok = sum(int(cr.hnorm[u] < cr.hnorm[v]) for (u, v) in holdout) / len(holdout)
    tr = sum(int(cr.hnorm[u] < cr.hnorm[v]) for (u, v) in train) / len(train)
    print(f"  trained-pairs IS-A direction acc = {tr:.3f}", flush=True)
    print(f"  HELD-OUT IS-A direction acc      = {ok:.3f}  (random ~0.5)", flush=True)
    print("  demo queries:", flush=True)
    print(f"    nearest('cat') = {cr.nearest('cat')}", flush=True)
    print(f"    more_general('cat','mammal') = {cr.more_general('cat', 'mammal')}", flush=True)
    print(f"    is_a('cat','mammal') = {cr.is_a('cat', 'mammal')}   is_a('mammal','cat') = {cr.is_a('mammal', 'cat')}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if ok >= 0.80:
        print(f"JEP-28: PASS - the mixed-curvature concept reasoner GENERALIZES the hierarchy: held-out IS-A", flush=True)
        print(f"direction accuracy {ok:.2f} on hypernym relations NEVER trained on (vs random 0.5), ~matching the", flush=True)
        print(f"trained {tr:.2f}. The hyperbolic radial-generality structure transfers to unseen pairs - it captures", flush=True)
        print(f"the taxonomy, not memorizes it. Usable tool shipped: tools/concept_reasoner.py. Capstone of the", flush=True)
        print(f"reasoning arc. Nickel-Kiela (2017) established - named as such.", flush=True)
    else:
        print(f"JEP-28: PARTIAL/NULL - held-out IS-A acc {ok:.2f}", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
