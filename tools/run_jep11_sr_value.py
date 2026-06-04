"""JEP-11 - SR-as-value-function maze navigation (local TD), the correct planner. 16-thread."""
import os
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"]: os.environ[v]="16"
import numpy as np
from collections import deque
rng=np.random.default_rng(31)
M=16
def gen_maze(M):
    adj={(x,y):set() for x in range(M) for y in range(M)}
    seen={(0,0)}; stack=[(0,0)]
    while stack:
        x,y=stack[-1]
        nb=[(x+dx,y+dy) for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)] if 0<=x+dx<M and 0<=y+dy<M and (x+dx,y+dy) not in seen]
        if nb:
            n=nb[rng.integers(len(nb))]; adj[(x,y)].add(n); adj[n].add((x,y)); seen.add(n); stack.append(n)
        else: stack.pop()
    return adj
ADJ=gen_maze(M); CELLS=[(x,y) for x in range(M) for y in range(M)]; ID={c:i for i,c in enumerate(CELLS)}; S=len(CELLS)
gamma=0.97
def sr_td(steps=4_000_000,alpha=0.02):
    Mt=np.zeros((S,S),np.float32); I=np.eye(S,dtype=np.float32); c=CELLS[rng.integers(S)]
    for _ in range(steps):
        nbs=list(ADJ[c]); nb=nbs[rng.integers(len(nbs))]; i,j=ID[c],ID[nb]
        Mt[i]+=alpha*(I[i]+gamma*Mt[j]-Mt[i]); c=nb
    return Mt
def navigate(policy,reps=200):
    ok=0
    for _ in range(reps):
        s=CELLS[rng.integers(S)]; g=CELLS[rng.integers(S)]
        if s==g: ok+=1; continue
        c=s
        for _ in range(6*S):
            c=policy(c,g)
            if c==g: ok+=1; break
    return ok/reps
def main():
    print(f"=== JEP-11: SR-as-value maze navigation (M={M}, S={S}, local TD, 16 threads) ===",flush=True)
    Mt=sr_td(); print("  SR (TD) learned",flush=True)
    def sr_pol(c,g): nbs=list(ADJ[c]); return max(nbs,key=lambda nb:Mt[ID[nb],ID[g]])
    def euc_pol(c,g): nbs=list(ADJ[c]); return min(nbs,key=lambda nb:abs(nb[0]-g[0])+abs(nb[1]-g[1]))
    def rnd_pol(c,g): nbs=list(ADJ[c]); return nbs[rng.integers(len(nbs))]
    n_sr=navigate(sr_pol); n_eu=navigate(euc_pol); n_rd=navigate(rnd_pol)
    print(f"  reached:  SR-VALUE={n_sr:.2f}   EUCLID-greedy={n_eu:.2f}   random={n_rd:.2f}   (BFS-optimal=1.00)",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if n_sr>=0.9 and n_sr>=n_eu+0.3 and n_sr>=n_rd+0.3:
        print(f"JEP-11: PASS - the LOCALLY-LEARNED Successor Representation, used as a VALUE FUNCTION (greedy ascent",flush=True)
        print(f"on M[s',goal]), navigates the maze at {n_sr:.2f} vs Euclidean-greedy {n_eu:.2f} (stuck at walls) and",flush=True)
        print(f"random {n_rd:.2f}. This CLOSES JEP-8/9: the prior failure was the PLANNER (1-step greedy on embedding",flush=True)
        print(f"distance), not the representation. SR encodes geodesic reachability and a local TD rule learns it.",flush=True)
        print(f"Substrate-compatible (local TD) planning works. SR/TD (Dayan 1993) established, named as such.",flush=True)
    else:
        print(f"JEP-11: PARTIAL/NULL - SR {n_sr:.2f}, euclid {n_eu:.2f}, random {n_rd:.2f}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()
