"""JEP-194 - re-validate the FULLY MATURED engine (all features through JEP-193): fuzz ROBUST + SOUND."""
import random, string
import numpy as np
from world.understanding import UnderstandingEngine
def fuzz():
    rnd=random.Random(194)
    toks=["dog","cat","heart","virus","fever","mammal","animal","bigger","than","part","of","causes","is","a","an",
          "located","in","has","furniture","water","form","of","government","not","kind","such","as","more","which"]
    junk=["", " ", ".", "is is is", "bigger than than", "part of of", "a of a", "such as as as", "X of of Y",
          "is bigger than a than", r"\x", "((", "?"*30, "of of of", "is a is a is a", "more more than"]
    def sent():
        if rnd.random()<0.3: return rnd.choice(junk)
        n=rnd.randint(1,8)
        return ("a " if rnd.random()<0.5 else "")+" ".join(
            rnd.choice(toks) if rnd.random()<0.75 else ''.join(rnd.choice(string.printable) for _ in range(rnd.randint(0,5)))
            for _ in range(n))+rnd.choice([".","","?"])
    crashes=[]
    for i in range(6000):
        e=UnderstandingEngine(seed=i%40)
        passage=". ".join(sent() for _ in range(rnd.randint(1,5)))
        try:
            e.read(passage)
            for q in ["is a dog an animal?","is a heart part of a dog?","does a virus cause a fever?",
                      "is a dog bigger than a cat?","what causes a fever?","describe a dog","why?"]:
                e.describe("a dog") if q=="describe a dog" else e.respond(q)
        except Exception as ex:
            if len(crashes)<8: crashes.append((repr(passage)[:60],type(ex).__name__,str(ex)[:70]))
    return crashes
def soundness():
    rnd=random.Random(3); viol=[]
    for t in range(300):
        e=UnderstandingEngine(seed=t)
        ks=[f"k{i}" for i in range(rnd.randint(3,6))]
        for i in range(len(ks)-1): e.tell(f"a {ks[i]} is a {ks[i+1]}.")
        e.tell_part("p0",ks[0]); e.tell_cause("c0",ks[0]); e.tell(f"a {ks[0]} is bigger than a sm.")
        # comparison/is-a interaction soundness: a subtype of the smaller side is also smaller
        for k in ks:
            if e.is_a(k,ks[0]) and k!=ks[0]:    # k is a subtype of ks[0]
                if not e._order_holds("bigger",ks[0],k):  # ks[0] should NOT be bigger than its own supertype-path... 
                    pass  # (ks[0] bigger than sm, k is-a ks[0]: k is bigger than sm, not the reverse)
        # invariant: ks[0] bigger than sm; any SUBTYPE of ks[0] is bigger than sm (cause-side inheritance)
        for k in ks:
            if k!=ks[0] and e.is_a(k,ks[0]):
                if not e._order_holds("bigger",k,"sm"): viol.append(("cmp-subtype",t,k))
        # leak: ks[0] is NOT bigger than an unrelated sibling
        if e._order_holds("bigger","sm",ks[0]): viol.append(("cmp-asym",t))
    return viol
def main():
    print("=== JEP-194: re-validate the FULLY MATURED engine (through JEP-193) ===", flush=True)
    c=fuzz(); print(f"[FUZZ] 6000 adversarial passages (incl comparison/of/mass-noun forms) x read+7 queries; crashes: {len(c)}", flush=True)
    for p,et,em in c: print(f"   CRASH read({p}) -> {et}: {em}", flush=True)
    v=soundness(); print(f"[SOUNDNESS] 300 taxonomies x comparison-interaction invariants; violations: {len(v)}", flush=True)
    for x in v[:8]: print(f"   VIOLATION {x}", flush=True)
    print(f"\n--- VERDICT --- {'ROBUST + SOUND' if not c and not v else 'ISSUES (valuable)'}: crashes={len(c)}, violations={len(v)}", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
