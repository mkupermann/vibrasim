"""JEP-121 - hypothetical/counterfactual reasoning, target 100%; KB must be unchanged after."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-121: hypothetical reasoning, target 100% ===", flush=True)
    e=UnderstandingEngine(seed=121)
    for f in ["A fish is an animal.","A bird is an animal.","A whale is a mammal.","A mammal is an animal."]:
        e.tell(f)
    before=dict((k,set(v)) for k,v in e.parents.items())
    cases=[
        ("if a whale were a fish, would it be an animal?", "Yes. A whale is a fish, a fish is an animal."),
        ("if a rock were a bird, would it be an animal?", "Yes. A rock is a bird, a bird is an animal."),
        ("if a whale were a fish, is a whale a vehicle?", None),   # unknown -> don't know / no
    ]
    res=[]
    for q,exp in cases:
        got=e.respond(q)
        ok = (got==exp) if exp is not None else (got.startswith("I don't know") or got.startswith("No"))
        res.append(ok); print(f"   Q: {q}\n   A: {got}", flush=True)
        if not ok: print(f"   !! expected: {exp}", flush=True)
    # KB unchanged?
    after=dict((k,set(v)) for k,v in e.parents.items())
    unchanged = (before==after)
    res.append(unchanged)
    print(f"   KB unchanged after hypotheticals: {unchanged}", flush=True)
    # and a real query still correct (no residue)
    real_ok = e.is_a("whale","animal") and not e.is_a("whale","fish")
    res.append(real_ok); print(f"   real KB intact (whale is animal via mammal, NOT a fish): {real_ok}", flush=True)
    npass=sum(res); n=len(res)
    print(f"\n   hypothetical battery: {npass}/{n} = {npass/n*100:.1f}%", flush=True)
    print("JEP-121: PASS - hypothetical reasoning works and leaves the KB unchanged." if npass==n
          else f"JEP-121: NOT YET 100% - {npass/n*100:.1f}%.", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
