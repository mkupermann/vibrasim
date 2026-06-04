"""GEO-43b — separate noise sources: paraphrase+typos ALONE vs adding near-duplicate entities."""
import numpy as np
from sentence_transformers import SentenceTransformer
from run_geo43_noisy import PEOPLE,CITIES,NEARDUP,TEMPLATES,typo


def main():
    print("=== GEO-43b: noise-source split ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2"); rng=np.random.default_rng(0); n=len(PEOPLE)
    Q=np.array(m.encode([f"What city does {p} live in?" for p in PEOPLE],normalize_embeddings=True))
    # A: paraphrase+typos ONLY (no near-dups)
    noisyA=[typo(TEMPLATES[rng.integers(len(TEMPLATES))].format(p=p,c=c),rng) for p,c in zip(PEOPLE,CITIES)]
    Fa=np.array(m.encode(noisyA,normalize_embeddings=True))
    accA=np.mean(np.argmax(Q@Fa.T,1)==np.arange(n))
    # B: clean facts + near-dups ONLY (no paraphrase/typo)
    cleanB=[f"{p} lives in {c}." for p,c in zip(PEOPLE,CITIES)]+[f"{p} lives in {c}." for p,c in NEARDUP]
    Fb=np.array(m.encode(cleanB,normalize_embeddings=True))
    predB=np.argmax(Q@Fb.T,1); accB=np.mean(predB==np.arange(n)); confB=np.mean(predB>=n)
    print(f"  A) paraphrase+typos only      1-hop = {accA:.2f}", flush=True)
    print(f"  B) near-duplicates only       1-hop = {accB:.2f}  (confusion {confB:.2f})", flush=True)
    print("\n--- VERDICT ---", flush=True)
    print(f"GEO-43b: paraphrase/typos cause {1-accA:.2f} loss; near-duplicates cause {1-accB:.2f} loss (confusion {confB:.2f}). Dominant cause: {'near-duplicates (need exact-ID entity resolution)' if (1-accB)>(1-accA) else 'paraphrase/typos'}.", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
