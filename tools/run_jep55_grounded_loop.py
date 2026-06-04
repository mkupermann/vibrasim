"""JEP-55 - complete grounded loop: form concepts from features -> reasoner on discovered taxonomy -> plan."""
import numpy as np
from collections import deque
from scipy.cluster.hierarchy import linkage
from tools.concept_reasoner import ConceptReasoner
rng=np.random.default_rng(55)
# 1) ground-truth tree + distinctive-coarse features (JEP-54b)
def build_tree(depth=4):
    parent={};nid=1;frontier=["n0"]
    for d in range(depth):
        new=[]
        for p in frontier:
            for i in range(2):
                c=f"n{nid}";nid+=1;parent[c]=p;new.append(c)
        frontier=new
    return parent,frontier
parent_t,leaves=build_tree(4)
def anc_t(v):
    a=[v];p=parent_t.get(v)
    while p is not None: a.append(p);p=parent_t.get(p)
    return a
nodes=set(parent_t)|{"n0"};FD=8;feat={n:rng.normal(0,1,FD) for n in nodes}
base={l:sum(feat[a]*(2.0**(-(len(anc_t(a))-1))) for a in anc_t(l)) for l in leaves}
X=np.array([base[l]+rng.normal(0,0.3,FD) for l in leaves])
# 2) FORM concepts: cluster -> dendrogram -> taxonomy (binary merge tree)
Z=linkage(X,method="ward"); Nl=len(leaves)
# build parent->children for discovered tree: leaves 0..Nl-1, internal Nl..2Nl-2
dtax={};dparent={}
for i,(a,b,_,_) in enumerate(Z):
    node=Nl+i; ch=[int(a),int(b)]; dtax[f"c{node}"]=[f"c{int(a)}" if a>=Nl else f"L{int(a)}", f"c{int(b)}" if b>=Nl else f"L{int(b)}"]
    for c in [int(a),int(b)]:
        dparent[c]=node
leafname={i:f"L{i}" for i in range(Nl)}
# 3) reasoner on DISCOVERED taxonomy
cr=ConceptReasoner(dtax); cr.fit(euc_dim=4,hyp_dim=10,iters=4000)
# discovered category = internal node; its leaves
def disc_leaves(catname):
    out=[];q=deque([catname])
    while q:
        n=q.popleft()
        for c in dtax.get(n,[]):
            if c.startswith("L"): out.append(c)
            else: q.append(c)
    return out
cats=[c for c in dtax if len(disc_leaves(c))>=3 and len(disc_leaves(c))<=Nl//2]
# true top-branch of each leaf (for purity)
def true_branch(Lname): 
    i=int(Lname[1:]); return anc_t(leaves[i])[-2]
# grid + SR
M=8
def gen_looped(M,extra=20):
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
def sr_td(steps=1_200_000,alpha=0.02):
    Mt=np.zeros((S,S),np.float32);I=np.eye(S,dtype=np.float32);c=CELLS[rng.integers(S)]
    for _ in range(steps):
        nbs=list(ADJ[c]);nb=nbs[rng.integers(len(nbs))];Mt[CID[c]]+=alpha*(I[CID[c]]+gamma*Mt[CID[nb]]-Mt[CID[c]]);c=nb
    return Mt
def main():
    print("=== JEP-55: grounded loop - form concepts -> reason -> act ===", flush=True)
    # purity of discovered categories
    purs=[]
    for cat in cats:
        dl=disc_leaves(cat); brs=[true_branch(l) for l in dl]; 
        from collections import Counter; mc=Counter(brs).most_common(1)[0][1]; purs.append(mc/len(dl))
    print(f"  discovered categories={len(cats)}, mean true-purity={np.mean(purs):.3f}", flush=True)
    Mt=sr_td()
    reached=trials=0
    Lnames=[leafname[i] for i in range(Nl)]
    for _ in range(120):
        cells=list(CELLS);rng.shuffle(cells);ent_cell={Lnames[i]:cells[i] for i in range(Nl)}
        cat=cats[rng.integers(len(cats))]; members=set(disc_leaves(cat))
        grounded=[e for e in Lnames if cr.is_a(e,cat)]
        grounded=[e for e in grounded if e in ent_cell]
        if not grounded: continue
        trials+=1;start=CELLS[rng.integers(S)]
        target=max(grounded,key=lambda e:Mt[CID[start],CID[ent_cell[e]]]);c=start
        for _ in range(6*S):
            nbs=list(ADJ[c]);c=max(nbs,key=lambda nb:Mt[CID[nb],CID[ent_cell[target]]])
            if c==ent_cell[target]: break
        arrived=next((e for e,cell in ent_cell.items() if cell==c),None)
        reached+=int(arrived in members)
    acc=reached/trials if trials else 0
    print(f"  trials={trials}  reached an entity in the goal DISCOVERED-category = {acc:.3f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if acc>=0.85 and np.mean(purs)>=0.9:
        print(f"JEP-55: PASS - the COMPLETE grounded loop works: from raw feature observations the agent FORMS", flush=True)
        print(f"concepts (clustering, true-purity {np.mean(purs):.2f}), REASONS over its self-discovered taxonomy", flush=True)
        print(f"(IS-A), and ACTS - grounded planning to a self-formed category reaches a correct member {acc:.2f} of", flush=True)
        print(f"the time. Experience -> concepts -> reasoning -> action, nothing given but features. Established", flush=True)
        print(f"methods (clustering, SR/TD, Poincare), named as such.", flush=True)
    else:
        print(f"JEP-55: PARTIAL/NULL - planning {acc:.2f}, purity {np.mean(purs):.2f}", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
