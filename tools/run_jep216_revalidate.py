"""JEP-216 - re-validate matured engine (through JEP-215): fuzz the newest capabilities (numeric, temporal, superlatives)."""
import random, string
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-216: re-validate matured engine (numeric + temporal + superlatives + open Q&A) ===", flush=True)
    rnd=random.Random(216)
    words=["dog","has","4","eight","legs","before","after","the","war","peace","is","bigger","than","capital","of",
           "Paris","France","more","what","how","many","happened","first","last","biggest","oldest","a","2","eyes"]
    junk=["","has has has","before after before","what is the est","how many of of","is bigger than than",
          "has 4 4 4","before","what happened","X has Y legs","the the of of","2 2 2 has",r"\x","?"*15]
    def sent():
        if rnd.random()<0.3: return rnd.choice(junk)
        n=rnd.randint(1,8)
        return " ".join(rnd.choice(words) if rnd.random()<0.8 else ''.join(rnd.choice(string.printable) for _ in range(rnd.randint(0,4))) for _ in range(n))+rnd.choice([".","","?"])
    crashes=[]
    qs=["how many legs does a dog have?","does a spider have more legs than a dog?","did the war happen before the peace?",
        "is X after Y?","what happened first?","what is the biggest?","what is the capital of France?","what is the est?","what happened last?"]
    for i in range(6000):
        e=UnderstandingEngine(seed=i%40)
        passage=". ".join(sent() for _ in range(rnd.randint(1,5)))
        try:
            e.read(passage); e.read_open(passage)
            for q in qs: e.respond(q)
            e.consistency_audit(); e.summarize(); e.describe("dog")
        except Exception as ex:
            if len(crashes)<8: crashes.append((repr(passage)[:50],type(ex).__name__,str(ex)[:70]))
    print(f"[FUZZ] 6000 passages x (read+read_open+{len(qs)} queries+audit+summarize+describe); crashes: {len(crashes)}", flush=True)
    for p,et,em in crashes: print(f"   CRASH ({p}) -> {et}: {em}", flush=True)
    print(f"\n--- VERDICT --- {'ROBUST' if not crashes else 'CRASHES (valuable)'}: {len(crashes)}", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
