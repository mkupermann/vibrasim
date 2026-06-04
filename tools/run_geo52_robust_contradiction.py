"""GEO-52 — same-subject pre-filter improves contradiction detection on a mixed store."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from geometric_reasoner import GeometricReasoner

PEOPLE=["Alice","Bob","Carol","David","Eve","Frank","Grace","Heidi","Ivan","Judy","Mike","Nina"]
TEAMS=["Analytics","Platform","Design","Analytics","Platform","Product","Design","Product","Analytics","Platform","Design","Product"]
TEAM_CITY={"Analytics":"Boston","Platform":"Denver","Design":"Austin","Product":"Seattle"}


def main():
    print("=== GEO-52: robust contradiction (same-subject filter) ===", flush=True)
    r=GeometricReasoner(abstain_tau=0.0)
    for p,t in zip(PEOPLE,TEAMS):
        r.add_fact(f"{p} is on the {t} team.", subject=p, object=t, kind="person")
    for t,c in TEAM_CITY.items():
        r.add_fact(f"The {t} team is based in {c}.", subject=t, object=c, kind="team")  # collision source
    alt={"Analytics":"Platform","Platform":"Design","Design":"Product","Product":"Analytics"}
    cand=[]; label=[]
    for i in range(8): cand.append((PEOPLE[i],alt[TEAMS[i]])); label.append(1)        # contradictory
    for i in range(4): cand.append((PEOPLE[i],TEAMS[i])); label.append(0)             # consistent (same)
    for i in range(4): cand.append((f"New{i}",TEAMS[i])); label.append(0)             # new person
    # (a) embedding-nearest (current module)
    def emb_check(p,t):
        v=r._embed([f"{p} is on the {t} team."])[0]; j=int(np.argmax(r.F@v))
        m=r.fact_meta[j]; return int(m.get("subject")==p and m.get("object") not in (None,t))
    # (b) same-subject pre-filter
    def subj_check(p,t):
        for m in r.fact_meta:
            if m.get("subject")==p and m.get("kind")=="person" and m.get("object") not in (None,t):
                return 1
        return 0
    def bal(fn):
        pred=[fn(p,t) for p,t in cand]; y=np.array(label); pr=np.array(pred)
        tpr=np.mean(pr[y==1]); tnr=np.mean(1-pr[y==0]); return (tpr+tnr)/2,tpr,tnr
    a, at,an=bal(emb_check); b,bt,bn=bal(subj_check)
    print(f"  (a) embedding-nearest  bal-acc = {a:.2f}  (TPR {at:.2f}, TNR {an:.2f})", flush=True)
    print(f"  (b) same-subject filter bal-acc = {b:.2f}  (TPR {bt:.2f}, TNR {bn:.2f})", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if b>=0.9 and b>=a:
        print(f"GEO-52: PASS - same-subject pre-filter is robust on mixed stores ({b:.2f} vs embedding-nearest {a:.2f}); avoids token-collision misses. Hardening confirmed - adopt same-subject filtering for contradiction detection.", flush=True)
    else:
        print(f"GEO-52: PARTIAL - subj-filter {b:.2f}, embedding {a:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
