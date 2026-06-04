"""GEO-27 — zero-shot transfer of a learned relation to UNSEEN entities: LLM-prior vs random-init."""
import numpy as np
from sentence_transformers import SentenceTransformer

WORDS=["mouse","rat","cat","rabbit","dog","fox","goat","sheep","pig","wolf","deer","horse","cow","bear","moose","elephant"]
SIZE=list(range(len(WORDS)))           # ascending true size = index
UNSEEN=[2,5,8,11,14]                    # cat, fox, pig, horse, moose held out of all training pairs
SEEN=[i for i in range(len(WORDS)) if i not in UNSEEN]


def learn(E0, seed):
    rng=np.random.default_rng(seed)
    w=rng.normal(0,.1,E0.shape[1])
    pairs=[(i,j) for i in SEEN for j in SEEN if SIZE[i]>SIZE[j]]   # train only among SEEN
    rng.shuffle(pairs); lr=0.1
    for _ in range(3000):
        for i,j in pairs:
            if E0[i]@w - E0[j]@w < 1.0:
                w+=lr*(E0[i]-E0[j])
        w/=np.linalg.norm(w)+1e-9
    return w


def evalacc(E0,w,pred):
    tp=[(i,j) for i in range(len(WORDS)) for j in range(len(WORDS)) if SIZE[i]>SIZE[j] and pred(i,j)]
    return np.mean([ (E0[i]@w)>(E0[j]@w) for i,j in tp]) if tp else 0.0


def main():
    print("=== GEO-27: zero-shot transfer to UNSEEN entities ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    L=np.array(m.encode(WORDS,normalize_embeddings=True))
    rng=np.random.default_rng(7); R=rng.normal(0,1,L.shape); R/=np.linalg.norm(R,axis=1,keepdims=True)
    US=set(UNSEEN)
    atleast1=lambda i,j: (i in US) or (j in US)
    bothunseen=lambda i,j: (i in US) and (j in US)
    bothseen=lambda i,j: (i not in US) and (j not in US)
    for name,E0 in [("LLM-init",L),("random-init",R)]:
        a1=[]; bu=[]; bs=[]
        for s in range(3):
            w=learn(E0,s)
            a1.append(evalacc(E0,w,atleast1)); bu.append(evalacc(E0,w,bothunseen)); bs.append(evalacc(E0,w,bothseen))
        print(f"  {name:11s}  seen-vs-seen={np.mean(bs):.2f}  >=1-unseen(zero-shot)={np.mean(a1):.2f}  unseen-vs-unseen={np.mean(bu):.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    # recompute LLM and random zero-shot for the bar
    lz=np.mean([evalacc(L,learn(L,s),atleast1) for s in range(3)])
    rz=np.mean([evalacc(R,learn(R,s),atleast1) for s in range(3)])
    if lz>=0.70 and lz>=rz+0.20:
        print(f"GEO-27: PASS - LLM prior enables ZERO-SHOT transfer to unseen entities ({lz:.2f}) where random-init cannot ({rz:.2f}). Geometry's irreducible edge: the semantic prior positions new entities so a learned relation transfers with zero examples of them.", flush=True)
    else:
        print(f"GEO-27: NULL/PARTIAL - LLM zero-shot {lz:.2f}, random {rz:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
