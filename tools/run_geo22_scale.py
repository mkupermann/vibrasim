"""GEO-22 — scale sweep: retrieval/multi-hop accuracy vs store size N. MiniLM, CPU."""
import numpy as np
from sentence_transformers import SentenceTransformer

FIRST=["Alice","Bob","Carol","Dan","Eve","Frank","Gina","Hugo","Iris","Jack","Kara","Leo","Mia","Ned",
       "Olga","Paul","Quinn","Rita","Sam","Tara","Uri","Vera","Will","Xena","Yann","Zoe"]
LAST=["Smith","Jones","Lee","Brown","Garcia","Khan","Patel","Nguyen","Kim","Lopez","Wang","Singh",
      "Rossi","Mueller","Costa","Tran","Diaz","Park","Cohen","Reyes"]
CTOK=["Acme","Globex","Initech","Umbra","Stark","Wayne","Cyber","Hooli","Soylent","Tyrell","Vande","Piper",
      "Nexus","Orbit","Quanta","Vertex","Zenith","Apex","Lumen","Helix"]
CITYTOK=["Boston","Denver","Austin","Seattle","Chicago","Portland","Atlanta","Dallas","Miami","Phoenix",
         "Reno","Tucson","Salem","Tampa","Fresno","Mesa","Akron","Boise","Ogden","Provo"]


def names(N):
    ppl=[]; comp=[]; city=[]
    for i in range(N):
        ppl.append(f"{FIRST[i%len(FIRST)]} {LAST[(i//len(FIRST))%len(LAST)]} {i}")
        comp.append(f"{CTOK[i%len(CTOK)]}Corp{i}")
        city.append(f"{CITYTOK[i%len(CITYTOK)]}ville{i}")
    return ppl,comp,city


def main():
    print("=== GEO-22: scale sweep ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    for N in [25,100,400]:
        ppl,comp,city=names(N)
        works=[f"{p} works at {c}." for p,c in zip(ppl,comp)]
        loc  =[f"{c} is in {ci}." for c,ci in zip(comp,city)]
        W=np.array(m.encode(works,normalize_embeddings=True,batch_size=64))
        Lc=np.array(m.encode(loc,normalize_embeddings=True,batch_size=64))
        h1=h2=0
        Q=np.array(m.encode([f"What company does {p} work at?" for p in ppl],normalize_embeddings=True,batch_size=64))
        j=np.argmax(Q@W.T,axis=1)
        h1=np.mean(j==np.arange(N))
        # 2-hop: use predicted company to probe location
        P=np.array(m.encode([f"What city is {comp[jj]} in?" for jj in j],normalize_embeddings=True,batch_size=64))
        k=np.argmax(P@Lc.T,axis=1)
        h2=np.mean(k==np.arange(N))
        print(f"  N={N:4d}  1-hop={h1:.2f}  2-hop={h2:.2f}  (chance {1/N:.3f})", flush=True)
    print("\n--- VERDICT ---", flush=True)
    print("GEO-22: characterization (curve above is the finding).", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
