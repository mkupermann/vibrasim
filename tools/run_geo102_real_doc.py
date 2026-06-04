"""GEO-102 — self-supervised adaptation on a real technical Wikipedia article."""
import warnings; warnings.filterwarnings("ignore")
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from document_learner import DocumentLearner

QA=[("How many membranes does a mitochondrion have?","two membranes"),
    ("What is the powerhouse of the cell?","powerhouse"),
    ("What molecule do mitochondria produce?","ATP"),
    ("What are the folds of the inner membrane called?","cristae"),
    ("What is the space inside the inner membrane called?","matrix"),
    ("Do mitochondria have their own DNA?","mitochondrial DNA"),
    ("What process makes ATP in mitochondria?","oxidative phosphorylation"),
    ("Where are mitochondria thought to originate from?","bacteria"),
    ("What is the inner membrane folded into?","cristae"),
    ("What inherits mitochondrial DNA?","maternally"),
    ("What is the citric acid cycle also called?","Krebs"),
    ("What gas is consumed in cellular respiration?","oxygen")]


def measure(dl):
    F=np.array(dl.r.model.encode(dl.chunks,normalize_embeddings=True))
    Q=np.array(dl.r.model.encode([q for q,_ in QA],normalize_embeddings=True))
    return np.mean([int(ans.lower() in dl.chunks[int(np.argmax(Q[i]@F.T))].lower()) for i,(q,ans) in enumerate(QA)])


def main():
    print("=== GEO-102: real technical document adaptation ===", flush=True)
    dl=DocumentLearner(rerank_k=0)
    try:
        n=dl.learn("https://en.wikipedia.org/wiki/Mitochondrion", source_name="mito")
    except Exception as e:
        print(f"  fetch failed ({e}); ABORT", flush=True); print("DONE",flush=True); return
    print(f"  ingested {n} chunks from the article", flush=True)
    before=measure(dl)
    print(f"  retrieval hits@1 BEFORE adaptation = {before:.2f}", flush=True)
    dl.adapt(epochs=3, batch_size=16)
    after=measure(dl)
    print(f"  retrieval hits@1 AFTER self-supervised adaptation = {after:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if after-before>=0.05:
        print(f"GEO-102: PASS - self-supervised adaptation helps on a REAL technical document ({before:.2f}->{after:.2f}). Confirms: give it a real article/book -> ingest + SimCSE-adapt improves retrieval on the content.", flush=True)
    elif after>=before-0.03:
        print(f"GEO-102: PARTIAL - ingestion makes the real article queryable ({before:.2f}); adaptation neutral ({after:.2f}) — pretrained model already handles this domain. Ingestion is the deliverable.", flush=True)
    else:
        print(f"GEO-102: adaptation hurt ({before:.2f}->{after:.2f}) — risk of overfitting; use ingestion alone or fewer epochs.", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
