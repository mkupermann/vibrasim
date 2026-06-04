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
    assert e.parents.get("dog") == "animal"      # not "nimal" — article must not eat the noun
    assert e.parents.get("animal") == "living thing"
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
