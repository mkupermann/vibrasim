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


def test_is_a_confidence_is_graded():
    e = UnderstandingEngine(seed=1)
    e.tell("A poodle is a dog."); e.tell("A dog is an animal."); e.tell("A poodle is a pet.")
    assert e.is_a_confidence("poodle", "animal") >= 1   # at least one derivation path
    assert e.is_a_confidence("poodle", "fish") == 0      # no path


def test_causal_reasoning_intervention():
    e = UnderstandingEngine(seed=141)
    for x, y in [("rain", "wetgrass"), ("wetgrass", "slippery"), ("sprinkler", "wetgrass")]:
        e.tell_cause(x, y)
    assert e.causes_effect("rain", "slippery")                       # transitive causation
    assert not e.causes_effect("slippery", "rain")                   # asymmetric
    assert not e.causes_effect("rain", "slippery", intervene="wetgrass")  # do(wetgrass) cuts incoming edges
    assert e.causes_effect("rain", "slippery", intervene="sprinkler")     # unrelated intervention


def test_probabilistic_reasoning():
    e = UnderstandingEngine(seed=142)
    for x, y in [("a", "b"), ("b", "c"), ("c", "d")]:
        e.tell_prob(x, y, 0.9)
    assert abs(e.is_a_prob("a", "d") - 0.729) < 0.02      # chain compounds: 0.9^3
    e2 = UnderstandingEngine(seed=2)
    for x, y in [("s", "m1"), ("m1", "t"), ("s", "m2"), ("m2", "t")]:
        e2.tell_prob(x, y, 0.9)
    assert e2.is_a_prob("s", "t") > 0.81                  # two paths noisy-OR > single path (aggregation)


def test_temporal_persistence_frame():
    e = UnderstandingEngine(seed=143)
    e.event("open door", {"door_open": True})
    e.event("turn on light", {"light_on": True})
    e.event("close door", {"door_open": False})
    assert e.fluent_at("door_open", 1) is True      # persists through the unrelated light event (frame axiom)
    assert e.fluent_at("door_open") is False        # changed by close
    assert e.fluent_at("light_on") is True          # persists, never turned off
    assert e.fluent_at("light_on", 0) is None       # not yet set at t0


def test_provenance_truth_maintenance():
    e = UnderstandingEngine(seed=145)
    for f in ["A poodle is a dog.", "A dog is an animal.", "An animal is a living thing."]:
        e.tell(f)
    assert e.provenance("poodle", "living thing") == [("poodle", "dog"), ("dog", "animal"), ("animal", "living thing")]
    assert e.is_a("poodle", "living thing")
    e.retract("dog", "animal")
    assert not e.is_a("poodle", "living thing")        # justification removed
    # redundancy survives retraction
    e2 = UnderstandingEngine(seed=2)
    for f in ["A poodle is a dog.", "A poodle is a mammal.", "A dog is an animal.", "A mammal is an animal."]:
        e2.tell(f)
    e2.retract("dog", "animal")
    assert e2.is_a("poodle", "animal")                 # survives via mammal path


def test_abduction():
    e = UnderstandingEngine(seed=146)
    for x, y in [("rain", "wetgrass"), ("sprinkler", "wetgrass"), ("wetgrass", "slippery")]:
        e.tell_cause(x, y)
    assert e.abduce("slippery") == ["wetgrass", "rain", "sprinkler"]   # most direct cause first
    assert e.abduce("slippery")[0] == "wetgrass"                       # best (parsimonious) explanation
    assert e.abduce("rain") == []                                      # root has no causes


def test_causal_planning():
    e = UnderstandingEngine(seed=148)
    for x, y in [("rain", "wetgrass"), ("sprinkler", "wetgrass"), ("wetgrass", "slippery"),
                 ("press_button", "sprinkler")]:
        e.tell_cause(x, y)
    assert e.achieve("slippery") == ["press_button", "rain"]   # actionable root causes (sprinkler not a root)
    assert e.achieve("rain") == []                             # already a root, nothing causes it


def test_spatial_perspective():
    e = UnderstandingEngine(seed=149)
    e.tell_spatial("cup", "left", "plate"); e.tell_spatial("plate", "left", "fork")
    e.tell_spatial("lamp", "above", "table")
    assert e.spatial_holds("cup", "left", "fork")                            # transitive
    assert e.spatial_holds("plate", "right", "cup")                          # inverse
    assert e.spatial_holds("cup", "right", "plate", viewpoint="opposite")    # perspective flip
    assert not e.spatial_holds("cup", "left", "plate", viewpoint="opposite")
    assert e.spatial_holds("lamp", "above", "table", viewpoint="opposite")   # above/below invariant


def test_mereology_distinct_from_isa():
    e = UnderstandingEngine(seed=150)
    e.tell_part("finger", "hand"); e.tell_part("hand", "arm"); e.tell_part("arm", "body")
    e.tell("A finger is a body_part.")
    assert e.part_of("finger", "body")          # transitive part-of
    assert not e.part_of("body", "finger")      # asymmetric
    assert not e.is_a("finger", "body")         # part-of is NOT is-a
    assert not e.is_a("finger", "hand")
    assert e.is_a("finger", "body_part")        # separate is-a graph still works


def test_read_from_prose_multirelation():
    # learn-from-prose: extract is-a + part-of + causal from an encyclopedic passage (JEP-155..159), no transformer
    e = UnderstandingEngine(seed=159)
    learned = e.read(
        "A dog is a mammal. A mammal is an animal. A heart is part of a dog. A cell is part of a heart. "
        "A virus causes an infection. An infection causes a fever. Mammals such as dogs and cats are common. "
        "A car is a vehicle."
    )
    assert learned["is_a"] >= 4 and learned["part_of"] == 2 and learned["causal"] == 2
    assert e.is_a("dog", "animal")              # multi-hop is-a, never stated in one sentence
    assert e.is_a("cat", "animal")              # recovered from 'such as ... are common' (trailing-VP truncation)
    assert e.part_of("cell", "dog")             # multi-hop part-of
    assert e.causes_effect("virus", "fever")    # causal chain
    assert not e.is_a("heart", "animal")        # correct NON-composition: part-of does not imply is-a
    # 'virus' must NOT be mangled to 'viru' by singularization
    assert e.is_a("virus", "microbe") is False  # not taught, but the term resolves cleanly (no crash/mangle)


def test_norm_not_plural_overstrip():
    # singularizer must not strip trailing -s from non-plural -us/-is/-ss nouns (JEP-159 bug fix)
    e = UnderstandingEngine(seed=1)
    for w in ("virus", "bus", "lens", "basis", "species", "glass"):
        assert e._norm(w) == w, f"{w} wrongly de-pluralized to {e._norm(w)}"
    assert e._norm("dogs") == "dog" and e._norm("animals") == "animal"   # real plurals still work


def test_describe_multirelation_profile():
    # COMMUNICATE what was learned: describe() composes is-a + part-of + causal into a coherent English profile (JEP-160)
    e = UnderstandingEngine(seed=160)
    e.read("A dog is a mammal. A mammal is an animal. A heart is part of a dog. A cell is part of a heart. "
           "A virus causes an infection. An infection causes a fever.")
    d_dog = e.describe("a dog")
    assert "is a mammal" in d_dog and "animal" in d_dog and "heart" in d_dog   # is-a (multi-hop) + part
    d_heart = e.describe("a heart")
    assert "part of a dog" in d_heart and "cell" in d_heart                     # both part-of directions
    assert "causes an infection" in e.describe("a virus")                       # causal effect
    assert "caused by an infection" in e.describe("a fever")                    # reverse causal
    # profile must NOT wrongly assert part-of as is-a
    assert "heart is a" not in d_heart.lower().replace("heart is a body", "")


def test_read_shallow_parse_extensions():
    # JEP-162: read() handles conjoined subjects, plural-category, multi-fact predicates, appositives (shallow parse)
    e = UnderstandingEngine(seed=162)
    e.read("A lion and a tiger are cats. Dogs are mammals. A whale is a mammal and an animal. "
           "A beagle, a kind of dog, is friendly. Mammals such as cats and horses are warm-blooded.")
    assert e.is_a("lion", "cat") and e.is_a("tiger", "cat")     # conjoined subject
    assert e.is_a("dog", "mammal")                              # plural category 'Dogs are mammals'
    assert e.is_a("whale", "mammal") and e.is_a("whale", "animal")  # multi-fact predicate
    assert e.is_a("beagle", "dog")                              # appositive
    assert e.is_a("horse", "mammal")                            # such-as 3-item (horses->horse, -ses fix)


def test_read_no_adjective_false_positives():
    # adjective predicates must NOT be read as is-a (the plural-noun guard)
    e = UnderstandingEngine(seed=1)
    e.read("Dogs are loyal. A cat is friendly. Birds are warm-blooded.")
    assert not e.is_a("dog", "loyal")
    assert not e.is_a("cat", "friendly")
    assert e._norm("horses") == "horse" and e._norm("roses") == "rose" and e._norm("glasses") == "glass"


def test_read_recency_pronoun_resolution():
    # JEP-163: cross-sentence recency coreference closes the common 'X is A. It is B.' pattern
    e = UnderstandingEngine(seed=163)
    e.read("A wolf is a canine. It is a mammal. A mammal is an animal.")
    assert e.is_a("wolf", "canine")
    assert e.is_a("wolf", "mammal")      # 'It' -> wolf (most recent subject)
    assert e.is_a("wolf", "animal")      # multi-hop after pronoun resolution
    # pronoun + adjective predicate still adds nothing (FP guard survives resolution)
    e2 = UnderstandingEngine(seed=1)
    e2.read("A cat is a feline. It is independent.")
    assert not e2.is_a("cat", "independent")


def test_read_belief_revision_from_prose():
    # JEP-164: a correcting source revises beliefs read from an earlier source (belief revision from prose)
    e = UnderstandingEngine(seed=164)
    e.read("A whale is a fish. A fish is an animal.")
    assert e.is_a("whale", "fish")
    e.read("A whale is not a fish. A whale is a mammal. A mammal is an animal.")
    assert not e.is_a("whale", "fish")     # retracted by the correction
    assert e.is_a("whale", "mammal")       # corrected parent
    assert e.is_a("whale", "animal")       # still an animal, now via mammal
    # negation coexists with positive facts; pronoun+negation composes
    e2 = UnderstandingEngine(seed=1)
    e2.read("A dog is a mammal. A dog is not a reptile. A whale is a creature. It is not a fish.")
    assert e2.is_a("dog", "mammal") and not e2.is_a("dog", "reptile") and not e2.is_a("whale", "fish")


def test_read_jep166_extensions():
    # JEP-166: has-part, irregular -ves plural, adjectival head-noun, relative clause 'which is a'
    e = UnderstandingEngine(seed=166)
    e.read("A fish has gills. A bird has feathers and wings. Dogs and wolves are canines. "
           "A mammal is a warm-blooded animal. A salmon, which is a fish, lives in rivers.")
    assert e.part_of("gill", "fish")                       # 'X has Y'
    assert e.part_of("feather", "bird") and e.part_of("wing", "bird")  # 'has Y and Z'
    assert e.is_a("wolf", "canine")                        # wolves -> wolf (-ves)
    assert e.is_a("mammal", "animal")                      # warm-blooded animal -> animal (head-noun link)
    assert e.is_a("salmon", "fish")                        # relative clause
    # irregular plurals normalize
    assert e._norm("wolves") == "wolf" and e._norm("leaves") == "leaf" and e._norm("mice") == "mouse"


def test_read_cross_domain_and_located_in():
    # JEP-167: read() generalizes across domains; 'X is located in Y' -> part-of; quantifier-stripping in 'has'
    e = UnderstandingEngine(seed=167)
    e.read("Paris is a city. Paris is located in France. France is a country. Europe has many countries.")
    assert e.is_a("paris", "city") and e.is_a("france", "country")
    assert e.part_of("paris", "france")        # 'located in' -> part-of
    assert e.part_of("country", "europe")      # 'has many countries' -> 'country' (quantifier stripped), not 'many country'
    et = UnderstandingEngine(seed=2)
    et.read("A laptop is a computer. A laptop has a processor. A processor is a chip. A bug causes a crash.")
    assert et.is_a("laptop", "computer") and et.part_of("processor", "laptop") and et.causes_effect("bug", "crash")


def test_respond_multirelation_questions():
    # JEP-168: respond() answers part-of and causal questions over read knowledge (conversational Q&A)
    e = UnderstandingEngine(seed=168)
    e.read("A dog is a mammal. A heart is part of a dog. A cell is part of a heart. A virus causes a fever.")
    assert e.respond("is a heart part of a dog?").startswith("Yes")
    assert e.respond("is a cell part of a dog?").startswith("Yes")        # multi-hop part-of
    assert e.respond("is a heart part of a cat?").startswith("No")
    assert "heart" in e.respond("what is part of a dog?").lower()
    assert e.respond("does a virus cause a fever?").startswith("Yes")
    assert "virus" in e.respond("what causes a fever?").lower()
    assert "fever" in e.respond("what does a virus cause?").lower()
    # capitalization correct (no .capitalize() flattening)
    assert "as far as I know" in e.respond("is a heart part of a cat?")


def test_part_of_isa_interaction():
    # JEP-169: mereology INTERACTS with taxonomy (correctly, without leaking)
    e = UnderstandingEngine(seed=169)
    e.read("A dog is a mammal. A mammal is an animal. A heart is part of a dog. A cell is part of a heart. "
           "A poodle is a kind of dog. A cat is a mammal.")
    assert e.part_of("heart", "animal")     # whole's supertype: a dog's heart is part of an animal
    assert e.part_of("cell", "animal")      # 2-hop part-of + is-a
    assert e.part_of("heart", "poodle")     # whole's subtype inherits the part: a poodle has a heart
    assert not e.part_of("heart", "cat")    # CRITICAL: up-then-down must NOT leak (dog's heart != cat's part)
    assert not e.is_a("heart", "animal")    # part-of is still NOT is-a
    assert not e.part_of("animal", "heart") # asymmetric


def test_causal_isa_interaction_asymmetry():
    # JEP-170: causal INTERACTS with taxonomy, but ASYMMETRICALLY vs mereology (effect-subtype NOT entailed)
    e = UnderstandingEngine(seed=170)
    e.read("Smoking causes cancer. A cancer is a disease. A disease is a condition. "
           "A poodle is a dog. A dog causes allergies. A lung-cancer is a cancer.")
    assert e.causes_effect("smoking", "disease")        # effect-side UP: cancer is-a disease
    assert e.causes_effect("smoking", "condition")      # 2-hop effect supertype
    assert e.causes_effect("poodle", "allergy")         # cause-side subtype inherits causal power
    assert e.causes_effect("smoking", "cancer")         # direct (regression)
    assert not e.causes_effect("smoking", "lung_cancer")  # effect-SUBtype NOT entailed (the asymmetry vs part-of)
    assert not e.causes_effect("animal", "allergy")     # supertype does NOT inherit a subtype's causal power
    assert not e.causes_effect("disease", "smoking")    # asymmetric


def test_novel_concept_learning_structural():
    # JEP-172: understanding is STRUCTURAL not lexical — learns/reasons about entirely novel nonsense words
    e = UnderstandingEngine(seed=172)
    e.read("A blicket is a kind of zorp. A zorp is a feb. A florp is part of a blicket. "
           "A glim causes a thrumble. A thrumble is a wibble.")
    assert e.is_a("blicket", "feb")               # 2-hop is-a on novel words
    assert e.part_of("florp", "blicket")          # part-of on novel words
    assert e.part_of("florp", "feb")              # part-of/is-a interaction on novel words
    assert e.causes_effect("glim", "wibble")      # causal+is-a interaction on novel words
    assert not e.is_a("florp", "feb")             # part is not type (holds for novel words)
    assert "zorp" in e.describe("a blicket")      # generates a profile for a never-seen concept


def test_why_across_relation_types():
    # JEP-173: 'why?' explains part-of and causal chains too (not just is-a), with correct recency
    e = UnderstandingEngine(seed=173)
    e.read("A heart is part of a dog. A cell is part of a heart. A virus causes an infection. "
           "An infection causes a fever. A dog is a mammal. A mammal is an animal.")
    e.respond("is a cell part of a dog?")
    assert e.respond("why?") == "Because a cell is part of a heart, and a heart is part of a dog."
    e.respond("does a virus cause a fever?")
    assert e.respond("why?") == "Because a virus causes an infection, and an infection causes a fever."
    e.respond("is a dog an animal?")                       # recency: most recent question type wins
    assert "is a mammal" in e.respond("why?") and "part of" not in e.respond("why?")


def test_rich_faculties_over_read_knowledge():
    # JEP-174: the full faculty set (quantification/hypothetical/Boolean/three-valued/contradiction) composes with read()
    e = UnderstandingEngine(seed=174)
    e.read("A poodle is a dog. A dog is a mammal. A mammal is an animal. A salmon is a fish. A fish is an animal.")
    assert e.respond("is every poodle an animal?") == "Yes."
    assert e.respond("if a poodle were a fish, would it be an animal?").startswith("Yes")  # hypothetical, KB unchanged
    assert "fish" not in e.parents.get("poodle", set())                                    # retracted cleanly
    assert e.ask_bool("is a poodle an animal and is a poodle not a fish") is True
    assert e.respond("is a poodle a vegetable?").startswith("I don't know")                # three-valued
    assert e.would_contradict("A poodle is not a dog.")                                     # contradiction detection


def test_document_scale_and_relative_clause():
    # JEP-175: full-document (multi-paragraph) operation + 'X is a Y that ...' relative-clause predicate
    e = UnderstandingEngine(seed=175)
    e.read("A penguin is a bird that cannot fly. A bird is an animal. A dog is a mammal. A mammal is an animal. "
           "A virus causes an infection. An infection causes inflammation. Inflammation causes pain.")
    assert e.is_a("penguin", "bird")                       # relative-clause predicate truncated to head NP
    assert e.respond("is a penguin an animal?").startswith("Yes")   # cross-fact multi-hop
    assert e.causes_effect("virus", "pain")                # 3-hop causal chain across the document
    assert not e.is_a("penguin", "fly")                    # 'that cannot fly' not misread as a parent


def test_grounded_prose_learned_concept():
    # JEP-178: ground a PROSE-LEARNED taxonomy in perception — perceive an instance, reason over read structure
    import numpy as np
    e = UnderstandingEngine(seed=178)
    e.read("A dog is a mammal. A cat is a mammal. A mammal is an animal. A robin is a bird. A bird is an animal.")
    rng = np.random.default_rng(0)
    protos = {c: rng.normal(0, 1, e.feat_dim) for c in ["dog", "cat", "robin"]}
    for c, v in protos.items():
        e.add_prototype(c, v)
    # a novel perceptual instance -> symbol -> multi-hop is_a over the PROSE-learned taxonomy
    inst = protos["dog"] + rng.normal(0, 0.5, e.feat_dim)
    seen = e.perceive(inst)
    assert seen == "dog"
    assert e.is_a(seen, "mammal") and e.is_a(seen, "animal")   # grounded multi-hop through read structure
    assert not e.is_a(seen, "bird")


def test_read_nominal_compound_of():
    # JEP-183: tight 'X of Y' nominal compounds ('form of government') are extractable as concepts
    e = UnderstandingEngine(seed=183)
    e.read("Democracy is a form of government. A form of government is a political system. Ice is a state of matter.")
    assert e.is_a("democracy", "form of government")
    assert e.is_a("democracy", "political system")     # chains through the X-of-Y concept
    assert e.is_a("ice", "state of matter")
    # 'of' is still rejected in longer prepositional fragments (precision preserved)
    assert not e._bare_np("admissibility of things which")
