"""GEO-29 — compositional zero-shot recovery: more entities + balanced conjunction (aquatic clean split)."""
import numpy as np
from sentence_transformers import SentenceTransformer

# 40 animals: (name, size_rank, aquatic) — aquatic is a clean semantic split MiniLM encodes well
RAW=[("minnow",1,1),("shrimp",0,1),("sardine",2,1),("crab",3,1),("trout",5,1),("herring",4,1),
     ("octopus",9,1),("salmon",7,1),("eel",6,1),("squid",8,1),("tuna",12,1),("seal",16,1),
     ("dolphin",18,1),("shark",20,1),("swordfish",15,1),("manta",19,1),("walrus",22,1),("orca",26,1),
     ("whale",30,1),("narwhal",24,1),
     ("mouse",1,0),("rabbit",4,0),("cat",6,0),("fox",8,0),("dog",10,0),("goat",11,0),("wolf",13,0),
     ("deer",17,0),("leopard",14,0),("horse",21,0),("cow",23,0),("lion",19,0),("tiger",22,0),
     ("bear",25,0),("bison",27,0),("rhino",28,0),("giraffe",29,0),("hippo",31,0),("elephant",33,0),("moose",20,0)]
WORDS=[r[0] for r in RAW]; SIZE=[r[1] for r in RAW]; AQUA=[r[2] for r in RAW]


def proj(E0,idx,target,seed,binary=False):
    rng=np.random.default_rng(seed)
    if binary:
        pos=[i for i in idx if target[i]==1]; neg=[i for i in idx if target[i]==0]
        if not pos or not neg: return rng.normal(0,1,E0.shape[1])
        w=E0[pos].mean(0)-E0[neg].mean(0); return w/(np.linalg.norm(w)+1e-9)
    w=rng.normal(0,.1,E0.shape[1]); pairs=[(i,j) for i in idx for j in idx if target[i]>target[j]]
    rng.shuffle(pairs); lr=0.1
    for _ in range(1500):
        for i,j in pairs:
            if E0[i]@w-E0[j]@w<1.0: w+=lr*(E0[i]-E0[j])
        w/=np.linalg.norm(w)+1e-9
    return w


def bal_acc(y,p):
    y=np.array(y);p=np.array(p)
    tpr=np.mean(p[y==1]) if (y==1).any() else 0; tnr=np.mean(1-p[y==0]) if (y==0).any() else 0
    return (tpr+tnr)/2


def main():
    print("=== GEO-29: compositional recovery (large AND aquatic, 40 items) ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    L=np.array(m.encode(WORDS,normalize_embeddings=True))
    rng0=np.random.default_rng(7); R=rng0.normal(0,1,L.shape); R/=np.linalg.norm(R,axis=1,keepdims=True)
    n=len(WORDS); smed=np.median(SIZE)
    truth=[1 if (SIZE[i]>smed and AQUA[i]==1) else 0 for i in range(n)]
    print(f"  positive rate (large AND aquatic) = {np.mean(truth):.2f}", flush=True)
    def run(E0):
        comp=[];sz=[];aq=[]
        for s in range(5):
            rng=np.random.default_rng(300+s)
            unseen=sorted(rng.choice(n,16,replace=False).tolist()); seen=[i for i in range(n) if i not in unseen]
            ws=proj(E0,seen,SIZE,s); wa=proj(E0,seen,AQUA,s,binary=True)
            st=np.median([E0[i]@ws for i in seen]); at=np.median([E0[i]@wa for i in seen])
            pc=[1 if ((E0[i]@ws>st) and (E0[i]@wa>at)) else 0 for i in unseen]
            comp.append(bal_acc([truth[i] for i in unseen],pc))
            sz.append(np.mean([(E0[i]@ws>st)==(SIZE[i]>smed) for i in unseen]))
            aq.append(np.mean([(E0[i]@wa>at)==(AQUA[i]==1) for i in unseen]))
        return np.mean(comp),np.mean(sz),np.mean(aq)
    lc,ls,la=run(L); rc,rs,ra=run(R)
    print(f"  LLM-init    composite={lc:.2f}  (size {ls:.2f}, aquatic {la:.2f})", flush=True)
    print(f"  random-init composite={rc:.2f}  (size {rs:.2f}, aquatic {ra:.2f})", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if lc>=0.70 and lc>=rc+0.20:
        print(f"GEO-29: PASS - compositional zero-shot RECOVERS with more entities + a clean balanced attribute ({lc:.2f} vs random {rc:.2f}). The GEO-28 collapse was practical (noise/imbalance), not fundamental: geometry DOES compose zero-shot attributes when each is cleanly encoded.", flush=True)
    elif lc<0.65:
        print(f"GEO-29: NULL - composition stays near chance ({lc:.2f}); the compositional zero-shot limit is more fundamental.", flush=True)
    else:
        print(f"GEO-29: PARTIAL - {lc:.2f} vs random {rc:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
