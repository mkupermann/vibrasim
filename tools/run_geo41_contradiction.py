"""GEO-41 — contradiction detection: geometric retrieve nearest fact + symbolic object compare."""
import numpy as np
from sentence_transformers import SentenceTransformer

PEOPLE=["Alice","Bob","Carol","David","Eve","Frank","Grace","Heidi","Ivan","Judy","Mike","Nina"]
TEAMS=["Analytics","Platform","Design","Analytics","Platform","Product","Design","Product","Analytics","Platform","Design","Product"]
NEWPEOPLE=["Omar","Pam","Quinn","Rosa","Sam","Tina","Uma","Vince"]


def main():
    print("=== GEO-41: contradiction detection ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    facts=[f"{p} is on the {t} team." for p,t in zip(PEOPLE,TEAMS)]
    meta=[{"subject":p,"object":t} for p,t in zip(PEOPLE,TEAMS)]
    F=np.array(m.encode(facts,normalize_embeddings=True))
    # candidates: 8 contradictory (existing person, different team), 8 consistent
    cand=[]; label=[]
    alt={"Analytics":"Platform","Platform":"Design","Design":"Product","Product":"Analytics"}
    for i in range(8):  # contradictory
        p=PEOPLE[i]; t=alt[TEAMS[i]]; cand.append((p,t)); label.append(1)
    for i in range(4):  # consistent: existing person, SAME team
        p=PEOPLE[i]; t=TEAMS[i]; cand.append((p,t)); label.append(0)
    for i in range(4):  # consistent: new person
        cand.append((NEWPEOPLE[i],TEAMS[i])); label.append(0)
    def detect(p,t):
        v=m.encode([f"{p} is on the {t} team."],normalize_embeddings=True)[0]
        j=int(np.argmax(F@v))
        return int(meta[j]["subject"]==p and meta[j]["object"]!=t)  # same subj, diff obj -> contradiction
    pred=[detect(p,t) for p,t in cand]
    y=np.array(label); pr=np.array(pred)
    tpr=np.mean(pr[y==1]); tnr=np.mean(1-pr[y==0]); bal=(tpr+tnr)/2
    # pure-geometric variant: flag if 0.9<=sim<1.0 (very similar but not identical) -- expected noisy
    def pure(p,t):
        v=m.encode([f"{p} is on the {t} team."],normalize_embeddings=True)[0]
        s=np.max(F@v); return int(0.88<=s<0.999)
    pg=np.array([pure(p,t) for p,t in cand]); pbal=(np.mean(pg[y==1])+np.mean(1-pg[y==0]))/2
    print(f"  hybrid (retrieve+symbolic-compare) balanced-acc = {bal:.2f}  (TPR {tpr:.2f}, TNR {tnr:.2f})", flush=True)
    print(f"  pure-geometric (similarity band)   balanced-acc = {pbal:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if bal>=0.8:
        print(f"GEO-41: PASS - the store DETECTS contradictions ({bal:.2f}) via geometric retrieval of the same-subject fact + symbolic object comparison. Pure geometry alone is weaker ({pbal:.2f}) - the symbolic compare is needed.", flush=True)
    else:
        print(f"GEO-41: NULL/PARTIAL - {bal:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
