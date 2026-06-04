"""GEO-25b — proper paraphrase test: DESCRIPTIVE queries sharing NO identifying token with the target fact.
Lexical must fail; only semantic geometry can succeed."""
import numpy as np, re
from sentence_transformers import SentenceTransformer

# (description with NO country/city name) -> target country fact
ITEMS=[("the country famous for the Eiffel Tower","France","Paris"),
       ("the nation known for sushi and Mount Fuji","Japan","Tokyo"),
       ("the land of the pyramids and the Nile","Egypt","Cairo"),
       ("the country home to the Colosseum and pasta","Italy","Rome"),
       ("the nation of flamenco and paella","Spain","Madrid"),
       ("the country of the Great Wall","China","Beijing"),
       ("the largest country, spanning Siberia","Russia","Moscow"),
       ("the birthplace of democracy and the Parthenon","Greece","Athens"),
       ("the maple-leaf country north of the USA","Canada","Ottawa"),
       ("the Amazon rainforest's largest country","Brazil","Brasilia")]


def toks(s): return set(re.findall(r"[a-z]+", s.lower()))
def jacc(a,b):
    A,B=toks(a),toks(b); return len(A&B)/len(A|B) if A|B else 0.0


def main():
    print("=== GEO-25b: descriptive queries (no shared token) — real geometry test ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    facts=[f"The capital of {c} is {city}." for _,c,city in ITEMS]
    F=np.array(m.encode(facts,normalize_embeddings=True)); n=len(ITEMS)
    qs=[f"What is the capital of {d}?" for d,_,_ in ITEMS]      # description, NOT the country name
    Q=np.array(m.encode(qs,normalize_embeddings=True))
    geo=np.mean(np.argmax(Q@F.T,1)==np.arange(n))
    lex=np.mean([int(int(np.argmax([jacc(q,f) for f in facts]))==i) for i,q in enumerate(qs)])
    print(f"  DESCRIPTIVE (no shared name)  geometric={geo:.2f}  lexical={lex:.2f}  (chance {1/n:.2f})", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if geo>=0.7 and (geo-lex)>=0.3:
        print(f"GEO-25b: PASS - geometry genuinely beats lexical ({geo:.2f} vs {lex:.2f}) when there is NO lexical shortcut. The LLM geometry's real value = semantic matching (resolving descriptions to entities), confirmed.", flush=True)
    else:
        print(f"GEO-25b: geo {geo:.2f}, lex {lex:.2f} - inspect", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
