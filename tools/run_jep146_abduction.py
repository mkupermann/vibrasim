"""JEP-146 - abduction (inference to the best explanation). Target 100%."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-146: abduction (effect -> best cause), target 100% ===", flush=True)
    e=UnderstandingEngine(seed=146)
    for x,y in [("rain","wetgrass"),("sprinkler","wetgrass"),("wetgrass","slippery")]:
        e.tell_cause(x,y)
    res=[]; ck=lambda n,g,x: res.append((n,g==x,g,x))
    ck("abduce(slippery): causes ranked by directness", e.abduce("slippery"), ["wetgrass","rain","sprinkler"])
    ck("abduce(wetgrass): rain & sprinkler (direct)", e.abduce("wetgrass"), ["rain","sprinkler"])
    ck("most direct explanation of slippery = wetgrass", e.abduce("slippery")[0], "wetgrass")
    ck("abduce(rain): no causes (rain is a root)", e.abduce("rain"), [])
    print(f"   abduce(slippery) -> {e.abduce('slippery')}  (most direct first)", flush=True)
    npass=0
    for n,ok,g,x in res:
        npass+=ok
        if not ok: print(f"   FAIL {n}: got {g} exp {x}", flush=True)
        else: print(f"   [ok] {n}", flush=True)
    print(f"\n   abduction battery: {npass}/{len(res)} = {npass/len(res)*100:.0f}%", flush=True)
    print("JEP-146: PASS - abduction works (effect -> candidate causes, most direct/parsimonious first). The third" if npass==len(res)
          else f"JEP-146: NOT YET - {npass}/{len(res)}", flush=True)
    if npass==len(res): print("   inference mode (Peirce): DEDUCTION (cause->effect), INDUCTION (instances->rule), ABDUCTION (effect->cause).", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
