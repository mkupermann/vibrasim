"""JEP-102 - learning through dialogue: inquire (identify gap) -> teach -> know. Target 100%."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-102: learning through dialogue (identify gap -> teach -> know), target 100% ===", flush=True)
    e=UnderstandingEngine(seed=102)
    for f in ["A poodle is a dog.","A dog is an animal."]:   # NOTE: animal->living thing NOT yet known
        e.tell(f)
    res=[]; ck=lambda name,got,exp: res.append((name, got==exp, got, exp))
    # 1) the engine cannot answer yet, and identifies the gap
    ck("before: assess unknown", e.assess("poodle","living thing"), "unknown")
    gap=e.inquire("poodle","living thing")
    print(f"   Q: is a poodle a living thing?", flush=True)
    print(f"   A(before): {e.explain('is a poodle a living thing?')}", flush=True)
    print(f"   engine identifies the gap: {gap}", flush=True)
    ck("gap message correct", gap, "I know a poodle is an animal, but I don't know whether an animal is a living thing.")
    # 2) teach exactly the identified missing link
    print(f"   [teach] An animal is a living thing.", flush=True)
    e.tell("An animal is a living thing.")
    # 3) now it knows
    ck("after: assess yes", e.assess("poodle","living thing"), "yes")
    after=e.explain("is a poodle a living thing?")
    print(f"   A(after):  {after}", flush=True)
    ck("after: full chain", after, "Yes. A poodle is a dog, a dog is an animal, an animal is a living thing.")
    ck("inquire now None", e.inquire("poodle","living thing"), None)
    npass=sum(r[1] for r in res); n=len(res)
    for name,ok,got,exp in res:
        if not ok: print(f"   FAIL: {name}: got {got!r} expected {exp!r}", flush=True)
    print(f"\n   dialogue battery: {npass}/{n} = {npass/n*100:.1f}%", flush=True)
    print("JEP-102: PASS - the engine LEARNS THROUGH DIALOGUE: it asks the right question, is taught, and then knows."
          if npass==n else f"JEP-102: NOT YET 100% - {npass/n*100:.1f}%. Diagnose vs prediction.", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
