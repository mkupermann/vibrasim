"""JEP-75 - LEARN relation embeddings from triples via TransE (Bordes 2013); link-predict held-out facts."""
import numpy as np
rng=np.random.default_rng(75)
def norm_rows(X): return X/(np.linalg.norm(X,axis=1,keepdims=True)+1e-9)
def main():
    print("=== JEP-75: LEARN relations from data (TransE) vs hand-specifying them ===", flush=True)
    N,Ld,RELS=60,5,4
    coords=rng.normal(0,1,(N,Ld)); offs=rng.normal(0,1,(RELS,Ld))*0.9
    # build triples: tail = nearest OTHER entity to coords[h]+offs[r]
    triples=[]
    for h in range(N):
        for r in range(RELS):
            tgt=coords[h]+offs[r]; d=np.linalg.norm(coords-tgt,axis=1); d[h]=1e9
            triples.append((h,r,int(np.argmin(d))))
    triples=np.array(triples)
    # true-tail filter set per (h,r)
    known={}
    for h,r,t in triples: known.setdefault((h,r),set()).add(t)
    idx=rng.permutation(len(triples)); nt=len(triples)//5
    test=triples[idx[:nt]]; train=triples[idx[nt:]]
    D=20
    E=norm_rows(rng.normal(0,1,(N,D))); R=rng.normal(0,1,(RELS,D))/np.sqrt(D)
    def evaluate(E,R):
        h10=mrr=0
        for h,r,t in test:
            sc=np.linalg.norm(E[h]+R[r]-E,axis=1)  # lower=better
            for tt in known[(h,r)]:
                if tt!=t: sc[tt]=1e9  # filtered ranking
            rank=int(np.sum(sc<sc[t]))+1
            h10+=int(rank<=10); mrr+=1.0/rank
        return h10/len(test), mrr/len(test)
    ch10,cmrr=evaluate(E,R); print(f"   control (random init): Hits@10={ch10:.3f}  MRR={cmrr:.3f}  (chance~{10/N:.3f})", flush=True)
    margin,lr=1.0,0.05
    for ep in range(300):
        E=norm_rows(E); rng.shuffle(train)
        for h,r,t in train:
            tn=int(rng.integers(N))
            pos=E[h]+R[r]-E[t]; neg=E[h]+R[r]-E[tn]
            dp=np.linalg.norm(pos)+1e-9; dn=np.linalg.norm(neg)+1e-9
            if margin+dp-dn>0:
                gp=pos/dp; gn=neg/dn
                E[h]-=lr*(gp-gn); R[r]-=lr*(gp-gn); E[t]+=lr*gp; E[tn]-=lr*gn
        if ep in (49,149,299):
            h10,mrr=evaluate(E,R); print(f"   epoch {ep+1:>3}: held-out Hits@10={h10:.3f}  MRR={mrr:.3f}", flush=True)
    h10,mrr=evaluate(E,R)
    # per-relation
    print("   per-relation held-out Hits@10:", flush=True)
    for r in range(RELS):
        msk=test[:,1]==r
        if msk.sum()==0: continue
        hh=0
        for h,_,t in test[msk]:
            sc=np.linalg.norm(E[h]+R[r]-E,axis=1)
            for tt in known[(h,r)]:
                if tt!=t: sc[tt]=1e9
            hh+=int(int(np.sum(sc<sc[t]))+1<=10)
        print(f"      R{r}: {hh/msk.sum():.3f} (n={int(msk.sum())})", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if h10>=0.80 and mrr>=0.50:
        print(f"JEP-75: PASS - relations LEARNED from triples (TransE) generalize to UNSEEN facts: held-out", flush=True)
        print(f"Hits@10={h10:.3f} (>=0.80), MRR={mrr:.3f} (>=0.50), vs random control {ch10:.3f}. The relational", flush=True)
        print(f"structure the system composes over need NOT be hand-specified - it can be LEARNED from relational", flush=True)
        print(f"data and predict new facts. Closes gap #5 in the toy regime. Established (TransE, Bordes 2013), named.", flush=True)
    else:
        print(f"JEP-75: NULL/PARTIAL - held-out Hits@10={h10:.3f}, MRR={mrr:.3f} (bar 0.80/0.50). Finding recorded.", flush=True)
    print("HONEST BOUND: this is the learnable regime (relations w/ consistent offset). TransE's known weakness is", flush=True)
    print("symmetric / 1-to-N / N-to-N relations; toy scale; supervised triples still required. No novelty.", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
