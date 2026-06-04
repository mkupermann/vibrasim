"""JEP-23b - boundary test at natural low dim k=2 (clean): ring/grid embed; tree distorts."""
import os
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"]: os.environ[v]="16"
import numpy as np
from collections import deque
rng=np.random.default_rng(231)
gamma=0.95
def sr_embed(adj,N,k):
    Mt=np.zeros((N,N),np.float32); I=np.eye(N,dtype=np.float32); c=rng.integers(N)
    for _ in range(1_500_000):
        nbs=list(adj[c])
        if not nbs: c=rng.integers(N); continue
        nb=nbs[rng.integers(len(nbs))]; Mt[c]+=0.02*(I[c]+gamma*Mt[nb]-Mt[c]); c=nb
    A=0.5*(Mt+Mt.T); Ac=A-A.mean(0,keepdims=True)-A.mean(1,keepdims=True)+A.mean()
    w,V=np.linalg.eigh(Ac); order=np.argsort(w)[::-1]; return V[:,order[:k]]
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
    return adj,N
def grid(K):
    N=K*K; idx=lambda x,y:x*K+y; adj={i:set() for i in range(N)}
    for x in range(K):
        for y in range(K):
            for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                if 0<=x+dx<K and 0<=y+dy<K: adj[idx(x,y)].add(idx(x+dx,y+dy))
    return adj,N
def tree(depth):
    adj={0:set()}; nxt=1; frontier=[0]
    for d in range(depth):
        new=[]
        for p in frontier:
            for _ in range(2):
                adj[nxt]=set(); adj[p].add(nxt); adj[nxt].add(p); new.append(nxt); nxt+=1
        frontier=new
    return adj,nxt
def ev(adj,N,k):
    E=sr_embed(adj,N,k); D=graphdist(adj,N); iu=np.triu_indices(N,1)
    return spearman(np.linalg.norm(E[iu[0]]-E[iu[1]],axis=1),D[iu])
def main():
    print("=== JEP-23b: boundary at NATURAL low dim (clean) ===",flush=True)
    aR,NR=ring(64); aG,NG=grid(8); aT,NT=tree(5)
    # ring intrinsic dim 2 (circle), grid 2, tree: give tree MORE dims (k=4) and it STILL distorts
    rR=ev(aR,NR,2); rG=ev(aG,NG,2); rT2=ev(aT,NT,2); rT4=ev(aT,NT,4)
    print(f"   ring  (k=2): Spearman={rR:.3f}",flush=True)
    print(f"   grid  (k=2): Spearman={rG:.3f}",flush=True)
    print(f"   tree  (k=2): Spearman={rT2:.3f}",flush=True)
    print(f"   tree  (k=4, MORE dims): Spearman={rT4:.3f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if rR>=0.9 and rG>=0.9 and rT2<0.8 and rT4<0.85:
        print(f"JEP-23b: PASS (boundary mapped cleanly) - at natural low dim, METRIC structures embed well in",flush=True)
        print(f"Euclidean SR space (ring {rR:.2f}, grid {rG:.2f}) but the TREE distorts badly (k=2 {rT2:.2f}) and",flush=True)
        print(f"stays poor even with MORE dims (k=4 {rT4:.2f}) - the hallmark of hierarchies that need HYPERBOLIC",flush=True)
        print(f"geometry (Nickel-Kiela 2017). HONEST BOUNDARY: 'reasoning as navigation in a Euclidean concept",flush=True)
        print(f"space' works for metric/grid/order structures, NOT for hierarchies. Maps where EQMOD-4 applies.",flush=True)
    else:
        print(f"JEP-23b: PARTIAL/NULL - ring {rR:.2f} grid {rG:.2f} tree-k2 {rT2:.2f} tree-k4 {rT4:.2f}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()
