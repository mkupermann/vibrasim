"""JEP-129 - discover a relation composition rule (uncle = parent o sibling) from observation."""
import numpy as np
from collections import defaultdict
rng=np.random.default_rng(129)
def main():
    print("=== JEP-129: learn a relation COMPOSITION rule from observation ===", flush=True)
    def trial(seed, holdout=0.3):
        r=np.random.default_rng(seed); N=14; ents=list(range(N))
        # base relations
        parent={}; 
        for x in ents:
            parent[x]=r.integers(N)  # each has one parent (random, may form structure)
        # siblings: random sibling groups
        groups=[[] for _ in range(4)]
        for x in ents: groups[r.integers(4)].append(x)
        sibling=set()
        for g in groups:
            for a in g:
                for b in g:
                    if a!=b: sibling.add((a,b))
        parent_set=set((x,parent[x]) for x in ents)
        # TARGET: uncle(x,z) = exists y: parent(x,y) and sibling(y,z)
        uncle=set()
        for x in ents:
            y=parent[x]
            for (yy,z) in sibling:
                if yy==y: uncle.add((x,z))
        base={"parent":parent_set,"sibling":sibling}
        def compose(R1,R2):
            out=set(); idx=defaultdict(set)
            for a,b in R1: idx[b].add(a)
            for b,c in R2:
                for a in idx[b]: out.add((a,c))
            return out
        # hold out some uncle facts
        ulist=list(uncle); r.shuffle(ulist); k=int(len(ulist)*holdout)
        held=set(ulist[:k]); observed_uncle=set(ulist[k:])
        # SEARCH compositions R1 o R2 over base relations (and identity) for best match to observed_uncle
        rels=dict(base); best=None; bestf1=-1
        cand=[(n1,n2) for n1 in rels for n2 in rels]
        for n1,n2 in cand:
            comp=compose(rels[n1],rels[n2])
            tp=len(comp & observed_uncle); 
            prec=tp/len(comp) if comp else 0; rec=tp/len(observed_uncle) if observed_uncle else 0
            f1=2*prec*rec/(prec+rec) if (prec+rec) else 0
            if f1>bestf1: bestf1=f1; best=(n1,n2); bestcomp=comp
        # predict held-out with the learned rule
        pred=compose(rels[best[0]],rels[best[1]])
        held_acc = len(held & pred)/len(held) if held else 1.0
        correct_rule = best==("parent","sibling")
        return correct_rule, held_acc, best
    cr=[]; ha=[]
    for s in range(150):
        c,h,b=trial(s); cr.append(c); ha.append(h)
    print(f"   discovered the correct rule (parent o sibling): {np.mean(cr):.2f}", flush=True)
    print(f"   held-out uncle prediction accuracy (learned rule): {np.mean(ha):.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if np.mean(cr)>=0.85 and np.mean(ha)>=0.85:
        print(f"JEP-129: PASS - the learner DISCOVERS the composition rule 'uncle = parent o sibling' from observed",flush=True)
        print(f"facts ({np.mean(cr):.2f}) and predicts held-out uncle facts ({np.mean(ha):.2f}). Learning compositional",flush=True)
        print(f"relational STRUCTURE from data - a real step on the JEP-69/70 frontier. Established (rule discovery/ILP", flush=True)
        print(f"simplest form), named; no novelty.",flush=True)
    else:
        print(f"JEP-129: PARTIAL/NULL - rule {np.mean(cr):.2f}, held-out {np.mean(ha):.2f}. Recorded honestly.",flush=True)
    print("HONEST: searches a SMALL space of 2-relation compositions over GIVEN base relations; deeper/longer rules,",flush=True)
    print("noise, and many candidate relations (spurious matches) are the limits. Single clean composition here.",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
