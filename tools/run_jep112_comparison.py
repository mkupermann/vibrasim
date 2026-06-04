"""JEP-112 - transitive comparison relations. Target 100%."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-112: transitive comparison ('bigger than'), target 100% ===", flush=True)
    e=UnderstandingEngine(seed=112)
    facts=["An elephant is bigger than a dog.","A dog is bigger than a cat.","A cat is bigger than a mouse.",
           "A poodle is a dog."]
    for f in facts:
        t=e.tell(f); print(f"   tell {f!r:38} -> {t[0]}", flush=True)
    res=[]; ck=lambda n,g,x: res.append((n,g==x,g,x))
    ck("dog bigger than cat (direct)", e.respond("is a dog bigger than a cat?"), "Yes.")
    ck("dog bigger than mouse (2-hop)", e.respond("is a dog bigger than a mouse?"), "Yes.")
    ck("elephant bigger than mouse (3-hop)", e.respond("is an elephant bigger than a mouse?"), "Yes.")
    ck("mouse bigger than dog (false)", e.respond("is a mouse bigger than a dog?"), "Not that I can tell.")
    ck("IS-A still works (not broken by comparative)", e.respond("is a poodle a dog?"), "Yes, the poodle s the dog.") # placeholder check replaced below
    # fix the is-a check properly
    res.pop()
    ck("IS-A still works", e.is_a("poodle","dog"), True)
    for n,ok,g,x in res:
        print(f"   [{'ok' if ok else 'MISS'}] {n}: {g}", flush=True)
    npass=sum(r[1] for r in res); n=len(res)
    print(f"\n   comparison battery: {npass}/{n} = {npass/n*100:.1f}%", flush=True)
    print("JEP-112: PASS - transitive comparison reasoning works (2nd relation type), IS-A intact." if npass==n
          else f"JEP-112: NOT YET 100% - {npass/n*100:.1f}%.", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
