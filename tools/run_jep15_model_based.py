"""JEP-15 - model-based MPC (local edit + replan) vs cached SR under transition change. 16-thread."""
import os
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"]: os.environ[v]="16"
import numpy as np
from collections import deque
rng=np.random.default_rng(70)
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
    print(f"=== JEP-15: model-based MPC vs cached SR under transition change, S={S} ===",flush=True)
    Mt=sr_td(ADJ)
    # pick a cycle edge to block (keeps connectivity), with enough detoured goals
    edges=[(c,nb) for c in CELLS for nb in ADJ[c] if ID[c]<ID[nb]]; chosen=None
    for _ in range(300):
        e0,e1=edges[rng.integers(len(edges))]
        ADJ2={c:set(v) for c,v in ADJ.items()}; ADJ2[e0].discard(e1); ADJ2[e1].discard(e0)
        if connected(ADJ2):
            d0=bfs(ADJ,e0); d2=bfs(ADJ2,e0); aff=[c for c in CELLS if d2.get(c,0)-d0.get(c,0)>=3]
            if len(aff)>=10: chosen=(ADJ2,aff[:30]); break
    ADJ2,aff=chosen
    def vr(M_,g): r=np.zeros(S,np.float32); r[ID[g]]=1.0; return M_@r
    def model_value(adj,g):  # MODEL-BASED: DP/BFS distance-to-goal on CURRENT model -> value=-dist
        d=bfs(adj,g); return np.array([-d.get(c,9999) for c in CELLS],np.float32)
    stale=reach(ADJ2,lambda g:vr(Mt,g),aff)                 # cached SR, stale
    mb=reach(ADJ2,lambda g:model_value(ADJ2,g),aff)         # model-based, local-edit + replan (zero relearning)
    print(f"  blocked a cycle edge; detoured goals={len(aff)}",flush=True)
    print(f"  cached SR (stale)                 reach={stale:.2f}",flush=True)
    print(f"  MODEL-BASED (local edit + MPC/DP) reach={mb:.2f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if mb>=0.9 and mb>=stale+0.2:
        print(f"JEP-15: PASS - an explicit, locally-editable transition MODEL + MPC replanning gives INSTANT",flush=True)
        print(f"transition-revaluation: after blocking a passage, a single local model edit + replan reaches {mb:.2f}",flush=True)
        print(f"of detoured goals with ZERO value relearning, vs the cached SR's stale {stale:.2f}. This is the",flush=True)
        print(f"model-based (JEPA/MPC) advantage, complementary to the SR's instant REWARD revaluation (JEP-14b):",flush=True)
        print(f"SR for reward changes, explicit model + MPC for transition changes. Established methods, named.",flush=True)
    else:
        print(f"JEP-15: PARTIAL/NULL - model-based {mb:.2f}, stale SR {stale:.2f}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()
