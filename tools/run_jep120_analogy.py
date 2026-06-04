"""JEP-120 - relational analogy ('A is to B as C is to ?'). Target 100%."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-120: relational analogy, target 100% ===", flush=True)
    e=UnderstandingEngine(seed=120)
    for f in ["the dog has the puppy.","the cat has the kitten.","the cow has the calf.",
              "the dog chases the cat."]:
        e.tell(f)
    cases=[
        ("dog is to puppy as cat is to?", "Kitten."),
        ("dog is to puppy as cow is to?", "Calf."),
        ("what is dog is to puppy as cat is to?", "Kitten."),
        ("dog is to puppy as fish is to?", "I can't complete that analogy."),
    ]
    res=[]
    for q,exp in cases:
        got=e.respond(q); ok=(got==exp); res.append(ok)
        print(f"   Q: {q}\n   A: {got}", flush=True)
        if not ok: print(f"   !! expected: {exp}", flush=True)
    npass=sum(res); n=len(res)
    print(f"\n   analogy battery: {npass}/{n} = {npass/n*100:.1f}%", flush=True)
    print("JEP-120: PASS - relational analogy works (find A->B relation, apply to C)." if npass==n
          else f"JEP-120: NOT YET 100% - {npass/n*100:.1f}%.", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
