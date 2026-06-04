"""JEP-119 - compositional queries (relation + taxonomy), target 100%."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-119: compositional queries (relation + taxonomy), target 100% ===", flush=True)
    e=UnderstandingEngine(seed=119)
    for f in ["A cat is an animal.","A mouse is an animal.","the dog chases the cat.","the cat eats the mouse.",
              "A car is a vehicle."]:
        e.tell(f)
    cases=[
        ("is what the dog chases an animal?", "Yes."),    # dog chases cat; cat is animal
        ("is what the cat eats an animal?", "Yes."),       # cat eats mouse; mouse is animal
        ("is what the dog chases a vehicle?", "No."),       # cat is not a vehicle
        ("is what the bird chases an animal?", None),       # unknown relation -> don't know
    ]
    res=[]
    for q,exp in cases:
        got=e.respond(q)
        ok = (got==exp) if exp is not None else got.startswith("I don't know")
        res.append(ok); print(f"   Q: {q}\n   A: {got}", flush=True)
        if not ok: print(f"   !! expected: {exp}", flush=True)
    npass=sum(res); n=len(res)
    print(f"\n   compositional battery: {npass}/{n} = {npass/n*100:.1f}%", flush=True)
    print("JEP-119: PASS - the engine COMPOSES relation + taxonomy reasoning for novel queries." if npass==n
          else f"JEP-119: NOT YET 100% - {npass/n*100:.1f}%.", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
