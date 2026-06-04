"""JEP-56 - grounded-loop operating envelope: formation purity + planning success vs feature noise."""
import numpy as np
from collections import deque, Counter
from scipy.cluster.hierarchy import linkage
from tools.concept_reasoner import ConceptReasoner
def run(sigma, seed):
    rng=np.random.default_rng(seed)
    parent_t={};nid=1;frontier=["n0"]
    for d in range(4):
        new=[]
        for p in frontier:
            for i in range(2): c=f"n{nid}";nid+=1;parent_t[c]=p;new.append(c)
        frontier=new
    leaves=frontier
    def anc_t(v):
        a=[v];p=parent_t.get(v)
        while p is not None: a.append(p);p=parent_t.get(p)
        return a
    nodes=set(parent_t)|{"n0"};FD=8;feat={n:rng.normal(0,1,FD) for n in nodes}
    base={l:sum(feat[a]*(2.0**(-(len(anc_t(a))-1))) for a in anc_t(l)) for l in leaves}
    X=np.array([base[l]+rng.normal(0,sigma,FD) for l in leaves]); Nl=len(leaves)
    Z=linkage(X,method="ward"); dtax={}
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
    cats=[c for c in dtax if 3<=len(disc_leaves(c))<=Nl//2]
    def true_branch(Lname): return anc_t(leaves[int(Lname[1:])])[-2]
    purs=[]
    for cat in cats:
        dl=disc_leaves(cat); brs=[true_branch(l) for l in dl]; purs.append(Counter(brs).most_common(1)[0][1]/len(dl))
    cr=ConceptReasoner(dtax); cr.fit(euc_dim=4,hyp_dim=10,iters=3500)
    # grid
    M=8
    adj={(x,y):set() for x in range(M) for y in range(M)};seen={(0,0)};st=[(0,0)]
    while st:
        x,y=st[-1];nb=[(x+dx,y+dy) for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)] if 0<=x+dx<M and 0<=y+dy<M and (x+dx,y+dy) not in seen]
        if nb: nn=nb[rng.integers(len(nb))];adj[(x,y)].add(nn);adj[nn].add((x,y));seen.add(nn);st.append(nn)
        else: st.pop()
    for _ in range(20):
        cs=[(x,y) for x in range(M) for y in range(M)];c=cs[rng.integers(len(cs))];x,y=c
        opts=[(x+dx,y+dy) for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)] if 0<=x+dx<M and 0<=y+dy<M and (x+dx,y+dy) not in adj[c]]
        if opts: nn=opts[rng.integers(len(opts))];adj[c].add(nn);adj[nn].add(c)
    CELLS=[(x,y) for x in range(M) for y in range(M)];CID={c:i for i,c in enumerate(CELLS)};S=len(CELLS);gamma=0.97
    Mt=np.zeros((S,S),np.float32);I=np.eye(S,dtype=np.float32);c=CELLS[rng.integers(S)]
    for _ in range(1_000_000):
        nbs=list(adj[c]);nb=nbs[rng.integers(len(nbs))];Mt[CID[c]]+=0.02*(I[CID[c]]+gamma*Mt[CID[nb]]-Mt[CID[c]]);c=nb
    Lnames=[f"L{i}" for i in range(Nl)]
    reached=trials=0
    for _ in range(100):
        cells=list(CELLS);rng.shuffle(cells);ent_cell={Lnames[i]:cells[i] for i in range(Nl)}
        cat=cats[rng.integers(len(cats))]
        # TRUE-category goal: the majority true-branch of the discovered category's members
        dl=disc_leaves(cat); goal_branch=Counter([true_branch(l) for l in dl]).most_common(1)[0][0]
        grounded=[e for e in Lnames if cr.is_a(e,cat) and e in ent_cell]
        if not grounded: continue
        trials+=1;start=CELLS[rng.integers(S)]
        target=max(grounded,key=lambda e:Mt[CID[start],CID[ent_cell[e]]]);cc=start
        for _ in range(6*S):
            nbs=list(adj[cc]);cc=max(nbs,key=lambda nb:Mt[CID[nb],CID[ent_cell[target]]])
            if cc==ent_cell[target]: break
        arrived=next((e for e,cell in ent_cell.items() if cell==cc),None)
        reached+=int(arrived is not None and true_branch(arrived)==goal_branch)
    return np.mean(purs), (reached/trials if trials else 0)
def main():
    print("=== JEP-56: grounded-loop operating envelope (formation purity + planning vs noise) ===", flush=True)
    print("   sigma   formation-purity   loop-planning-success", flush=True)
    for sigma in [0.3,0.8,1.5,2.5]:
        ps=[];gs=[]
        for seed in range(3):
            p,g=run(sigma,seed); ps.append(p); gs.append(g)
        print(f"   {sigma:.1f}     {np.mean(ps):.3f}             {np.mean(gs):.3f}", flush=True)
    print("\n--- FINDING ---", flush=True)
    print("Reports how the complete form->reason->act loop degrades with feature noise. Honest operating envelope", flush=True)
    print("of the grounded loop (JEP-55 was the clean sigma=0.3 point). Established methods, named.", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
