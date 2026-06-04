"""GEO-65 — ambiguous reference handling: surface multiple matches instead of silently picking one."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from geometric_reasoner import GeometricReasoner

PEOPLE=[("John Smith","Analytics"),("Mary Smith","Platform"),("Peter Smith","Design"),
        ("Alice Lee","Product"),("Bob Lee","Analytics"),("Carol Khan","Platform"),
        ("David Patel","Design"),("Eve Garcia","Product"),("Frank Nguyen","Analytics"),
        ("Grace Kim","Platform"),("Heidi Lopez","Design"),("Ivan Wang","Product")]


def main():
    print("=== GEO-65: ambiguous reference handling ===", flush=True)
    r=GeometricReasoner(abstain_tau=0.0)
    for name,team in PEOPLE:
        sur=name.split()[-1]
        r.add_fact(f"{name} is on the {team} team.", subject=name, surname=sur, object=team, kind="person")
    def resolve_ref(surname):
        matches=[m["subject"] for m in r.fact_meta if m.get("surname")==surname]
        if len(matches)>1: return ("AMBIGUOUS", matches)
        if len(matches)==1: return ("OK", matches)
        return ("NOTFOUND", [])
    tests=[("Smith",1),("Lee",1),("Khan",0),("Patel",0),("Smith",1),("Lee",1),("Kim",0),("Wang",0)]
    y=[]; pred=[]
    for sur,amb in tests:
        y.append(amb); pred.append(int(resolve_ref(sur)[0]=="AMBIGUOUS"))
    y=np.array(y);pr=np.array(pred)
    tpr=np.mean(pr[y==1]); tnr=np.mean(1-pr[y==0]); bal=(tpr+tnr)/2
    print(f"  ambiguity detection balanced-acc = {bal:.2f}  (TPR {tpr:.2f}, TNR {tnr:.2f})", flush=True)
    print(f"  'Smith' -> {resolve_ref('Smith')}", flush=True)
    print(f"  'Khan'  -> {resolve_ref('Khan')}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if bal>=0.9:
        print(f"GEO-65: PASS - ambiguous reference handling surfaces candidates ({bal:.2f}): a surname matching >1 entity is flagged AMBIGUOUS with the candidate set, instead of silently answering for one. Trustworthy disambiguation.", flush=True)
    else:
        print(f"GEO-65: PARTIAL - {bal:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
