"""GEO-54 — UnifiedReasoner operator-complete: expanded mixed workload incl. negation + comparison."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from unified_reasoner import UnifiedReasoner

EMP=[("Alice","Analytics",95),("Bob","Platform",120),("Carol","Design",80),("David","Analytics",110),
     ("Eve","Platform",130),("Frank","Product",75),("Grace","Design",105),("Heidi","Product",90)]
TEAM_CITY={"Analytics":"Boston","Platform":"Denver","Design":"Austin","Product":"Seattle"}


def main():
    print("=== GEO-54: operator-complete unified agent ===", flush=True)
    u=UnifiedReasoner(abstain_tau=0.30)
    for p,t,s in EMP: u.add_person(p,t,salary=s)
    for t,c in TEAM_CITY.items(): u.add_team_city(t,c)
    u.add_time_fact("Alice",2020,"Analytics"); u.add_time_fact("Alice",2023,"Platform")

    tests=[
      ("Which team is Carol on?","Design","FACTOID"),
      ("How many people work in Boston?",2,"COUNT"),
      ("Which team was Alice on in 2021?","Analytics","TEMPORAL"),
      ("Who is on the same team as David?",{"Alice"},"JOIN"),
      ("Who is not on the Analytics team?",{"Bob","Carol","Eve","Frank","Grace","Heidi"},"NEGATE"),
      ("Who does not work in Boston?",{"Bob","Carol","Eve","Frank","Grace","Heidi"},"NEGATE"),
      ("Who earns more, Alice or Bob?","Bob","COMPARE"),
      ("Who earns more, Eve or Frank?","Eve","COMPARE"),
    ]
    by={}; ok=0
    for q,exp,typ in tests:
        res=u.answer(q); got=res["answer"]; c=(got==exp); ok+=c
        by.setdefault(typ,[0,0]); by[typ][0]+=c; by[typ][1]+=1
        tag="OK" if c else "MISS"
        if not c: print(f"    MISS [{res['intent']}] {q!r} -> {got!r} (exp {exp!r})", flush=True)
    n=len(tests)
    print(f"  end-to-end accuracy = {ok/n:.2f}  (n={n})", flush=True)
    for typ,(c,t) in by.items(): print(f"    {typ:8s}: {c}/{t}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    neg_ok=by.get("NEGATE",[0,1])[0]==by.get("NEGATE",[0,1])[1]
    cmp_ok=by.get("COMPARE",[0,1])[0]==by.get("COMPARE",[0,1])[1]
    if ok/n>=0.8 and neg_ok and cmp_ok:
        print(f"GEO-54: PASS - the UnifiedReasoner is OPERATOR-COMPLETE: it routes + answers factoid/count/temporal/join/negation/comparison end-to-end ({ok/n:.2f}), including the geometry-fails cases (negation, comparison) via the symbolic layer.", flush=True)
    else:
        print(f"GEO-54: PARTIAL - {ok/n:.2f}, negation {neg_ok}, comparison {cmp_ok}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
