"""The DEFINITIVE showcase of the complete understanding engine - all faculties, no transformer (EQMOD-4, JEP-92..143)."""
from world.understanding import UnderstandingEngine
def ask(e,q): print(f"  you> {q}\n  ai > {e.respond(q)}\n")
def main():
    e=UnderstandingEngine(seed=7)
    print("=== The understanding engine - a complete demonstration (no transformer) ===\n  [learning a world]")
    for f in ["A poodle is a dog.","A poodle is a pet.","A dog is an animal.","An animal is a living thing.",
              "A cat is an animal.","A robin is a bird.","A sparrow is a bird.","A bird is an animal.","A penguin is a bird.",
              "A robin can fly.","A sparrow can fly.","A penguin cannot fly.",
              "An elephant is bigger than a dog.","A dog is bigger than a cat.",
              "the poodle chases the cat.","the dog has the puppy.","the cat has the kitten."]:
        e.tell(f)
    e.induce()
    print("  (taught 16 facts)\n")
    ask(e,"what is a poodle?")                                  # multi-parent
    ask(e,"is a poodle a living thing?")                        # multi-hop deduction
    ask(e,"why?")                                               # justification
    ask(e,"can all birds fly?")                                 # quantified + counterexample
    ask(e,"is an elephant bigger than a cat?")                  # transitive comparison
    ask(e,"is what the poodle chases an animal?")               # compositional (relation+taxonomy)
    ask(e,"dog is to puppy as cat is to?")                      # analogy
    ask(e,"if a poodle were a bird, would it be an animal?")    # hypothetical
    ask(e,"is a poodle a quark?")                               # epistemic humility
    print("  you> describe a penguin.")
    print(f"  ai > {e.describe('a penguin')}\n")                # generation (correctly: no flight)
    # causal + intervention
    e.tell_cause("rain","wetgrass"); e.tell_cause("wetgrass","slippery")
    print(f"  Q: does rain cause slippery?  A: {'Yes' if e.causes_effect('rain','slippery') else 'No'}")
    print(f"  Q: if I set the grass wet myself (do), does rain still cause slippery?  A: "
          f"{'Yes' if e.causes_effect('rain','slippery',intervene='wetgrass') else 'No'}  (intervention cuts the cause)\n")
    # temporal persistence
    e.event("open the door",{"door_open":True}); e.event("turn on the light",{"light_on":True})
    print(f"  Q: after opening the door and turning on the light, is the door still open?  A: "
          f"{'Yes' if e.fluent_at('door_open') else 'No'}  (persists - the frame axiom)\n")
    # learning by correction
    e2=UnderstandingEngine(seed=8)
    e2.tell("A whale is a fish."); e2.tell("A mammal is an animal.")
    print("  you> Actually, a whale is not a fish. A whale is a mammal.")
    print(f"  ai > (check) {e2.would_contradict('A whale is not a fish.')}")
    e2.tell("A whale is not a fish."); e2.tell("A whale is a mammal.")
    ask(e2,"is a whale an animal?")                             # corrected
if __name__=="__main__": main()
