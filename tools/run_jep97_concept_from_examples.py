"""JEP-97 - learn a NEW concept from perceptual examples, then integrate it into comprehension. Target pass."""
import numpy as np
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-97: engine tier 6 - learn a concept from EXAMPLES (shown, not told) ===", flush=True)
    rng=np.random.default_rng(97)
    eng=UnderstandingEngine(seed=97)
    # existing world
    for c in ["dog","cat","fish","animal"]:
        eng.add_prototype(c, rng.normal(0,1,eng.feat_dim))
    eng.tell("A dog is an animal."); eng.tell("A fish is an animal.")
    # a NEW concept 'bird' has a hidden true prototype; show 5 noisy examples
    true_bird=rng.normal(0,1,eng.feat_dim)
    examples=[true_bird+rng.normal(0,0.6,eng.feat_dim) for _ in range(5)]
    eng.learn_concept("bird", examples)
    # held-out recognition of new concept
    held=[eng.perceive(true_bird+rng.normal(0,0.6,eng.feat_dim))=="bird" for _ in range(100)]
    bird_acc=float(np.mean(held))
    # existing concepts unaffected
    exist=[]
    for c in ["dog","cat","fish","animal"]:
        for _ in range(50): exist.append(eng.perceive(eng.prototypes[c]+rng.normal(0,0.6,eng.feat_dim))==c)
    exist_acc=float(np.mean(exist))
    # integrate: tell 'a bird is an animal', then comprehend a NEWLY perceived bird
    eng.tell("A bird is an animal.")
    comp=[]
    for _ in range(50):
        seen=eng.perceive(true_bird+rng.normal(0,0.6,eng.feat_dim))
        comp.append(eng.is_a(seen,"animal"))
    comp_acc=float(np.mean(comp))
    seen=eng.perceive(true_bird+rng.normal(0,0.6,eng.feat_dim))
    print(f"   learned 'bird' from 5 examples.", flush=True)
    print(f"   held-out bird recognition = {bird_acc:.3f}", flush=True)
    print(f"   existing concepts recognition = {exist_acc:.3f}", flush=True)
    print(f"   grounded comprehension (perceive bird -> is animal) = {comp_acc:.3f}", flush=True)
    print(f"   explain('is a bird an animal?') -> {eng.explain('is a bird an animal?')}", flush=True)
    print("--- VERDICT ---", flush=True)
    if bird_acc>=0.90 and exist_acc>=0.95 and comp_acc==1.0:
        print("JEP-97: PASS - the engine LEARNS a new concept from EXAMPLES (prototype from a few instances),",flush=True)
        print("recognizes held-out instances, leaves existing concepts intact, and integrates the new concept into",flush=True)
        print("comprehension (perceive a new bird -> infer it is an animal). Human-like concept acquisition. Named.",flush=True)
    else:
        print(f"JEP-97: NOT YET - bird {bird_acc:.2f}, existing {exist_acc:.2f}, comp {comp_acc:.2f}. Diagnose vs prediction.",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
