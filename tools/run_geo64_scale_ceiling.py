"""GEO-64 — retrieval latency vs N (isolate the cosine scan; find the interactive ceiling)."""
import time as _t
import numpy as np

D=384
def main():
    print("=== GEO-64: scale ceiling (retrieval matmul latency) ===", flush=True)
    rng=np.random.default_rng(0)
    embed_cost_ms=6.0  # measured query-embedding forward pass (GEO-63)
    for N in [1000,10000,50000,200000]:
        F=rng.normal(0,1,(N,D)).astype(np.float32); F/=np.linalg.norm(F,axis=1,keepdims=True)
        qs=[rng.normal(0,1,D).astype(np.float32) for _ in range(50)]
        for q in qs[:3]: _=F@q  # warm
        t0=_t.perf_counter()
        for q in qs:
            sims=F@q; _=int(np.argmax(sims))
        scan=(_t.perf_counter()-t0)/len(qs)*1000
        total=embed_cost_ms+scan
        print(f"  N={N:6d}  retrieval-scan={scan:6.2f}ms  total(+embed)={total:6.1f}ms  {'INTERACTIVE' if total<100 else 'SLOW'}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    print("GEO-64: characterization — the N where total > 100ms (or scan >> 6ms embed) is the brute-force ceiling; beyond it use an ANN index.", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
