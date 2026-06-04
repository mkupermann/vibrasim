"""JEP-32 - verify the fixed is_a (calibrated containment) on sanity + classification accuracy."""
import numpy as np
from tools.concept_reasoner import ConceptReasoner
TAX={'living_thing':['animal','plant'],'animal':['mammal','bird'],'mammal':['carnivore','primate'],
 'carnivore':['cat','dog','wolf'],'primate':['human','chimp'],'bird':['eagle','sparrow','owl'],
 'plant':['tree','flower'],'tree':['oak','pine','maple'],'flower':['rose','tulip','daisy']}
def main():
    print("=== JEP-32: fixed is_a (calibrated containment) ===", flush=True)
    cr=ConceptReasoner(TAX); cr.fit(hyp_dim=10,iters=4000)
    sanity=[('cat','mammal',True),('cat','animal',True),('cat','plant',False),('cat','bird',False),
            ('rose','plant',True),('rose','animal',False),('oak','tree',True),('oak','mammal',False),
            ('cat','dog',False),('mammal','cat',False)]
    print("  sanity:", flush=True); wrong=0
    for a,b,exp in sanity:
        r=cr.is_a(a,b); tag='OK' if r==exp else 'WRONG'; wrong+=(r!=exp)
        print(f"    is_a({a},{b})={r} exp={exp} {tag}", flush=True)
    # classification accuracy on all pairs: positive=true ancestor, negative=non-ancestor
    anc={(v,u) for v in range(cr.N) for u in cr._ancestors(v)}
    rng=np.random.default_rng(2); pos=list(anc); neg=[]
    while len(neg)<len(pos):
        a,b=int(rng.integers(cr.N)),int(rng.integers(cr.N))
        if a!=b and (a,b) not in anc: neg.append((a,b))
    tp=sum(cr.is_a(cr.nodes[a],cr.nodes[b]) for a,b in pos)/len(pos)
    tn=sum(not cr.is_a(cr.nodes[a],cr.nodes[b]) for a,b in neg)/len(neg)
    acc=(tp*len(pos)+tn*len(neg))/(len(pos)+len(neg))
    print(f"  is-a classification: TPR={tp:.3f} TNR={tn:.3f} acc={acc:.3f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if acc>=0.85 and wrong==0:
        print(f"JEP-32: PASS - the calibrated is_a fixes the flaw: classification acc {acc:.2f} (TPR {tp:.2f}, TNR", flush=True)
        print(f"{tn:.2f}), and ALL sanity cases correct (rose NOT is_a animal, oak NOT is_a mammal, cat is_a mammal", flush=True)
        print(f"True). Adding the CONTAINMENT condition (distance) to generality makes is_a a proper is-a classifier", flush=True)
        print(f"that rejects cross-branch general concepts. Deliverable corrected. Established methods, named.", flush=True)
    else:
        print(f"JEP-32: PARTIAL/NULL - acc {acc:.2f}, sanity wrong {wrong}", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
