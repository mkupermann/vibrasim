"""JEP-109 - contradiction detection (consistency checking). Target 100%."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-109: contradiction detection, target 100% ===", flush=True)
    e=UnderstandingEngine(seed=109)
    for f in ["A whale is a mammal.","A mammal is an animal."]:
        e.tell(f)
    res=[]; ck=lambda n,g,x: res.append((n,(g is not None)==x,g,x))
    ck("'whale is not a mammal' contradicts (direct)", e.would_contradict("A whale is not a mammal."), True)
    ck("'whale is not an animal' contradicts (via closure)", e.would_contradict("A whale is not an animal."), True)
    ck("'whale is a fish' no conflict (unknown)", e.would_contradict("A whale is a fish."), False)
    ck("'whale is a mammal' no conflict (already true)", e.would_contradict("A whale is a mammal."), False)
    # now explicitly negate, then the positive contradicts
    e.tell("A whale is not a fish.")
    ck("'whale is a fish' contradicts (explicit negative)", e.would_contradict("A whale is a fish."), True)
    # correction still works (non-blocking)
    e.tell("A shark is a fish."); e.tell("A shark is not a fish.")
    ck("correction not blocked (shark not a fish now)", (not e.is_a("shark","fish")) or None, True)
    for n,ok,g,x in res:
        print(f"   [{'ok' if ok else 'MISS'}] {n}: {g}", flush=True)
    npass=sum(r[1] for r in res); n=len(res)
    print(f"\n   contradiction battery: {npass}/{n} = {npass/n*100:.1f}%", flush=True)
    print("JEP-109: PASS - the engine detects contradictions (consistency checking), non-blocking." if npass==n
          else f"JEP-109: NOT YET 100% - {npass/n*100:.1f}%.", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
