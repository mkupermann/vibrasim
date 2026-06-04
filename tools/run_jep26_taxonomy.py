"""JEP-26 - Euclidean vs hyperbolic embedding on a REAL irregular taxonomy; IS-A inference. torch."""
import numpy as np, torch
from collections import deque
rng=np.random.default_rng(260); torch.manual_seed(4)
# realistic irregular taxonomy: parent -> children
TAX={
 "living_thing":["animal","plant"],
 "animal":["vertebrate","invertebrate"],
 "vertebrate":["mammal","bird","reptile","fish"],
 "mammal":["carnivore","primate","rodent","ungulate"],
 "carnivore":["feline","canine"],
 "feline":["cat","lion","tiger"], "canine":["dog","wolf","fox"],
 "primate":["human","chimp","gorilla"], "rodent":["mouse","rat","squirrel"],
 "ungulate":["horse","cow","deer"],
 "bird":["raptor","waterfowl","songbird"],
 "raptor":["eagle","hawk","owl"], "waterfowl":["duck","goose","swan"], "songbird":["sparrow","robin","finch"],
 "reptile":["snake","lizard","turtle","crocodile"],
 "fish":["salmon","shark","tuna","trout"],
 "invertebrate":["insect","arachnid","mollusk"],
 "insect":["ant","bee","butterfly","beetle"], "arachnid":["spider","scorpion","tick"],
 "mollusk":["snail","octopus","clam"],
 "plant":["tree","flower","grass"],
 "tree":["oak","pine","maple","birch"], "flower":["rose","tulip","daisy","lily"], "grass":["wheat","corn","bamboo"],
}
nodes=set(["living_thing"])
for p,cs in TAX.items():
    nodes.add(p); nodes.update(cs)
nodes=sorted(nodes); ID={n:i for i,n in enumerate(nodes)}; N=len(nodes)
adj={i:set() for i in range(N)}; parent={}
for p,cs in TAX.items():
    for c in cs:
        adj[ID[p]].add(ID[c]); adj[ID[c]].add(ID[p]); parent[ID[c]]=ID[p]
def graphdist():
    D=np.zeros((N,N))
    for s in range(N):
        d={s:0};q=deque([s])
        while q:
            c=q.popleft()
            for nb in adj[c]:
                if nb not in d: d[nb]=d[c]+1; q.append(nb)
        for j in range(N): D[s,j]=d.get(j,N)
    return D
GD=graphdist()
def anc(v):
    a=[]; p=parent.get(v)
    while p is not None: a.append(p); p=parent.get(p)
    return a
ANCPAIRS=[(u,v) for v in range(N) for u in anc(v)]  # u is ancestor of v
POS=[]
for v in range(N):
    for u in anc(v): POS.append((u,v)); POS.append((v,u))
POS=torch.tensor(POS); iu=np.triu_indices(N,1); gd_np=GD[iu]
I=torch.tensor(iu[0]); J=torch.tensor(iu[1])
def spearman(u,v):
    ru=np.argsort(np.argsort(u)); rv=np.argsort(np.argsort(v)); return float(np.corrcoef(ru,rv)[0,1])
def euc_d(X,i,j): return ((X[i]-X[j])**2).sum(-1).clamp(min=1e-9).sqrt()
def poin_d(X,i,j):
    diff=((X[i]-X[j])**2).sum(-1); nx=(X[i]**2).sum(-1); ny=(X[j]**2).sum(-1)
    return torch.acosh(torch.clamp(1+2*diff/((1-nx)*(1-ny)+1e-9),min=1+1e-7))
def poin_dc(a,b):
    diff=((a-b)**2).sum(-1); na=(a**2).sum(-1); nb=(b**2).sum(-1)
    return torch.acosh(torch.clamp(1+2*diff/((1-na)*(1-nb)+1e-9),min=1+1e-7))
def fit_euclid(iters=3000):
    X=torch.randn(N,4)*0.1; X.requires_grad_(True); s=torch.tensor(1.0,requires_grad=True)
    opt=torch.optim.Adam([X,s],lr=0.02)
    for it in range(iters):
        opt.zero_grad(); d=euc_d(X,I,J); loss=((d-s*torch.tensor(GD[iu],dtype=torch.float32))**2).mean()
        loss.backward(); opt.step()
    return X.detach()
def fit_hyper(iters=4000):
    X=torch.randn(N,2)*0.001
    for it in range(iters):
        X.requires_grad_(True)
        u=POS[:,0]; v=POS[:,1]; negs=torch.randint(0,N,(len(POS),15))
        du=poin_dc(X[u],X[v]); dn=poin_dc(X[u].unsqueeze(1).expand(-1,15,-1), X[negs])
        logits=torch.cat([(-du).unsqueeze(1),-dn],dim=1)
        loss=torch.nn.functional.cross_entropy(logits,torch.zeros(len(POS),dtype=torch.long))
        loss.backward()
        with torch.no_grad():
            g=X.grad; sc=((1-(X**2).sum(1,keepdim=True)).clamp(min=1e-4)**2)/4.0
            X=X-0.3*sc*g; nrm=X.norm(dim=1,keepdim=True); X=torch.where(nrm>=0.999,X/nrm*0.999,X)
        X=X.detach()
    return X
def spear_of(X,hyp):
    if hyp: d=np.array([float(poin_d(X,torch.tensor([a]),torch.tensor([b]))) for a,b in zip(*iu)])
    else: d=np.array([float(euc_d(X,torch.tensor([a]),torch.tensor([b]))) for a,b in zip(*iu)])
    return spearman(d,gd_np)
def ancestor_acc(X):
    # predict which of (u,v) is ancestor by smaller norm (more general = closer to origin)
    norms=(X**2).sum(1).numpy()
    ok=0
    for (u,v) in ANCPAIRS:  # u is the true ancestor
        ok+=int(norms[u]<norms[v])
    return ok/len(ANCPAIRS)
def main():
    print(f"=== JEP-26: real taxonomy ({N} concepts), Euclidean vs hyperbolic IS-A inference ===",flush=True)
    Xe=fit_euclid(); Xh=fit_hyper()
    spe=spear_of(Xe,False); sph=spear_of(Xh,True)
    ae=ancestor_acc(Xe); ah=ancestor_acc(Xh)
    print(f"  Spearman(emb,graph):   Euclidean={spe:.3f}   hyperbolic={sph:.3f}",flush=True)
    print(f"  IS-A ancestor-direction acc (smaller norm=more general):  Euclidean={ae:.3f}   hyperbolic={ah:.3f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if ah>=0.85 and ah>=ae+0.2 and sph>spe:
        print(f"JEP-26: PASS - on a REAL irregular taxonomy, the HYPERBOLIC cognitive map captures IS-A structure:",flush=True)
        print(f"ancestor-direction (generality) accuracy {ah:.2f} vs Euclidean {ae:.2f}, and better distance",flush=True)
        print(f"preservation ({sph:.2f} vs {spe:.2f}). The radial axis encodes GENERALITY (general concepts near",flush=True)
        print(f"origin) - so 'a cat IS-A mammal' is read off the geometry. Real taxonomic structure needs hyperbolic",flush=True)
        print(f"cognitive maps. Grounds JEP-24 in real data. Nickel-Kiela (2017) established - named as such.",flush=True)
    else:
        print(f"JEP-26: PARTIAL/NULL - anc acc E{ae:.2f}/H{ah:.2f}, Spearman E{spe:.2f}/H{sph:.2f}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()
