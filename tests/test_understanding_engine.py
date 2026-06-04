"""Regression test: the UnderstandingEngine must stay 100% on its target domain (JEP-92)."""
import numpy as np
from world.understanding import UnderstandingEngine

def _engine():
    eng = UnderstandingEngine(seed=92)
    for f in ["A poodle is a dog.","A collie is a dog.","A dog is an animal.","A cat is an animal.",
              "An animal is a living_thing.","A salmon is a fish.","A fish is an animal.",
              "the dog chases the cat.","the cat eats the mouse.","the salmon swims in the water."]:
        assert eng.tell(f)[0] != "none", f"failed to parse: {f}"
    rng = np.random.default_rng(920)
    for c in ["poodle","collie","dog","cat","mouse","salmon","fish","animal","living_thing","water"]:
        eng.add_prototype(c, rng.normal(0, 1, eng.feat_dim))
    return eng

def test_isa_multihop_and_negatives():
    e = _engine()
    assert e.is_a("poodle","animal") and e.is_a("poodle","living_thing")
    assert e.is_a("salmon","living_thing")
    assert not e.is_a("poodle","fish") and not e.is_a("dog","poodle")

def test_relational_same_bag_truth():
    e = _engine()
    assert e.relation_true("dog","chases","cat")
    assert not e.relation_true("cat","chases","dog")     # same bag, swapped roles
    assert not e.relation_true("dog","eats","cat")       # 2/3-role overlap must NOT pass

def test_verb_agreement_question():
    e = _engine()
    assert e.ask("does the dog chase the cat?") is True   # interrogative 'chase' vs stored 'chases'
    assert e.ask("does the cat chase the dog?") is False
    assert e.ask("is a poodle an animal?") is True        # article 'an' must not lose a letter

def test_grounding_recognition():
    e = _engine()
    rng = np.random.default_rng(7)
    ok = [e.perceive(e.prototypes[c] + rng.normal(0, 0.6, e.feat_dim)) == c
          for c in e.prototypes for _ in range(20)]
    assert np.mean(ok) >= 0.95


def test_boolean_composition():
    e = _engine()
    assert e.ask_bool("is a poodle an animal and is a poodle not a fish") is True
    assert e.ask_bool("is a poodle a fish and is a poodle an animal") is False
    assert e.ask_bool("is a poodle a fish or is a poodle an animal") is True
    assert e.ask_bool("does the dog not chase the cat") is False
    assert e.ask_bool("is a poodle not a fish") is True


def test_parse_robustness_varied_phrasings():
    e = UnderstandingEngine(seed=94)
    for v in ["Poodles are dogs.", "A dog is an animal.", "Dogs are animals.",
              "An animal is a living_thing.", "Every poodle is a dog.", "Dogs are a type of animal."]:
        assert e.tell(v)[0] == "isa", f"failed: {v}"
    assert "animal" in e.parents.get("dog", set())      # not "nimal" — article must not eat the noun
    assert "living thing" in e.parents.get("animal", set())
    assert e.is_a("poodle", "living_thing")      # multi-hop across varied phrasings


def test_communication_explains_in_english():
    e = _engine()
    assert e.explain("is a poodle a living_thing?") == \
        "Yes. A poodle is a dog, a dog is an animal, an animal is a living thing."
    assert e.explain("is a poodle a fish?").startswith("No.")
    assert e.explain("does the dog chase the cat?") == "Yes, the dog chases the cat."
    assert e.explain("does the cat chase the dog?").startswith("No,")


def test_learning_by_correction():
    e = UnderstandingEngine(seed=96)
    e.tell("A fish is an animal."); e.tell("A mammal is an animal.")
    e.tell("A whale is a fish.")
    assert e.is_a("whale", "fish")
    assert e.tell("A whale is not a fish.")[0] == "neg_isa"
    e.tell("A whale is a mammal.")
    assert not e.is_a("whale", "fish")          # belief retracted
    assert e.is_a("whale", "mammal") and e.is_a("whale", "animal")
    assert e.explain("is a whale an animal?").startswith("Yes. A whale is a mammal")


def test_learn_concept_from_examples():
    import numpy as np
    rng = np.random.default_rng(97)
    e = UnderstandingEngine(seed=97)
    for c in ["dog", "fish", "animal"]:
        e.add_prototype(c, rng.normal(0, 1, e.feat_dim))
    e.tell("A dog is an animal."); e.tell("A fish is an animal.")
    true_bird = rng.normal(0, 1, e.feat_dim)
    e.learn_concept("bird", [true_bird + rng.normal(0, 0.6, e.feat_dim) for _ in range(5)])
    e.tell("A bird is an animal.")
    seen = e.perceive(true_bird + rng.normal(0, 0.6, e.feat_dim))
    assert seen == "bird" and e.is_a(seen, "animal")


def test_multiword_concepts():
    e = UnderstandingEngine(seed=1)
    e.tell("A poodle is a dog."); e.tell("A dog is an animal."); e.tell("An animal is a living thing.")
    assert e.is_a("poodle", "living thing")           # multi-word category, 3-hop
    assert e.explain("is a poodle a living thing?") == \
        "Yes. A poodle is a dog, a dog is an animal, an animal is a living thing."
    assert e.is_a("poodle", "living_thing")           # underscore form still works (regression)


def test_natural_input_adjectival_and_plural():
    e = UnderstandingEngine(seed=99)
    assert e.tell("A big dog is an animal.")[0] == "isa"      # adjectival/multi-word subject
    assert e.is_a("big dog", "animal")
    assert e.ask("is a big dog an animal?") is True           # multi-word subject in the QUESTION too
    assert e.tell("Poodles chase cats.")[0] == "rel"          # plural SVO, no "the"
    assert e.relation_true("poodle", "chase", "cat")


def test_wh_questions():
    e = _engine()
    assert e.respond("what is a poodle?") == "A poodle is a dog."
    assert e.respond("what does the dog chase?") == "The dog chases the cat."
    assert e.respond("what is a unicorn?") == "I don't know what a unicorn is."   # 'a', not 'an'
    assert e.respond("what does the cat chase?").startswith("I don't know")


def test_three_valued_epistemic():
    e = UnderstandingEngine(seed=101)
    for f in ["A poodle is a dog.", "A dog is an animal.", "A salmon is a fish.", "A whale is not a fish."]:
        e.tell(f)
    assert e.assess("poodle", "animal") == "yes"
    assert e.assess("poodle", "fish") == "no"           # fish known, no path
    assert e.assess("whale", "fish") == "no"            # explicit negative
    assert e.assess("poodle", "vegetable") == "unknown" # never heard of
    assert e.explain("is a poodle a vegetable?").startswith("I don't know")


def test_learning_through_dialogue():
    e = UnderstandingEngine(seed=102)
    e.tell("A poodle is a dog."); e.tell("A dog is an animal.")   # animal->living thing NOT known
    assert e.assess("poodle", "living thing") == "unknown"
    assert e.inquire("poodle", "living thing") == \
        "I know a poodle is an animal, but I don't know whether an animal is a living thing."
    e.tell("An animal is a living thing.")                         # taught the identified gap
    assert e.assess("poodle", "living thing") == "yes"
    assert e.inquire("poodle", "living thing") is None
    assert e.explain("is a poodle a living thing?") == \
        "Yes. A poodle is a dog, a dog is an animal, an animal is a living thing."


def test_conjunction_and_pronoun_rejection():
    e = UnderstandingEngine(seed=103)
    e.tell("A bird is an animal.")
    e.tell("Robins and sparrows are birds.")          # conjoined subjects -> two facts
    assert e.is_a("robin", "bird") and e.is_a("sparrow", "bird")
    assert e.is_a("robin", "animal")                  # multi-hop through the split fact
    # pronoun with NO antecedent is rejected (fresh engine, no prior subject)
    e2 = UnderstandingEngine(seed=200)
    assert e2.tell("It is an animal.")[0] == "none"
    assert "it" not in e2.parents


def test_pronoun_coreference_with_antecedent():
    e = UnderstandingEngine(seed=107)
    e.tell("A robin is a bird.")
    assert e.tell("It is an animal.") == ("isa", "robin", "animal")   # it -> robin (recency)
    e.tell("An animal is a living thing.")
    assert e.is_a("robin", "living thing")


def test_multi_parent_dag():
    e = UnderstandingEngine(seed=104)
    e.tell("A poodle is a dog."); e.tell("A poodle is a pet.")
    e.tell("A dog is an animal."); e.tell("A pet is owned.")
    assert e.parents.get("poodle") == {"dog", "pet"}      # two parents kept (no overwrite)
    assert e.is_a("poodle", "dog") and e.is_a("poodle", "pet")
    assert e.is_a("poodle", "animal") and e.is_a("poodle", "owned")  # both lineages
    assert e.respond("what is a poodle?") == "A poodle is a dog and a pet."


def test_inductive_generalization_defeasible():
    e = UnderstandingEngine(seed=105)
    for f in ["A robin is a bird.", "A sparrow is a bird.", "An eagle is a bird.",
              "A penguin is a bird.", "A wren is a bird.",
              "A robin can fly.", "A sparrow can fly.", "An eagle can fly.", "A penguin cannot fly."]:
        e.tell(f)
    e.induce()
    assert "fly" in e._induced.get("bird", set())
    assert e.has_property("wren", "fly")        # induced, never observed
    assert not e.has_property("penguin", "fly") # explicit exception overrides (defeasible)
    assert not e.has_property("robin", "swim")  # not induced


def test_respond_routes_boolean():
    e = _engine()
    assert e.respond("is a poodle an animal and is a poodle a dog?") == "Yes."
    assert e.respond("is a poodle a fish and is a poodle a dog?") == "No."


def test_concept_validity_guard_rejects_complex_prose():
    e = UnderstandingEngine(seed=108)
    # a long clausal sentence must be REJECTED, not parsed into a clause-as-concept
    assert e.tell("The design of the following treatise is to investigate the fundamental laws of reasoning.")[0] == "none"
    # a simple definitional sentence still parses
    assert e.tell("A poodle is a dog.")[0] == "isa"
    assert e.is_a("poodle", "dog")


def test_contradiction_detection():
    e = UnderstandingEngine(seed=109)
    e.tell("A whale is a mammal."); e.tell("A mammal is an animal.")
    assert e.would_contradict("A whale is not an animal.") is not None   # via closure
    assert e.would_contradict("A whale is a fish.") is None              # unknown, no conflict
    e.tell("A whale is not a fish.")
    assert e.would_contradict("A whale is a fish.") is not None          # explicit negative
    e.tell("A whale is a fish.")                                         # correction still works (non-blocking)
    assert e.is_a("whale", "fish")


def test_quantified_questions():
    e = UnderstandingEngine(seed=110)
    for f in ["A poodle is a dog.", "A dog is an animal.", "A robin is a bird.", "A penguin is a bird.",
              "A robin can fly.", "A sparrow is a bird.", "A sparrow can fly.", "A penguin cannot fly."]:
        e.tell(f)
    e.induce()
    assert e.respond("is every poodle an animal?") == "Yes."   # multi-hop universal
    assert e.respond("can all birds fly?").startswith("No")    # penguin counterexample
    assert e.respond("do all robins fly?").startswith("Yes")


def test_why_followup():
    e = _engine()
    e.respond("is a poodle a living_thing?")
    assert e.respond("why?").startswith("Because a poodle is a dog")
    e.respond("is a poodle a vegetable?")
    assert e.respond("why?").startswith("Because I was never told")


def test_transitive_comparison():
    e = UnderstandingEngine(seed=112)
    for f in ["An elephant is bigger than a dog.", "A dog is bigger than a cat.", "A cat is bigger than a mouse."]:
        assert e.tell(f)[0] == "order"
    assert e.respond("is an elephant bigger than a mouse?") == "Yes."   # 3-hop transitive
    assert e.respond("is a mouse bigger than a dog?").startswith("Not")
    e.tell("A poodle is a dog.")
    assert e.is_a("poodle", "dog")                                      # IS-A not broken by comparatives


def test_induction_most_specific_no_overgeneralization():
    e = UnderstandingEngine(seed=115)
    for f in ["A poodle is a dog.", "A dog is an animal.", "A robin is a bird.", "A bird is an animal.",
              "A robin can fly.", "A sparrow is a bird.", "A sparrow can fly."]:
        e.tell(f)
    e.induce()
    assert e.has_property("robin", "fly")            # bird-level induction
    assert not e.has_property("poodle", "fly")       # an animal but NOT a bird -> must not inherit flight
    assert "fly" in e._induced.get("bird", set())
    assert "fly" not in e._induced.get("animal", set())   # NOT over-generalized to animal


def test_describe_generation():
    e = UnderstandingEngine(seed=115)
    for f in ["A poodle is a dog.", "A poodle is a pet.", "A dog is an animal.", "the poodle chases the cat."]:
        e.tell(f)
    d = e.describe("a poodle")                        # leading article must be handled
    assert "is a dog and a pet" in d and "animal" in d and "chases the cat" in d
    assert e.describe("a quark").startswith("I don't know")


def test_compositional_relation_taxonomy():
    e = UnderstandingEngine(seed=119)
    for f in ["A cat is an animal.", "A mouse is an animal.", "the dog chases the cat.", "A car is a vehicle."]:
        e.tell(f)
    assert e.respond("is what the dog chases an animal?") == "Yes."   # compose relation + taxonomy
    assert e.respond("is what the dog chases a vehicle?") == "No."
    assert e.respond("is what the bird chases an animal?").startswith("I don't know")


def test_relational_analogy():
    e = UnderstandingEngine(seed=120)
    for f in ["the dog has the puppy.", "the cat has the kitten.", "the cow has the calf."]:
        e.tell(f)
    assert e.respond("dog is to puppy as cat is to?") == "Kitten."
    assert e.respond("dog is to puppy as cow is to?") == "Calf."
    assert e.respond("dog is to puppy as fish is to?").startswith("I can't")


def test_hypothetical_reasoning():
    e = UnderstandingEngine(seed=121)
    for f in ["A fish is an animal.", "A bird is an animal.", "A whale is a mammal.", "A mammal is an animal."]:
        e.tell(f)
    before = {k: set(v) for k, v in e.parents.items()}
    assert e.respond("if a whale were a fish, would it be an animal?").startswith("Yes")
    assert e.respond("if a rock were a bird, would it be an animal?").startswith("Yes")
    assert {k: set(v) for k, v in e.parents.items()} == before     # KB unchanged (clean retraction)
    assert e.is_a("whale", "animal") and not e.is_a("whale", "fish")


def test_is_a_property_based_vs_reference():
    import numpy as np
    rng = np.random.default_rng(0)
    for t in range(40):
        nC = int(rng.integers(5, 11)); concepts = [f"kx{i}" for i in range(nC)]
        ref = {c: set() for c in concepts}
        for i, c in enumerate(concepts):
            for _ in range(int(rng.integers(0, 3))):
                if i + 1 < nC:
                    ref[c].add(concepts[int(rng.integers(i + 1, nC))])
        def anc(x, seen=None):
            seen = set() if seen is None else seen
            for p in ref.get(x, ()):
                if p not in seen:
                    seen.add(p); anc(p, seen)
            return seen
        e = UnderstandingEngine(seed=t)
        for c in concepts:
            for p in ref[c]:
                e.tell(f"A {c} is a {p}.")
        for x in concepts:
            ra = anc(x)
            for c in concepts:
                if x != c:
                    assert e.is_a(x, c) == (c in ra), f"is_a({x},{c}) mismatch"


def test_parser_fuzz_no_crash():
    import random, string
    rnd = random.Random(0)
    vocab = ["dog", "is", "a", "an", "the", "not", "can", "bigger", "than", "what", "if", "and", "or"]
    nasty = ["", " ", ".", "?", r"\x", "((", "?" * 30, r"A \1 is a \2.", "\\", r"\g<0>", "a\nb\tc", "!@#$%^&*"]
    e = UnderstandingEngine(seed=0)
    for _ in range(500):
        s = rnd.choice(nasty) if rnd.random() < 0.4 else " ".join(
            rnd.choice(vocab) if rnd.random() < 0.7 else ''.join(rnd.choice(string.printable) for _ in range(rnd.randint(0, 6)))
            for _ in range(rnd.randint(0, 10)))
        e.tell(s); e.respond(s); e.describe(s)   # must never raise


def test_learned_composition_rule():
    e = UnderstandingEngine(seed=130)
    e.tell("the alice parents the carol."); e.tell("the carol siblings the tom.")
    e.add_rule("uncle", "parent", "sibling")          # a learned (JEP-129) composition rule
    assert e.relation_holds("alice", "uncle", "tom")  # derived, never stored
    assert not e.relation_holds("alice", "uncle", "carol")
