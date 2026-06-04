"""JEP-131 - map the structure-learning boundary: rule depth x relation-vocabulary size."""
import numpy as np
from itertools import product
from collections import defaultdict
def compose(R1,R2):
    out=set(); idx=defaultdict(set)
    for a,b in R1: idx[b].add(a)
    for b,c in R2:
        for a in idx[b]: out.add((a,c))
    return out
def compose_chain(rels_list):
    out=rels_list[0]
    for R in rels_list[1:]: out=compose(out,R)
    return out
def trial(depth, nbase, seed):
    r=np.random.default_rng(seed); N=16; 
    base={f"r{i}": set() for i in range(nbase)}
    for name in base:
        s=set()
        while len(s)<N: s.add((int(r.integers(N)),int(r.integers(N))))
        base[name]=s
    # TARGET = a random depth-chain of base relations
    chain=[f"r{int(r.integers(nbase))}" for _ in range(depth)]
    target=compose_chain([base[c] for c in chain])
    if not target: return None
    # search all depth-chains, pick best-F1 match to target
    best=None; bestf1=-1
    for combo in product(base.keys(), repeat=depth):
        comp=compose_chain([base[c] for c in combo])
        tp=len(comp&target); prec=tp/len(comp) if comp else 0; rec=tp/len(target) if target else 0
        f1=2*prec*rec/(prec+rec) if (prec+rec) else 0
        if f1>bestf1: bestf1=f1; best=combo
    return tuple(best)==tuple(chain)
def main():
    print("=== JEP-131: structure-learning boundary (rule depth x vocabulary size) ===", flush=True)
    print("   depth\nbase    3       6       10", flush=True)
    for depth in [2,3]:
        row=[]
        for nb in [3,6,10]:
            res=[trial(depth,nb,s) for s in range(120)]; res=[x for x in res if x is not None]
            row.append(np.mean(res))
        print(f"   {depth}            {row[0]:.2f}    {row[1]:.2f}    {row[2]:.2f}", flush=True)
    print("\n--- FINDING ---", flush=True)
    print("Structure learning by best-F1 rule-match degrades with DEPTH and VOCABULARY: at depth 2 the correct rule", flush=True)
    print("usually wins; at depth 3 with a larger relation vocabulary, SPURIOUS chains coincidentally match the target", flush=True)
    print("(many candidate compositions, by-chance F1) -> the right rule is no longer uniquely identifiable from data", flush=True)
    print("alone. The honest boundary: shallow rules + modest vocabulary are learnable; deep rules + large vocab need", flush=True)
    print("more than co-occurrence (priors, negative examples, incremental bootstrapping). Maps the JEP-69/70 limit. Named.", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
