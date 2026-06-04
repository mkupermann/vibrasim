"""GEO-71 — compositional/word-order accuracy vs model size (MiniLM vs mpnet)."""
import numpy as np
from sentence_transformers import SentenceTransformer
from run_geo70b_clean_order import ITEMS


def acc(model):
    m=SentenceTransformer(model); ok=0
    for fa,fb,q,correct in ITEMS:
        e=m.encode([fa,fb,q],normalize_embeddings=True)
        pick=0 if e[2]@e[0]>=e[2]@e[1] else 1; ok+= int(pick==correct)
    return ok/len(ITEMS)


def main():
    print("=== GEO-71: compositional understanding vs model size ===", flush=True)
    for name,size in [("all-MiniLM-L6-v2","22M"),("all-mpnet-base-v2","110M")]:
        a=acc(name); print(f"  {name:24s} ({size:5s}) word-order 2-way acc = {a:.2f}", flush=True)
    print("  (static order-blind baseline: 0.38, chance 0.50)", flush=True)
    print("\n--- VERDICT ---", flush=True)
    mini=acc("all-MiniLM-L6-v2"); mp=acc("all-mpnet-base-v2")
    if mp>=mini+0.1:
        print(f"GEO-71: compositional encoding SCALES with model size (MiniLM {mini:.2f} -> mpnet {mp:.2f}). Bigger models handle word order/roles better; use mpnet for compositional/role-sensitive tasks.", flush=True)
    elif mp>=0.7 and mini>=0.7:
        print(f"GEO-71: both handle word order ({mini:.2f}/{mp:.2f}); compositional encoding present even in the small model.", flush=True)
    else:
        print(f"GEO-71: MiniLM {mini:.2f}, mpnet {mp:.2f} — see cells.", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
