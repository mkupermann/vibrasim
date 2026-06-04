"""GEO-24 — does LLM-init give data-efficient structure learning, and only when structure ~ semantics?"""
import numpy as np
from sentence_transformers import SentenceTransformer

WORDS=["mouse","rat","cat","rabbit","dog","fox","goat","sheep","pig","wolf","deer","horse","cow","bear","moose","elephant"]
# Relation A: real-world size order = index order above (ascending). bigger_than(i,j) if size[i]>size[j].
SIZE_A=list(range(len(WORDS)))                      # ascending true size
RNG0=np.random.default_rng(123); SIZE_B=list(RNG0.permutation(len(WORDS)))  # arbitrary order


def learn_order(E0, order, k, seed):
    """Learn a scalar score s.t. score[i]>score[j] iff order[i]>order[j], from k random training pairs."""
    rng=np.random.default_rng(seed); nE=len(order)
    w=rng.normal(0,.1,E0.shape[1])                  # linear projection -> scalar score
    # training pairs (i,j) with known order
    allp=[(i,j) for i in range(nE) for j in range(nE) if order[i]>order[j]]
    rng.shuffle(allp); train=allp[:k]; test=allp[k:k+200]
    lr=0.1
    for _ in range(2000):
        for i,j in train:
            si=E0[i]@w; sj=E0[j]@w
            if si-sj<1.0:                            # margin
                g=E0[i]-E0[j]; w+=lr*g
        w/=np.linalg.norm(w)+1e-9
    acc=np.mean([ (E0[i]@w)>(E0[j]@w) for i,j in test]) if test else 0.0
    return acc


def main():
    print("=== GEO-24: LLM-prior for data-efficient structure learning ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    L=np.array(m.encode(WORDS,normalize_embeddings=True))     # LLM init
    rng=np.random.default_rng(7); R=rng.normal(0,1,L.shape); R/=np.linalg.norm(R,axis=1,keepdims=True)  # random init
    for name,order in [("A semantic-size",SIZE_A),("B arbitrary",SIZE_B)]:
        print(f"  relation {name}:", flush=True)
        for k in [4,8,16,32]:
            la=np.mean([learn_order(L,order,k,s) for s in range(3)])
            ra=np.mean([learn_order(R,order,k,s) for s in range(3)])
            print(f"    k={k:2d}  LLM-init={la:.2f}  random-init={ra:.2f}  delta={la-ra:+.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    print("GEO-24: characterization — compare delta(LLM-random) for semantic A vs arbitrary B (curves above).", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
