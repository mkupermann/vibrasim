"""JEP-30c - LCA with a better embedding (20D, more iters): does embedding quality fix distant-pair LCA?"""
import numpy as np, torch
from tools.concept_reasoner import ConceptReasoner, _poin_dc
from tools.run_jep30_lca import TAX, true_lca
def main():
    print("=== JEP-30c: compositional LCA, better embedding (20D, 9000 iters) ===", flush=True)
    cr = ConceptReasoner(TAX); cr.fit(euc_dim=4, hyp_dim=20, iters=9000)
    X=cr.Xh; nm=cr.hnorm
    def pred_lca(ia,ib):
        cap=min(nm[ia],nm[ib]); cands=[c for c in range(cr.N) if nm[c]<cap-1e-6 and c!=ia and c!=ib]
        if not cands: return None
        return min(((float(_poin_dc(X[c:c+1],X[ia:ia+1])+_poin_dc(X[c:c+1],X[ib:ib+1])),c) for c in cands))[1]
    rng=np.random.default_rng(0); exact=common=tot=0
    for _ in range(500):
        ia,ib=rng.integers(cr.N),rng.integers(cr.N)
        if ia==ib: continue
        tl=true_lca(cr,cr.nodes[ia],cr.nodes[ib]); pl=pred_lca(ia,ib)
        if tl is None or pl is None: continue
        tot+=1; exact+=int(pl==tl)
        aa=set([ia]+cr._ancestors(ia)); bb=set([ib]+cr._ancestors(ib)); common+=int(pl in aa and pl in bb)
    ea,ca=exact/tot,common/tot
    print(f"  pairs={tot}  exact-LCA={ea:.3f}  common-ancestor={ca:.3f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if ea>=0.6 and ca>=0.85:
        print(f"JEP-30c: PASS - a better hyperbolic embedding (20D) supports COMPOSITIONAL LCA queries: exact-LCA", flush=True)
        print(f"{ea:.2f}, valid-common-ancestor {ca:.2f}. 'What category includes both X and Y' read from geometry.", flush=True)
        print(f"Embedding quality was the limiter (JEP-30b 0.55/0.75). Step toward compositional reasoning. Named established.", flush=True)
    else:
        print(f"JEP-30c: PARTIAL/NULL - exact {ea:.2f}, common-anc {ca:.2f} (better embedding helped but bars not met)", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
