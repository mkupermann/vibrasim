"""JEP-76b - decisive systematicity test: knows R1 and R2 => zero-shot knows R1 then R2 (never trained on it)."""
import numpy as np
rng=np.random.default_rng(761)
def norm_rows(X): return X/(np.linalg.norm(X,axis=1,keepdims=True)+1e-9)
def main():
    print("=== JEP-76b: compose two DISTINCT learned relations zero-shot (R1 then R2) ===", flush=True)
    N,Ld,D=70,6,24
    coords=rng.normal(0,1,(N,Ld)); o1=rng.normal(0,1,Ld)*0.6; o2=rng.normal(0,1,Ld)*0.6
    def near(v,h): d=np.linalg.norm(coords-v,axis=1); d[h]=1e9; return int(np.argmin(d))
    r1=np.array([near(coords[h]+o1,h) for h in range(N)])
    r2=np.array([near(coords[h]+o2,h) for h in range(N)])
    # ground-truth composition R1 then R2 (apply r1, then r2 from that node)
    comp=np.array([r2[r1[h]] for h in range(N)])
    triples=[(h,0,int(r1[h])) for h in range(N)]+[(h,1,int(r2[h])) for h in range(N)]  # train r1,r2 ONLY
    E=norm_rows(rng.normal(0,1,(N,D))); R=rng.normal(0,1,(2,D))/np.sqrt(D)
    for ep in range(450):
        E=norm_rows(E); rng.shuffle(triples)
        for h,r,t in triples:
            tn=int(rng.integers(N)); pos=E[h]+R[r]-E[t]; neg=E[h]+R[r]-E[tn]
            dp=np.linalg.norm(pos)+1e-9; dn=np.linalg.norm(neg)+1e-9
            if 1.0+dp-dn>0:
                gp=pos/dp; gn=neg/dn
                E[h]-=0.05*(gp-gn); R[r]-=0.05*(gp-gn); E[t]+=0.05*gp; E[tn]-=0.05*gn
    def hits(relvec,truth,topk=10):
        hh=tot=0
        for h in range(N):
            if truth[h]==h: continue
            sc=np.linalg.norm(E[h]+relvec-E,axis=1); sc[h]=1e9
            hh+=int(int(np.sum(sc<sc[truth[h]]))+1<=topk); tot+=1
        return hh/tot
    h1=hits(R[0],r1); h2=hits(R[1],r2); hc=hits(R[0]+R[1],comp)
    print(f"   chance Hits@10 ~ {10/N:.3f}", flush=True)
    print(f"   R1 (trained)         Hits@10 = {h1:.3f}", flush=True)
    print(f"   R2 (trained)         Hits@10 = {h2:.3f}", flush=True)
    print(f"   R1 then R2 ZERO-SHOT Hits@10 = {hc:.3f}   (relvec = R1+R2, composition NEVER trained)", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if hc>=0.60:
        print(f"JEP-76b: PASS - distinct learned relations COMPOSE zero-shot: trained on R1 and R2 separately, the", flush=True)
        print(f"model predicts the composed relation R1-then-R2 (Hits@10={hc:.3f}) via R1+R2, NEVER trained on it.", flush=True)
        print(f"'Knows R1 and R2 => knows R1.R2' - systematic relational composition (Lake-Baroni) of LEARNED", flush=True)
        print(f"relations. Established (TransE additive composition), named; no novelty. Toy, translational regime.", flush=True)
    else:
        print(f"JEP-76b: NULL - composed Hits@10={hc:.3f} (bar 0.60). Recorded honestly.", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
