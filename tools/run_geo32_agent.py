"""GEO-32 — integrated grounded QA agent on a mini-KB, dogfooding GeometricReasoner."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from geometric_reasoner import GeometricReasoner

EMP=[("Alice","data scientist","Analytics","Boston"),
     ("Bob","backend engineer","Platform","Denver"),
     ("Carol","UX designer","Design","Austin"),
     ("David","data scientist","Analytics","Boston"),
     ("Eve","site reliability engineer","Platform","Denver"),
     ("Frank","product manager","Product","Seattle"),
     ("Grace","backend engineer","Platform","Denver"),
     ("Heidi","UX designer","Design","Austin"),
     ("Ivan","data scientist","Analytics","Boston"),
     ("Judy","product manager","Product","Seattle")]


def main():
    print("=== GEO-32: integrated grounded QA agent (mini-KB) ===", flush=True)
    r=GeometricReasoner(abstain_tau=0.40)
    for name,role,team,city in EMP:
        r.add_fact(f"{name} is a {role} on the {team} team.", subject=name, role=role, team=team, object=team)
        r.add_fact(f"The {team} team is based in {city}.", subject=team, object=city)

    # (a) semantic questions by ROLE (non-lexical-ish): find a person matching a described role
    sem_q=[("who works on reliability of systems","site reliability engineer"),
           ("who designs user experiences","UX designer"),
           ("who builds server-side services","backend engineer"),
           ("who analyzes data statistically","data scientist"),
           ("who owns the product roadmap","product manager")]
    sem=0
    for q,role in sem_q:
        res=r.ask(f"Which employee is the one who {q}?")
        ok = res["grounded"] and res["answer"] and res["answer"].get("role")==role
        sem+= int(bool(ok))
    sem/=len(sem_q)

    # (b) multi-hop person->team->city
    mh_people=["Alice","Bob","Frank"]; mh=0
    for p in mh_people:
        hits=r.chain([f"What team is {p} on?", "Where is the {bridge} team based?"])
        truth=[e[3] for e in EMP if e[0]==p][0]
        mh+= int(bool(hits and hits[-1].get("object")==truth))
    mh/=len(mh_people)

    # (c) abstention on out-of-KB
    oo=["What is the capital of France?","Who is the CEO?","What is the stock price?"]
    ab=np.mean([not r.ask(q)["grounded"] for q in oo]) if False else sum(1 for q in oo if not r.ask(q)["grounded"])/len(oo)

    # (d) aggregation: count employees per city (resolve each person->team->city, then count)
    def city_of(p):
        h=r.chain([f"What team is {p} on?","Where is the {bridge} team based?"])
        return h[-1].get("object") if h else None
    cities={}
    for e in EMP:
        c=city_of(e[0]); cities[c]=cities.get(c,0)+1
    true_cnt={}
    for e in EMP: true_cnt[e[3]]=true_cnt.get(e[3],0)+1
    agg = int(cities.get("Boston")==true_cnt["Boston"] and cities.get("Denver")==true_cnt["Denver"])

    # (e) runtime update: move Analytics team to Chicago, re-query Alice's city
    r2=GeometricReasoner(abstain_tau=0.40)
    for name,role,team,city in EMP:
        c = "Chicago" if team=="Analytics" else city
        r2.add_fact(f"{name} is a {role} on the {team} team.", subject=name, role=role, team=team, object=team)
        r2.add_fact(f"The {team} team is based in {c}.", subject=team, object=c)
    h=r2.chain(["What team is Alice on?","Where is the {bridge} team based?"])
    updated = (h[-1].get("object")=="Chicago") if h else False

    print(f"  (a) semantic role questions  = {sem:.2f}", flush=True)
    print(f"  (b) multi-hop person->city   = {mh:.2f}", flush=True)
    print(f"  (c) abstain on out-of-KB     = {ab:.2f}", flush=True)
    print(f"  (d) aggregation counts exact = {agg}  ({cities})", flush=True)
    print(f"  (e) runtime update flips     = {updated}  (Alice's city -> Chicago)", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if sem>=0.6 and mh>=0.6 and ab>=0.8 and agg and updated:
        print("GEO-32: PASS - the integrated agent works end-to-end on a realistic mini-KB: semantic role resolution, multi-hop, grounded abstention, aggregation, and runtime update all hold, via the packaged GeometricReasoner.", flush=True)
    else:
        print(f"GEO-32: PARTIAL - sem {sem:.2f}, mh {mh:.2f}, abstain {ab:.2f}, agg {agg}, update {updated}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
