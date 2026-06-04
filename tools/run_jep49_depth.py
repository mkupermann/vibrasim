"""JEP-49 - Poincare vs order is-a held-out accuracy vs tree DEPTH (synthetic balanced binary trees)."""
import numpy as np
from tools.concept_reasoner import ConceptReasoner
def tree(depth):
    tax={}; nxt=1; frontier=["n0"]; labels={"n0"}
    for d in range(depth):
        new=[]
        for p in frontier:
            ch=[f"{p}_{i}" for i in range(2)]; tax[p]=ch; new+=ch; labels.update(ch)
        frontier=new
    return tax
def evalm(TAX,method):
    cr=ConceptReasoner(TAX)
    ALL=[(u,v) for v in range(cr.N) for u in cr._ancestors(v)]
    rng=np.random.default_rng(0);idx=rng.permutation(len(ALL));cut=max(1,int(0.3*len(ALL)));HO=set(ALL[i] for i in idx[:cut])
    cr.fit(euc_dim=6,hyp_dim=16,iters=8000,holdout_pairs=HO,isa_method=method)
    tp=np.mean([cr.is_a(cr.nodes[v],cr.nodes[u]) for (u,v) in HO])
    ANC=set(ALL);neg=[]; tries=0
    while len(neg)<len(HO) and tries<20000:
        a,b=int(rng.integers(cr.N)),int(rng.integers(cr.N)); tries+=1
        if a!=b and (a,b) not in ANC: neg.append((a,b))
    tn=np.mean([not cr.is_a(cr.nodes[b],cr.nodes[a]) for (a,b) in neg]) if neg else 1.0
    return cr.N,(tp+tn)/2
def main():
    print("=== JEP-49: held-out IS-A vs tree DEPTH (poincare vs order) ===", flush=True)
    print("   depth  N    poincare  order", flush=True)
    rows=[]
    for depth in [3,5,7,9]:
        TAX=tree(depth)
        N,p=evalm(TAX,"poincare"); _,o=evalm(TAX,"order")
        rows.append((depth,N,p,o)); print(f"   {depth}     {N:>3}   {p:.3f}     {o:.3f}", flush=True)
    print("\n--- FINDING ---", flush=True)
    gaps=[o-p for _,_,p,o in rows]
    print(f"order-minus-poincare gap by depth: {[f'd{d}:{g:+.2f}' for (d,_,_,_),g in zip(rows,gaps)]}", flush=True)
    if gaps[-1] > gaps[0] + 0.05:
        print(f"DEPTH drives the gap: poincare degrades with depth while order stays high, so the order-vs-poincare", flush=True)
        print(f"advantage GROWS with depth. Principled guidance: use order embeddings for DEEP hierarchies; poincare", flush=True)
        print(f"is competitive only on shallow ones. Confirms the JEP-48 cross-domain observation (vehicles shallow).", flush=True)
    else:
        print(f"Depth does not clearly drive the gap (gaps {gaps}); the order advantage is not primarily depth.", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
