"""A full conversation exercising the WHOLE understanding engine - learn, induce, reason, generate, communicate.
No transformer, no LLM. (EQMOD-4, JEP-92..115)"""
from world.understanding import UnderstandingEngine
def say(e, q):
    print(f"  you> {q}")
    print(f"  ai > {e.respond(q)}\n")
def main():
    e=UnderstandingEngine(seed=7)
    print("=== A conversation with the understanding engine (no transformer) ===\n  [teaching it a small world]")
    for f in ["A poodle is a dog.","A poodle is a pet.","A dog is an animal.","An animal is a living thing.",
              "A robin is a bird.","A sparrow is a bird.","A bird is an animal.","A penguin is a bird.",
              "A robin can fly.","A sparrow can fly.","A penguin cannot fly.",
              "An elephant is bigger than a dog.","A dog is bigger than a cat.","the poodle chases the cat."]:
        print(f"    teach: {f}"); e.tell(f)
    e.induce(); print()
    say(e, "what is a poodle?")
    say(e, "is a poodle a living thing?")
    say(e, "why?")                                       # justification
    say(e, "is a poodle an animal and is a poodle a pet?")
    say(e, "can all birds fly?")                         # quantified, with counterexample
    say(e, "is an elephant bigger than a cat?")          # transitive comparison
    say(e, "is a poodle a quark?")                       # epistemic humility
    print("  you> describe a poodle.")
    print(f"  ai > {e.describe('a poodle')}\n")          # generation
    print("  you> describe a penguin.")
    print(f"  ai > {e.describe('a penguin')}\n")         # penguin: bird, but cannot fly (defeasible)
    print("  [learning through dialogue + correction]")
    e2=UnderstandingEngine(seed=8); e2.tell("A poodle is a dog."); e2.tell("A dog is an animal.")
    say(e2, "is a poodle a living thing?")
    print(f"  ai > (gap) {e2.inquire('poodle','living thing')}")
    print("  you> An animal is a living thing.  [teaching the gap]"); e2.tell("An animal is a living thing.")
    say(e2, "is a poodle a living thing?")
    e2.tell("A whale is a fish."); print("  you> Actually, a whale is not a fish. A whale is a mammal.")
    print(f"  ai > (check) {e2.would_contradict('A whale is not a fish.')}")
    e2.tell("A whale is not a fish."); e2.tell("A whale is a mammal."); e2.tell("A mammal is an animal.")
    say(e2, "is a whale an animal?")
if __name__=="__main__": main()
