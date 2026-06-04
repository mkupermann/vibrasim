"""JEP-46 - abstract-goal planning on real WordNet using order-embedding is-a (does the component fix propagate?)."""
import numpy as np
from collections import deque
from nltk.corpus import wordnet as wn
from tools.concept_reasoner import ConceptReasoner
rng=np.random.default_rng(46)
def build_tax(root):
    r=wn.synset(root);seen=set()
    def cl(s):
        seen.add(s)
        for h in s.hyponyms():
            if h not in seen: cl(h)
    cl(r);tax={}
    for s in seen:
        for c in s.hyponyms():
            if c in seen: tax.setdefault(s.name(),[]).append(c.name())
    return tax
M=10
def gen_looped(M,extra=30):
    adj={(x,y):set() for x in range(M) for y in range(M)};seen={(0,0)};st=[(0,0)]
    while st:
        x,y=st[-1];nb=[(x+dx,y+dy) for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)] if 0<=x+dx<M and 0<=y+dy<M and (x+dx,y+dy) not in seen]
        if nb: n=nb[rng.integers(len(nb))];adj[(x,y)].add(n);adj[n].add((x,y));seen.add(n);st.append(n)
        else: st.pop()
    cells=[(x,y) for x in range(M) for y in range(M)];added=0
    while added<extra:
        c=cells[rng.integers(len(cells))];x,y=c
        opts=[(x+dx,y+dy) for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)] if 0<=x+dx<M and 0<=y+dy<M and (x+dx,y+dy) not in adj[c]]
        if opts: n=opts[rng.integers(len(opts))];adj[c].add(n);adj[n].add(c);added+=1
    return adj
ADJ=gen_looped(M);CELLS=[(x,y) for x in range(M) for y in range(M)];ID={c:i for i,c in enumerate(CELLS)};S=len(CELLS);gamma=0.97
def sr_td(steps=2_000_000,alpha=0.02):
    Mt=np.zeros((S,S),np.float32);I=np.eye(S,dtype=np.float32);c=CELLS[rng.integers(S)]
    for _ in range(steps):
        nbs=list(ADJ[c]);nb=nbs[rng.integers(len(nbs))];Mt[ID[c]]+=alpha*(I[ID[c]]+gamma*Mt[ID[nb]]-Mt[ID[c]]);c=nb
    return Mt
def descendants(cr,name):
    children={p:[] for p in range(cr.N)}
    for c,p in cr.parent.items(): children[p].append(c)
    out=set();q=deque([cr.ID[name]])
    while q:
        n=q.popleft()
        for c in children[n]: out.add(cr.nodes[c]);q.append(c)
    return out
def main():
    print("=== JEP-46: integration on real WordNet with ORDER is-a ===", flush=True)
    cr=ConceptReasoner(build_tax("carnivore.n.01")); cr.fit(euc_dim=8,hyp_dim=20,iters=8000,isa_method="order")
    Mt=sr_td()
    leaves=[n for n in cr.nodes if not any(cr.parent.get(c)==cr.ID[n] for c in range(cr.N))]
    cats=[n for n in cr.nodes if len(descendants(cr,n)&set(leaves))>=3 and n!="carnivore.n.01"]
    sample=list(rng.choice(leaves,min(16,len(leaves)),replace=False))
    reached=trials=0
    for _ in range(150):
        cells=list(CELLS);rng.shuffle(cells);ent_cell={sample[i]:cells[i] for i in range(len(sample))}
        cat=cats[rng.integers(len(cats))]
        grounded=[e for e in sample if cr.is_a(e,cat)]
        if not grounded: continue
        trials+=1;start=CELLS[rng.integers(S)]
        target=max(grounded,key=lambda e:Mt[ID[start],ID[ent_cell[e]]]);c=start
        for _ in range(6*S):
            nbs=list(ADJ[c]);c=max(nbs,key=lambda nb:Mt[ID[nb],ID[ent_cell[target]]])
            if c==ent_cell[target]: break
        arrived=next((e for e,cell in ent_cell.items() if cell==c),None)
        reached+=int(arrived in (descendants(cr,cat)&set(sample)))
    acc=reached/trials if trials else 0
    print(f"  trials={trials}  reached-correct-category = {acc:.3f}  (JEP-37 poincare was 0.79)", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if acc>=0.88:
        print(f"JEP-46: PASS - the component fix PROPAGATES: with order-embedding is-a, abstract-goal planning on", flush=True)
        print(f"real WordNet reaches {acc:.2f} (vs 0.79 with poincare, JEP-37). Fixing the is-a method (JEP-42-45)", flush=True)
        print(f"improves the integrated behaviour - closing the loop on JEP-37's 'inherits component limits'.", flush=True)
        print(f"Established methods (Vendrov 2016, SR/TD), named as such.", flush=True)
    else:
        print(f"JEP-46: PARTIAL/NULL - reached {acc:.2f} (vs 0.79 poincare)", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
