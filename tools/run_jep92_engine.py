"""JEP-92 - exercise the integrated UnderstandingEngine on a full comprehension battery (must be 100%)."""
import numpy as np
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-92: UnderstandingEngine - full comprehension battery (target: 100%) ===", flush=True)
    eng=UnderstandingEngine(seed=92)
    facts=["A poodle is a dog.","A collie is a dog.","A dog is an animal.","A cat is an animal.",
           "An animal is a living_thing.","A salmon is a fish.","A fish is an animal.",
           "the dog chases the cat.","the cat eats the mouse.","the salmon swims in the water."]
    told=[eng.tell(f) for f in facts]
    parsed_ok=all(t[0]!="none" for t in told)
    print(f"   parsed {sum(t[0]!='none' for t in told)}/{len(facts)} facts (all parsed: {parsed_ok})", flush=True)
    # prototypes for grounding
    rng=np.random.default_rng(920)
    for c in ["poodle","collie","dog","cat","mouse","salmon","fish","animal","living_thing","water"]:
        eng.add_prototype(c, rng.normal(0,1,eng.feat_dim))
    results=[]
    def check(name, got, exp): results.append((name, got==exp, got, exp))
    # (1) IS-A direct
    check("dog is animal", eng.is_a("dog","animal"), True)
    check("poodle is dog", eng.is_a("poodle","dog"), True)
    # (2) IS-A multi-hop (never stated)
    check("poodle is animal (2-hop)", eng.is_a("poodle","animal"), True)
    check("poodle is living_thing (3-hop)", eng.is_a("poodle","living_thing"), True)
    check("salmon is animal (2-hop)", eng.is_a("salmon","animal"), True)
    check("salmon is living_thing (3-hop)", eng.is_a("salmon","living_thing"), True)
    # (3) IS-A negatives
    check("poodle is NOT fish", eng.is_a("poodle","fish"), False)
    check("cat is NOT fish", eng.is_a("cat","fish"), False)
    check("dog is NOT poodle", eng.is_a("dog","poodle"), False)
    # (4) relational same-bag truth
    check("dog chases cat (true)", eng.relation_true("dog","chases","cat"), True)
    check("cat chases dog (false same-bag)", eng.relation_true("cat","chases","dog"), False)
    check("cat eats mouse (true)", eng.relation_true("cat","eats","mouse"), True)
    check("mouse eats cat (false same-bag)", eng.relation_true("mouse","eats","cat"), False)
    check("dog eats cat (false unstated)", eng.relation_true("dog","eats","cat"), False)
    # (5) grounded perception + grounded comprehension
    grec=[]
    for c in eng.prototypes:
        for _ in range(20):
            grec.append(eng.perceive(eng.prototypes[c]+rng.normal(0,0.6,eng.feat_dim))==c)
    check("grounding recognition >=0.95", np.mean(grec)>=0.95, True)
    seen=eng.perceive(eng.prototypes["poodle"]+rng.normal(0,0.6,eng.feat_dim))
    check("perceive poodle -> is animal", eng.is_a(seen,"animal"), True)
    # (6) ask() routing
    check("ask: is a poodle an animal", eng.ask("is a poodle an animal?"), True)
    check("ask: does the dog chase the cat", eng.ask("does the dog chase the cat?"), True)
    check("ask: does the cat chase the dog", eng.ask("does the cat chase the dog?"), False)
    npass=sum(r[1] for r in results); n=len(results); acc=npass/n
    for name,ok,got,exp in results:
        if not ok: print(f"   FAIL: {name}: got {got}, expected {exp}", flush=True)
    print(f"\n   battery: {npass}/{n} = {acc*100:.1f}%   (grounding mean {np.mean(grec):.3f})", flush=True)
    print("--- VERDICT ---", flush=True)
    if acc==1.0 and parsed_ok:
        print("JEP-92: PASS - the UnderstandingEngine is 100% on its target domain. Integrated parse->ground->bind->",flush=True)
        print("infer machinery, one module (world/understanding.py). The 100%-working foundation to scale FROM. Named.",flush=True)
    else:
        print(f"JEP-92: NOT YET 100% - {acc*100:.1f}%. Diagnose, fix, re-run (engine must reach 100%).",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
