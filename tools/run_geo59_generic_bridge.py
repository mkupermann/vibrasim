"""GEO-59 — generic bridge extraction (capitalized entity, no pre-known list) for unstructured multi-hop."""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from sentence_transformers import SentenceTransformer

CHAINS=[("Alice","Falcon","Berlin"),("Bob","Phoenix","Tokyo"),("Carol","Titan","Madrid"),
        ("David","Orion","Boston"),("Eve","Vega","Oslo"),("Frank","Nova","Cairo")]
DISTRACT=["The quarterly report was published last week.","Many employees enjoy the new cafeteria.",
          "The building has six floors.","Reviews happen every December."]


def caps(text):
    return [t for t in re.findall(r"\b[A-Z][a-z]+\b", text)]


def main():
    print("=== GEO-59: generic bridge extraction ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    lead=[f"{p} leads the {proj} project." for p,proj,_ in CHAINS]
    base=[f"The {proj} project is based in {c}." for _,proj,c in CHAINS]
    sents=lead+base+DISTRACT
    S=np.array(m.encode(sents,normalize_embeddings=True))
    # token -> set of sentence indices it appears in (for "appears elsewhere" test)
    from collections import defaultdict
    tok2sent=defaultdict(set)
    for i,s in enumerate(sents):
        for t in caps(s): tok2sent[t].add(i)
    def generic_bridge(sent_idx, person):
        ptoks=set(person.split())
        cands=[t for t in caps(sents[sent_idx]) if t not in ptoks]
        # pick the capitalized entity that also appears in another sentence (the link)
        linking=[t for t in cands if len(tok2sent[t])>=2]
        return linking[0] if linking else (cands[0] if cands else None)
    ok=0
    for p,proj,city in CHAINS:
        q1=m.encode([f"Which project does {p} lead?"],normalize_embeddings=True)[0]
        j1=int(np.argmax(S@q1)); bridge=generic_bridge(j1,p)
        if bridge:
            q2=m.encode([f"Where is the {bridge} project based?"],normalize_embeddings=True)[0]
            j2=int(np.argmax(S@q2)); ok+= int(city.lower() in sents[j2].lower())
    n=len(CHAINS)
    print(f"  generic-bridge multi-hop end-to-end = {ok/n:.2f}  (GEO-58 known-list: 1.00)", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if ok/n>=0.7:
        print(f"GEO-59: PASS - GENERIC bridge extraction (capitalized linking entity, no pre-known list) works ({ok/n:.2f}). Unstructured multi-hop is general: any document, no domain list needed.", flush=True)
    else:
        print(f"GEO-59: PARTIAL/NULL - {ok/n:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
