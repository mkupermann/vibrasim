"""JEP-23 - embedding distortion by structure type (ring/grid/tree/random): boundary of Euclidean cognitive maps."""
import os
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"]: os.environ[v]="16"
import numpy as np
from collections import deque
rng=np.random.default_rng(230)
gamma=0.95
def sr_embed(adj,N,k=6):
    Mt=np.zeros((N,N),np.float32); I=np.eye(N,dtype=np.float32); c=rng.integers(N)
    for _ in range(1_500_000):
        nbs=list(adj[c]); 
        if not nbs: c=rng.integers(N); continue
        nb=nbs[rng.integers(len(nbs))]; Mt[c]+=0.02*(I[c]+gamma*Mt[nb]-Mt[c]); c=nb
    A=0.5*(Mt+Mt.T); Ac=A-A.mean(0,keepdims=True)-A.mean(1,keepdims=True)+A.mean()
    w,V=np.linalg.eigh(Ac); order=np.argsort(w)[::-1]; return V[:,order[:k]]*np.sqrt(np.abs(w[order[:k]]))
def graphdist(adj,N):
    D=np.full((N,N),0.0)
    for s in range(N):
        d={s:0}; q=deque([s])
        while q:
            c=q.popleft()
            for nb in adj[c]:
                if nb not in d: d[nb]=d[c]+1; q.append(nb)
        for j in range(N): D[s,j]=d.get(j,N)
    return D
def spearman(u,v):
    ru=np.argsort(np.argsort(u)); rv=np.argsort(np.argsort(v)); return float(np.corrcoef(ru,rv)[0,1])
def ring(N):
    adj={i:set() for i in range(N)}
    for i in range(N): adj[i].add((i+1)%N); adj[(i+1)%N].add(i)
    return adj
def grid(K):
    N=K*K; idx=lambda x,y:x*K+y; adj={i:set() for i in range(N)}
    for x in range(K):
        for y in range(K):
            for dx,dy in [(1,0),(0,1)]:
                if x+dx<K and y+dy<K: pass
            for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                if 0<=x+dx<K and 0<=y+dy<K: adj[idx(x,y)].add(idx(x+dx,y+dy))
    return adj,N
def tree(depth):
    # balanced binary tree
    adj={0:set()}; nodes=[0]; nxt=1
    frontier=[0]
    for d in range(depth):
        new=[]
        for p in frontier:
            for _ in range(2):
                adj[nxt]=set(); adj[p].add(nxt); adj[nxt].add(p); new.append(nxt); nxt+=1
        frontier=new
    return adj,nxt
def randomg(N,p=0.06):
    adj={i:set() for i in range(N)}
    for i in range(N):
        for j in range(i+1,N):
            if rng.random()<p: adj[i].add(j); adj[j].add(i)
    # ensure connected: link components
    seen={0}; q=deque([0])
    while q:
        c=q.popleft()
        for nb in adj[c]:
            if nb not in seen: seen.add(nb); q.append(nb)
    for i in range(N):
        if i not in seen: adj[i].add(0); adj[0].add(i); seen.add(i)
    return adj
def evaluate(name,adj,N):
    E=sr_embed(adj,N); D=graphdist(adj,N)
    iu=np.triu_indices(N,1); gd=D[iu]; ed=np.linalg.norm(E[iu[0]]-E[iu[1]],axis=1)
    sp=spearman(ed,gd)
    # relative distortion: std of (ed/gd) normalized
    ratio=ed/(gd+1e-9); dist=float(np.std(ratio)/ (np.mean(ratio)+1e-9))
    return sp,dist
def main():
    print("=== JEP-23: embedding distortion by structure (boundary of Euclidean cognitive maps) ===",flush=True)
    results={}
    aR=ring(64); results["ring"]=evaluate("ring",aR,64)
    aG,NG=grid(8); results["grid"]=evaluate("grid",aG,NG)
    aT,NT=tree(5); results["tree"]=evaluate("tree",aT,NT)   # depth5 binary -> 63 nodes
    aX=randomg(64); results["random"]=evaluate("random",aX,64)
    print("   structure   Spearman(emb,graph)   rel-distortion",flush=True)
    for k in ["ring","grid","tree","random"]:
        sp,ds=results[k]; print(f"   {k:9}    {sp:.3f}              {ds:.3f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    spR=results["ring"][0]; spG=results["grid"][0]; spT=results["tree"][0]
    if spR>=0.9 and spG>=0.9 and spT<0.8 and results["tree"][1]>results["grid"][1]:
        print(f"JEP-23: PASS (boundary mapped) - Euclidean cognitive maps match METRIC structures but DISTORT",flush=True)
        print(f"hierarchies: ring {spR:.2f} and grid {spG:.2f} embed well (low-dim metric), but the TREE embeds",flush=True)
        print(f"POORLY (Spearman {spT:.2f}, higher distortion) - a balanced tree's exponential leaf growth does NOT",flush=True)
        print(f"fit low-dim Euclidean space. This is the honest BOUNDARY of 'reasoning as navigation in a Euclidean",flush=True)
        print(f"concept space'; hierarchies need HYPERBOLIC geometry (Nickel-Kiela 2017, established - named as such).",flush=True)
        print(f"Maps where the EQMOD-4 relational approach works and where it does not.",flush=True)
    else:
        print(f"JEP-23: PARTIAL/NULL - ring {spR:.2f} grid {spG:.2f} tree {spT:.2f} (expected tree<0.8<ring,grid)",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()
