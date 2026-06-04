"""JEP-105 - inductive generalization from instances, defeasible. Target 100%."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-105: inductive generalization (birds fly; penguins don't), target 100% ===", flush=True)
    e=UnderstandingEngine(seed=105)
    for f in ["A robin is a bird.","A sparrow is a bird.","An eagle is a bird.","A penguin is a bird.","A wren is a bird.",
              "A robin can fly.","A sparrow can fly.","An eagle can fly.","A penguin cannot fly."]:
        e.tell(f)
    e.induce()
    res=[]; ck=lambda n,g,x: res.append((n,g==x,g,x))
    ck("induced: bird has 'fly'", "fly" in e._induced.get("bird",set()), True)
    ck("robin flies (observed)", e.has_property("robin","fly"), True)
    ck("wren flies (INDUCED, never observed)", e.has_property("wren","fly"), True)
    ck("penguin does NOT fly (explicit override)", e.has_property("penguin","fly"), False)
    ck("robin does not 'swim' (not induced)", e.has_property("robin","swim"), False)
    npass=sum(r[1] for r in res); n=len(res)
    for nm,ok,g,x in res:
        if not ok: print(f"   FAIL {nm}: got {g!r} exp {x!r}", flush=True)
    print(f"   induced bird properties: {sorted(e._induced.get('bird',set()))}", flush=True)
    print(f"\n   induction battery: {npass}/{n} = {npass/n*100:.1f}%", flush=True)
    print("JEP-105: PASS - the engine INDUCES a rule from instances and applies it (defeasibly) to new cases."
          if npass==n else f"JEP-105: NOT YET 100% - {npass/n*100:.1f}%.", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
