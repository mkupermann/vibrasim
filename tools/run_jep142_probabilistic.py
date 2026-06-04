"""JEP-142 - probabilistic is_a (noisy-OR over paths); quantifies compounding vs aggregation."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-142: probabilistic reasoning (quantifies compounding/aggregation) ===", flush=True)
    e=UnderstandingEngine(seed=142)
    # CHAIN: a->b->c->d each edge p=0.9 (compounding)
    for x,y in [("a","b"),("b","c"),("c","d")]: e.tell_prob(x,y,0.9)
    res=[]; close=lambda g,x,t=0.02: abs(g-x)<t
    ck=lambda n,g,x: res.append((n,close(g,x),round(g,3),x))
    ck("P(a is-a b) = 0.9 (1 hop)", e.is_a_prob("a","b"), 0.9)
    ck("P(a is-a c) = 0.81 (2 hop, compounds)", e.is_a_prob("a","c"), 0.81)
    ck("P(a is-a d) = 0.729 (3 hop, compounds)", e.is_a_prob("a","d"), 0.729)
    # DAG: two independent paths from s to t, each 2 edges @0.9 (path prob 0.81); noisy-OR = 1-(1-.81)^2 = 0.964
    e2=UnderstandingEngine(seed=2)
    for x,y,p in [("s","m1",0.9),("m1","t",0.9),("s","m2",0.9),("m2","t",0.9)]: e2.tell_prob(x,y,p)
    ck("DAG noisy-OR (2 indep paths) = 0.964 > single 0.81", e2.is_a_prob("s","t"), 0.9639)
    npass=0
    for n,ok,g,x in res:
        npass+=ok; print(f"   [{'ok' if ok else 'MISS'}] {n}: got {g}", flush=True)
    print(f"\n   probabilistic battery: {npass}/{len(res)}", flush=True)
    print("   QUANTIFIES the insight: chains MULTIPLY edge-probs (compounding decay 0.9->0.81->0.729);", flush=True)
    print("   redundant DAG paths NOISY-OR to HIGHER confidence (0.964 > 0.81) = aggregation robustness.", flush=True)
    print("JEP-142: PASS - probabilistic reasoning works and quantifies compounding vs aggregation." if npass==len(res)
          else f"JEP-142: NOT YET - {npass}/{len(res)}", flush=True)
    print("HONEST: noisy-OR assumes INDEPENDENT paths; shared edges over-count (a known approximation).", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
