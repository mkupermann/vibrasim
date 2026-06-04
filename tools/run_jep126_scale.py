"""JEP-126 - scale: 1000-concept deep taxonomy, verify correctness + measure query latency."""
import numpy as np, time
from world.understanding import UnderstandingEngine
rng=np.random.default_rng(126)
def main():
    print("=== JEP-126: scale validation (1000 concepts, deep hierarchy) ===", flush=True)
    N=1000
    concepts=[f"c{i}" for i in range(N)]
    # deep DAG: each concept points to 1-2 higher-indexed (depth emerges)
    ref_parents={c:set() for c in concepts}
    e=UnderstandingEngine(seed=1)
    t0=time.time()
    for i in range(N-1):
        npar=int(rng.integers(1,3))
        for _ in range(npar):
            j=int(rng.integers(i+1,min(i+50,N)))   # parent within 50 ahead -> builds depth
            ref_parents[concepts[i]].add(concepts[j])
    for c in concepts:
        for p in ref_parents[c]: e.tell(f"A {c} is a {p}.")
    build_t=time.time()-t0
    def ref_anc(x):
        out=set(); stack=[x]
        while stack:
            cur=stack.pop()
            for p in ref_parents.get(cur,()):
                if p not in out: out.add(p); stack.append(p)
        return out
    # correctness on a sample
    mism=0; checks=0
    for _ in range(2000):
        x=concepts[int(rng.integers(N))]; c=concepts[int(rng.integers(N))]
        if x==c: continue
        checks+=1; mism+=int(e.is_a(x,c)!=(c in ref_anc(x)))
    # latency
    t0=time.time()
    for _ in range(2000):
        x=concepts[int(rng.integers(N))]; c=concepts[int(rng.integers(N))]; e.is_a(x,c)
    qt=(time.time()-t0)/2000*1000
    # depth
    maxd=max(len(ref_anc(c)) for c in concepts[:200])
    print(f"   built {N} concepts in {build_t:.2f}s; max ancestor-set size (sampled) {maxd}", flush=True)
    print(f"   correctness: {checks-mism}/{checks} match reference; mean is_a query {qt:.3f} ms", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if mism==0 and qt<5:
        print(f"JEP-126: PASS - at 1000 concepts the engine is CORRECT (0 mismatches vs reference) and FAST",flush=True)
        print(f"({qt:.2f} ms/query). The core reasoning scales to real-size knowledge bases. Established, named; no novelty.",flush=True)
    else:
        print(f"JEP-126: PARTIAL - {mism} mismatches, {qt:.2f} ms/query. Recorded honestly.",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
