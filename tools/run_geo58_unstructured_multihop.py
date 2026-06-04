"""GEO-58 — multi-hop over unstructured text: extract the bridge from sentence text, then chain."""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from sentence_transformers import SentenceTransformer

CHAINS=[("Alice","Falcon","Berlin"),("Bob","Phoenix","Tokyo"),("Carol","Titan","Madrid"),
        ("David","Orion","Boston"),("Eve","Vega","Oslo"),("Frank","Nova","Cairo")]
DISTRACT=["The quarterly report was published last week.","Many employees enjoy the new cafeteria.",
          "The building has six floors and a rooftop garden.","Annual reviews happen every December."]


def main():
    print("=== GEO-58: unstructured multi-hop (text bridge) ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    lead=[f"{p} leads the {proj} project." for p,proj,_ in CHAINS]
    base=[f"The {proj} project is based in {c}." for _,proj,c in CHAINS]
    sents=lead+base+DISTRACT
    S=np.array(m.encode(sents,normalize_embeddings=True))
    projects=[proj for _,proj,_ in CHAINS]
    def extract_project(text):
        for proj in projects:
            if proj in text: return proj
        return None
    ok=0; single=0
    for p,proj,city in CHAINS:
        # hop-1: retrieve the person's sentence
        q1=m.encode([f"Which project does {p} lead?"],normalize_embeddings=True)[0]
        j1=int(np.argmax(S@q1)); bridge=extract_project(sents[j1])
        # hop-2: retrieve the bridge project's base sentence
        if bridge:
            q2=m.encode([f"Where is the {bridge} project based?"],normalize_embeddings=True)[0]
            j2=int(np.argmax(S@q2)); ans=sents[j2]
            ok+= int(city.lower() in ans.lower())
        # single-hop baseline: ask the city question directly
        qd=m.encode([f"Which city is {p}'s project based in?"],normalize_embeddings=True)[0]
        jd=int(np.argmax(S@qd)); single+= int(city.lower() in sents[jd].lower())
    n=len(CHAINS)
    print(f"  multi-hop (text-bridge) end-to-end = {ok/n:.2f}", flush=True)
    print(f"  single-hop baseline (no chain)     = {single/n:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if ok/n>=0.7 and ok/n>single/n:
        print(f"GEO-58: PASS - multi-hop over UNSTRUCTURED text works ({ok/n:.2f}): bridge entity extracted from sentence text + iterative retrieval, where single-hop fails ({single/n:.2f}). Multi-hop reasoning extends to free text, not just structured stores.", flush=True)
    else:
        print(f"GEO-58: PARTIAL/NULL - multi-hop {ok/n:.2f}, single {single/n:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
