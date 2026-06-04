"""JEP-104 - multi-parent (DAG) taxonomy: a concept can have several parents. Target 100%."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-104: multi-parent DAG taxonomy, target 100% ===", flush=True)
    e=UnderstandingEngine(seed=104)
    for f in ["A poodle is a dog.","A poodle is a pet.","A dog is an animal.","A pet is owned.",
              "An animal is a living thing."]:
        e.tell(f)
    res=[]; ck=lambda n,g,x: res.append((n,g==x,g,x))
    ck("poodle parents = {dog,pet}", e.parents.get("poodle")=={"dog","pet"}, True)
    ck("poodle is a dog", e.is_a("poodle","dog"), True)
    ck("poodle is a pet", e.is_a("poodle","pet"), True)
    ck("poodle is an animal (via dog)", e.is_a("poodle","animal"), True)
    ck("poodle is owned (via pet)", e.is_a("poodle","owned"), True)
    ck("poodle is a living thing (via dog->animal)", e.is_a("poodle","living thing"), True)
    ck("poodle is NOT a fish", e.is_a("poodle","fish"), False)
    print(f"   what is a poodle? -> {e.respond('what is a poodle?')}", flush=True)
    print(f"   explain animal:   -> {e.explain('is a poodle an animal?')}", flush=True)
    npass=sum(r[1] for r in res); n=len(res)
    for nm,ok,g,x in res:
        if not ok: print(f"   FAIL {nm}: got {g!r} exp {x!r}", flush=True)
    print(f"\n   DAG battery: {npass}/{n} = {npass/n*100:.1f}%", flush=True)
    print("JEP-104: PASS - multi-parent DAG taxonomy works (a poodle is BOTH a dog and a pet)." if npass==n
          else f"JEP-104: NOT YET 100% - {npass/n*100:.1f}%.", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
