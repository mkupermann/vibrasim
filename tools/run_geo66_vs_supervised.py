"""GEO-66 — geometric relation learning vs plain supervised (logistic) baseline on embeddings."""
import numpy as np
from sentence_transformers import SentenceTransformer

WORDS=["ant","bee","mouse","sparrow","rat","squirrel","cat","rabbit","fox","dog","goat","sheep","pig",
       "wolf","deer","donkey","horse","cow","bison","bear","moose","rhino","hippo","elephant"]
SIZE=list(range(len(WORDS)))


def logistic_pairwise(X, pairs_idx, labels, epochs=300, lr=0.1):
    """Train w on (emb_i - emb_j) -> sign(size_i - size_j). Plain logistic regression."""
    rng=np.random.default_rng(0); w=rng.normal(0,.01,X.shape[1])
    Xp=np.array([X[i]-X[j] for i,j in pairs_idx]); y=np.array(labels)
    for _ in range(epochs):
        p=1/(1+np.exp(-(Xp@w))); g=Xp.T@(p-y)/len(y); w-=lr*g
    return w


def geo_rank(X, pairs_idx, seed):
    rng=np.random.default_rng(seed); w=rng.normal(0,.1,X.shape[1]); lr=0.1
    for _ in range(2000):
        for i,j in pairs_idx:  # size_i > size_j assumed (caller orders)
            if X[i]@w - X[j]@w < 1.0: w+=lr*(X[i]-X[j])
        w/=np.linalg.norm(w)+1e-9
    return w


def main():
    print("=== GEO-66: geometric vs supervised baseline ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2"); X=np.array(m.encode(WORDS,normalize_embeddings=True)); nE=len(WORDS)
    # (a) few-shot
    print("  (a) few-shot ordinal:", flush=True)
    for k in [4,8]:
        ga=[];la=[]
        for s in range(5):
            rng=np.random.default_rng(s)
            allp=[(i,j) for i in range(nE) for j in range(nE) if SIZE[i]>SIZE[j]]
            rng.shuffle(allp); tr=allp[:k]; te=allp[k:k+200]
            wg=geo_rank(X,tr,s); ga.append(np.mean([(X[i]@wg)>(X[j]@wg) for i,j in te]))
            wl=logistic_pairwise(X,tr,[1]*len(tr)); la.append(np.mean([(X[i]@wl)>(X[j]@wl) for i,j in te]))
        print(f"    k={k}  geometric={np.mean(ga):.2f}  supervised-logistic={np.mean(la):.2f}", flush=True)
    # (b) zero-shot transfer (unseen-vs-unseen)
    print("  (b) zero-shot transfer (unseen-vs-unseen):", flush=True)
    gz=[];lz=[]
    for s in range(5):
        rng=np.random.default_rng(100+s); unseen=set(rng.choice(nE,8,replace=False).tolist())
        seen=[i for i in range(nE) if i not in unseen]
        trp=[(i,j) for i in seen for j in seen if SIZE[i]>SIZE[j]]
        wg=geo_rank(X,trp,s); wl=logistic_pairwise(X,trp,[1]*len(trp))
        tp=[(i,j) for i in unseen for j in unseen if SIZE[i]>SIZE[j]]
        gz.append(np.mean([(X[i]@wg)>(X[j]@wg) for i,j in tp])); lz.append(np.mean([(X[i]@wl)>(X[j]@wl) for i,j in tp]))
    g=np.mean(gz); l=np.mean(lz)
    print(f"    geometric={g:.2f}  supervised-logistic={l:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    print(f"GEO-66: HONEST COMPARISON — zero-shot geometric {g:.2f} vs logistic {l:.2f}. {'Geometric framing is NOT necessary (plain supervised matches it) - honest deflation: the value is the EMBEDDINGS + a linear readout, geometric or logistic.' if abs(g-l)<0.05 else ('Geometric edge.' if g>l else 'Supervised edge.')}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
