"""A short DIALOGUE demo of the UnderstandingEngine - learning, understanding, communicating (no transformer)."""
from world.understanding import UnderstandingEngine
def main():
    e=UnderstandingEngine(seed=1)
    print("=== Understanding Engine - a dialogue (no transformer) ===\n")
    for f in ["A poodle is a dog.","A dog is an animal.","An animal is a living thing.","the dog chases the cat."]:
        e.tell(f); print(f"  [told]  {f}")
    print()
    for q in ["is a poodle a living thing?","does the cat chase the dog?","is a poodle an animal and is a poodle not a fish?"]:
        print(f"  Q: {q}")
        print(f"  A: {e.explain(q) if not (' and ' in q or ' or ' in q) else e.ask_bool(q)}\n")
    print("  [correction] 'A whale is a fish.' ... 'A whale is not a fish.' 'A whale is a mammal.'")
    e.tell("A whale is a fish."); e.tell("A mammal is an animal.")
    e.tell("A whale is not a fish."); e.tell("A whale is a mammal.")
    print(f"  Q: is a whale an animal?")
    print(f"  A: {e.explain('is a whale an animal?')}")
if __name__=="__main__": main()
