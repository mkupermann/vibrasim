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
    # LEARN FROM A PROSE PASSAGE (the learn-from-sources capability, JEP-155..159) - no transformer
    print("  [reading an encyclopedic passage and learning from it]")
    e3=UnderstandingEngine(seed=9)
    passage=("A poodle is a kind of dog. A dog is a mammal. A mammal is an animal. "
             "A heart is part of a dog. A cell is part of a heart. "
             "A virus causes an infection. An infection causes a fever. "
             "Mammals such as dogs and cats are warm-blooded.")
    learned=e3.read(passage)
    print(f'  you> "{passage}"')
    print(f"  ai > (learned {learned['is_a']} is-a, {learned['part_of']} part-of, {learned['causal']} causal facts)\n")
    print(f"  Q: is a poodle an animal?  A: {'Yes' if e3.is_a('poodle','animal') else 'No'}  (3-hop, no single sentence says it)")
    print(f"  Q: is a cat an animal?  A: {'Yes' if e3.is_a('cat','animal') else 'No'}  (from 'mammals such as ... cats')")
    print(f"  Q: is a cell part of a dog?  A: {'Yes' if e3.part_of('cell','dog') else 'No'}  (multi-hop part-of)")
    print(f"  Q: does a virus cause a fever?  A: {'Yes' if e3.causes_effect('virus','fever') else 'No'}  (causal chain)")
    print(f"  Q: is a heart an animal?  A: {'Yes' if e3.is_a('heart','animal') else 'No'}  (correct: part-of is NOT is-a)\n")
    # COMMUNICATE back what it learned — a coherent multi-relation profile in English (JEP-160)
    print("  you> describe a dog.")
    print(f"  ai > {e3.describe('a dog')}")
    print("  you> describe a virus.")
    print(f"  ai > {e3.describe('a virus')}\n")
if __name__=="__main__": main()
