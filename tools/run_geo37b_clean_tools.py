"""GEO-37b — clean tools semantic retrieval: SYNONYM descriptions sharing no token with the fact's action."""
import numpy as np, re
from sentence_transformers import SentenceTransformer
# (synonym description sharing NO token with the action phrase, tool, action-in-fact)
TOOLS=[("the thing carpenters pound fasteners into wood with","hammer","drive nails"),
       ("the handheld blades that snip sheets","scissors","cut paper"),
       ("the gripper that loosens or fastens hexagonal heads","wrench","tighten bolts"),
       ("the gauge that reads how hot something is","thermometer","measure temperature"),
       ("the bristled stick that clears dust off the ground","broom","sweep floors"),
       ("the blade on a handle that excavates earth","shovel","dig soil"),
       ("the dial that shows the hour","clock","tell time"),
       ("the long lens that brings far galaxies near","telescope","see far"),
       ("the inked stylus for marking pages","pen","write"),
       ("the shallow metal dish that sizzles meals","skillet","fry food")]
def toks(s): return set(re.findall(r"[a-z]+", s.lower()))
def jacc(a,b):
    A,B=toks(a),toks(b); return len(A&B)/len(A|B) if A|B else 0.0
def main():
    print("=== GEO-37b: clean tools retrieval (synonym descriptions) ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    facts=[f"A {t} is used to {a}." for _,t,a in TOOLS]
    F=np.array(m.encode(facts,normalize_embeddings=True)); n=len(TOOLS)
    qs=[f"What is {d}?" for d,_,_ in TOOLS]
    Q=np.array(m.encode(qs,normalize_embeddings=True))
    geo=np.mean(np.argmax(Q@F.T,1)==np.arange(n))
    lex=np.mean([int(int(np.argmax([jacc(q,f) for f in facts]))==i) for i,q in enumerate(qs)])
    print(f"  geometric={geo:.2f}  lexical={lex:.2f}  (chance {1/n:.2f})", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if geo>=0.7 and (geo-lex)>=0.3:
        print("GEO-37b: PASS - clean (synonym, no shared token) tools retrieval: geometry beats lexical, confirming semantic retrieval is DOMAIN-robust.", flush=True)
    else:
        print(f"GEO-37b: PARTIAL - geo {geo:.2f}, lex {lex:.2f}", flush=True)
    print("DONE", flush=True)
if __name__=="__main__":
    main()
