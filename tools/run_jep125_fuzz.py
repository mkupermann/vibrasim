"""JEP-125 - fuzz the parser with random/malformed/adversarial input; the engine must never crash."""
import random, string, traceback
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-125: parser robustness fuzz test ===", flush=True)
    rnd=random.Random(125)
    vocab=["dog","cat","is","are","a","an","the","not","can","bigger","than","what","if","were","and","or",
           "chases","fly","mammal","animal"]
    specials=["", " ", ".", "?", "a", "is", r"\x", "((", "a a a a a a a a a a", "?"*50, "is is is is",
              "A  is  a  .", "the the the", "a\nb\tc", "123 456", "!@#$%^&*()", "is what the", "if , ",
              r"A \1 is a \2.", "dog"*100, "is a a a a an b", "\\", "(((((", r"\g<0>"]
    def rand_sentence():
        kind=rnd.random()
        if kind<0.3: return rnd.choice(specials)
        n=rnd.randint(0,12)
        toks=[rnd.choice(vocab) if rnd.random()<0.7 else ''.join(rnd.choice(string.printable) for _ in range(rnd.randint(0,8))) for _ in range(n)]
        return " ".join(toks)+rnd.choice([".","","?",","])
    crashes=[]; n=8000
    e=UnderstandingEngine(seed=125)
    for i in range(n):
        s=rand_sentence()
        for fn in (e.tell, e.respond, e.describe):
            try: fn(s)
            except Exception as ex:
                if len(crashes)<10: crashes.append((fn.__name__, repr(s)[:60], type(ex).__name__, str(ex)[:80]))
        if i%2000==0: e.induce()  # also exercise induce on the accumulating garbage
    print(f"   fuzzed {n} inputs x 3 entry points; crashes: {len(crashes)}", flush=True)
    for fn,s,et,em in crashes: print(f"      CRASH {fn}({s}) -> {et}: {em}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if not crashes:
        print(f"JEP-125: PASS - 0 crashes across {n} random/malformed/adversarial inputs x 3 entry points. The parser",flush=True)
        print(f"is robust: bad input is handled cleanly (parsed, ignored, or 'none'), never an exception. Established",flush=True)
        print(f"(fuzz testing), named; no novelty.",flush=True)
    else:
        print(f"JEP-125: BUG(S) FOUND - {len(crashes)} crash type(s). Recorded for fix (valuable).",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
