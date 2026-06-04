"""GEO-43 — robustness to a noisy store: paraphrase + typos + near-duplicate entity names."""
import numpy as np
from sentence_transformers import SentenceTransformer

PEOPLE=["John Smith","Mary Johnson","Robert Lee","Linda Brown","James Garcia","Patricia Khan",
        "Michael Patel","Barbara Nguyen","William Kim","Elizabeth Lopez","David Wang","Jennifer Singh",
        "Richard Rossi","Susan Mueller","Joseph Costa"]
CITIES=["Boston","Denver","Austin","Seattle","Chicago","Portland","Atlanta","Dallas","Miami","Phoenix",
        "Reno","Tucson","Salem","Tampa","Fresno"]
NEARDUP=[("Jon Smith","Denver"),("Mary Jonson","Austin"),("Robert Li","Miami"),("Linda Browne","Reno"),
         ("James Garca","Salem")]  # near-duplicate names, DIFFERENT cities
TEMPLATES=["{p} lives in {c}.","{p} is based in {c}.","{p}'s home city is {c}.","{p} resides in {c}.",
           "The city where {p} lives is {c}."]


def typo(s,rng,rate=0.10):
    out=[]
    for ch in s:
        if ch.isalpha() and rng.random()<rate:
            out.append(chr(((ord(ch.lower())-97+1)%26)+97))  # shift letter
        else: out.append(ch)
    return "".join(out)


def main():
    print("=== GEO-43: noisy-store robustness ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2"); rng=np.random.default_rng(0); n=len(PEOPLE)
    # clean store
    clean=[f"{p} lives in {c}." for p,c in zip(PEOPLE,CITIES)]
    Fc=np.array(m.encode(clean,normalize_embeddings=True))
    # noisy store: paraphrased + typos + near-dup distractors
    noisy=[typo(TEMPLATES[rng.integers(len(TEMPLATES))].format(p=p,c=c),rng) for p,c in zip(PEOPLE,CITIES)]
    noisy_people=list(PEOPLE)
    for ndp,ndc in NEARDUP:
        noisy.append(TEMPLATES[rng.integers(len(TEMPLATES))].format(p=ndp,c=ndc)); noisy_people.append(ndp)
    Fn=np.array(m.encode(noisy,normalize_embeddings=True))
    # queries (canonical) for the 15 real people
    Q=np.array(m.encode([f"What city does {p} live in?" for p in PEOPLE],normalize_embeddings=True))
    clean_acc=np.mean(np.argmax(Q@Fc.T,1)==np.arange(n))
    noisy_pred=np.argmax(Q@Fn.T,1)
    noisy_acc=np.mean(noisy_pred==np.arange(n))   # correct = the real person's (noisy) fact, indices 0..14
    # near-dup confusion: how often a real-person query returns a near-dup fact (index >= n)
    confusion=np.mean(noisy_pred>=n)
    print(f"  clean-store 1-hop accuracy = {clean_acc:.2f}", flush=True)
    print(f"  noisy-store 1-hop accuracy = {noisy_acc:.2f}  (paraphrase+typos+{len(NEARDUP)} near-dups)", flush=True)
    print(f"  near-duplicate confusion rate = {confusion:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    drop=clean_acc-noisy_acc
    if drop<=0.1:
        print(f"GEO-43: ROBUST - noisy store holds within 0.1 of clean (drop {drop:.2f}); embedding retrieval tolerates paraphrase/typos/near-dups. Deployable on messy data.", flush=True)
    elif drop<=0.2:
        print(f"GEO-43: MODERATE - graceful degradation (drop {drop:.2f}); usable but add entity normalization for near-dups.", flush=True)
    else:
        print(f"GEO-43: FRAGILE - noise hurts (drop {drop:.2f}); needs preprocessing/normalization.", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
