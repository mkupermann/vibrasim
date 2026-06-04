"""JEP-96 - human-like learning by correction: believe -> correct -> answers flip. Target 100%."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-96: engine tier 5 - learning by correction in dialogue (target 100%) ===", flush=True)
    eng=UnderstandingEngine(seed=96)
    for f in ["A fish is an animal.","A mammal is an animal."]:
        eng.tell(f)
    res=[]; 
    def ck(name, got, exp): res.append((name, got==exp, got, exp))
    # 1) initial (wrong) belief
    eng.tell("A whale is a fish.")
    ck("initially whale is fish", eng.is_a("whale","fish"), True)
    ck("initially whale is animal (via fish)", eng.is_a("whale","animal"), True)
    # 2) CORRECTION
    print("   [correction] 'A whale is not a fish.'  then  'A whale is a mammal.'", flush=True)
    t=eng.tell("A whale is not a fish.")
    ck("negation parsed as neg_isa", t[0], "neg_isa")
    eng.tell("A whale is a mammal.")
    # 3) answers must flip
    ck("after: whale is NOT fish", eng.is_a("whale","fish"), False)
    ck("after: whale IS mammal", eng.is_a("whale","mammal"), True)
    ck("after: whale IS animal (via mammal)", eng.is_a("whale","animal"), True)
    ck("explain: is a whale a fish -> No", eng.explain("is a whale a fish?").startswith("No"), True)
    ck("explain: is a whale an animal -> Yes", eng.explain("is a whale an animal?").startswith("Yes"), True)
    npass=sum(r[1] for r in res); n=len(res)
    for name,ok,got,exp in res:
        if not ok: print(f"   FAIL: {name}: got {got!r}, expected {exp!r}", flush=True)
    print(f"   explain after correction: 'is a whale an animal?' -> {eng.explain('is a whale an animal?')}", flush=True)
    print(f"\n   correction battery: {npass}/{n} = {npass/n*100:.1f}%", flush=True)
    print("--- VERDICT ---", flush=True)
    if npass==n:
        print("JEP-96: PASS - the engine LEARNS BY CORRECTION: a 'not' retracts a wrong belief, a new fact installs",flush=True)
        print("the correction, and its answers + explanations flip accordingly - human-like learning from a teacher.",flush=True)
    else:
        print(f"JEP-96: NOT YET 100% - {npass/n*100:.1f}%. Diagnose vs prediction, fix, re-run.",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
