"""GEO-37 — domain robustness: zero-shot transfer on materials-hardness + semantic retrieval on tools."""
import numpy as np, re
from sentence_transformers import SentenceTransformer

MATERIALS=["talc","gypsum","chalk","clay","coal","calcite","fluorite","copper","apatite","glass",
           "feldspar","steel","quartz","topaz","garnet","emerald","ruby","sapphire","diamond","graphene"]
HARD=list(range(len(MATERIALS)))  # ascending hardness proxy (ordinal)
TOOLS=[("the implement for driving nails","hammer","drive nails"),
       ("the device for cutting paper","scissors","cut paper"),
       ("the tool for tightening bolts","wrench","tighten bolts"),
       ("the instrument for measuring temperature","thermometer","measure temperature"),
       ("the implement for sweeping floors","broom","sweep floors"),
       ("the tool for digging soil","shovel","dig soil"),
       ("the device for telling time","clock","tell time"),
       ("the instrument for amplifying distant objects","telescope","see far"),
       ("the tool for writing on paper","pen","write"),
       ("the implement for frying food","pan","fry food")]


def toks(s): return set(re.findall(r"[a-z]+", s.lower()))
def jacc(a,b):
    A,B=toks(a),toks(b); return len(A&B)/len(A|B) if A|B else 0.0
def learn(E0,seen,seed):
    rng=np.random.default_rng(seed); w=rng.normal(0,.1,E0.shape[1])
    pairs=[(i,j) for i in seen for j in seen if HARD[i]>HARD[j]]; rng.shuffle(pairs); lr=0.1
    for _ in range(2500):
        for i,j in pairs:
            if E0[i]@w-E0[j]@w<1.0: w+=lr*(E0[i]-E0[j])
        w/=np.linalg.norm(w)+1e-9
    return w


def main():
    print("=== GEO-37: domain robustness ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    # (1) zero-shot transfer on materials
    L=np.array(m.encode(MATERIALS,normalize_embeddings=True)); nE=len(MATERIALS)
    rng0=np.random.default_rng(7); R=rng0.normal(0,1,L.shape); R/=np.linalg.norm(R,axis=1,keepdims=True)
    def zs(E0):
        accs=[]
        for s in range(5):
            rng=np.random.default_rng(100+s); unseen=set(rng.choice(nE,8,replace=False).tolist())
            seen=[i for i in range(nE) if i not in unseen]; w=learn(E0,seen,s)
            tp=[(i,j) for i in unseen for j in unseen if HARD[i]>HARD[j]]
            accs.append(np.mean([(E0[i]@w)>(E0[j]@w) for i,j in tp]))
        return np.mean(accs)
    zl,zr=zs(L),zs(R)
    # (2) semantic retrieval on tools
    facts=[f"A {t} is used to {a}." for _,t,a in TOOLS]
    F=np.array(m.encode(facts,normalize_embeddings=True)); n=len(TOOLS)
    qs=[f"What is {d}?" for d,_,_ in TOOLS]
    Q=np.array(m.encode(qs,normalize_embeddings=True))
    geo=np.mean(np.argmax(Q@F.T,1)==np.arange(n))
    lex=np.mean([int(int(np.argmax([jacc(q,f) for f in facts]))==i) for i,q in enumerate(qs)])
    print(f"  (1) materials zero-shot: LLM-init={zl:.2f}  random={zr:.2f}", flush=True)
    print(f"  (2) tools semantic retrieval: geometric={geo:.2f}  lexical={lex:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    r1 = zl>=0.70 and zl>=zr+0.15
    r2 = geo>=0.7 and (geo-lex)>=0.3
    if r1 and r2:
        print("GEO-37: PASS - both findings REPLICATE on new domains (materials-hardness zero-shot, tools semantic retrieval). The core claims are DOMAIN-robust, not geography/animal specific.", flush=True)
    elif r1 or r2:
        print(f"GEO-37: PARTIAL - one replicates (materials {r1}, tools {r2}).", flush=True)
    else:
        print("GEO-37: NULL - neither replicates; findings were domain-specific.", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
