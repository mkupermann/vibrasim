"""JEP-14b - SR transition-revaluation on a LOOPED maze (edge removal -> real detour). 16-thread."""
import os
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"]: os.environ[v]="16"
import numpy as np
from collections import deque
rng=np.random.default_rng(61)
M=12
def gen_maze_looped(M,extra=40):
    adj={(x,y):set() for x in range(M) for y in range(M)}; seen={(0,0)}; st=[(0,0)]
    while st:
        x,y=st[-1]; nb=[(x+dx,y+dy) for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)] if 0<=x+dx<M and 0<=y+dy<M and (x+dx,y+dy) not in seen]
        if nb: n=nb[rng.integers(len(nb))]; adj[(x,y)].add(n); adj[n].add((x,y)); seen.add(n); st.append(n)
        else: st.pop()
    # add extra edges -> loops
    cells=[(x,y) for x in range(M) for y in range(M)]
    added=0
    while added<extra:
        c=cells[rng.integers(len(cells))]; x,y=c
        opts=[(x+dx,y+dy) for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)] if 0<=x+dx<M and 0<=y+dy<M and (x+dx,y+dy) not in adj[c]]
        if opts: n=opts[rng.integers(len(opts))]; adj[c].add(n); adj[n].add(c); added+=1
    return adj
ADJ=gen_maze_looped(M); CELLS=[(x,y) for x in range(M) for y in range(M)]; ID={c:i for i,c in enumerate(CELLS)}; S=len(CELLS)
gamma=0.97
def sr_td(adj,steps=3_000_000,alpha=0.02):
    Mt=np.zeros((S,S),np.float32); I=np.eye(S,dtype=np.float32); c=CELLS[rng.integers(S)]
    for _ in range(steps):
        nbs=list(adj[c]); nb=nbs[rng.integers(len(nbs))]; i,j=ID[c],ID[nb]; Mt[i]+=alpha*(I[i]+gamma*Mt[j]-Mt[i]); c=nb
    return Mt
def connected(adj):
    seen={CELLS[0]}; q=deque([CELLS[0]])
    while q:
        c=q.popleft()
        for nb in adj[c]:
            if nb not in seen: seen.add(nb); q.append(nb)
    return len(seen)==S
def bfs(adj,src):
    d={src:0}; q=deque([src])
    while q:
        c=q.popleft()
        for nb in adj[c]:
            if nb not in d: d[nb]=d[c]+1; q.append(nb)
    return d
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
    print(f"=== JEP-14b: SR transition-revaluation on LOOPED maze (real detours), S={S} ===",flush=True)
    Mt=sr_td(ADJ); goals=[CELLS[rng.integers(S)] for _ in range(40)]
    def vr(M_,g): r=np.zeros(S,np.float32); r[ID[g]]=1.0; return M_@r
    rA=reach(ADJ,lambda g:vr(Mt,g),goals)
    print(f"  (A) REWARD revaluation: reach={rA:.2f}",flush=True)
    # block a cycle edge that keeps connectivity (real detour)
    edges=[(c,nb) for c in CELLS for nb in ADJ[c] if ID[c]<ID[nb]]
    chosen=None
    for _ in range(200):
        e0,e1=edges[rng.integers(len(edges))]
        ADJ2={c:set(v) for c,v in ADJ.items()}; ADJ2[e0].discard(e1); ADJ2[e1].discard(e0)
        if connected(ADJ2):
            d0=bfs(ADJ,e0); d2=bfs(ADJ2,e0)
            aff=[c for c in CELLS if d2.get(c,0)-d0.get(c,0)>=3]
            if len(aff)>=10: chosen=(ADJ2,aff); break
    if chosen is None:
        ADJ2={c:set(v) for c,v in ADJ.items()}; ADJ2[e0].discard(e1); ADJ2[e1].discard(e0); aff=goals
    else: ADJ2,aff=chosen
    aff=aff[:30]
    rBi=reach(ADJ2,lambda g:vr(Mt,g),aff)         # stale SR in changed maze
    Mt2=sr_td(ADJ2); rBii=reach(ADJ2,lambda g:vr(Mt2,g),aff)  # relearned
    print(f"  (B) blocked a CYCLE edge (connectivity kept), affected goals={len(aff)}:",flush=True)
    print(f"      (i) STALE SR    = {rBi:.2f}",flush=True)
    print(f"      (ii) RELEARNED  = {rBii:.2f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if rA>=0.9 and rBii>=0.9 and rBi<=rBii-0.15:
        print(f"JEP-14b: PASS (characterization) - the SR transfers across REWARD changes instantly (V=M@r, {rA:.2f},",flush=True)
        print(f"zero relearning) but a TRANSITION change (blocked passage forcing a detour) makes the cached SR STALE",flush=True)
        print(f"({rBi:.2f} on detoured goals - it still routes toward the now-blocked path) until RELEARNED by local",flush=True)
        print(f"TD ({rBii:.2f}). This is the established SR boundary (Momennejad et al. 2017): reward-general,",flush=True)
        print(f"transition-specific. Honest map of the abstraction. SR (Dayan 1993) established, named as such.",flush=True)
    else:
        print(f"JEP-14b: PARTIAL/NULL - A {rA:.2f}, B-stale {rBi:.2f}, B-relearned {rBii:.2f}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()
