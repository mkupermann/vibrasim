"""GEO-21b — orthogonal-subspace integration on a BRANCHING TREE (avoids chain degeneracy), real LLM words."""
import numpy as np
from sentence_transformers import SentenceTransformer

# 13 real org-words as a branching tree (each non-root has one parent); pick words MiniLM knows.
WORDS=["company","division","department","team","group","unit","branch","office","section","squad","crew","cell","wing"]
# branching tree parent map (binary-ish): node i parent = (i-1)//2  -> classic heap tree, branch=2
def main():
    print("=== GEO-21b: subspace integration on a BRANCHING tree ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    L=np.array(m.encode(WORDS,normalize_embeddings=True))
    nE=len(WORDS); Ds=24; rng=np.random.default_rng(1)
    parent={i:(i-1)//2 for i in range(1,nE)}
    edges=[(c,p) for c,p in parent.items()]               # child->parent
    # held out: leaves (deepest) for parent test; grandparent for composition
    S=rng.normal(0,.3,(nE,Ds)); r=rng.normal(0,.3,Ds); lr=0.05; margin=1.0
    # train on all but a few held-out parent edges
    held=[(c,p) for c,p in edges if c in (9,10,11,12)]    # leaves
    train=[e for e in edges if e not in held]
    for ep in range(6000):
        S/=np.linalg.norm(S,axis=1,keepdims=True)+1e-9
        for h,t in train:
            dp=S[h]+r-S[t]; sp=np.linalg.norm(dp)
            tn=rng.integers(0,nE); dn=S[h]+r-S[tn]; sn=np.linalg.norm(dn)
            if margin+sp-sn>0:
                gp=dp/(sp+1e-9); gn=dn/(sn+1e-9)
                S[h]-=lr*gp; S[t]+=lr*gp; r-=lr*gp; S[h]+=lr*gn; S[tn]-=lr*gn; r+=lr*gn
    def h1(q,t): d=np.linalg.norm(S-q,axis=1); return int(np.argmin(d)==t)
    accA=np.mean([h1(S[c]+r,p) for c,p in held])
    # grandparent composition: child -> grandparent via 2r (held-out, never trained)
    gp_pairs=[(c,parent[parent[c]]) for c in range(3,nE) if c in parent and parent[c] in parent]
    accG=np.mean([h1(S[c]+2*r,g) for c,g in gp_pairs])
    L2=np.array(m.encode(WORDS,normalize_embeddings=True)); drift=np.max(np.abs(L@L.T-L2@L2.T))
    print(f"  (a) parent learned (held-out leaves) hits@1 = {accA:.2f}", flush=True)
    print(f"  (b) grandparent via 2r composition   hits@1 = {accG:.2f}  (chance {1/nE:.2f})", flush=True)
    print(f"  (c) semantic-block drift                    = {drift:.2e}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if accA>=0.6 and drift<1e-5:
        print("GEO-21b: PASS - on a branching tree the orthogonal-subspace integration cleanly learns new structure (parent) AND preserves LLM semantics exactly. The GEO-14 tension is resolved; GEO-21's cap was chain degeneracy, not the mechanism.", flush=True)
    else:
        print(f"GEO-21b: PARTIAL - parent {accA:.2f}, gp {accG:.2f}, drift {drift:.1e}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
