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
    assert e.parents.get("animal") == "living_thing"
    assert e.is_a("poodle", "living_thing")      # multi-hop across varied phrasings


def test_communication_explains_in_english():
    e = _engine()
    assert e.explain("is a poodle a living_thing?") == \
        "Yes. A poodle is a dog, a dog is an animal, an animal is a living thing."
    assert e.explain("is a poodle a fish?").startswith("No.")
    assert e.explain("does the dog chase the cat?") == "Yes, the dog chases the cat."
    assert e.explain("does the cat chase the dog?").startswith("No,")
