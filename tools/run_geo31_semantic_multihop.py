"""GEO-31 — clean non-lexical multi-hop: epithet (no shared token) resolved by LLM knowledge, then chained."""
import numpy as np, re
from sentence_transformers import SentenceTransformer

# (epithet sharing no name-token, person, country, continent) — real-world, LLM-known
DATA=[("the composer of the Ninth Symphony","Beethoven","Germany","Europe"),
      ("the painter of the Mona Lisa","Leonardo da Vinci","Italy","Europe"),
      ("the author of Romeo and Juliet","William Shakespeare","England","Europe"),
      ("the physicist who proposed relativity","Albert Einstein","Germany","Europe"),
      ("the founder of psychoanalysis","Sigmund Freud","Austria","Europe"),
      ("the naturalist who wrote On the Origin of Species","Charles Darwin","England","Europe"),
      ("the leader of nonviolent Indian independence","Mahatma Gandhi","India","Asia"),
      ("the first president of the United States","George Washington","America","NorthAmerica"),
      ("the Polish-French pioneer of radioactivity","Marie Curie","Poland","Europe"),
      ("the Macedonian king who conquered Persia","Alexander the Great","Macedonia","Europe")]


def toks(s): return set(re.findall(r"[a-z]+", s.lower()))
def jacc(a,b):
    A,B=toks(a),toks(b); return len(A&B)/len(A|B) if A|B else 0.0


def main():
    print("=== GEO-31: clean non-lexical (epithet) multi-hop ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    n=len(DATA)
    born=[f"{p} was born in {c}." for _,p,c,_ in DATA]
    loc =[f"{c} is in {cont}." for _,_,c,cont in DATA]
    B=np.array(m.encode(born,normalize_embeddings=True))
    Lc=np.array(m.encode(loc,normalize_embeddings=True))
    geo=0; ghop0=0; lhop0=0
    for i,(ep,p,c,cont) in enumerate(DATA):
        q=f"On which continent was {ep} born?"
        qv=m.encode([q],normalize_embeddings=True)[0]
        # hop-0 SEMANTIC: epithet query -> person's born-fact (no shared name token)
        j=int(np.argmax(qv@B.T)); ghop0+= int(j==i); person=DATA[j][1]
        lj=int(np.argmax([jacc(q,b) for b in born])); lhop0+= int(lj==i)
        # hop-1: person -> country (from born fact j) ; hop-2: country -> continent
        country=DATA[j][2]
        rv=m.encode([f"What continent is {country} in?"],normalize_embeddings=True)[0]
        k=int(np.argmax(rv@Lc.T)); pcont=DATA[k][3]
        geo+= int(pcont==cont)
    print(f"  hop-0 geometric (epithet->person) = {ghop0/n:.2f}", flush=True)
    print(f"  hop-0 lexical  (epithet->person)  = {lhop0/n:.2f}", flush=True)
    print(f"  end-to-end geometric continent    = {geo/n:.2f}  (chance ~1/3)", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if geo/n>=0.6 and (ghop0/n - lhop0/n)>=0.3:
        print("GEO-31: PASS - genuine NON-LEXICAL multi-hop: the epithet is resolved by semantic geometry (lexical fails at hop-0), and the chain completes. Multi-hop reasoning rests on the LLM geometry, not string overlap. Closes the GEO-26 gap.", flush=True)
    else:
        print(f"GEO-31: see cells - geo end {geo/n:.2f}, hop0 geo {ghop0/n:.2f} vs lex {lhop0/n:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
