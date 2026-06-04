"""JEP-111 - 'why?' follow-up questions. Target 100%."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-111: 'why?' follow-up questions, target 100% ===", flush=True)
    e=UnderstandingEngine(seed=111)
    for f in ["A poodle is a dog.","A dog is an animal.","An animal is a living thing.","A salmon is a fish."]:
        e.tell(f)
    res=[]; ck=lambda n,g,x: res.append((n,g==x,g,x))
    # fresh "why"
    ck("why with no prior", e.respond("why?"), "You haven't asked me a question I can justify yet.")
    # yes-answer then why
    e.respond("is a poodle a living thing?")
    ck("why after yes -> chain", e.respond("why?"),
       "Because a poodle is a dog, and a dog is an animal, and an animal is a living thing.")
    # unknown then why
    e.respond("is a poodle a vegetable?")
    ck("why after unknown", e.respond("why?"), "Because I was never told whether a poodle is a vegetable.")
    # no (known, no path) then why
    e.respond("is a poodle a fish?")
    ck("why after no", e.respond("why?"), "Because nothing I was told makes a poodle a fish.")
    for n,ok,g,x in res:
        print(f"   [{'ok' if ok else 'MISS'}] {n}:\n        {g}", flush=True)
        if not ok: print(f"        expected: {x}", flush=True)
    npass=sum(r[1] for r in res); n=len(res)
    print(f"\n   why battery: {npass}/{n} = {npass/n*100:.1f}%", flush=True)
    print("JEP-111: PASS - the engine justifies its answers on 'why?' (conversational context)." if npass==n
          else f"JEP-111: NOT YET 100% - {npass/n*100:.1f}%.", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
