"""JEP-95 - the engine COMMUNICATES: explain answers + reasoning in English (target 100%)."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-95: engine tier 4 - communicate reasoning in English (target 100%) ===", flush=True)
    eng=UnderstandingEngine(seed=95)
    for f in ["A poodle is a dog.","A dog is an animal.","An animal is a living_thing.",
              "A salmon is a fish.","A fish is an animal.","the dog chases the cat."]:
        eng.tell(f)
    cases=[
        ("is a poodle a living_thing", "Yes. A poodle is a dog, a dog is an animal, an animal is a living thing."),
        ("is a poodle an animal", "Yes. A poodle is a dog, a dog is an animal."),
        ("is a poodle a fish", "No. A poodle is not a fish as far as I know."),
        ("does the dog chase the cat", "Yes, the dog chases the cat."),
        ("does the cat chase the dog", "No, I was not told that the cat chases the dog."),
    ]
    res=[]
    for q,exp in cases:
        got=eng.explain(q); ok=(got==exp); res.append(ok)
        print(f"   Q: {q}", flush=True)
        print(f"   A: {got}", flush=True)
        if not ok: print(f"   !! expected: {exp}", flush=True)
    npass=sum(res); n=len(res)
    print(f"\n   communication battery: {npass}/{n} = {npass/n*100:.1f}%", flush=True)
    print("--- VERDICT ---", flush=True)
    if npass==n:
        print("JEP-95: PASS - the engine COMMUNICATES its reasoning in correct English (content + article + verb",flush=True)
        print("agreement). A step toward human-like communication: it explains WHY, not just yes/no. No transformer.",flush=True)
    else:
        print(f"JEP-95: NOT YET 100% - {npass/n*100:.1f}%. Diagnose vs prediction, fix, re-run.",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
