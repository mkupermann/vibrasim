"""GEO-72 — cross-encoder on word-order pairs (does joint encoding fix role-sensitivity?)."""
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
from run_geo70b_clean_order import ITEMS


def main():
    print("=== GEO-72: cross-encoder on word-order pairs ===", flush=True)
    bi=SentenceTransformer("all-MiniLM-L6-v2")
    ce=CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    bi_ok=0; ce_ok=0
    for fa,fb,q,correct in ITEMS:
        e=bi.encode([fa,fb,q],normalize_embeddings=True)
        bpick=0 if e[2]@e[0]>=e[2]@e[1] else 1; bi_ok+= int(bpick==correct)
        sc=ce.predict([(q,fa),(q,fb)]); cpick=0 if sc[0]>=sc[1] else 1; ce_ok+= int(cpick==correct)
    n=len(ITEMS)
    print(f"  bi-encoder   word-order acc = {bi_ok/n:.2f}", flush=True)
    print(f"  cross-encoder word-order acc = {ce_ok/n:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if ce_ok/n>=0.85 and ce_ok/n>bi_ok/n:
        print(f"GEO-72: PASS - the cross-encoder FIXES word-order/role matching ({bi_ok/n:.2f}->{ce_ok/n:.2f}): joint query+fact encoding sees word order, where the pooled bi-encoder cannot. Validates the design rule: cross-encoder for role-sensitive matching.", flush=True)
    else:
        print(f"GEO-72: bi {bi_ok/n:.2f}, cross {ce_ok/n:.2f} - cross-encoder {'helps' if ce_ok/n>bi_ok/n else 'does not help'}.", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
