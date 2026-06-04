"""JEP-145 - provenance + truth maintenance. Target 100%."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-145: provenance / truth maintenance, target 100% ===", flush=True)
    e=UnderstandingEngine(seed=145)
    for f in ["A poodle is a dog.","A dog is an animal.","An animal is a living thing."]:
        e.tell(f)
    res=[]; ck=lambda n,g,x: res.append((n,g==x,g,x))
    ck("provenance(poodle, living thing) = the 3-edge chain",
       e.provenance("poodle","living thing"),
       [("poodle","dog"),("dog","animal"),("animal","living thing")])
    ck("poodle is a living thing (before)", e.is_a("poodle","living thing"), True)
    # retract a supporting fact -> conclusion invalidated (single path)
    e.retract("dog","animal")
    ck("after retracting dog->animal: poodle is NOT a living thing", e.is_a("poodle","living thing"), False)
    ck("provenance now empty (underivable)", e.provenance("poodle","living thing"), [])
    # REDUNDANT path survives retraction
    e2=UnderstandingEngine(seed=2)
    for f in ["A poodle is a dog.","A poodle is a mammal.","A dog is an animal.","A mammal is an animal."]:
        e2.tell(f)
    ck("redundant: poodle is an animal (two paths)", e2.is_a("poodle","animal"), True)
    e2.retract("dog","animal")   # remove ONE path
    ck("after retracting one path: still an animal via mammal", e2.is_a("poodle","animal"), True)
    e2.retract("mammal","animal")  # remove the other
    ck("after retracting BOTH paths: no longer an animal", e2.is_a("poodle","animal"), False)
    npass=0
    for n,ok,g,x in res:
        npass+=ok
        if not ok: print(f"   FAIL {n}: got {g} exp {x}", flush=True)
        else: print(f"   [ok] {n}", flush=True)
    print(f"\n   provenance/TMS battery: {npass}/{len(res)} = {npass/len(res)*100:.0f}%", flush=True)
    print("JEP-145: PASS - provenance tracks justifications; retraction invalidates dependents, redundancy survives." if npass==len(res)
          else f"JEP-145: NOT YET - {npass}/{len(res)}", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
