"""GEO-78 — abstract concept resolution from descriptions (vs concrete entities)."""
import numpy as np, re
from sentence_transformers import SentenceTransformer

CONCEPTS=[("nostalgia","the bittersweet longing for times that have passed"),
          ("empathy","the ability to share and feel what another person experiences"),
          ("serendipity","a fortunate discovery made entirely by accident"),
          ("procrastination","the habit of delaying tasks that should be done now"),
          ("resilience","the capacity to recover quickly from hardship"),
          ("curiosity","a strong desire to learn or know more about something"),
          ("jealousy","resentment toward someone who has what one wants"),
          ("ambition","a strong drive to achieve success or power"),
          ("humility","a modest view of one's own importance"),
          ("gratitude","a warm feeling of thankfulness for what one has"),
          ("loneliness","the painful feeling of being isolated from others"),
          ("inspiration","a sudden spark that motivates creative action")]


def toks(s): return set(re.findall(r"[a-z]+", s.lower()))
def jacc(a,b):
    A,B=toks(a),toks(b); return len(A&B)/len(A|B) if A|B else 0.0


def main():
    print("=== GEO-78: abstract concept resolution ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    words=[c for c,_ in CONCEPTS]; descs=[d for _,d in CONCEPTS]; n=len(CONCEPTS)
    W=np.array(m.encode(words,normalize_embeddings=True)); D=np.array(m.encode(descs,normalize_embeddings=True))
    geo=np.mean(np.argmax(D@W.T,1)==np.arange(n))
    lex=np.mean([int(int(np.argmax([jacc(descs[i],words[j]) for j in range(n)]))==i) for i in range(n)])
    print(f"  abstract concept geometric hits@1 = {geo:.2f}  (concrete entity GEO-25b: 0.80)", flush=True)
    print(f"  lexical baseline                  = {lex:.2f}  (chance {1/n:.2f})", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if geo>=0.6 and geo-lex>=0.3:
        print(f"GEO-78: PASS - semantic matching extends to ABSTRACT concepts ({geo:.2f} vs lexical {lex:.2f}): descriptions of emotions/ideas resolve to the concept word. The distributional semantic capability is not limited to concrete entities.", flush=True)
    else:
        print(f"GEO-78: PARTIAL/finding - abstract {geo:.2f}, lexical {lex:.2f} (vs concrete 0.80)", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
