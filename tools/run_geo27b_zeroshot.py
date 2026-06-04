"""GEO-27b — cleaner zero-shot transfer: larger entity set, unseen-vs-unseen as PRIMARY metric."""
import numpy as np
from sentence_transformers import SentenceTransformer

# 24 entities with a real-world size order (ascending)
WORDS=["ant","bee","mouse","sparrow","rat","squirrel","cat","rabbit","fox","dog","goat","sheep","pig",
       "wolf","deer","donkey","horse","cow","bison","bear","moose","rhino","hippo","elephant"]
SIZE=list(range(len(WORDS)))


def learn(E0, seen, seed):
    rng=np.random.default_rng(seed); w=rng.normal(0,.1,E0.shape[1])
    pairs=[(i,j) for i in seen for j in seen if SIZE[i]>SIZE[j]]
    rng.shuffle(pairs); lr=0.1
    for _ in range(2500):
        for i,j in pairs:
            if E0[i]@w - E0[j]@w < 1.0: w+=lr*(E0[i]-E0[j])
        w/=np.linalg.norm(w)+1e-9
    return w


def main():
    print("=== GEO-27b: clean zero-shot transfer (unseen-vs-unseen primary) ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    L=np.array(m.encode(WORDS,normalize_embeddings=True))
    rng0=np.random.default_rng(7); R=rng0.normal(0,1,L.shape); R/=np.linalg.norm(R,axis=1,keepdims=True)
    n=len(WORDS)
    def run(E0):
        accs=[]
        for s in range(5):
            rng=np.random.default_rng(100+s)
            unseen=set(rng.choice(n,8,replace=False).tolist())   # 8 unseen of 24
            seen=[i for i in range(n) if i not in unseen]
            w=learn(E0,seen,s)
            tp=[(i,j) for i in unseen for j in unseen if SIZE[i]>SIZE[j]]
            accs.append(np.mean([(E0[i]@w)>(E0[j]@w) for i,j in tp]))
        return np.mean(accs),np.std(accs)
    lm,ls=run(L); rm,rs=run(R)
    print(f"  LLM-init    unseen-vs-unseen = {lm:.2f} +/- {ls:.2f}", flush=True)
    print(f"  random-init unseen-vs-unseen = {rm:.2f} +/- {rs:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if lm>=0.75 and lm>=rm+0.20:
        print(f"GEO-27b: PASS - LLM prior enables genuine ZERO-SHOT transfer to fully-unseen entities ({lm:.2f}) vs random near-chance ({rm:.2f}). Geometry's irreducible edge confirmed: the semantic prior places new entities so a learned relation orders them with zero examples.", flush=True)
    else:
        print(f"GEO-27b: NULL/PARTIAL - LLM {lm:.2f}, random {rm:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
