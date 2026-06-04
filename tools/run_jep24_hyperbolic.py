"""JEP-24 - Poincare (hyperbolic) embedding recovers tree hierarchy where Euclidean fails. torch autograd."""
import numpy as np, torch
from collections import deque
rng=np.random.default_rng(240)
torch.manual_seed(0)
def tree(depth):
    adj={0:set()}; nxt=1; frontier=[0]
    for d in range(depth):
        new=[]
        for p in frontier:
            for _ in range(2):
                adj[nxt]=set(); adj[p].add(nxt); adj[nxt].add(p); new.append(nxt); nxt+=1
        frontier=new
    return adj,nxt
ADJ,N=tree(5)
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
GD=graphdist(ADJ,N)
edges=[(u,v) for u in range(N) for v in ADJ[u] if u<v]
def poincare_dist(x,y):
    diff=((x-y)**2).sum(-1)
    nx=(x**2).sum(-1); ny=(y**2).sum(-1)
    return torch.acosh(1+2*diff/((1-nx)*(1-ny)+1e-9)+1e-9)
def spearman(u,v):
    ru=np.argsort(np.argsort(u)); rv=np.argsort(np.argsort(v)); return float(np.corrcoef(ru,rv)[0,1])
def main():
    print(f"=== JEP-24: Poincare embedding of a tree (N={N}) ===",flush=True)
    X=torch.nn.Parameter(torch.randn(N,2)*0.01)
    opt=torch.optim.Adam([X],lr=0.02)
    E=torch.tensor(edges)
    for it in range(3000):
        opt.zero_grad()
        u=E[:,0]; v=E[:,1]
        # negatives: random nodes for each edge's u
        negs=torch.randint(0,N,(len(edges),10))
        du=poincare_dist(X[u],X[v])  # positive distance
        dn=poincare_dist(X[u].unsqueeze(1).expand(-1,10,-1), X[negs])  # (E,10)
        # ranking: -log softmax(-d) with positive vs negatives
        logits=torch.cat([(-du).unsqueeze(1),-dn],dim=1)
        loss=torch.nn.functional.cross_entropy(logits,torch.zeros(len(edges),dtype=torch.long))
        loss.backward(); opt.step()
        with torch.no_grad():  # project into ball
            nrm=X.norm(dim=1,keepdim=True); X.data=torch.where(nrm>=0.999, X/nrm*0.999, X)
    with torch.no_grad():
        Xn=X.detach().numpy()
        iu=np.triu_indices(N,1)
        hd=[]
        for a,b in zip(*iu):
            x=torch.tensor(Xn[a]); y=torch.tensor(Xn[b]); hd.append(float(poincare_dist(x,y)))
        hd=np.array(hd); gd=GD[iu]
        sp_h=spearman(hd,gd)
    print(f"  hyperbolic Spearman(emb-dist, graph-dist) = {sp_h:.3f}  (Euclidean baseline from JEP-23b = 0.41)",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if sp_h>=0.85 and sp_h>=0.41+0.3:
        print(f"JEP-24: PASS - a 2D HYPERBOLIC (Poincare) cognitive map recovers the tree hierarchy at Spearman",flush=True)
        print(f"{sp_h:.2f}, vs the Euclidean cognitive map's 0.41 (JEP-23b). Confirms the geometry-mismatch diagnosis:",flush=True)
        print(f"hierarchies fit hyperbolic, not Euclidean, space (exponential volume matches exponential branching).",flush=True)
        print(f"Extends the EQMOD-4 relational machinery to HIERARCHIES (IS-A/taxonomies) - the structure conceptual",flush=True)
        print(f"knowledge most needs. Poincare embeddings (Nickel-Kiela 2017) established - named as such.",flush=True)
    else:
        print(f"JEP-24: PARTIAL/NULL - hyperbolic Spearman {sp_h:.2f}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()
