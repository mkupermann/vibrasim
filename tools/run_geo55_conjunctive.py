"""GEO-55 — conjunctive multi-constraint queries: extract multiple constraints + symbolic AND-filter."""
import re

PEOPLE=["Alice","Bob","Carol","David","Eve","Frank","Grace","Heidi","Ivan","Judy","Mike","Nina"]
TEAMS=["Analytics","Platform","Design","Analytics","Platform","Product","Design","Product","Analytics","Platform","Design","Product"]
SAL=[95,120,80,110,130,75,105,90,140,100,85,115]
TEAM_CITY={"Analytics":"Boston","Platform":"Denver","Design":"Austin","Product":"Seattle"}
ROWS=[{"name":p,"team":t,"city":TEAM_CITY[t],"salary":s} for p,t,s in zip(PEOPLE,TEAMS,SAL)]
TEAMSET=set(TEAMS); CITYSET=set(TEAM_CITY.values())


def f1(pred,true):
    p=set(pred);t=set(true)
    if not p and not t: return 1.0
    tp=len(p&t); pr=tp/len(p) if p else 0; rc=tp/len(t) if t else 0
    return 0.0 if pr+rc==0 else 2*pr*rc/(pr+rc)


def constraints(q):
    """Extract conjunctive constraints from the query."""
    cons=[]
    for tm in TEAMSET:
        if tm.lower() in q.lower(): cons.append(lambda r,tm=tm: r["team"]==tm)
    for c in CITYSET:
        if c.lower() in q.lower(): cons.append(lambda r,c=c: r["city"]==c)
    m=re.search(r"more than (\d+)", q.lower())
    if m: thr=int(m.group(1)); cons.append(lambda r,thr=thr: r["salary"]>thr)
    m=re.search(r"less than (\d+)", q.lower())
    if m: thr=int(m.group(1)); cons.append(lambda r,thr=thr: r["salary"]<thr)
    return cons


def answer(q):
    cons=constraints(q)
    return [r["name"] for r in ROWS if all(c(r) for c in cons)] if cons else []


def main():
    print("=== GEO-55: conjunctive multi-constraint queries ===", flush=True)
    tests=[
      ("Who is on Analytics and earns more than 100?",["David","Ivan"]),
      ("Who is on Platform and earns more than 110?",["Bob","Eve","Nina"]),
      ("Who works in Boston and earns less than 100?",["Alice"]),
      ("Who is on Design and based in Austin?",["Carol","Grace","Mike"]),
      ("Who is on Product and earns less than 100?",["Frank","Heidi"]),
      ("Who works in Denver and earns more than 100?",["Bob","Eve","Nina"]),
      ("Who is on Analytics and earns less than 100?",["Alice"]),
      ("Who is on Product and based in Seattle?",["Frank","Heidi","Nina"]),
    ]
    f1s=[]
    for q,exp in tests:
        pred=answer(q); s=f1(pred,exp); f1s.append(s)
        if s<1.0: print(f"    [{s:.2f}] {q!r} -> {sorted(pred)} (exp {sorted(exp)})", flush=True)
    mean=sum(f1s)/len(f1s)
    print(f"  conjunctive query mean-F1 = {mean:.2f}  (n={len(tests)})", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if mean>=0.85:
        print(f"GEO-55: PASS - the system composes CONJUNCTIVE constraints ({mean:.2f}): extract multiple constraints (team/city/salary-threshold) + symbolic AND-filter. Multi-constraint queries work.", flush=True)
    else:
        print(f"GEO-55: PARTIAL/NULL - {mean:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
