"""JEP-94 - engine parse robustness: varied IS-A phrasings must yield the same structure (target 100%)."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-94: engine tier 3 - parse robustness on varied phrasings (target 100%) ===", flush=True)
    # the SAME facts phrased many ways
    variants=[
        "A poodle is a dog.","Poodles are dogs.","A poodle is a kind of dog.","Every poodle is a dog.",
        "A dog is an animal.","Dogs are animals.","Dogs are a type of animal.",
        "An animal is a living_thing.","Animals are living_things.","All animals are living_things.",
    ]
    eng=UnderstandingEngine(seed=94)
    parsed=[(v, eng.tell(v)) for v in variants]
    res=[]
    def ck(name, got, exp): res.append((name, got==exp, got, exp))
    # every variant must parse to an isa
    for v,t in parsed: ck(f"parse: {v}", t[0], "isa")
    # the extracted edges must be the intended ones
    ck("poodle->dog", "dog" in eng.parents.get("poodle", set()), True)
    ck("dog->animal", "animal" in eng.parents.get("dog", set()), True)
    ck("animal->living thing", "living thing" in eng.parents.get("animal", set()), True)
    # comprehension incl multi-hop holds
    ck("poodle is animal (2-hop)", eng.is_a("poodle","animal"), True)
    ck("poodle is living_thing (3-hop)", eng.is_a("poodle","living_thing"), True)
    ck("poodle is NOT fish", eng.is_a("poodle","fish"), False)
    npass=sum(r[1] for r in res); n=len(res)
    for name,ok,got,exp in res:
        if not ok: print(f"   FAIL: {name}: got {got!r}, expected {exp!r}", flush=True)
    print(f"\n   parse-robustness battery: {npass}/{n} = {npass/n*100:.1f}%", flush=True)
    print("--- VERDICT ---", flush=True)
    if npass==n:
        print("JEP-94: PASS - engine tier 3 holds 100%: varied phrasings of the same facts all yield the correct",flush=True)
        print("structure and comprehension. The parse boundary scaled outward one controlled tier.",flush=True)
    else:
        print(f"JEP-94: NOT YET 100% - {npass/n*100:.1f}%. Diagnose vs prediction, fix, re-run.",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
