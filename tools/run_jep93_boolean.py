"""JEP-93 - Boolean-composed comprehension (AND/OR/NOT) on the UnderstandingEngine. Target 100%."""
import numpy as np
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-93: engine tier 2 - Boolean comprehension (AND/OR/NOT), target 100% ===", flush=True)
    eng=UnderstandingEngine(seed=93)
    for f in ["A poodle is a dog.","A dog is an animal.","An animal is a living_thing.",
              "A salmon is a fish.","A fish is an animal.","the dog chases the cat."]:
        eng.tell(f)
    res=[]
    def ck(q, exp): got=eng.ask_bool(q); res.append((q,got==exp,got,exp))
    ck("is a poodle an animal", True)
    ck("is a poodle not a fish", True)                 # negation
    ck("is a poodle a fish", False)
    ck("is a poodle an animal and is a poodle not a fish", True)   # AND
    ck("is a poodle a fish and is a poodle an animal", False)      # AND with a false conjunct
    ck("is a poodle a fish or is a poodle an animal", True)        # OR
    ck("is a poodle a fish or is a salmon a bird", False)          # OR both false (bird unknown -> is_a False)
    ck("is a salmon an animal and is a salmon a living_thing", True)
    ck("does the dog chase the cat", True)
    ck("does the dog not chase the cat", False)        # negated relation
    ck("does the dog chase the cat and is a poodle an animal", True)  # mixed clause types, AND
    ck("is a poodle a living_thing", True)             # 3-hop atomic
    npass=sum(r[1] for r in res); n=len(res)
    for q,ok,got,exp in res:
        if not ok: print(f"   FAIL: '{q}' -> got {got}, expected {exp}", flush=True)
    print(f"\n   Boolean battery: {npass}/{n} = {npass/n*100:.1f}%", flush=True)
    print("--- VERDICT ---", flush=True)
    if npass==n:
        print("JEP-93: PASS - engine tier 2 holds 100% with Boolean AND/OR/NOT composition (Boole's connectives).",flush=True)
    else:
        print(f"JEP-93: NOT YET 100% - {npass/n*100:.1f}%. Diagnose vs prediction, fix, re-run.",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
