"""GEO-63 — performance benchmark: indexing + query latency at N=10/100/1000."""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from geometric_reasoner import GeometricReasoner

# NOTE: time.time via perf_counter-like; the workflow forbids Date.now in JS but Python time is fine here.
import time as _t


def main():
    print("=== GEO-63: performance benchmark (CPU) ===", flush=True)
    # warm the model once (download/load excluded from per-query timing)
    base=GeometricReasoner(abstain_tau=0.0); base.add_fact("warmup fact.", subject="w", object="w"); _=base.F
    for N in [10,100,1000]:
        r=GeometricReasoner(abstain_tau=0.0)
        for i in range(N):
            r.add_fact(f"Person{i} works at Company{i} in City{i}.", subject=f"Person{i}", object=f"Company{i}")
        t0=_t.perf_counter(); _=r.F; idx=_t.perf_counter()-t0   # index build = embed all facts
        qs=[f"Where does Person{i} work?" for i in range(0,N,max(1,N//20))][:20]
        # per-query (no rerank): embed + retrieve
        t0=_t.perf_counter()
        for q in qs: r.retrieve(q)
        per=(_t.perf_counter()-t0)/len(qs)*1000
        print(f"  N={N:4d}  index-build={idx*1000:6.0f}ms  per-query={per:6.1f}ms  ({1000/per:.0f} q/s)", flush=True)
    # rerank cost at N=1000
    rr=GeometricReasoner(abstain_tau=0.0, rerank_k=10)
    for i in range(1000): rr.add_fact(f"Person{i} works at Company{i}.", subject=f"Person{i}", object=f"Company{i}")
    _=rr.F; q="Where does Person500 work?"; rr.retrieve(q)  # warm CE
    t0=_t.perf_counter()
    for _ in range(10): rr.retrieve(q)
    per_rr=(_t.perf_counter()-t0)/10*1000
    print(f"  N=1000 + rerank_k=10  per-query={per_rr:6.1f}ms", flush=True)
    print("\n--- VERDICT ---", flush=True)
    print("GEO-63: characterization — latency curve above is the finding (interactive if per-query < ~100ms).", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
