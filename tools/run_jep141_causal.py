"""JEP-141 - causal reasoning with intervention (do-operator). Target 100%."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-141: causal reasoning + intervention (do-operator), target 100% ===", flush=True)
    e=UnderstandingEngine(seed=141)
    # rain -> wet_grass -> slippery ; sprinkler -> wet_grass
    for x,y in [("rain","wetgrass"),("wetgrass","slippery"),("sprinkler","wetgrass")]:
        e.tell_cause(x,y)
    res=[]; ck=lambda n,g,x: res.append((n,g==x,g,x))
    ck("rain causes wetgrass (direct)", e.causes_effect("rain","wetgrass"), True)
    ck("rain causes slippery (2-hop)", e.causes_effect("rain","slippery"), True)
    ck("sprinkler causes slippery (2-hop)", e.causes_effect("sprinkler","slippery"), True)
    ck("slippery does NOT cause rain (asymmetric)", e.causes_effect("slippery","rain"), False)
    # INTERVENTION: do(wetgrass) — set wet grass externally; now rain no longer affects slippery THROUGH wetgrass
    ck("do(wetgrass): rain no longer causes slippery", e.causes_effect("rain","slippery",intervene="wetgrass"), False)
    ck("do(wetgrass): rain still causes wetgrass? no — edge into wetgrass cut", e.causes_effect("rain","wetgrass",intervene="wetgrass"), False)
    # intervention elsewhere doesn't block an unrelated path
    ck("do(sprinkler): rain still causes slippery", e.causes_effect("rain","slippery",intervene="sprinkler"), True)
    npass=0
    for n,ok,g,x in res:
        npass+=ok
        if not ok: print(f"   FAIL {n}: got {g} exp {x}", flush=True)
        else: print(f"   [ok] {n}: {g}", flush=True)
    print(f"\n   causal battery: {npass}/{len(res)} = {npass/len(res)*100:.0f}%", flush=True)
    print("JEP-141: PASS - causal transitive reasoning + intervention (do-operator cuts incoming edges)." if npass==len(res)
          else f"JEP-141: NOT YET - {npass}/{len(res)}", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
