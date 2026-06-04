"""GEO-62 — query-time conflict handling: surface inconsistent facts instead of silently picking one."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from geometric_reasoner import GeometricReasoner

CONSISTENT=[("Alice","Analytics"),("Bob","Platform"),("Carol","Design"),("David","Analytics"),("Eve","Platform"),("Frank","Product")]
CONFLICT=[("Grace",["Design","Platform"]),("Heidi",["Product","Analytics"]),("Ivan",["Analytics","Design"]),
          ("Judy",["Platform","Product"]),("Mike",["Design","Analytics"]),("Nina",["Product","Platform"])]


def main():
    print("=== GEO-62: query-time conflict handling ===", flush=True)
    r=GeometricReasoner(abstain_tau=0.0)
    for p,t in CONSISTENT: r.add_fact(f"{p} is on the {t} team.", subject=p, object=t, kind="person")
    for p,teams in CONFLICT:
        for t in teams: r.add_fact(f"{p} is on the {t} team.", subject=p, object=t, kind="person")
    def conflict_aware(person):
        objs={m["object"] for m in r.fact_meta if m.get("subject")==person and m.get("kind")=="person"}
        return ("CONFLICT", objs) if len(objs)>1 else ("OK", objs)
    # evaluate: consistent should be OK, conflicting should be CONFLICT
    y=[0]*len(CONSISTENT)+[1]*len(CONFLICT); pred=[]
    for p,_ in CONSISTENT: pred.append(int(conflict_aware(p)[0]=="CONFLICT"))
    for p,_ in CONFLICT: pred.append(int(conflict_aware(p)[0]=="CONFLICT"))
    y=np.array(y);pr=np.array(pred)
    tpr=np.mean(pr[y==1]); tnr=np.mean(1-pr[y==0]); bal=(tpr+tnr)/2
    print(f"  conflict detection balanced-acc = {bal:.2f}  (TPR {tpr:.2f}, TNR {tnr:.2f})", flush=True)
    print(f"  example: Grace -> {conflict_aware('Grace')}", flush=True)
    print(f"  example: Alice -> {conflict_aware('Alice')}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if bal>=0.9:
        print(f"GEO-62: PASS - query-time conflict handling SURFACES inconsistency ({bal:.2f}): gather same-subject facts, flag if >1 distinct object. A trustworthy store reports data conflicts at query time instead of silently returning one answer.", flush=True)
    else:
        print(f"GEO-62: PARTIAL - {bal:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
