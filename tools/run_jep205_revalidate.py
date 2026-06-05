"""JEP-205 - re-validate the matured engine (through JEP-204): fuzz the NEW capabilities (open relations, proper nouns, unified read)."""
import random, string
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-205: re-validate matured engine (open relations + proper nouns + unified read) ===", flush=True)
    rnd=random.Random(205)
    words=["Paris","France","dog","mammal","is","the","capital","of","London","England","discovered",
           "X","Y","is capital of","A","an","not","causes","part","Berlin","Germany","Einstein"]
    junk=["", " ", "is the of of", "Capital Of Of", "X is is is Y", "A B C D E F", "the the the of of",
          r"\x", "((", "?"*20, "is capital of of of", "A. B. C. A. B. C.", "X Y. X Z. X W."]
    def sent():
        if rnd.random()<0.3: return rnd.choice(junk)
        n=rnd.randint(1,7)
        return " ".join(rnd.choice(words) if rnd.random()<0.8 else
                        ''.join(rnd.choice(string.printable) for _ in range(rnd.randint(0,5))) for _ in range(n))+rnd.choice([".","","?"])
    crashes=[]
    for i in range(6000):
        e=UnderstandingEngine(seed=i%40)
        passage=". ".join(sent() for _ in range(rnd.randint(1,6)))
        try:
            e.read(passage)                          # unified read (fixed + open + proper-noun detection)
            e.read_open(passage)
            e.learn_relation([sent() for _ in range(rnd.randint(0,3))])
            for q in ["is a dog an animal?","what is a dog?","describe dog","summarize"]:
                e.summarize() if q=="summarize" else (e.describe("dog") if q=="describe dog" else e.respond(q))
            e.extract_relation(sent())
            e.consistency_audit()
        except Exception as ex:
            if len(crashes)<8: crashes.append((repr(passage)[:55],type(ex).__name__,str(ex)[:70]))
    print(f"[FUZZ] 6000 adversarial passages x (read+read_open+learn_relation+describe+summarize+extract+audit); crashes: {len(crashes)}", flush=True)
    for p,et,em in crashes: print(f"   CRASH ({p}) -> {et}: {em}", flush=True)
    print(f"\n--- VERDICT --- {'ROBUST' if not crashes else 'CRASHES FOUND (valuable)'}: {len(crashes)} crashes", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
