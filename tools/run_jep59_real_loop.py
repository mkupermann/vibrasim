"""JEP-59 - complete grounded loop on REAL Fashion-MNIST (form visual concepts -> reason -> act)."""
import numpy as np
from collections import deque
from scipy.cluster.hierarchy import linkage
from tools.concept_reasoner import ConceptReasoner
rng=np.random.default_rng(59)
d=np.load("data/fashion_mnist.npz")
X=d["x_train"].reshape(-1,784).astype(np.float32)/255.0; y=d["y_train"]
names=["t-shirt","trouser","pullover","dress","coat","sandal","shirt","sneaker","bag","ankle_boot"]
means=np.array([X[y==k].mean(0) for k in range(10)]); Nl=10
Z=linkage(means,method="ward")
dtax={}
for i,(a,b,_,_) in enumerate(Z):
    node=Nl+i
    dtax[f"c{node}"]=[(f"c{int(a)}" if a>=Nl else f"L{int(a)}"),(f"c{int(b)}" if b>=Nl else f"L{int(b)}")]
def disc_leaves(catname):
    out=[];q=deque([catname])
    while q:
        n=q.popleft()
        for c in dtax.get(n,[]):
            if c.startswith("L"): out.append(c)
            else: q.append(c)
    return out
cats=[c for c in dtax if 2<=len(disc_leaves(c))<=Nl//2]
cr=ConceptReasoner(dtax); cr.fit(euc_dim=4,hyp_dim=10,iters=4000)
M=8
def gen_looped(M,extra=18):
    adj={(x,y):set() for x in range(M) for y in range(M)};seen={(0,0)};st=[(0,0)]
    while st:
        x,y=st[-1];nb=[(x+dx,y+dy) for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)] if 0<=x+dx<M and 0<=y+dy<M and (x+dx,y+dy) not in seen]
        if nb: nn=nb[rng.integers(len(nb))];adj[(x,y)].add(nn);adj[nn].add((x,y));seen.add(nn);st.append(nn)
        else: st.pop()
    cells=[(x,y) for x in range(M) for y in range(M)];added=0
    while added<extra:
        c=cells[rng.integers(len(cells))];x,y=c
        opts=[(x+dx,y+dy) for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)] if 0<=x+dx<M and 0<=y+dy<M and (x+dx,y+dy) not in adj[c]]
        if opts: nn=opts[rng.integers(len(opts))];adj[c].add(nn);adj[nn].add(c);added+=1
    return adj
ADJ=gen_looped(M);CELLS=[(x,y) for x in range(M) for y in range(M)];CID={c:i for i,c in enumerate(CELLS)};S=len(CELLS);gamma=0.97
def sr_td(steps=1_000_000,alpha=0.02):
    Mt=np.zeros((S,S),np.float32);I=np.eye(S,dtype=np.float32);c=CELLS[rng.integers(S)]
    for _ in range(steps):
        nbs=list(ADJ[c]);nb=nbs[rng.integers(len(nbs))];Mt[CID[c]]+=alpha*(I[CID[c]]+gamma*Mt[CID[nb]]-Mt[CID[c]]);c=nb
    return Mt
def main():
    print("=== JEP-59: complete grounded loop on REAL Fashion-MNIST ===", flush=True)
    print(f"  discovered categories: {len(cats)}", flush=True)
    for cat in cats[:6]:
        print(f"    {cat} = {[names[int(l[1:])] for l in disc_leaves(cat)]}", flush=True)
    Mt=sr_td(); Lnames=[f"L{i}" for i in range(Nl)]
    reached=trials=0
    for _ in range(120):
        cells=list(CELLS);rng.shuffle(cells);ent_cell={Lnames[i]:cells[i] for i in range(Nl)}
        cat=cats[rng.integers(len(cats))]; members=set(disc_leaves(cat))
        grounded=[e for e in Lnames if cr.is_a(e,cat) and e in ent_cell]
        if not grounded: continue
        trials+=1;start=CELLS[rng.integers(S)]
        target=max(grounded,key=lambda e:Mt[CID[start],CID[ent_cell[e]]]);c=start
        for _ in range(6*S):
            nbs=list(ADJ[c]);c=max(nbs,key=lambda nb:Mt[CID[nb],CID[ent_cell[target]]])
            if c==ent_cell[target]: break
        arrived=next((e for e,cell in ent_cell.items() if cell==c),None)
        reached+=int(arrived in members)
    acc=reached/trials if trials else 0
    print(f"\n  grounded-planning success (reach a member of the goal visual-category) = {acc:.3f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if acc>=0.85:
        print(f"JEP-59: PASS - the complete form->reason->act loop works on REAL Fashion-MNIST: the agent forms", flush=True)
        print(f"VISUAL concepts from real image features, reasons over its self-discovered taxonomy (IS-A), and plans", flush=True)
        print(f"to a discovered category, reaching a member {acc:.2f} of the time. The grounded loop is NOT synthetic-", flush=True)
        print(f"only. Honest caveat (JEP-58): the concepts are VISUAL, not functional. Established methods, named.", flush=True)
    else:
        print(f"JEP-59: PARTIAL/NULL - planning {acc:.2f}", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
