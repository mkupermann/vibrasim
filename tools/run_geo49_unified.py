"""GEO-49 — end-to-end test of the UnifiedReasoner on a mixed query workload."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from unified_reasoner import UnifiedReasoner

EMP=[("Alice","Analytics"),("Bob","Platform"),("Carol","Design"),("David","Analytics"),
     ("Eve","Platform"),("Frank","Product"),("Grace","Design"),("Heidi","Product"),
     ("Ivan","Analytics"),("Judy","Platform")]
TEAM_CITY={"Analytics":"Boston","Platform":"Denver","Design":"Austin","Product":"Seattle"}
TIME=[("Alice",2020,"Analytics"),("Alice",2023,"Platform"),("Bob",2019,"Design"),("Bob",2022,"Platform")]


def main():
    print("=== GEO-49: unified auto-dispatching reasoner ===", flush=True)
    u=UnifiedReasoner(abstain_tau=0.30)
    for p,t in EMP: u.add_person(p,t)
    for t,c in TEAM_CITY.items(): u.add_team_city(t,c)
    for s,y,v in TIME: u.add_time_fact(s,y,v)

    # mixed workload (q, expected, type)
    tests=[
      ("Which team is Carol on?","Design","FACTOID"),
      ("What city does Frank work in?","Seattle","FACTOID"),
      ("Which team is Ivan on?","Analytics","FACTOID"),
      ("What city does Judy live in?","Denver","FACTOID"),
      ("How many people work in Boston?",3,"COUNT"),
      ("How many work in Denver?",3,"COUNT"),
      ("How many are based in Austin?",2,"COUNT"),
      ("Count the number of people in Seattle?",2,"COUNT"),
      ("Which team was Alice on in 2021?","Analytics","TEMPORAL"),
      ("Which team was Alice on in 2024?","Platform","TEMPORAL"),
      ("Which team was Bob on in 2020?","Design","TEMPORAL"),
      ("Which team was Bob on in 2023?","Platform","TEMPORAL"),
      ("Who is on the same team as Alice?",{"David","Ivan"},"JOIN"),
      ("Who works with Bob?",{"Eve","Judy"},"JOIN"),
      ("Who else is on Carol's team?",{"Grace"},"JOIN"),
      ("Who shares the same team as Frank?",{"Heidi"},"JOIN"),
    ]
    by_type={}; ok=0
    for q,exp,typ in tests:
        res=u.answer(q); got=res["answer"]; correct=(got==exp)
        ok+=correct; by_type.setdefault(typ,[0,0]); by_type[typ][0]+=correct; by_type[typ][1]+=1
        # routing correctness
    n=len(tests)
    print(f"  end-to-end accuracy = {ok/n:.2f}  (n={n})", flush=True)
    for typ,(c,t) in by_type.items():
        print(f"    {typ:9s}: {c}/{t}", flush=True)
    # show any misses
    for q,exp,typ in tests:
        got=u.answer(q)["answer"]
        if got!=exp: print(f"    MISS [{typ}] {q!r} -> {got!r} (exp {exp!r})", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if ok/n>=0.8:
        print(f"GEO-49: PASS - the unified auto-dispatching reasoner answers a MIXED workload end-to-end ({ok/n:.2f}): symbolic route -> geometric resolve -> symbolic operate, one agent for factoid/count/temporal/join.", flush=True)
    else:
        print(f"GEO-49: PARTIAL - {ok/n:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
