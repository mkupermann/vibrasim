"""JEP-143 - temporal persistence / frame problem. Target 100%."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-143: temporal reasoning with persistence (frame problem), target 100% ===", flush=True)
    e=UnderstandingEngine(seed=143)
    # t0: open door; t1: turn on light; t2: close door; t3: (unrelated) sit down
    e.event("open the door", {"door_open": True})
    e.event("turn on the light", {"light_on": True})
    e.event("close the door", {"door_open": False})
    e.event("sit down", {"seated": True})
    res=[]; ck=lambda n,g,x: res.append((n,g==x,g,x))
    ck("door open at t0 (just opened)", e.fluent_at("door_open",0), True)
    ck("door open at t1 (persists, light event doesn't touch it)", e.fluent_at("door_open",1), True)
    ck("door open at t2 (just closed)", e.fluent_at("door_open",2), False)
    ck("door open now (stays closed)", e.fluent_at("door_open"), False)
    ck("light on at t0 (not yet)", e.fluent_at("light_on",0), None)
    ck("light on at t1 (just turned on)", e.fluent_at("light_on",1), True)
    ck("light on now (persists, never turned off)", e.fluent_at("light_on"), True)
    ck("seated at t1 (not yet)", e.fluent_at("seated",1), None)
    ck("seated now", e.fluent_at("seated"), True)
    npass=0
    for n,ok,g,x in res:
        npass+=ok
        if not ok: print(f"   FAIL {n}: got {g} exp {x}", flush=True)
        else: print(f"   [ok] {n}: {g}", flush=True)
    print(f"\n   temporal battery: {npass}/{len(res)} = {npass/len(res)*100:.0f}%", flush=True)
    print("JEP-143: PASS - fluents PERSIST across events until changed (frame axiom); state-at-time correct." if npass==len(res)
          else f"JEP-143: NOT YET - {npass}/{len(res)}", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
