"""JEP-100 - conversational WH-questions on the engine (target 100%)."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-100: WH-questions (what is X / what does X do), target 100% ===", flush=True)
    e=UnderstandingEngine(seed=100)
    for f in ["A poodle is a dog.","A dog is an animal.","An animal is a living thing.","the dog chases the cat."]:
        e.tell(f)
    cases=[
        ("what is a poodle?", "A poodle is a dog."),
        ("what is a dog?", "A dog is an animal."),
        ("what is an animal?", "An animal is a living thing."),
        ("what does the dog chase?", "The dog chases the cat."),
        ("what is a unicorn?", "I don't know what a unicorn is."),
        ("what does the cat chase?", "I don't know what the cat chases."),
    ]
    res=[]
    for q,exp in cases:
        got=e.respond(q); ok=(got==exp); res.append(ok)
        print(f"   Q: {q}\n   A: {got}", flush=True)
        if not ok: print(f"   !! expected: {exp}", flush=True)
    npass=sum(res); n=len(res)
    print(f"\n   WH battery: {npass}/{n} = {npass/n*100:.1f}%", flush=True)
    print("--- VERDICT ---", flush=True)
    print("JEP-100: PASS - the engine answers WH-questions conversationally." if npass==n
          else f"JEP-100: NOT YET 100% - {npass/n*100:.1f}%. Diagnose vs prediction.", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
