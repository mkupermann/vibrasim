"""JEP-150 - mereology (part-whole) distinct from IS-A. Target 100%."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-150: mereology (part-whole) vs IS-A, target 100% ===", flush=True)
    e=UnderstandingEngine(seed=150)
    e.tell_part("finger","hand"); e.tell_part("hand","arm"); e.tell_part("arm","body")
    e.tell("A finger is a body_part."); e.tell("A body_part is a thing.")
    res=[]; ck=lambda n,g,x: res.append((n,g==x,g,x))
    ck("finger part-of hand (direct)", e.part_of("finger","hand"), True)
    ck("finger part-of body (transitive)", e.part_of("finger","body"), True)
    ck("finger part-of arm (transitive)", e.part_of("finger","arm"), True)
    ck("body NOT part-of finger (asymmetric)", e.part_of("body","finger"), False)
    # DISTINCTNESS from is-a: finger is part-of body but is NOT a body
    ck("finger is NOT a body (part-of != is-a)", e.is_a("finger","body"), False)
    ck("finger is NOT a hand (part-of != is-a)", e.is_a("finger","hand"), False)
    ck("finger IS a body_part (separate is-a graph)", e.is_a("finger","thing"), True)
    ck("finger NOT part-of thing (is-a doesn't leak into part-of)", e.part_of("finger","thing"), False)
    npass=0
    for n,ok,g,x in res:
        npass+=ok
        if not ok: print(f"   FAIL {n}: got {g} exp {x}", flush=True)
        else: print(f"   [ok] {n}", flush=True)
    print(f"\n   mereology battery: {npass}/{len(res)} = {npass/len(res)*100:.0f}%", flush=True)
    print("JEP-150: PASS - part-of is transitive AND distinct from is-a (a finger is part of a body, not a body)." if npass==len(res)
          else f"JEP-150: NOT YET - {npass}/{len(res)}", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
