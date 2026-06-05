"""JEP-171 - validate the learn-from-prose -> reason -> communicate pipeline: fuzz ROBUST + property-based SOUND."""
import random, string
from world.understanding import UnderstandingEngine
def fuzz():
    rnd=random.Random(171)
    nouns=["dog","cat","heart","virus","fever","mammal","animal","bird","cell","tree","wolf","poodle"]
    verbs=["is a","is an","is a kind of","is part of","has","causes","is located in","are","is not a","such as"]
    junk=["", " ", ".", ",", "a a a", "is is is", r"\x", "(((", "?"*20, "is part of part of", "a, which is a, b",
          "X and and Y are", "has has has", "located in in in", "a "*40, "\n\t", "123 456 causes 789"]
    def sent():
        if rnd.random()<0.3: return rnd.choice(junk)
        n=rnd.randint(1,6)
        toks=[]
        for _ in range(n):
            r=rnd.random()
            toks.append(rnd.choice(nouns) if r<0.5 else rnd.choice(verbs) if r<0.8 else
                        ''.join(rnd.choice(string.printable) for _ in range(rnd.randint(0,6))))
        return ("a " if rnd.random()<0.5 else "")+" ".join(toks)+rnd.choice([".","","?",", "])
    crashes=[]
    for i in range(6000):
        e=UnderstandingEngine(seed=i%50)
        passage=". ".join(sent() for _ in range(rnd.randint(1,5)))
        try:
            e.read(passage)
            for q in ["is a dog an animal?","is a heart part of a dog?","does a virus cause a fever?",
                      "what causes a fever?","describe a dog"]:
                (e.respond(q) if q!="describe a dog" else e.describe("a dog"))
        except Exception as ex:
            if len(crashes)<10: crashes.append((repr(passage)[:70], type(ex).__name__, str(ex)[:80]))
    return crashes
def soundness():
    """property-based: random valid taxonomies; check the relation-interaction invariants hold."""
    rnd=random.Random(2); viol=[]
    for t in range(400):
        e=UnderstandingEngine(seed=t)
        # build a small random is-a chain + part-of + causal
        kinds=[f"k{i}" for i in range(rnd.randint(3,6))]
        for i in range(len(kinds)-1): e.tell(f"a {kinds[i]} is a {kinds[i+1]}.")
        part="p0"; e.tell_part(part, kinds[0])           # p0 part-of k0 (the most specific)
        e.tell_cause("c0", kinds[0])                      # c0 causes k0
        # INVARIANT 1: p0 is part of every ANCESTOR of k0 (interaction up), and is part of k0 itself
        for anc in [kinds[0]]+ [k for k in kinds if e.is_a(kinds[0],k)]:
            if not e.part_of(part, anc): viol.append(("part-up", t, anc))
        # INVARIANT 2: p0 is NOT is_a anything (part is not type)
        for k in kinds:
            if e.is_a(part, k): viol.append(("part-not-isa", t, k))
        # INVARIANT 3: c0 causes every ANCESTOR of k0 (effect-up), NOT non-ancestors
        for k in kinds:
            should = (k==kinds[0]) or e.is_a(kinds[0], k)
            if e.causes_effect("c0", k) != should: viol.append(("cause-up", t, k, should))
        # INVARIANT 4: asymmetry - k0 is not part of p0, k0 does not cause c0
        if e.part_of(kinds[0], part): viol.append(("part-asym", t))
        if e.causes_effect(kinds[0], "c0"): viol.append(("cause-asym", t))
    return viol
def main():
    print("=== JEP-171: validate learn-from-prose pipeline ===", flush=True)
    crashes=fuzz()
    print(f"\n[FUZZ] 6000 adversarial passages x read+5 queries; crashes: {len(crashes)}", flush=True)
    for p,et,em in crashes: print(f"   CRASH read({p}) -> {et}: {em}", flush=True)
    viol=soundness()
    print(f"\n[SOUNDNESS] 400 random taxonomies x relation-interaction invariants; violations: {len(viol)}", flush=True)
    for v in viol[:10]: print(f"   VIOLATION {v}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    print(f"{'ROBUST + SOUND' if not crashes and not viol else 'ISSUES FOUND (valuable)'}: "
          f"fuzz crashes={len(crashes)}, invariant violations={len(viol)}", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
