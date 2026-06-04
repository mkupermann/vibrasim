"""GEO-36 — reproduce GEO-25b + GEO-27b on a second embedding model (all-mpnet-base-v2)."""
import numpy as np, re
from sentence_transformers import SentenceTransformer

# --- GEO-25b data: descriptive (no shared token) -> capital fact ---
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
# --- GEO-27b data: animals with size order ---
WORDS=["ant","bee","mouse","sparrow","rat","squirrel","cat","rabbit","fox","dog","goat","sheep","pig",
       "wolf","deer","donkey","horse","cow","bison","bear","moose","rhino","hippo","elephant"]
SIZE=list(range(len(WORDS)))


def toks(s): return set(re.findall(r"[a-z]+", s.lower()))
def jacc(a,b):
    A,B=toks(a),toks(b); return len(A&B)/len(A|B) if A|B else 0.0
def learn(E0,seen,seed):
    rng=np.random.default_rng(seed); w=rng.normal(0,.1,E0.shape[1])
    pairs=[(i,j) for i in seen for j in seen if SIZE[i]>SIZE[j]]; rng.shuffle(pairs); lr=0.1
    for _ in range(2500):
        for i,j in pairs:
            if E0[i]@w-E0[j]@w<1.0: w+=lr*(E0[i]-E0[j])
        w/=np.linalg.norm(w)+1e-9
    return w


def run_model(name):
    m=SentenceTransformer(name)
    # GEO-25b
    facts=[f"The capital of {c} is {city}." for _,c,city in ITEMS]
    F=np.array(m.encode(facts,normalize_embeddings=True)); n=len(ITEMS)
    qs=[f"What is the capital of {d}?" for d,_,_ in ITEMS]
    Q=np.array(m.encode(qs,normalize_embeddings=True))
    geo=np.mean(np.argmax(Q@F.T,1)==np.arange(n))
    lex=np.mean([int(int(np.argmax([jacc(q,f) for f in facts]))==i) for i,q in enumerate(qs)])
    # GEO-27b
    L=np.array(m.encode(WORDS,normalize_embeddings=True)); nE=len(WORDS)
    rng0=np.random.default_rng(7); R=rng0.normal(0,1,L.shape); R/=np.linalg.norm(R,axis=1,keepdims=True)
    def zs(E0):
        accs=[]
        for s in range(5):
            rng=np.random.default_rng(100+s); unseen=set(rng.choice(nE,8,replace=False).tolist())
            seen=[i for i in range(nE) if i not in unseen]; w=learn(E0,seen,s)
            tp=[(i,j) for i in unseen for j in unseen if SIZE[i]>SIZE[j]]
            accs.append(np.mean([(E0[i]@w)>(E0[j]@w) for i,j in tp]))
        return np.mean(accs)
    return geo,lex,zs(L),zs(R)


def main():
    print("=== GEO-36: reproduce on all-mpnet-base-v2 ===", flush=True)
    print("  model                    | 25b geo | 25b lex | 27b LLM | 27b rand", flush=True)
    res={}
    for name in ["all-MiniLM-L6-v2","all-mpnet-base-v2"]:
        g,l,zl,zr=run_model(name); res[name]=(g,l,zl,zr)
        print(f"  {name:24s} |  {g:.2f}   |  {l:.2f}   |  {zl:.2f}   |  {zr:.2f}", flush=True)
    g,l,zl,zr=res["all-mpnet-base-v2"]
    print("\n--- VERDICT ---", flush=True)
    r1 = g>=0.7 and (g-l)>=0.3
    r2 = zl>=0.75 and zl>=zr+0.20
    if r1 and r2:
        print("GEO-36: PASS - both irreducible-edge findings REPLICATE on MPNet (semantic retrieval + zero-shot transfer). The programme's core claims are model-robust, not MiniLM artifacts.", flush=True)
    elif r1 or r2:
        print(f"GEO-36: PARTIAL - one replicates (25b {r1}, 27b {r2}).", flush=True)
    else:
        print("GEO-36: NULL - neither replicates on MPNet; findings were model-specific.", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
