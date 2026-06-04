"""JEP-154 - combine reuse+prior+active on the hard (deep+noisy+minimal) regime; find the binding constraint."""
import numpy as np
from itertools import product
from collections import defaultdict
def compose(rels):
    out=rels[0]
    for R in rels[1:]:
        nxt=set(); idx=defaultdict(set)
        for a,b in out: idx[b].add(a)
        for b,c in R:
            for a in idx[b]: nxt.add((a,c))
        out=nxt
    return out
def setup(seed):
    r=np.random.default_rng(seed); N=14; nbase=5
    base={f"r{i}": set() for i in range(nbase)}
    for nm in base:
        s=set()
        while len(s)<N: s.add((int(r.integers(N)),int(r.integers(N))))
        base[nm]=s
    subnames=[(f"r{int(r.integers(nbase))}",f"r{int(r.integers(nbase))}") for _ in range(4)]
    subrules={f"s{i}": compose([base[a],base[b]]) for i,(a,b) in enumerate(subnames)}
    s1,s2=list(subrules)[0],list(subrules)[1]
    target=compose([subrules[s1],subrules[s2]])
    return base,subrules,target,r
def noisy_obs(pool, k, noise, r, universe):
    """draw k observed POSITIVE pairs, each flipped to a random wrong pair w.p. noise"""
    pool=list(pool)
    if len(pool)<1: return set()
    obs=set()
    for _ in range(k):
        p=pool[int(r.integers(len(pool)))]
        if r.random()<noise: p=(int(r.integers(universe)),int(r.integers(universe)))
        obs.add(p)
    return obs
def identify(cands, target, obs):
    consistent=[c for c in cands if obs<=c]
    if not consistent: return False
    return sum(c==target for c in consistent)/len(consistent) >= 0.5
def identify_prior(cands, target, obs):
    # Occam: among consistent, prefer SMALLEST (fewest pairs); correct if that is target
    consistent=[c for c in cands if obs<=c]
    if not consistent: return False
    m=min(len(c) for c in consistent)
    small=[c for c in consistent if len(c)==m]
    return sum(c==target for c in small)/len(small) >= 0.5
def main():
    print("=== JEP-154: ingredient ladder on the HARD regime (deep target, noise=0.15) ===", flush=True)
    noise=0.15; N=14
    rows=[("scratch passive 1-shot","scratch","passive",1,False),
          ("+reuse 1-shot","reuse","passive",1,False),
          ("+reuse +prior 1-shot","reuse","passive",1,True),
          ("+reuse +prior +active 1-shot","reuse","active",1,True),
          ("+reuse +prior +active FEW-shot k=5","reuse","active",5,True),
          ("+reuse +prior +active FEW-shot k=12","reuse","active",12,True)]
    for label,space,mode,k,prior in rows:
        acc=[]
        for s in range(250):
            base,subrules,target,r=setup(s)
            if len(target)<1: continue
            # candidate hypotheses
            if space=="scratch":
                cands=[]
                for d in (1,2,3,4):
                    for combo in product(base.keys(),repeat=d):
                        cands.append(compose([base[x] for x in combo]))
            else:
                cands=[compose([subrules[a],subrules[b]]) for a,b in product(subrules.keys(),repeat=2)]
            # observations
            if mode=="active":
                # active = query pairs KNOWN to discriminate: sample from target (informative positives)
                obs=noisy_obs(target,k,noise,r,N)
            else:
                obs=noisy_obs(target,min(k,1),noise,r,N)
            ok = identify_prior(cands,target,obs) if prior else identify(cands,target,obs)
            acc.append(ok)
        print(f"   {label:42s} {np.mean(acc):.2f}", flush=True)
    print("\n--- FINDING ---", flush=True)
    print("Reading the ladder tells us which constraint BINDS at each step. If reuse jumps scratch sharply, SEARCH was", flush=True)
    print("binding; if prior/active add little at 1-shot but FEW-shot jumps, the NOISE+one-shot tension binds (can't", flush=True)
    print("denoise from one example - redundancy via few-shot is what closes it). Honest capstone of the residual.", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
