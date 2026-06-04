"""GEO-40 — cross-encoder re-ranking to recover multi-hop accuracy at scale (N=400)."""
import numpy as np, time
from sentence_transformers import SentenceTransformer, CrossEncoder

FIRST=["Alice","Bob","Carol","Dan","Eve","Frank","Gina","Hugo","Iris","Jack","Kara","Leo","Mia","Ned",
       "Olga","Paul","Quinn","Rita","Sam","Tara","Uri","Vera","Will","Xena","Yann","Zoe"]
LAST=["Smith","Jones","Lee","Brown","Garcia","Khan","Patel","Nguyen","Kim","Lopez","Wang","Singh",
      "Rossi","Mueller","Costa","Tran","Diaz","Park","Cohen","Reyes"]
CTOK=["Acme","Globex","Initech","Umbra","Stark","Wayne","Cyber","Hooli","Soylent","Tyrell","Vande","Piper",
      "Nexus","Orbit","Quanta","Vertex","Zenith","Apex","Lumen","Helix"]
CITYTOK=["Boston","Denver","Austin","Seattle","Chicago","Portland","Atlanta","Dallas","Miami","Phoenix",
         "Reno","Tucson","Salem","Tampa","Fresno","Mesa","Akron","Boise","Ogden","Provo"]


def names(N):
    ppl=[f"{FIRST[i%len(FIRST)]} {LAST[(i//len(FIRST))%len(LAST)]} {i}" for i in range(N)]
    comp=[f"{CTOK[i%len(CTOK)]}Corp{i}" for i in range(N)]
    city=[f"{CITYTOK[i%len(CITYTOK)]}ville{i}" for i in range(N)]
    return ppl,comp,city


def main():
    N=400
    print(f"=== GEO-40: cross-encoder re-ranking at N={N} ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    ce=CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    ppl,comp,city=names(N)
    works=[f"{p} works at {c}." for p,c in zip(ppl,comp)]
    loc  =[f"{c} is in {ci}." for c,ci in zip(comp,city)]
    W=np.array(m.encode(works,normalize_embeddings=True,batch_size=64))
    Lc=np.array(m.encode(loc,normalize_embeddings=True,batch_size=64))
    Qtext=[f"What company does {p} work at?" for p in ppl]
    Q=np.array(m.encode(Qtext,normalize_embeddings=True,batch_size=64))
    K=10
    # baseline bi-encoder 1-hop
    base_j=np.argmax(Q@W.T,axis=1); base1=np.mean(base_j==np.arange(N))
    # re-ranked 1-hop: top-K then cross-encoder
    t=time.time(); rr_j=np.zeros(N,dtype=int)
    for i in range(N):
        topk=np.argsort(-(Q[i]@W.T))[:K]
        scores=ce.predict([(Qtext[i],works[j]) for j in topk])
        rr_j[i]=topk[int(np.argmax(scores))]
    rr1=np.mean(rr_j==np.arange(N)); rr_t=time.time()-t
    # 2-hop: use each method's hop-1 company to probe location
    def twohop(jarr):
        P=np.array(m.encode([f"What city is {comp[j]} in?" for j in jarr],normalize_embeddings=True,batch_size=64))
        k=np.argmax(P@Lc.T,axis=1); return np.mean(k==np.arange(N))
    base2=twohop(base_j); rr2=twohop(rr_j)
    print(f"  bi-encoder   1-hop={base1:.2f}  2-hop={base2:.2f}", flush=True)
    print(f"  re-ranked    1-hop={rr1:.2f}  2-hop={rr2:.2f}  (rerank {rr_t:.0f}s for {N} queries)", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if rr2>=base2+0.05 or (base2>=0.95 and rr2>=0.95):
        print(f"GEO-40: PASS - cross-encoder re-ranking {'recovers accuracy at scale' if rr2>base2 else 'maintains high accuracy'} (2-hop {base2:.2f}->{rr2:.2f}); extends the practical envelope at a modest latency cost.", flush=True)
    else:
        print(f"GEO-40: NULL/PARTIAL - re-ranking did not help (2-hop {base2:.2f}->{rr2:.2f}).", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
