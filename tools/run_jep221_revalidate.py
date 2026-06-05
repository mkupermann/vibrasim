"""JEP-221 - final robustness check including the conversational features (follow-up, why-all-chains)."""
import random, string
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-221: final robustness — conversational features + all queries ===", flush=True)
    rnd=random.Random(221)
    words=["dog","mammal","animal","is","a","bigger","than","cat","before","after","war","peace","has","4","legs",
           "what","about","why","Paris","capital","of","France","the","biggest","first","all","mammals"]
    junk=["","why","what about","what about ?","why why why","what about a a a","and","how about of of",
          "what about the the", r"\x","?"*12,"what about an"]
    def sent():
        if rnd.random()<0.3: return rnd.choice(junk)
        n=rnd.randint(1,7); return " ".join(rnd.choice(words) if rnd.random()<0.8 else ''.join(rnd.choice(string.printable) for _ in range(rnd.randint(0,4))) for _ in range(n))+rnd.choice([".","","?"])
    crashes=[]
    convo=["is a dog an animal?","what about a cat?","why?","is an elephant bigger than a cat?","why?",
           "what about a rock?","and a fish?","what about ?","why?","what are all the mammals?","what about a mammal?"]
    for i in range(6000):
        e=UnderstandingEngine(seed=i%40)
        try:
            e.read(". ".join(sent() for _ in range(rnd.randint(1,4))))
            for q in convo + [sent()+"?" for _ in range(3)]:    # the canned convo + fuzzed questions, in sequence
                e.respond(q)
            e.summarize(); e.consistency_audit()
        except Exception as ex:
            if len(crashes)<8: crashes.append((type(ex).__name__,str(ex)[:75]))
    print(f"[FUZZ] 6000 engines x (read + 11-turn convo + 3 fuzzed Qs + summarize + audit); crashes: {len(crashes)}", flush=True)
    for et,em in crashes: print(f"   CRASH {et}: {em}", flush=True)
    print(f"\n--- VERDICT --- {'ROBUST' if not crashes else 'CRASHES'}: {len(crashes)}", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
