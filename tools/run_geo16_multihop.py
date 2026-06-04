"""GEO-16 — multi-hop QA by iterative geometric retrieval over an LLM-embedded fact store. No generator. CPU."""
import numpy as np
from sentence_transformers import SentenceTransformer

PEOPLE=["Alice","Bob","Carol","David","Eve","Frank","Grace","Heidi","Ivan","Judy"]
COMP  =["Acme","Globex","Initech","Umbrella","Stark","Wayne","Cyberdyne","Hooli","Soylent","Tyrell"]
CITY  =["Boston","Denver","Austin","Seattle","Chicago","Portland","Atlanta","Dallas","Miami","Phoenix"]


def main():
    print("=== GEO-16: multi-hop QA via iterative geometric retrieval ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    works=[f"{p} works at {c}." for p,c in zip(PEOPLE,COMP)]
    hq   =[f"{c} is headquartered in {city}." for c,city in zip(COMP,CITY)]
    W=np.array(m.encode(works,normalize_embeddings=True))
    H=np.array(m.encode(hq,   normalize_embeddings=True))
    n=len(PEOPLE)
    correct=0; direct_correct=0
    for i in range(n):
        q=f"Which city does {PEOPLE[i]} work in?"
        qv=m.encode([q],normalize_embeddings=True)[0]
        # hop1: nearest works-fact -> bridge company
        j=int(np.argmax(qv@W.T)); comp=COMP[j]
        # hop2: probe with bridge company -> nearest hq-fact -> city
        pv=m.encode([f"{comp} is headquartered in"],normalize_embeddings=True)[0]
        k=int(np.argmax(pv@H.T)); city=CITY[k]
        correct+= int(city==CITY[i])
        # control: answer directly from question against hq facts (no chain)
        kd=int(np.argmax(qv@H.T)); direct_correct+= int(CITY[kd]==CITY[i])
    acc=correct/n; dacc=direct_correct/n
    print(f"  multi-hop (chain) accuracy   = {acc:.2f}  (chance {1/n:.2f})", flush=True)
    print(f"  no-chain direct control      = {dacc:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if acc>=0.7 and acc>dacc:
        print("GEO-16: PASS - multi-hop understanding by iterative geometric retrieval works; the chain is necessary (beats no-chain). Generator-free reasoning over an LLM-embedded fact store.", flush=True)
    else:
        print(f"GEO-16: PARTIAL/NULL - chain {acc:.2f} vs no-chain {dacc:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
