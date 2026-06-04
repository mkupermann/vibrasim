"""JEP-107 - simple recency coreference: resolve it/they to last subject; measure where it works/fails."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-107: pronoun coreference (recency), honestly measured ===", flush=True)
    e=UnderstandingEngine(seed=107)
    discourse=[
        ("A robin is a bird.", None),
        ("It is an animal.", ("robin","animal","isa-correct: subject antecedent")),   # it=robin, robin IS animal OK
        ("An animal is a living thing.", None),
        ("It can move.", ("animal","move","prop-correct: subject antecedent")),        # it=animal OK
        ("A sparrow is a bird.", None),
        ("They can fly.", ("sparrow","fly","they=sparrow, topic continuity")),         # they=sparrow OK
    ]
    correct=0; total=0
    for sent,exp in discourse:
        t=e.tell(sent)
        print(f"   tell {sent!r:42} -> {t}", flush=True)
    # verify the resolved facts
    checks=[
        ("robin is an animal (from 'It is an animal')", e.is_a("robin","animal"), True),
        ("animal can move (from 'It can move')", e.has_property("animal","move"), True),
        ("sparrow can fly (from 'They can fly')", e.has_property("sparrow","fly"), True),
        ("robin is a living thing (multi-hop via resolved chain)", e.is_a("robin","living thing"), True),
    ]
    for n,g,x in checks:
        ok=(g==x); correct+=ok; total+=1
        print(f"   [{'ok' if ok else 'MISS'}] {n}: {g}", flush=True)
    # no-antecedent rejection (fresh engine)
    e2=UnderstandingEngine(seed=108)
    rej = e2.tell("It is an animal.")[0]=="none"
    print(f"   no-antecedent 'It is an animal' rejected: {rej}", flush=True)
    print(f"\n   recency-coreference correctness: {correct}/{total} on topic-continuity discourse; no-antecedent rejected: {rej}", flush=True)
    print("   HONEST: works for SUBJECT antecedents (topic continuity); object-antecedent cases would mis-resolve -", flush=True)
    print("   the known hard part of coreference. Recency is the simplest baseline, not a solver.", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
