"""GEO-56b — re-ranked QA over unstructured prose (does the cross-encoder lift 0.67?)."""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
from run_geo56_unstructured import PARAS, QA


def main():
    print("=== GEO-56b: re-ranked unstructured QA ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2"); ce=CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    sents=[]
    for para in PARAS:
        sents+=[s.strip() for s in re.split(r"(?<=[.!?])\s+", para) if s.strip()]
    S=np.array(m.encode(sents,normalize_embeddings=True))
    base=0; rr=0
    for q,exp in QA:
        qv=m.encode([q],normalize_embeddings=True)[0]; sims=S@qv
        jb=int(np.argmax(sims)); base+= int(exp.lower() in sents[jb].lower())
        topk=np.argsort(-sims)[:5]
        sc=ce.predict([(q,sents[t]) for t in topk]); jr=int(topk[int(np.argmax(sc))])
        rr+= int(exp.lower() in sents[jr].lower())
    n=len(QA)
    print(f"  bi-encoder hits@1  = {base/n:.2f}", flush=True)
    print(f"  + cross-encoder rerank = {rr/n:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if rr/n>=0.8 and rr/n>base/n:
        print(f"GEO-56b: PASS - re-ranking lifts unstructured-prose QA ({base/n:.2f}->{rr/n:.2f}); the system works on real documents with the re-ranker. Same fix as structured scale (GEO-40b).", flush=True)
    else:
        print(f"GEO-56b: PARTIAL - base {base/n:.2f}, reranked {rr/n:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
