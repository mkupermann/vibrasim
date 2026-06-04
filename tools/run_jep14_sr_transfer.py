"""JEP-14 - SR transfer: reward-revaluation (instant) vs transition-revaluation (needs relearning). 16-thread."""
import os
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"]: os.environ[v]="16"
import numpy as np
from collections import deque
rng=np.random.default_rng(60)
M=12
def gen_maze(M):
    adj={(x,y):set() for x in range(M) for y in range(M)}; seen={(0,0)}; st=[(0,0)]
    while st:
        x,y=st[-1]; nb=[(x+dx,y+dy) for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)] if 0<=x+dx<M and 0<=y+dy<M and (x+dx,y+dy) not in seen]
        if nb: n=nb[rng.integers(len(nb))]; adj[(x,y)].add(n); adj[n].add((x,y)); seen.add(n); st.append(n)
        else: st.pop()
    return adj
ADJ=gen_maze(M); CELLS=[(x,y) for x in range(M) for y in range(M)]; ID={c:i for i,c in enumerate(CELLS)}; S=len(CELLS)
gamma=0.97
def sr_td(adj,steps=3_000_000,alpha=0.02):
    Mt=np.zeros((S,S),np.float32); I=np.eye(S,dtype=np.float32); c=CELLS[rng.integers(S)]
    for _ in range(steps):
        nbs=list(adj[c]); 
        if not nbs: c=CELLS[rng.integers(S)]; continue
        nb=nbs[rng.integers(len(nbs))]; i,j=ID[c],ID[nb]; Mt[i]+=alpha*(I[i]+gamma*Mt[j]-Mt[i]); c=nb
    return Mt
def reach(adj,value_of,goals,reps=3):
    ok=0;tot=0
    for g in goals:
        Vf=value_of(g)
        for _ in range(reps):
            s=CELLS[rng.integers(S)]; tot+=1
            if s==g: ok+=1; continue
            c=s; seen=set()
            for _ in range(8*S):
                nbs=list(adj[c]); c=max(nbs,key=lambda nb:Vf[ID[nb]])
                if c==g: ok+=1; break
                if c in seen: break
                seen.add(c)
    return ok/tot
def main():
    print(f"=== JEP-14: SR transfer (reward vs transition revaluation), S={S} ===",flush=True)
    Mt=sr_td(ADJ)
    goals=[CELLS[rng.integers(S)] for _ in range(40)]
    # (A) reward revaluation: value = M @ r, r=one-hot goal (instant, no relearning)
    def val_reward(g): r=np.zeros(S,np.float32); r[ID[g]]=1.0; return Mt@r
    rA=reach(ADJ,val_reward,goals)
    print(f"  (A) REWARD revaluation (V=M@r, ZERO relearning): reach={rA:.2f}",flush=True)
    # (B) transition change: block one edge on a busy corridor
    # find an edge whose removal still leaves graph connected, used by many shortest paths
    edges=[(c,nb) for c in CELLS for nb in ADJ[c] if ID[c]<ID[nb]]
    (e0,e1)=edges[rng.integers(len(edges))]
    ADJ2={c:set(v) for c,v in ADJ.items()}; ADJ2[e0].discard(e1); ADJ2[e1].discard(e0)
    # connectivity check
    def connected(adj):
        seen={CELLS[0]}; q=deque([CELLS[0]])
        while q:
            c=q.popleft()
            for nb in adj[c]:
                if nb not in seen: seen.add(nb); q.append(nb)
        return len(seen)==S
    tries=0
    while not connected(ADJ2) and tries<50:
        ADJ2={c:set(v) for c,v in ADJ.items()}; (e0,e1)=edges[rng.integers(len(edges))]; ADJ2[e0].discard(e1); ADJ2[e1].discard(e0); tries+=1
    # goals on the far side of the blocked edge (their optimal path changes)
    def bfs(adj,src):
        d={src:0}; q=deque([src])
        while q:
            c=q.popleft()
            for nb in adj[c]:
                if nb not in d: d[nb]=d[c]+1; q.append(nb)
        return d
    d_old=bfs(ADJ,e0); d_new=bfs(ADJ2,e0)
    affected=[c for c in CELLS if d_new.get(c,999)-d_old.get(c,0)>=4][:30] or goals
    # (B-i) STALE SR (old Mt) planning in the CHANGED maze
    rBi=reach(ADJ2,val_reward,affected)
    # (B-ii) RELEARN SR in changed maze, then plan
    Mt2=sr_td(ADJ2)
    def val_reward2(g): r=np.zeros(S,np.float32); r[ID[g]]=1.0; return Mt2@r
    rBii=reach(ADJ2,val_reward2,affected)
    print(f"  (B) TRANSITION change (blocked 1 passage), goals on far side ({len(affected)}):",flush=True)
    print(f"      (i) STALE SR planning in changed maze   = {rBi:.2f}",flush=True)
    print(f"      (ii) RELEARNED SR planning              = {rBii:.2f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if rA>=0.9 and rBii>=0.9 and rBi<=rBii-0.2:
        print(f"JEP-14: PASS (characterization) - the SR abstraction TRANSFERS across REWARD changes instantly",flush=True)
        print(f"(V=M@r, reach {rA:.2f}, zero relearning) but NOT across TRANSITION changes: a blocked passage makes",flush=True)
        print(f"the cached SR STALE (reach {rBi:.2f} on affected goals) until it is RELEARNED by local TD (reach",flush=True)
        print(f"{rBii:.2f}). This is exactly the known SR boundary (Momennejad et al. 2017): reward-general,",flush=True)
        print(f"transition-specific. An honest map of what this abstraction buys. SR (Dayan 1993) established, named.",flush=True)
    else:
        print(f"JEP-14: PARTIAL/NULL - A {rA:.2f}, B-stale {rBi:.2f}, B-relearned {rBii:.2f}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()
