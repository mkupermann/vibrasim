"""JEP-50 - order vs poincare is-a on BALANCED vs IRREGULAR trees (test the irregularity hypothesis)."""
import numpy as np
from tools.concept_reasoner import ConceptReasoner
rng=np.random.default_rng(50)
def balanced(depth):
    tax={};frontier=["n0"]
    for d in range(depth):
        new=[]
        for p in frontier:
            ch=[f"{p}_{i}" for i in range(2)];tax[p]=ch;new+=ch
        frontier=new
    return tax
def irregular(target=250):
    tax={};cnt=[0];root="r"; 
    def grow(node,depth):
        if cnt[0]>=target or depth>9: return
        k=int(rng.integers(1,5))  # 1-4 children (irregular branching)
        if rng.random()<0.25 and depth>2: return  # random early termination (variable depth)
        ch=[]
        for i in range(k):
            if cnt[0]>=target: break
            c=f"{node}_{i}_{cnt[0]}";cnt[0]+=1;ch.append(c)
        if ch:
            tax[node]=ch
            for c in ch: grow(c,depth+1)
    grow(root,0)
    return tax
def evalm(TAX,method):
    cr=ConceptReasoner(TAX)
    ALL=[(u,v) for v in range(cr.N) for u in cr._ancestors(v)]
    r=np.random.default_rng(0);idx=r.permutation(len(ALL));cut=max(1,int(0.3*len(ALL)));HO=set(ALL[i] for i in idx[:cut])
    cr.fit(euc_dim=6,hyp_dim=16,iters=9000,holdout_pairs=HO,isa_method=method)
    tp=np.mean([cr.is_a(cr.nodes[v],cr.nodes[u]) for (u,v) in HO])
    ANC=set(ALL);neg=[];t=0
    while len(neg)<len(HO) and t<30000:
        a,b=int(r.integers(cr.N)),int(r.integers(cr.N));t+=1
        if a!=b and (a,b) not in ANC: neg.append((a,b))
    tn=np.mean([not cr.is_a(cr.nodes[b],cr.nodes[a]) for (a,b) in neg]) if neg else 1.0
    return cr.N,(tp+tn)/2
def main():
    print("=== JEP-50: order vs poincare on BALANCED vs IRREGULAR trees ===", flush=True)
    bal=balanced(7); irr=irregular(250)
    for label,TAX in [("BALANCED",bal),("IRREGULAR",irr)]:
        N,p=evalm(TAX,"poincare"); _,o=evalm(TAX,"order")
        print(f"  {label:9} N={N:>3}: poincare={p:.3f}  order={o:.3f}  gap(order-poincare)={o-p:+.3f}", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
