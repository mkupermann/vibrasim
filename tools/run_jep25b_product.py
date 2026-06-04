"""JEP-25b - mixed-curvature on a true GRID x TREE Cartesian product (each pure geometry fails half). torch."""
import numpy as np, torch
from collections import deque
rng=np.random.default_rng(251); torch.manual_seed(3)
K=3  # grid KxK
TD=3 # tree depth
# grid nodes
gnodes=[(x,y) for x in range(K) for y in range(K)]
gadj={i:set() for i in range(len(gnodes))}
gid={c:i for i,c in enumerate(gnodes)}
for (x,y) in gnodes:
    for dx,dy in [(1,0),(0,1)]:
        if x+dx<K and y+dy<K: a,b=gid[(x,y)],gid[(x+dx,y+dy)]; gadj[a].add(b); gadj[b].add(a)
# tree nodes
tadj={0:set()}; nxt=1; frontier=[0]
for d in range(TD):
    new=[]
    for p in frontier:
        for _ in range(2):
            tadj[nxt]=set(); tadj[p].add(nxt); tadj[nxt].add(p); new.append(nxt); nxt+=1
    frontier=new
NT=nxt; NG=len(gnodes)
def bfsdist(adj,n):
    D=np.zeros((n,n))
    for s in range(n):
        d={s:0};q=deque([s])
        while q:
            c=q.popleft()
            for nb in adj[c]:
                if nb not in d: d[nb]=d[c]+1; q.append(nb)
        for j in range(n): D[s,j]=d.get(j,n)
    return D
GDg=bfsdist(gadj,NG); GDt=bfsdist(tadj,NT)
# product graph: node=(g,t); distance = grid_dist(g,g') + tree_dist(t,t')
N=NG*NT
def pid(g,t): return g*NT+t
GD=np.zeros((N,N))
for g in range(NG):
    for t in range(NT):
        for g2 in range(NG):
            for t2 in range(NT):
                GD[pid(g,t),pid(g2,t2)]=GDg[g,g2]+GDt[t,t2]
GD=torch.tensor(GD,dtype=torch.float32); iu=np.triu_indices(N,1); gd_np=GD.numpy()[iu]
I=torch.tensor(iu[0]); J=torch.tensor(iu[1])
def spearman(u,v):
    ru=np.argsort(np.argsort(u)); rv=np.argsort(np.argsort(v)); return float(np.corrcoef(ru,rv)[0,1])
def euc_d(X,i,j): return ((X[i]-X[j])**2).sum(-1).clamp(min=1e-9).sqrt()
def poin_d(X,i,j):
    diff=((X[i]-X[j])**2).sum(-1); nx=(X[i]**2).sum(-1); ny=(X[j]**2).sum(-1)
    return torch.acosh(torch.clamp(1+2*diff/((1-nx)*(1-ny)+1e-9),min=1+1e-7))
def fit(kind,iters=2500):
    if kind=="euclid": E=torch.randn(N,4)*0.1; params=[E]; hyp=None
    elif kind=="hyper": H=torch.randn(N,4)*0.001; params=[H]; hyp=H
    else: E=torch.randn(N,2)*0.1; H=torch.randn(N,2)*0.001; params=[E,H]; hyp=H
    s=torch.tensor(1.0,requires_grad=True)
    for p in params: p.requires_grad_(True)
    opt=torch.optim.Adam([p for p in params if p is not hyp]+[s],lr=0.02)
    for it in range(iters):
        opt.zero_grad()
        if hyp is not None and hyp.grad is not None: hyp.grad.zero_()
        if kind=="euclid": d=euc_d(params[0],I,J)
        elif kind=="hyper": d=poin_d(params[0],I,J)
        else: d=torch.sqrt(euc_d(params[0],I,J)**2+poin_d(params[1],I,J)**2+1e-9)
        loss=((d-s*GD[I,J])**2).mean(); loss.backward(); opt.step()
        if hyp is not None:
            with torch.no_grad():
                g=hyp.grad; sc=((1-(hyp**2).sum(1,keepdim=True)).clamp(min=1e-4)**2)/4.0
                hyp-=0.05*sc*g; nrm=hyp.norm(dim=1,keepdim=True); hyp[:]=torch.where(nrm>=0.999,hyp/nrm*0.999,hyp)
    with torch.no_grad():
        if kind=="euclid": d=euc_d(params[0],I,J)
        elif kind=="hyper": d=poin_d(params[0],I,J)
        else: d=torch.sqrt(euc_d(params[0],I,J)**2+poin_d(params[1],I,J)**2+1e-9)
    return spearman(d.numpy(),gd_np)
def main():
    print(f"=== JEP-25b: GRID x TREE product (N={N}={NG}x{NT}), each pure geometry fails half ===",flush=True)
    e=fit("euclid"); h=fit("hyper"); m=fit("mixed")
    print(f"  pure Euclidean (4D):        Spearman={e:.3f}",flush=True)
    print(f"  pure Hyperbolic (4D):       Spearman={h:.3f}",flush=True)
    print(f"  MIXED (Euclid2D x Hyper2D): Spearman={m:.3f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if m>=max(e,h)+0.03 and m>=0.85:
        print(f"JEP-25b: PASS - on a true grid x tree product (BOTH geometries genuinely needed), the MIXED-curvature",flush=True)
        print(f"map ({m:.2f}) beats pure Euclidean ({e:.2f}, fails the tree factor) AND pure hyperbolic ({h:.2f},",flush=True)
        print(f"distorts the grid factor). The synthesis holds: structures with BOTH metric and hierarchical relations",flush=True)
        print(f"need MIXED-curvature cognitive maps. Product manifolds (Gu et al. 2019) established - named as such.",flush=True)
    else:
        print(f"JEP-25b: PARTIAL/NULL - euclid {e:.2f}, hyper {h:.2f}, mixed {m:.2f}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()
