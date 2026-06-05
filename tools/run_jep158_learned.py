"""JEP-158 - multi-hop inference over LEARNED embeddings: does it compound? is nearest-entity (Hopfield) cleanup the cure?"""
import numpy as np
def main():
    print("=== JEP-158: multi-hop inference over learned embeddings (TransE-style) ===", flush=True)
    print("    deliberately IMPERFECT embeddings (per JEP-157 lesson: match regime to mechanism)", flush=True)
    D=64; N=40  # entities along a chain e0 -r-> e1 -r-> e2 ... (single relation = 'parent')
    for emb_noise in [0.0, 0.15, 0.30]:
        accs_no=[]; accs_cl=[]
        for seed in range(200):
            r=np.random.default_rng(seed)
            # ideal TransE: e_{i+1} = e_i + t. Build clean entity vecs on a lattice + translation t.
            t=r.standard_normal(D); t/=np.linalg.norm(t)
            base=r.standard_normal(D)
            ent=np.array([base + i*t for i in range(N)])  # exact translation chain
            # IMPERFECT learned embeddings: add per-entity learning noise
            ent_learned = ent + emb_noise*r.standard_normal((N,D))
            t_learned = t + emb_noise*r.standard_normal(D)*0.5
            # multi-hop query: from e0, apply translation k times, identify target entity e_k
            for depth in [1,2,4,8]:
                if depth>=N: continue
                # WITHOUT cleanup: e0 + depth*t_learned, nearest entity
                v=ent_learned[0]+depth*t_learned
                pred_no=int(np.argmin(np.linalg.norm(ent_learned-v,axis=1)))
                # WITH per-hop cleanup: after each +t, snap to nearest entity (attractor/Hopfield)
                v=ent_learned[0].copy()
                for _ in range(depth):
                    v=v+t_learned
                    v=ent_learned[int(np.argmin(np.linalg.norm(ent_learned-v,axis=1)))]
                pred_cl=int(np.argmin(np.linalg.norm(ent_learned-v,axis=1)))
                accs_no.append((depth,pred_no==depth)); accs_cl.append((depth,pred_cl==depth))
        def bydepth(rows):
            d={}
            for dep,ok in rows: d.setdefault(dep,[]).append(ok)
            return {k:np.mean(v) for k,v in d.items()}
        no=bydepth(accs_no); cl=bydepth(accs_cl)
        print(f"\n  emb_noise={emb_noise:.2f}", flush=True)
        print(f"    NO cleanup : "+" ".join(f"d{k}:{no[k]:.2f}" for k in sorted(no)), flush=True)
        print(f"    cleanup    : "+" ".join(f"d{k}:{cl[k]:.2f}" for k in sorted(cl)), flush=True)
    print("\n--- FINDING ---", flush=True)
    print("If NO-cleanup accuracy falls with depth while per-hop cleanup holds, the LEARNED/continuous path COMPOUNDS", flush=True)
    print("errors like symbolic chains (universal insight) and nearest-entity attractor cleanup (the substrate Hopfield,", flush=True)
    print("JEP-4) is the native AGGREGATION cure - re-anchoring each hop. Ties four pillars + universal insight + substrate.", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
