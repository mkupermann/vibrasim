"""JEP-39b - do entailment cones hold at real scale (WordNet carnivore 366)? Held-out IS-A classification."""
import numpy as np, torch
from nltk.corpus import wordnet as wn
def build_tax(root):
    r=wn.synset(root); seen=set()
    def cl(s):
        seen.add(s)
        for h in s.hyponyms():
            if h not in seen: cl(h)
    cl(r); tax={}
    for s in seen:
        for c in s.hyponyms():
            if c in seen: tax.setdefault(s.name(),[]).append(c.name())
    return tax
TAX=build_tax("carnivore.n.01")
nodes=set()
for p,cs in TAX.items(): nodes.add(p); nodes.update(cs)
nodes=sorted(nodes); ID={n:i for i,n in enumerate(nodes)}; N=len(nodes); parent={}
for p,cs in TAX.items():
    for c in cs: parent[ID[c]]=ID[p]
def anc(v):
    a=[];p=parent.get(v)
    while p is not None: a.append(p); p=parent.get(p)
    return a
ALL=[(u,v) for v in range(N) for u in anc(v)]; ANCS=set(ALL)
rng=np.random.default_rng(0); idx=rng.permutation(len(ALL)); cut=int(0.3*len(ALL))
HO=set(ALL[i] for i in idx[:cut]); TR=[ALL[i] for i in idx[cut:]]
EPS=0.1;K=0.1; torch.manual_seed(0)
def nrm(x): return x.norm(dim=-1).clamp(min=EPS,max=1-1e-4)
def aperture(x):
    nx=nrm(x); return torch.asin(torch.clamp(K*(1-nx**2)/nx,max=1-1e-6))
def xi(x,y):
    nx=nrm(x);ny=nrm(y);xy=(x*y).sum(-1);nxy=(x-y).norm(dim=-1).clamp(min=1e-6)
    num=xy*(1+nx**2)-nx**2*(1+ny**2); den=nx*nxy*torch.sqrt(torch.clamp(1+nx**2*ny**2-2*xy,min=1e-9))
    return torch.acos(torch.clamp(num/den,-1+1e-6,1-1e-6))
def energy(x,y): return torch.clamp(xi(x,y)-aperture(x),min=0.0)
def main():
    print(f"=== JEP-39b: entailment cones at scale (WordNet carnivore N={N}) ===", flush=True)
    X=(torch.randn(N,5)*0.1)
    with torch.no_grad():
        n=X.norm(dim=1,keepdim=True); X*=(EPS+0.3)/n.clamp(min=1e-6)
    px=torch.tensor([p[0] for p in TR]); py=torch.tensor([p[1] for p in TR])
    for it in range(8000):
        X.requires_grad_(True)
        ep=energy(X[px],X[py]).mean()
        nx=torch.randint(0,N,(len(TR),)); ny=torch.randint(0,N,(len(TR),))
        en=torch.clamp(0.3-energy(X[nx],X[ny]),min=0.0).mean()
        (ep+en).backward()
        with torch.no_grad():
            X=X-0.05*X.grad; nn=X.norm(dim=1,keepdim=True)
            X=torch.where(nn<EPS,X*EPS/nn.clamp(min=1e-6),X); X=torch.where(nn>1-1e-3,X/nn*(1-1e-3),X)
        X=X.detach()
    with torch.no_grad():
        def isa_pair(u,v): return float(energy(X[u:u+1],X[v:v+1]))<0.05  # v in u's cone => v is_a u
        # held-out classification: positives = held-out ancestor pairs (v is_a u); negatives = random non-anc
        tp=np.mean([isa_pair(u,v) for (u,v) in HO])
        neg=[]
        while len(neg)<len(HO):
            a,b=int(rng.integers(N)),int(rng.integers(N))
            if a!=b and (a,b) not in ANCS: neg.append((a,b))
        tn=np.mean([not isa_pair(a,b) for (a,b) in neg])
        acc=(tp+tn)/2
    print(f"  held-out IS-A classification: TPR={tp:.3f} TNR={tn:.3f} balanced-acc={acc:.3f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if acc>=0.85:
        print(f"JEP-39b: PASS - entailment cones hold at real scale: held-out balanced IS-A accuracy {acc:.2f} on 366", flush=True)
        print(f"WordNet concepts (TPR {tp:.2f}, TNR {tn:.2f}). The cone approach scales - worth integrating as the", flush=True)
        print(f"reasoner's is_a. Ganea 2018 established, named.", flush=True)
    else:
        print(f"JEP-39b: PARTIAL/NULL - balanced-acc {acc:.2f} (TPR {tp:.2f} TNR {tn:.2f})", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
