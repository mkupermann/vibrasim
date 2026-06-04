"""JEP-24b - proper Poincare embedding: transitive-closure positives + Riemannian SGD. torch."""
import numpy as np, torch
from collections import deque
rng=np.random.default_rng(241); torch.manual_seed(1)
def tree(depth):
    adj={0:set()}; parent={0:-1}; nxt=1; frontier=[0]
    for d in range(depth):
        new=[]
        for p in frontier:
            for _ in range(2):
                adj[nxt]=set(); adj[p].add(nxt); adj[nxt].add(p); parent[nxt]=p; new.append(nxt); nxt+=1
        frontier=new
    return adj,parent,nxt
ADJ,PAR,N=tree(5)
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
# transitive closure ancestor pairs (u ancestor of v) -> positives (both directions)
def ancestors(v):
    a=[]; p=PAR[v]
    while p!=-1: a.append(p); p=PAR[p]
    return a
POS=[]
for v in range(N):
    for u in ancestors(v): POS.append((u,v)); POS.append((v,u))
POS=torch.tensor(POS)
def pdist(x,y):
    diff=((x-y)**2).sum(-1); nx=(x**2).sum(-1); ny=(y**2).sum(-1)
    return torch.acosh(torch.clamp(1+2*diff/((1-nx)*(1-ny)+1e-9),min=1+1e-7))
def spearman(u,v):
    ru=np.argsort(np.argsort(u)); rv=np.argsort(np.argsort(v)); return float(np.corrcoef(ru,rv)[0,1])
def main():
    print(f"=== JEP-24b: Poincare via transitive-closure + Riemannian SGD (N={N}) ===",flush=True)
    X=torch.randn(N,2)*0.001; X.requires_grad_(True)
    lr=0.5
    P=POS
    for it in range(4000):
        u=P[:,0]; v=P[:,1]; negs=torch.randint(0,N,(len(P),15))
        du=pdist(X[u],X[v]); dn=pdist(X[u].unsqueeze(1).expand(-1,15,-1),X[negs])
        logits=torch.cat([(-du).unsqueeze(1),-dn],dim=1)
        loss=torch.nn.functional.cross_entropy(logits,torch.zeros(len(P),dtype=torch.long))
        loss.backward()
        with torch.no_grad():
            g=X.grad
            scale=((1-(X**2).sum(1,keepdim=True))**2)/4.0   # Riemannian conformal factor
            X-= lr*scale*g
            nrm=X.norm(dim=1,keepdim=True); X[:]=torch.where(nrm>=0.9995, X/nrm*0.9995, X)
            X.grad.zero_()
    with torch.no_grad():
        Xn=X.detach().numpy(); iu=np.triu_indices(N,1)
        hd=np.array([float(pdist(torch.tensor(Xn[a]),torch.tensor(Xn[b]))) for a,b in zip(*iu)])
        sp=spearman(hd,GD[iu])
    print(f"  hyperbolic Spearman = {sp:.3f}   (Euclidean 0.41, JEP-24 plain 0.54)",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if sp>=0.85 and sp>=0.71:
        print(f"JEP-24b: PASS - proper Poincare embedding (transitive-closure positives + Riemannian SGD) recovers",flush=True)
        print(f"the tree hierarchy at Spearman {sp:.2f}, vs Euclidean 0.41 (JEP-23b). Confirms the geometry-mismatch",flush=True)
        print(f"diagnosis and extends the cognitive-map approach to HIERARCHIES (IS-A/taxonomies). Hyperbolic",flush=True)
        print(f"geometry (Nickel-Kiela 2017) is the right space for conceptual hierarchy - established, named as such.",flush=True)
    else:
        print(f"JEP-24b: PARTIAL/NULL - hyperbolic Spearman {sp:.2f}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()
