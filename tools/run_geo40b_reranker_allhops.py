"""GEO-40b — re-rank BOTH hops to recover 2-hop accuracy at scale (completes GEO-40)."""
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
from run_geo40_reranker import names


def main():
    N=400; K=10
    print(f"=== GEO-40b: re-rank BOTH hops at N={N} ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2"); ce=CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    ppl,comp,city=names(N)
    works=[f"{p} works at {c}." for p,c in zip(ppl,comp)]
    loc  =[f"{c} is in {ci}." for c,ci in zip(comp,city)]
    W=np.array(m.encode(works,normalize_embeddings=True,batch_size=64))
    Lc=np.array(m.encode(loc,normalize_embeddings=True,batch_size=64))
    def rerank(qtext, pool_emb, pool_text, qv):
        topk=np.argsort(-(qv@pool_emb.T))[:K]
        sc=ce.predict([(qtext,pool_text[j]) for j in topk]); return topk[int(np.argmax(sc))]
    Q1=[f"What company does {p} work at?" for p in ppl]
    Q1e=np.array(m.encode(Q1,normalize_embeddings=True,batch_size=64))
    base_j=np.argmax(Q1e@W.T,axis=1)
    # both hops re-ranked
    h1=np.array([rerank(Q1[i],W,works,Q1e[i]) for i in range(N)])
    Q2=[f"What city is {comp[h1[i]]} in?" for i in range(N)]
    Q2e=np.array(m.encode(Q2,normalize_embeddings=True,batch_size=64))
    h2=np.array([rerank(Q2[i],Lc,loc,Q2e[i]) for i in range(N)])
    # baseline 2-hop (no rerank, both hops bi-encoder)
    base_city=np.argmax(np.array(m.encode([f"What city is {comp[j]} in?" for j in base_j],normalize_embeddings=True,batch_size=64))@Lc.T,axis=1)
    base2=np.mean(base_city==np.arange(N)); rr2=np.mean(h2==np.arange(N))
    print(f"  bi-encoder 2-hop          = {base2:.2f}", flush=True)
    print(f"  re-ranked BOTH hops 2-hop = {rr2:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if rr2>=base2+0.05:
        print(f"GEO-40b: PASS - re-ranking EVERY hop recovers multi-hop accuracy at scale (2-hop {base2:.2f}->{rr2:.2f}). The scale limit is mitigable: bi-encoder retrieve top-k + cross-encoder re-rank per hop. Practical envelope extended.", flush=True)
    else:
        print(f"GEO-40b: NULL - even all-hop re-ranking didn't recover 2-hop ({base2:.2f}->{rr2:.2f}).", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
