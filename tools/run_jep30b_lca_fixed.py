"""JEP-30b - LCA readout fixed: candidates STRICTLY more general than both inputs."""
import numpy as np, torch
from tools.concept_reasoner import ConceptReasoner, _poin_dc
from tools.run_jep30_lca import TAX, true_lca
def main():
    print("=== JEP-30b: LCA compositional query (fixed readout) ===", flush=True)
    cr = ConceptReasoner(TAX); cr.fit(euc_dim=4, hyp_dim=10, iters=5000)
    X = cr.Xh; nm = cr.hnorm
    def pred_lca(ia, ib):
        cap = min(nm[ia], nm[ib])
        cands = [c for c in range(cr.N) if nm[c] < cap - 1e-6 and c != ia and c != ib]
        if not cands: return None
        return min(((float(_poin_dc(X[c:c+1],X[ia:ia+1])+_poin_dc(X[c:c+1],X[ib:ib+1])),c) for c in cands))[1]
    rng = np.random.default_rng(0); exact=common=tot=0; ex=[]
    for _ in range(400):
        ia,ib=rng.integers(cr.N),rng.integers(cr.N)
        if ia==ib: continue
        tl=true_lca(cr,cr.nodes[ia],cr.nodes[ib]); pl=pred_lca(ia,ib)
        if tl is None or pl is None: continue
        tot+=1; exact+=int(pl==tl)
        aa=set([ia]+cr._ancestors(ia)); bb=set([ib]+cr._ancestors(ib)); common+=int(pl in aa and pl in bb)
        if len(ex)<6: ex.append((cr.nodes[ia],cr.nodes[ib],cr.nodes[tl],cr.nodes[pl]))
    print(f"  pairs={tot}  exact-LCA={exact/tot:.3f}  predicted-is-common-ancestor={common/tot:.3f}", flush=True)
    for a,b,t,p in ex: print(f"    {a},{b} -> true {t} / pred {p}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    ea,ca=exact/tot,common/tot
    if ea>=0.6 and ca>=0.85:
        print(f"JEP-30b: PASS - fixed readout: geometric LCA matches true LCA {ea:.2f} and is a valid common ancestor", flush=True)
        print(f"{ca:.2f}. The hyperbolic embedding supports COMPOSITIONAL category queries ('what includes both X and", flush=True)
        print(f"Y') from geometry. A step toward compositional conceptual reasoning. Established methods, named.", flush=True)
    else:
        print(f"JEP-30b: PARTIAL/NULL - exact {ea:.2f}, common-anc {ca:.2f}", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
