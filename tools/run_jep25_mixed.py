"""JEP-25 - mixed-curvature (Euclidean x Poincare) embedding vs pure, on a grid-with-trees graph. torch."""
import numpy as np, torch
from collections import deque
rng=np.random.default_rng(250); torch.manual_seed(2)
K=4; TREE_DEPTH=2
adj={}; nxt=0; grid_id={}
for x in range(K):
    for y in range(K):
        grid_id[(x,y)]=nxt; adj[nxt]=set(); nxt+=1
for x in range(K):
    for y in range(K):
        for dx,dy in [(1,0),(0,1)]:
            if x+dx<K and y+dy<K:
                a,b=grid_id[(x,y)],grid_id[(x+dx,y+dy)]; adj[a].add(b); adj[b].add(a)
# attach a small binary tree (depth 2) to each grid node
for x in range(K):
    for y in range(K):
        root=grid_id[(x,y)]; frontier=[root]
        for d in range(TREE_DEPTH):
            new=[]
            for p in frontier:
                for _ in range(2):
                    adj[nxt]=set(); adj[p].add(nxt); adj[nxt].add(p); new.append(nxt); nxt+=1
            frontier=new
N=nxt
def graphdist(adj,N):
    D=np.zeros((N,N))
    for s in range(N):
        d={s:0}; q=deque([s])
        while q:
            c=q.popleft()
            for nb in adj[c]:
                if nb not in d: d[nb]=d[c]+1; q.append(nb)
        for j in range(N): D[s,j]=d.get(j,N)
    return D
GD=torch.tensor(graphdist(adj,N),dtype=torch.float32)
iu=np.triu_indices(N,1)
gd_np=GD.numpy()[iu]
def spearman(u,v):
    ru=np.argsort(np.argsort(u)); rv=np.argsort(np.argsort(v)); return float(np.corrcoef(ru,rv)[0,1])
def euc_d(X,i,j): return ((X[i]-X[j])**2).sum(-1).clamp(min=1e-9).sqrt()
def poin_d(X,i,j):
    diff=((X[i]-X[j])**2).sum(-1); nx=(X[i]**2).sum(-1); ny=(X[j]**2).sum(-1)
    return torch.acosh(torch.clamp(1+2*diff/((1-nx)*(1-ny)+1e-9),min=1+1e-7))
I=torch.tensor(iu[0]); J=torch.tensor(iu[1])
def fit(kind,iters=3000):
    if kind=="euclid":
        E=torch.randn(N,4)*0.1; params=[E]; hyp=None
    elif kind=="hyper":
        H=torch.randn(N,4)*0.001; params=[H]; hyp=H
    else:
        E=torch.randn(N,2)*0.1; H=torch.randn(N,2)*0.001; params=[E,H]; hyp=H
    s=torch.tensor(1.0,requires_grad=True)
    for p in params: p.requires_grad_(True)
    opt=torch.optim.Adam([p for p in params if p is not hyp]+[s],lr=0.02)
    for it in range(iters):
        opt.zero_grad()
        if hyp is not None and hyp.grad is not None: hyp.grad.zero_()
        if kind=="euclid": d=euc_d(params[0],I,J)
        elif kind=="hyper": d=poin_d(params[0],I,J)
        else: d=torch.sqrt(euc_d(params[0],I,J)**2 + poin_d(params[1],I,J)**2 + 1e-9)
        loss=((d - s*GD[I,J])**2).mean()
        loss.backward()
        opt.step()
        if hyp is not None:
            with torch.no_grad():
                g=hyp.grad; scale=((1-(hyp**2).sum(1,keepdim=True)).clamp(min=1e-4)**2)/4.0
                hyp-=0.05*scale*g
                nrm=hyp.norm(dim=1,keepdim=True); hyp[:]=torch.where(nrm>=0.999,hyp/nrm*0.999,hyp)
    with torch.no_grad():
        if kind=="euclid": d=euc_d(params[0],I,J)
        elif kind=="hyper": d=poin_d(params[0],I,J)
        else: d=torch.sqrt(euc_d(params[0],I,J)**2 + poin_d(params[1],I,J)**2 + 1e-9)
    return spearman(d.numpy(),gd_np)
def main():
    print(f"=== JEP-25: mixed-curvature embedding, grid-with-trees (N={N}, {K}x{K} grid + depth-{TREE_DEPTH} trees) ===",flush=True)
    e=fit("euclid"); h=fit("hyper"); m=fit("mixed")
    print(f"  pure Euclidean (4D):        Spearman={e:.3f}",flush=True)
    print(f"  pure Hyperbolic (4D):       Spearman={h:.3f}",flush=True)
    print(f"  MIXED (Euclid2D x Hyper2D): Spearman={m:.3f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if m>=max(e,h)+0.05 and m>=0.85:
        print(f"JEP-25: PASS - on a structure with BOTH metric (grid) and hierarchical (tree) parts, the MIXED-",flush=True)
        print(f"curvature map ({m:.2f}) beats BOTH pure Euclidean ({e:.2f}) and pure hyperbolic ({h:.2f}), each of",flush=True)
        print(f"which fits only half. This is the synthesis the geometry thread pointed to: conceptual knowledge",flush=True)
        print(f"needs MIXED-curvature cognitive maps. Product manifolds (Gu et al. 2019) established - named as such.",flush=True)
    else:
        print(f"JEP-25: PARTIAL/NULL - euclid {e:.2f}, hyper {h:.2f}, mixed {m:.2f}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()
