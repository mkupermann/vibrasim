"""Permanent gate for the talk-to-it conversation (JEP-340..348): learn-as-you-talk, make-connections, gaps,
prose normalizer, pronouns, messy phrasings. Fast, no Tk, no transformer.
"""
import tempfile
from world.conversation import Conversation


def _conv():
    return Conversation(brain_dir=tempfile.mkdtemp(), seed=0)


def test_learn_then_answer_multihop():
    c = _conv()
    c.say("A poodle is a dog."); c.say("A dog is a mammal."); c.say("A mammal is an animal.")
    assert c.say("Is a poodle an animal?").strip().lower() == "yes."        # multi-hop across taught facts
    assert c.say("Is a poodle a fish?").strip().lower() == "no."


def test_memory_grows_each_teach():
    c = _conv()
    n0 = c.n_facts
    c.say("A cat is a mammal.")
    assert c.n_facts > n0


def test_make_connections():
    c = _conv()
    c.say("A dog is a mammal."); c.say("A mammal is an animal."); c.say("A dog can bark.")
    resp = c.say("A poodle is a dog.")
    assert "connect" in resp.lower() and "mammal" in resp.lower() and "animal" in resp.lower()


def test_gaps_what_is_not_clear():
    c = _conv()
    c.say("A poodle is a dog.")               # 'dog' referenced but undefined -> a gap
    assert "dog" in c.gaps()
    resp = c.say("what is not clear to you?")
    assert "dog" in resp.lower()


def test_prose_normalizer_forms():
    c = _conv()
    c._learn_one("A poodle is a kind of dog.")
    c._learn_one("Dogs are carnivores.")
    c._learn_one("A dog has four legs.")
    from world.brain_query import BrainQuery
    bq = BrainQuery(c.sm, seed=0)
    assert bq.is_a("poodle", "dog") is True          # 'is a kind of'
    assert bq.is_a("dog", "carnivore") is True        # plural is-a
    assert bq.how_many("dog") == 4                     # numeric possession


def test_messy_phrasings():
    c = _conv()
    for s in ["A poodle is a dog.", "A dog is a mammal.", "A dog can bark."]:
        c.say(s)
    assert c.say("isn't a poodle a dog?").strip().lower() == "yes."
    assert c.say("do poodles bark?").strip().lower() == "yes."
    assert c.say("so, is a poodle a mammal?").strip().lower() == "yes."


def test_pronoun_it():
    c = _conv()
    c.say("A poodle is a dog."); c.say("A dog can bark.")
    c.say("Tell me about a poodle")               # last subject = poodle
    assert c.say("can it bark?").strip().lower() == "yes."


def test_prose_forms_conjunction_relclause_locational():
    c = _conv()
    c._learn_one("Cats and dogs are mammals.")
    c._learn_one("A poodle, which is a dog, can bark.")
    c._learn_one("Paris is in France.")
    from world.brain_query import BrainQuery
    bq = BrainQuery(c.sm, seed=0)
    assert bq.is_a("cat", "mammal") is True and bq.is_a("dog", "mammal") is True
    assert bq.is_a("poodle", "dog") is True and bq.has_property("poodle", "bark") is True
    assert ("paris", "located_in", "france") in c.sm.facts


def test_interactive_construction_teaching():
    # NOTE: passive 'X was VERBed by Y' is now parsed directly (JEP-385), so this uses an active SVO
    # construction 'X chases Y' which is still unknown, to exercise the ask -> teach -> learn -> apply flow.
    c = _conv()
    assert "couldn't" not in c.say("A poodle is a dog.").lower()          # normal -> no ask
    assert "couldn't" in c.say("The dog chases the cat.").lower()         # unparseable -> asks
    c.say("dog chases cat")
    c.say("The fox chases the rabbit.")
    assert "pattern" in c.say("fox chases rabbit").lower()                # learns the construction
    c.say("The wolf chases the deer.")
    assert ("wolf", "chases", "deer") in c.sm.facts                       # reads held-out itself


def test_question_vs_statement_routing():
    c = _conv()
    assert Conversation.is_question("Is a dog a mammal?")
    assert Conversation.is_question("tell me about a dog")
    assert not Conversation.is_question("A dog is a mammal.")
