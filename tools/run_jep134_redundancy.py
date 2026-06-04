"""JEP-134 - rescue noisy structure learning with redundant observations + majority voting."""
import numpy as np
from itertools import combinations
def closure(pairs, items):
    adj={i:set() for i in items}
    for a,b in pairs: adj[a].add(b)
    ch=True
    while ch:
        ch=False
        for a in items:
            for b in list(adj[a]):
                for c in adj[b]:
                    if c not in adj[a]: adj[a].add(c); ch=True
    return adj
def run(kred, noise, seed, transitive=True):
    r=np.random.default_rng(seed); n=6; items=list(range(n))
    allp=[(a,b) for a in items for b in items if a!=b]
    if transitive:
        true=set((i,j) for i,j in combinations(items,2))
    else:
        true=set(); 
        for i,j in combinations(items,2): true.add((i,j) if r.random()<0.5 else (j,i))
    # k redundant noisy observations per pair, majority-vote the label
    voted_true=set(); voted_false=set()
    for p in allp:
        truth = p in true
        votes=sum(1 for _ in range(kred) if (truth if r.random()>noise else not truth))
        (voted_true if votes>kred/2 else voted_false).add(p)
    cl=closure(voted_true, items)
    contradictions=sum(1 for a,b in voted_false if b in cl.get(a,set()))
    inferred_trans = contradictions <= 0.1*max(1,len(voted_false))
    return inferred_trans==transitive
def main():
    print("=== JEP-134: redundancy rescue of noisy structure learning (per-obs noise=0.3) ===", flush=True)
    print("   k(redundancy)   accuracy(transitive+nontransitive)", flush=True)
    for k in [1,3,5,9,15,25]:
        acc=np.mean([run(k,0.3,s,True) for s in range(150)]+[run(k,0.3,s,False) for s in range(150)])
        print(f"   {k:>3}             {acc:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    a1=np.mean([run(15,0.3,s,True) for s in range(150)]+[run(15,0.3,s,False) for s in range(150)])
    if a1>=0.9:
        print(f"JEP-134: PASS - REDUNDANCY rescues noisy structure learning: at 30% per-observation noise, majority-",flush=True)
        print(f"voting over k redundant observations denoises the facts, and structure inference recovers (acc {a1:.2f}",flush=True)
        print(f"at k=15). The noisy-data limit (JEP-133) is addressable with REPEATED observation — the standard noise",flush=True)
        print(f"rescue. So noisy structure learning needs DATA REDUNDANCY, not just a tolerance. Established, named.",flush=True)
    else:
        print(f"JEP-134: PARTIAL - acc {a1:.2f} at k=15. Recorded honestly.",flush=True)
    print("HONEST: needs each fact observed many times (k~15 at 30% noise); rare facts / one-shot observations can't",flush=True)
    print("be denoised this way. Redundancy trades data for noise-robustness; the cost grows with the noise rate.",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
