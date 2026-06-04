"""JEP-22 - SR-value navigation under stochastic (slippery) transitions. 16-thread."""
import os
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"]: os.environ[v]="16"
import numpy as np
from collections import deque
rng=np.random.default_rng(220)
M=12
def gen_looped(M,extra=40):
    adj={(x,y):set() for x in range(M) for y in range(M)}; seen={(0,0)}; st=[(0,0)]
    while st:
        x,y=st[-1]; nb=[(x+dx,y+dy) for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)] if 0<=x+dx<M and 0<=y+dy<M and (x+dx,y+dy) not in seen]
        if nb: n=nb[rng.integers(len(nb))]; adj[(x,y)].add(n); adj[n].add((x,y)); seen.add(n); st.append(n)
        else: st.pop()
    cells=[(x,y) for x in range(M) for y in range(M)]; added=0
    while added<extra:
        c=cells[rng.integers(len(cells))]; x,y=c
        opts=[(x+dx,y+dy) for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)] if 0<=x+dx<M and 0<=y+dy<M and (x+dx,y+dy) not in adj[c]]
        if opts: n=opts[rng.integers(len(opts))]; adj[c].add(n); adj[n].add(c); added+=1
    return adj
ADJ=gen_looped(M); CELLS=[(x,y) for x in range(M) for y in range(M)]; ID={c:i for i,c in enumerate(CELLS)}; S=len(CELLS)
gamma=0.97
def sr_td(eps,steps=3_000_000,alpha=0.02):
    Mt=np.zeros((S,S),np.float32); I=np.eye(S,dtype=np.float32); c=CELLS[rng.integers(S)]
    for _ in range(steps):
        nbs=list(ADJ[c]); nb=nbs[rng.integers(len(nbs))]  # behaviour policy = random walk (slip is part of env)
        Mt[ID[c]]+=alpha*(I[ID[c]]+gamma*Mt[ID[nb]]-Mt[ID[c]]); c=nb
    return Mt
def stochastic_step(c,intended,eps):
    nbs=list(ADJ[c])
    if rng.random()<eps: return nbs[rng.integers(len(nbs))]   # slip to random neighbour
    return intended
def main():
    print(f"=== JEP-22: SR-value navigation under stochastic transitions (S={S}) ===",flush=True)
    Mt=sr_td(0.0)  # SR from random-walk occupancy (policy-agnostic structure)
    print("   eps     reached",flush=True)
    curve=[]
    for eps in [0.0,0.1,0.2,0.3,0.5]:
        ok=0;reps=200
        for _ in range(reps):
            s=CELLS[rng.integers(S)]; g=CELLS[rng.integers(S)]
            if s==g: ok+=1; continue
            c=s
            for _ in range(10*S):
                nbs=list(ADJ[c]); intended=max(nbs,key=lambda nb:Mt[ID[nb],ID[g]])
                c=stochastic_step(c,intended,eps)
                if c==g: ok+=1; break
        r=ok/reps; curve.append((eps,r)); print(f"   {eps:.1f}     {r:.2f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    d=dict(curve)
    robust = d[0.0]>=0.95 and d[0.1]>=0.9 and d[0.2]>=0.9
    monotone = all(curve[i][1]>=curve[i+1][1]-0.05 for i in range(len(curve)-1))
    if robust and monotone:
        print(f"JEP-22: PASS - the closed-loop SR-value agent is ROBUST to stochastic transitions: reach stays >=0.9",flush=True)
        print(f"up to eps=0.2 (deterministic {d[0.0]:.2f}, 10% slip {d[0.1]:.2f}, 20% slip {d[0.2]:.2f}) and degrades",flush=True)
        print(f"gracefully ({d[0.3]:.2f} at 30%, {d[0.5]:.2f} at 50%). The SR (expected occupancy) + closed-loop",flush=True)
        print(f"replanning self-corrects from slips. Realistic-noise robustness confirmed. SR / closed-loop control",flush=True)
        print(f"established - named as such.",flush=True)
    else:
        print(f"JEP-22: PARTIAL/NULL - curve {curve} (robust={robust}, monotone={monotone})",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()
