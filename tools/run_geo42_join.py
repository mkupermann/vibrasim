"""GEO-42 — relational JOIN queries: geometric resolve + symbolic join/compare."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from geometric_reasoner import GeometricReasoner

EMP=[("Alice","Analytics"),("Bob","Platform"),("Carol","Design"),("David","Analytics"),
     ("Eve","Platform"),("Frank","Product"),("Grace","Design"),("Heidi","Product"),
     ("Ivan","Analytics"),("Judy","Platform"),("Mike","Design"),("Nina","Product")]
TEAM_CITY={"Analytics":"Boston","Platform":"Denver","Design":"Austin","Product":"Seattle"}


def f1(pred,true):
    p=set(pred); t=set(true)
    if not p and not t: return 1.0
    tp=len(p&t); prec=tp/len(p) if p else 0; rec=tp/len(t) if t else 0
    return 0.0 if prec+rec==0 else 2*prec*rec/(prec+rec)


def main():
    print("=== GEO-42: relational join queries ===", flush=True)
    r=GeometricReasoner(abstain_tau=0.30)
    for p,team in EMP:
        r.add_fact(f"{p} is on the {team} team.", subject=p, object=team)
    for team,city in TEAM_CITY.items():
        r.add_fact(f"The {team} team is based in {city}.", subject=team, object=city)
    def city_of(p):
        h=r.chain([f"What team is {p} on?","Where is the {bridge} team based?"])
        return h[-1].get("object") if h else None
    def team_of(p):
        j,_=r.retrieve(f"What team is {p} on?"); return r.fact_meta[j].get("object") if j is not None else None
    # (A) same-city joins
    f1s=[]
    for p,_ in EMP:
        c=city_of(p)
        pred=[q for q,_ in EMP if q!=p and city_of(q)==c]
        truth=[q for q,qt in EMP if q!=p and TEAM_CITY[qt]==TEAM_CITY[dict(EMP)[p]]]
        f1s.append(f1(pred,truth))
    A=sum(f1s)/len(f1s)
    # (B) same-team comparison
    import itertools
    pairs=list(itertools.combinations([p for p,_ in EMP],2))[:12]
    correct=0
    for x,y in pairs:
        pred= team_of(x)==team_of(y)
        truth= dict(EMP)[x]==dict(EMP)[y]
        correct+= int(pred==truth)
    B=correct/len(pairs)
    print(f"  (A) same-city join mean F1   = {A:.2f}", flush=True)
    print(f"  (B) same-team comparison acc = {B:.2f}  (n={len(pairs)})", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if A>=0.7 and B>=0.8:
        print(f"GEO-42: PASS - relational JOIN queries work: geometric entity resolution + symbolic join/compare answers same-city sets (F1 {A:.2f}) and same-team comparisons ({B:.2f}). Richer-than-chaining relational reasoning over the store.", flush=True)
    else:
        print(f"GEO-42: PARTIAL/NULL - A {A:.2f}, B {B:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
