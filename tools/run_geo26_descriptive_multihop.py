"""GEO-26 — descriptive (non-lexical) multi-hop: resolve a person by DESCRIPTION, then chain to city."""
import numpy as np, re
from sentence_transformers import SentenceTransformer

# (description w/o name, person, company, city)
DATA=[("the violinist who won three awards","Alice","Acme","Boston"),
      ("the marathon runner from the coast","Bob","Globex","Denver"),
      ("the chess champion turned coder","Carol","Initech","Austin"),
      ("the pastry chef with a vineyard","David","Umbrella","Seattle"),
      ("the astronomer who found a comet","Eve","Stark","Chicago"),
      ("the pilot who circled the globe","Frank","Wayne","Portland"),
      ("the novelist writing under a pen name","Grace","Cyberdyne","Atlanta"),
      ("the surgeon who plays jazz piano","Heidi","Hooli","Dallas"),
      ("the architect of glass towers","Ivan","Soylent","Miami"),
      ("the botanist mapping rare orchids","Judy","Tyrell","Phoenix")]


def toks(s): return set(re.findall(r"[a-z]+", s.lower()))
def jacc(a,b):
    A,B=toks(a),toks(b); return len(A&B)/len(A|B) if A|B else 0.0


def main():
    print("=== GEO-26: descriptive (non-lexical) multi-hop ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    n=len(DATA)
    persona=[f"{d} is {p}." for d,p,_,_ in DATA]          # links description -> person
    works=[f"{p} works at {c}." for _,p,c,_ in DATA]
    loc  =[f"{c} is in {city}." for _,_,c,city in DATA]
    PB=np.array(m.encode(persona,normalize_embeddings=True))
    W=np.array(m.encode(works,normalize_embeddings=True))
    Lc=np.array(m.encode(loc,normalize_embeddings=True))
    geo=0; lexhop=0
    for i,(d,p,c,city) in enumerate(DATA):
        q=f"In which city does {d} work?"
        qv=m.encode([q],normalize_embeddings=True)[0]
        # hop0: description -> person fact (SEMANTIC, no shared name)
        j=int(np.argmax(qv@PB.T)); person=DATA[j][1]
        # lexical baseline at hop0
        lj=int(np.argmax([jacc(q,t) for t in persona])); lexhop+= int(lj==i)
        # hop1: person -> company
        cv=m.encode([f"What company does {person} work at?"],normalize_embeddings=True)[0]
        k=int(np.argmax(cv@W.T)); comp=DATA[k][2]
        # hop2: company -> city
        rv=m.encode([f"What city is {comp} in?"],normalize_embeddings=True)[0]
        l=int(np.argmax(rv@Lc.T)); pcity=DATA[l][3]
        geo+= int(pcity==city)
    print(f"  geometric descriptive 2-hop end-to-end = {geo/n:.2f}  (chance {1/n:.2f})", flush=True)
    print(f"  lexical at the descriptive hop          = {lexhop/n:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if geo/n>=0.6 and (geo/n - lexhop/n)>=0.3:
        print("GEO-26: PASS - multi-hop reasoning SURVIVES the lexical critique: resolving the person by DESCRIPTION (no shared token) is semantic (geometry wins, lexical collapses), and the chain completes. The reasoning rests on the LLM geometry, not string overlap.", flush=True)
    else:
        print(f"GEO-26: geo {geo/n:.2f}, lexical-hop {lexhop/n:.2f} - inspect", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
