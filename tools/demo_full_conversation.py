"""A full conversation exercising the WHOLE understanding engine - learn, induce, correct, reason, communicate.
No transformer, no LLM. (EQMOD-4, JEP-92..105)"""
from world.understanding import UnderstandingEngine
def say(e, q):
    print(f"  you> {q}")
    print(f"  ai > {e.respond(q)}\n")
def main():
    e=UnderstandingEngine(seed=7)
    print("=== A conversation with the understanding engine (no transformer) ===\n")
    print("  [teaching it a small world]")
    for f in ["A poodle is a dog.","A poodle is a pet.","A dog is an animal.","An animal is a living thing.",
              "A robin is a bird.","A sparrow is a bird.","A bird is an animal.",
              "A robin can fly.","A sparrow can fly.","the dog chases the cat."]:
        print(f"    teach: {f}"); e.tell(f)
    e.induce()
    print()
    say(e, "what is a poodle?")                       # multi-parent
    say(e, "is a poodle a living thing?")             # multi-hop deduction, explained
    say(e, "is a poodle an animal and is a poodle a pet?")  # Boolean
    say(e, "does the cat chase the dog?")             # relational, same-bag
    say(e, "is a poodle a fish?")                     # known category, no path -> No
    say(e, "is a poodle a quark?")                    # never heard of -> I don't know
    # induction
    print("  [it has never been told a sparrow flies as a fact about THIS query - it INDUCED 'birds fly']")
    print(f"  you> can a wren fly?  (wren = a brand-new bird)")
    e.tell("A wren is a bird."); e.induce()
    print(f"  ai > {'Yes' if e.has_property('wren','fly') else 'No'} - I induced that birds fly.\n")
    # learning through dialogue
    print("  [learning through dialogue]")
    e2=UnderstandingEngine(seed=8); e2.tell("A poodle is a dog."); e2.tell("A dog is an animal.")
    say(e2, "is a poodle a living thing?")            # I don't know
    print(f"  ai > (gap) {e2.inquire('poodle','living thing')}")
    print("  you> An animal is a living thing.   [teaching the exact gap]"); e2.tell("An animal is a living thing.")
    say(e2, "is a poodle a living thing?")            # now Yes, with full chain
    # correction
    print("  [correcting a mistake]")
    e2.tell("A whale is a fish."); say(e2, "is a whale a fish?")
    print("  you> No - a whale is not a fish. A whale is a mammal.  A mammal is an animal.")
    e2.tell("A whale is not a fish."); e2.tell("A whale is a mammal."); e2.tell("A mammal is an animal.")
    say(e2, "is a whale an animal?")
if __name__=="__main__": main()
