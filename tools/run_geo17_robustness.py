"""GEO-17 — realism stress test for multi-hop geometric retrieval: 3 hops, big distractor store, paraphrase."""
import numpy as np
from sentence_transformers import SentenceTransformer

PEOPLE=["Alice","Bob","Carol","David","Eve","Frank","Grace","Heidi","Ivan","Judy","Mallory","Niaj"]
COMP  =["Acme","Globex","Initech","Umbrella","Stark","Wayne","Cyberdyne","Hooli","Soylent","Tyrell","Vandelay","Pied Piper"]
CITY  =["Boston","Denver","Austin","Seattle","Chicago","Portland","Atlanta","Dallas","Miami","Phoenix","Reno","Tucson"]
CTRY  =["Usa1","Usa2","Usa3","Usa4","Usa5","Usa6","Usa7","Usa8","Usa9","Usa10","Usa11","Usa12"]  # distinct tags

DISTRACT=[f"The {a} {b} is {c}." for a in ["red","blue","old","new","tall","small","bright","quiet","heavy","fast"]
          for b in ["river","mountain","engine","garden","signal","ladder","window","planet","anchor","puzzle"]
          for c in ["nearby"]][:120]


def main():
    print("=== GEO-17: 3-hop + distractors + paraphrase stress test ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    n=len(PEOPLE)
    works=[f"{p} works at {c}." for p,c in zip(PEOPLE,COMP)]
    hq   =[f"{c} is headquartered in {city}." for c,city in zip(COMP,CITY)]
    loc  =[f"{city} is located in {ctry}." for city,ctry in zip(CITY,CTRY)]
    Wt=np.array(m.encode(works,normalize_embeddings=True))
    Ht=np.array(m.encode(hq,normalize_embeddings=True))
    Lt=np.array(m.encode(loc,normalize_embeddings=True))
    Dt=np.array(m.encode(DISTRACT,normalize_embeddings=True)) if DISTRACT else np.zeros((0,Wt.shape[1]))
    # combine each hop's candidate pool WITH distractors (so retrieval can be fooled)
    def retr(qv, T, labels):
        pool=np.vstack([T,Dt]); lab=labels+[None]*len(Dt)
        k=int(np.argmax(qv@pool.T)); return lab[k]
    h1=h2=h3=correct=0
    for i in range(n):
        q=f"In which country is the firm employing {PEOPLE[i]} based?"   # paraphrased
        qv=m.encode([q],normalize_embeddings=True)[0]
        comp=retr(qv,Wt,COMP); ok1=comp==COMP[i]; h1+=ok1
        pv=m.encode([f"Where is {comp} headquartered?"],normalize_embeddings=True)[0]
        city=retr(pv,Ht,CITY); ok2=city==CITY[i]; h2+=ok2
        rv=m.encode([f"Which country is {city} located in?"],normalize_embeddings=True)[0]
        ctry=retr(rv,Lt,CTRY); ok3=ctry==CTRY[i]; h3+=ok3
        correct+= int(ctry==CTRY[i])
    print(f"  hop1 (person->company) acc = {h1/n:.2f}", flush=True)
    print(f"  hop2 (company->city)   acc = {h2/n:.2f}", flush=True)
    print(f"  hop3 (city->country)   acc = {h3/n:.2f}", flush=True)
    print(f"  FULL 3-hop end-to-end  acc = {correct/n:.2f}  (chance {1/n:.2f}, +{len(DISTRACT)} distractors, paraphrased)", flush=True)
    print("\n--- VERDICT ---", flush=True)
    a=correct/n
    if a>=0.6:
        print(f"GEO-17: PASS - 3-hop geometric reasoning survives distractors + paraphrase ({a:.2f}).", flush=True)
    elif a>=0.3:
        print(f"GEO-17: PARTIAL - degrades under stress ({a:.2f}); per-hop shows where.", flush=True)
    else:
        print(f"GEO-17: NULL - breaks under realistic stress ({a:.2f}).", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
