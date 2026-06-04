"""JEP-110 - quantified questions: universal IS-A + universal property with exceptions. Target 100%."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-110: quantified questions (every/all), target 100% ===", flush=True)
    e=UnderstandingEngine(seed=110)
    for f in ["A poodle is a dog.","A dog is an animal.","A robin is a bird.","A sparrow is a bird.",
              "A penguin is a bird.","A robin can fly.","A sparrow can fly.","A penguin cannot fly."]:
        e.tell(f)
    e.induce()
    cases=[
        ("is every dog an animal?", "Yes."),
        ("are all poodles dogs?", "Yes."),
        ("is every poodle an animal?", "Yes."),                 # multi-hop universal
        ("can all birds fly?", "No — not all. For example, a penguin cannot fly."),
        ("do all robins fly?", "Yes, all robins can fly."),     # robin has no exception
    ]
    res=[]
    for q,exp in cases:
        got=e.respond(q); ok=(got==exp); res.append(ok)
        print(f"   Q: {q}\n   A: {got}", flush=True)
        if not ok: print(f"   !! expected: {exp}", flush=True)
    npass=sum(res); n=len(res)
    print(f"\n   quantifier battery: {npass}/{n} = {npass/n*100:.1f}%", flush=True)
    print("JEP-110: PASS - quantified reasoning (every/all) works, with named counterexamples." if npass==n
          else f"JEP-110: NOT YET 100% - {npass/n*100:.1f}%.", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
