"""JEP-148 - causal/means-ends planning. Target 100%."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-148: causal planning (achieve a goal effect), target 100% ===", flush=True)
    e=UnderstandingEngine(seed=148)
    for x,y in [("rain","wetgrass"),("sprinkler","wetgrass"),("wetgrass","slippery"),
                ("press_button","sprinkler")]:   # press_button -> sprinkler -> wetgrass -> slippery (multi-step root)
        e.tell_cause(x,y)
    res=[]; ck=lambda n,g,x: res.append((n,g==x,g,x))
    ck("achieve(slippery): root actions = rain, press_button (sprinkler not a root)", e.achieve("slippery"), ["press_button","rain"])
    ck("achieve(wetgrass): rain, press_button", e.achieve("wetgrass"), ["press_button","rain"])
    ck("achieve(rain): rain is already a root, nothing causes it -> []", e.achieve("rain"), [])
    ck("achieve(unknown): []", e.achieve("flying"), [])
    print(f"   achieve(slippery) -> {e.achieve('slippery')}  (actionable root causes)", flush=True)
    npass=0
    for n,ok,g,x in res:
        npass+=ok
        if not ok: print(f"   FAIL {n}: got {g} exp {x}", flush=True)
        else: print(f"   [ok] {n}: {g}", flush=True)
    print(f"\n   causal-planning battery: {npass}/{len(res)} = {npass/len(res)*100:.0f}%", flush=True)
    print("JEP-148: PASS - causal/means-ends planning: to achieve an effect, do the action whose consequences reach it." if npass==len(res)
          else f"JEP-148: NOT YET - {npass}/{len(res)}", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
