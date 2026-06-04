"""GEO-28 — compositional zero-shot: learn size + predator on seen animals, compose on unseen."""
import numpy as np
from sentence_transformers import SentenceTransformer

# (animal, size_rank, predator)
DATA=[("mouse",0,0),("rabbit",2,0),("squirrel",1,0),("cat",4,1),("fox",5,1),("dog",6,0),("goat",7,0),
      ("sheep",8,0),("wolf",9,1),("lynx",3,1),("deer",10,0),("leopard",11,1),("horse",13,0),("cow",14,0),
      ("lion",12,1),("tiger",15,1),("bear",16,1),("bison",17,0),("rhino",18,0),("elephant",19,0)]
WORDS=[d[0] for d in DATA]; SIZE=[d[1] for d in DATA]; PRED=[d[2] for d in DATA]


def proj(E0, idx, target, seed, binary=False):
    """Learn a linear score; for size use ranking, for predator use mean-difference direction."""
    rng=np.random.default_rng(seed)
    if binary:
        pos=[i for i in idx if target[i]==1]; neg=[i for i in idx if target[i]==0]
        if not pos or not neg: return rng.normal(0,1,E0.shape[1])
        w=E0[pos].mean(0)-E0[neg].mean(0); return w/(np.linalg.norm(w)+1e-9)
    w=rng.normal(0,.1,E0.shape[1])
    pairs=[(i,j) for i in idx for j in idx if target[i]>target[j]]; rng.shuffle(pairs); lr=0.1
    for _ in range(2000):
        for i,j in pairs:
            if E0[i]@w-E0[j]@w<1.0: w+=lr*(E0[i]-E0[j])
        w/=np.linalg.norm(w)+1e-9
    return w


def bal_acc(y,p):
    y=np.array(y);p=np.array(p)
    tpr=np.mean(p[y==1]) if (y==1).any() else 0; tnr=np.mean(1-p[y==0]) if (y==0).any() else 0
    return (tpr+tnr)/2


def main():
    print("=== GEO-28: compositional zero-shot (size AND predator) ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    L=np.array(m.encode(WORDS,normalize_embeddings=True))
    rng0=np.random.default_rng(7); R=rng0.normal(0,1,L.shape); R/=np.linalg.norm(R,axis=1,keepdims=True)
    n=len(WORDS); size_med=np.median(SIZE)
    truth=[1 if (SIZE[i]>size_med and PRED[i]==1) else 0 for i in range(n)]
    def run(E0):
        comp=[];sz=[];pr=[]
        for s in range(5):
            rng=np.random.default_rng(200+s)
            unseen=sorted(rng.choice(n,8,replace=False).tolist()); seen=[i for i in range(n) if i not in unseen]
            ws=proj(E0,seen,SIZE,s); wp=proj(E0,seen,PRED,s,binary=True)
            # thresholds from SEEN
            st=np.median([E0[i]@ws for i in seen])
            pred_comp=[1 if ((E0[i]@ws>st) and (E0[i]@wp>0)) else 0 for i in unseen]
            comp.append(bal_acc([truth[i] for i in unseen],pred_comp))
            sz.append(np.mean([ (E0[i]@ws>st)==(SIZE[i]>size_med) for i in unseen]))
            pr.append(np.mean([ (E0[i]@wp>0)==(PRED[i]==1) for i in unseen]))
        return np.mean(comp),np.mean(sz),np.mean(pr)
    lc,ls,lp=run(L); rc,rs,rp=run(R)
    print(f"  LLM-init    composite-bal-acc={lc:.2f}  (size {ls:.2f}, predator {lp:.2f}) on unseen", flush=True)
    print(f"  random-init composite-bal-acc={rc:.2f}  (size {rs:.2f}, predator {rp:.2f})", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if lc>=0.70 and lc>=rc+0.20:
        print(f"GEO-28: PASS - compositional ZERO-SHOT understanding: two attributes learned on seen animals compose correctly on UNSEEN animals ({lc:.2f}) via geometry, where random-init cannot ({rc:.2f}).", flush=True)
    else:
        print(f"GEO-28: NULL/PARTIAL - LLM {lc:.2f} vs random {rc:.2f} (size {ls:.2f}/pred {lp:.2f})", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
