"""GEO-25 — adversarial lexical baseline vs geometric retrieval, templated vs paraphrased queries."""
import numpy as np, re
from sentence_transformers import SentenceTransformer

PAIRS=[("France","Paris"),("Germany","Berlin"),("Italy","Rome"),("Spain","Madrid"),("Japan","Tokyo"),
       ("China","Beijing"),("Egypt","Cairo"),("Canada","Ottawa"),("Russia","Moscow"),("Greece","Athens"),
       ("Poland","Warsaw"),("Norway","Oslo"),("Brazil","Brasilia"),("India","Delhi"),("Kenya","Nairobi")]


def toks(s): return set(re.findall(r"[a-z]+", s.lower()))
def jacc(a,b):
    A,B=toks(a),toks(b); 
    return len(A&B)/len(A|B) if A|B else 0.0


def main():
    print("=== GEO-25: lexical baseline vs geometric (templated vs paraphrased) ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    facts=[f"The capital of {c} is {city}." for c,city in PAIRS]
    F=np.array(m.encode(facts,normalize_embeddings=True)); n=len(PAIRS)
    templ=[f"What is the capital of {c}?" for c,_ in PAIRS]
    para =[f"Which city serves as {c}'s seat of government?" for c,_ in PAIRS]
    def geo(qs):
        Q=np.array(m.encode(qs,normalize_embeddings=True)); return np.mean(np.argmax(Q@F.T,1)==np.arange(n))
    def lex(qs):
        hit=0
        for i,q in enumerate(qs):
            sc=[jacc(q,f) for f in facts]; hit+= int(int(np.argmax(sc))==i)
        return hit/n
    gt,gp=geo(templ),geo(para); lt,lp=lex(templ),lex(para)
    print(f"  TEMPLATED   geometric={gt:.2f}  lexical={lt:.2f}", flush=True)
    print(f"  PARAPHRASED geometric={gp:.2f}  lexical={lp:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if lt>=0.8 and gp>=0.7 and (gp-lp)>=0.3:
        print("GEO-25: PASS-as-designed (honest) - lexical TIES geometry on templated queries (so templated 1.00s don't prove geometry), but geometry WINS paraphrases where lexical collapses. The LLM geometry's real contribution = semantic/paraphrase robustness, not the templated headline numbers.", flush=True)
    else:
        print(f"GEO-25: see cells - templated geo {gt:.2f}/lex {lt:.2f}, paraphrase geo {gp:.2f}/lex {lp:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
