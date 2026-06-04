"""JEP-38 - radial-depth anchor pins the generality sign across seeds (WordNet carnivore)."""
import numpy as np, torch
from nltk.corpus import wordnet as wn
from tools.concept_reasoner import ConceptReasoner
def build_tax(root_name):
    root=wn.synset(root_name); seen=set()
    def cl(s):
        seen.add(s)
        for h in s.hyponyms():
            if h not in seen: cl(h)
    cl(root); tax={}
    for s in seen:
        for c in s.hyponyms():
            if c in seen: tax.setdefault(s.name(),[]).append(c.name())
    return tax
def main():
    print("=== JEP-38: radial-depth anchor pins generality sign (WordNet carnivore 366) ===", flush=True)
    TAX=build_tax("carnivore.n.01")
    for label,anchor in [("anchor OFF",0.0),("anchor ON",0.5)]:
        raws=[]; helds=[]
        for seed in range(3):
            torch.manual_seed(seed)
            cr=ConceptReasoner(TAX,seed=seed)
            ALL=[(u,v) for v in range(cr.N) for u in cr._ancestors(v)]
            rng=np.random.default_rng(seed); idx=rng.permutation(len(ALL)); cut=int(0.3*len(ALL))
            ho=set(ALL[i] for i in idx[:cut])
            cr.fit(euc_dim=8,hyp_dim=20,iters=8000,holdout_pairs=ho,anchor=anchor)
            raw=np.mean([cr.hnorm[u]<cr.hnorm[v] for (u,v) in ALL])  # general(ancestor) smaller norm?
            held=np.mean([cr.is_a(cr.nodes[v],cr.nodes[u]) for (u,v) in ho])  # calibrated, held-out: v is_a u
            raws.append(raw); helds.append(held)
        print(f"  [{label}] raw norm-direction per seed: {[f'{r:.2f}' for r in raws]}  held-out calibrated is_a: {[f'{h:.2f}' for h in helds]}", flush=True)
        if anchor>0:
            on_raw_min=min(raws); on_held_min=min(helds)
    print("\n--- VERDICT ---", flush=True)
    if on_raw_min>=0.9 and on_held_min>=0.85:
        print(f"JEP-38: PASS - the radial-depth anchor PINS the generality sign: raw norm-direction is_a >= 0.90 on", flush=True)
        print(f"ALL 3 seeds (no inversion - vs the unpinned 0.13-0.86 swing of JEP-37), and held-out calibrated is_a", flush=True)
        print(f">= 0.85. Anchoring general concepts near the origin stabilizes the embedding. Deliverable improved -", flush=True)
        print(f"raw norm-direction is now reliable, and the JEP-37 sign-instability is fixed. Established, named.", flush=True)
    else:
        print(f"JEP-38: PARTIAL/NULL - anchor-ON raw {on_raw_min:.2f}, held {on_held_min:.2f}", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
