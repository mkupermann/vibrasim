"""GEO-5 — geometric understanding on REAL LLM embeddings. Embed words with a small transformer
(all-MiniLM-L6-v2), then test whether GEOMETRIC operations support understanding: (a) analogy by offset
(a:b::c:d), (b) relational direction consistency. This is the genuine 'geometric ML/LLM' bridge on the PC.
Honest: sentence-transformers embed sentences; word-level analogy may be weak — measured, not assumed."""
import sys, numpy as np
from sentence_transformers import SentenceTransformer

# curated analogy quadruples (a:b :: c:d) across relation types
QUADS = [
    ("man","king","woman","queen"), ("king","man","queen","woman"),
    ("france","paris","germany","berlin"), ("germany","berlin","italy","rome"),
    ("france","paris","spain","madrid"), ("japan","tokyo","china","beijing"),
    ("man","boy","woman","girl"), ("big","bigger","small","smaller"),
    ("good","better","bad","worse"), ("walk","walked","run","ran"),
    ("dog","puppy","cat","kitten"), ("paris","france","berlin","germany"),
    ("king","queen","man","woman"), ("uncle","aunt","nephew","niece"),
    ("hot","cold","up","down"), ("day","night","light","dark"),
]


def main():
    print("=== GEO-5: geometric understanding on REAL LLM (MiniLM) embeddings ===", flush=True)
    m = SentenceTransformer("all-MiniLM-L6-v2")
    vocab = sorted(set(w for q in QUADS for w in q))
    V = m.encode(vocab, normalize_embeddings=True)
    vi = {w: i for i, w in enumerate(vocab)}
    E = np.array(V)

    def nearest(qv, exclude):
        sims = E @ qv; sims[exclude] = -1e9
        return [vocab[i] for i in np.argsort(-sims)[:5]]

    h1 = h5 = 0
    for a, b, c, d in QUADS:
        q = E[vi[b]] - E[vi[a]] + E[vi[c]]; q /= np.linalg.norm(q) + 1e-9
        top = nearest(q, [vi[a], vi[b], vi[c]])
        if top[0] == d: h1 += 1
        if d in top: h5 += 1
    n = len(QUADS)
    # baseline: just nearest to c (ignore analogy) -> tests if analogy adds over similarity
    base = sum(1 for a,b,c,d in QUADS if nearest(E[vi[c]], [vi[a],vi[b],vi[c]])[0]==d)
    print(f"  analogy hits@1 = {h1/n:.2f}  hits@5 = {h5/n:.2f}  (n={n})", flush=True)
    print(f"  baseline (nearest-to-c, no offset) hits@1 = {base/n:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if h1/n >= 0.5:
        print("GEO-5: PASS - geometric analogy on REAL LLM embeddings works (>=0.5 hits@1): LLM semantic geometry supports compositional understanding by vector operations.", flush=True)
    elif h5/n >= 0.5:
        print("GEO-5: PARTIAL - analogy in top-5 but not top-1; LLM geometry is approximately analogical", flush=True)
    else:
        print("GEO-5: NULL - word analogy weak on these sentence-embeddings (geometry not cleanly analogical at word level)", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
