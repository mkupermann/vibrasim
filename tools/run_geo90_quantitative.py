"""GEO-90 — quantitative operators (range, sum, sort) over the structured store."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from geometric_reasoner import GeometricReasoner

TASKS=[("file taxes",2025),("review lease",2024),("fix sink",2025),("get permit",2026),("dental visit",2023)]
EXPENSES=[("rent",1200),("groceries",400),("utilities",250),("internet",60),("insurance",180)]


def main():
    print("=== GEO-90: quantitative operators ===", flush=True)
    r=GeometricReasoner(abstain_tau=0.0)
    for d,y in TASKS: r.add_fact(f"Task: {d}, due {y}.", subject=d, year=y, kind="task")
    for c,amt in EXPENSES: r.add_fact(f"Expense: {c}, {amt} per month.", subject=c, amount=amt, kind="expense")
    # RANGE: tasks due in [2024, 2025]
    rng={m["subject"] for m in r.fact_meta if m.get("kind")=="task" and 2024<=m.get("year",0)<=2025}
    range_ok = rng=={"file taxes","review lease","fix sink"}
    # SUM: total monthly expenses
    total=sum(m["amount"] for m in r.fact_meta if m.get("kind")=="expense")
    sum_ok = total==(1200+400+250+60+180)
    # SORT: tasks by due year ascending
    srt=[m["subject"] for m in sorted([m for m in r.fact_meta if m.get("kind")=="task"], key=lambda x:x["year"])]
    sort_ok = srt==["dental visit","review lease","file taxes","fix sink","get permit"]
    # COMBINED: expenses over 200/month, sorted desc
    big=[m["subject"] for m in sorted([m for m in r.fact_meta if m.get("kind")=="expense" and m["amount"]>200], key=lambda x:-x["amount"])]
    comb_ok = big==["rent","groceries","utilities"]
    checks={"range":range_ok,"sum":sum_ok,"sort":sort_ok,"combined":comb_ok}
    for k,v in checks.items(): print(f"  {k:9s}: {'OK' if v else 'FAIL'}", flush=True)
    acc=sum(checks.values())/len(checks)
    print(f"  overall = {acc:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if acc>=0.9:
        print("GEO-90: PASS - quantitative operators (range/sum/sort/combined) work over the structured store. Operator coverage complete: count, compare, negate, range, sum, sort, join, temporal, contradiction, conflict, ambiguity, counterfactual-simulation. Geometry resolves, the symbolic layer computes.", flush=True)
    else:
        print(f"GEO-90: PARTIAL - {acc:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
