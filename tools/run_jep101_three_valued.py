"""JEP-101 - three-valued comprehension: Yes / No / I-don't-know (epistemic humility). Target 100%."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-101: three-valued comprehension (Yes/No/I-don't-know), target 100% ===", flush=True)
    e=UnderstandingEngine(seed=101)
    for f in ["A poodle is a dog.","A dog is an animal.","A salmon is a fish.","A fish is an animal.",
              "A whale is not a fish."]:
        e.tell(f)
    cases=[
        ("poodle","animal","yes"),      # path
        ("poodle","dog","yes"),
        ("poodle","fish","no"),         # fish is KNOWN, no path -> no
        ("whale","fish","no"),          # explicit negative
        ("poodle","vegetable","unknown"),  # vegetable never heard of -> unknown
        ("salmon","mineral","unknown"),
    ]
    res=[]
    for x,c,exp in cases:
        got=e.assess(x,c); ok=(got==exp); res.append(ok)
        print(f"   assess({x},{c}) = {got}  (expected {exp}){'  **MISS**' if not ok else ''}", flush=True)
    # natural-language epistemic responses
    print(f"   explain('is a poodle a vegetable?') -> {e.explain('is a poodle a vegetable?')}", flush=True)
    print(f"   explain('is a poodle a fish?')      -> {e.explain('is a poodle a fish?')}", flush=True)
    print(f"   explain('is a poodle an animal?')   -> {e.explain('is a poodle an animal?')}", flush=True)
    npass=sum(res); n=len(res)
    print(f"\n   three-valued battery: {npass}/{n} = {npass/n*100:.1f}%", flush=True)
    print("JEP-101: PASS - the engine knows what it does NOT know (Yes/No/I-don't-know)." if npass==n
          else f"JEP-101: NOT YET 100% - {npass/n*100:.1f}%. Diagnose vs prediction.", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
