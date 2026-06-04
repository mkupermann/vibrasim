"""GEO-77 — symbolic counterfactual simulation over the structured store."""
import re

EMP={"Alice":"Analytics","Bob":"Platform","Carol":"Design","David":"Analytics","Eve":"Platform","Frank":"Product"}


def members(team_map, team):
    return {p for p,t in team_map.items() if t==team}


def counterfactual(query):
    # parse "if <P> moved to <T>, who would be on <S>?"
    m=re.search(r"if (\w+) moved to (\w+).*on (\w+)", query, re.I)
    if not m: return None
    p,newt,askt=m.group(1),m.group(2),m.group(3)
    sim=dict(EMP); 
    if p in sim: sim[p]=newt
    return members(sim, askt)


def f1(pred,true):
    p=set(pred);t=set(true)
    if not p and not t: return 1.0
    tp=len(p&t); pr=tp/len(p) if p else 0; rc=tp/len(t) if t else 0
    return 0.0 if pr+rc==0 else 2*pr*rc/(pr+rc)


def main():
    print("=== GEO-77: symbolic counterfactual simulation ===", flush=True)
    tests=[
      ("If Bob moved to Design, who would be on Platform?",{"Eve"}),
      ("If Bob moved to Design, who would be on Design?",{"Carol","Bob"}),
      ("If Alice moved to Product, who would be on Analytics?",{"David"}),
      ("If Eve moved to Analytics, who would be on Platform?",{"Bob"}),
      ("If Carol moved to Platform, who would be on Design?",set()),
      ("If David moved to Product, who would be on Product?",{"Frank","David"}),
      ("If Frank moved to Platform, who would be on Platform?",{"Bob","Eve","Frank"}),
      ("If Alice moved to Design, who would be on Analytics?",{"David"}),
    ]
    f1s=[]
    for q,exp in tests:
        pred=counterfactual(q); s=f1(pred,exp); f1s.append(s)
        if s<1.0: print(f"    [{s:.2f}] {q!r} -> {pred} (exp {exp})", flush=True)
    mean=sum(f1s)/len(f1s)
    print(f"  counterfactual-simulation mean-F1 = {mean:.2f}  (n={len(tests)})", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if mean>=0.85:
        print(f"GEO-77: PASS - symbolic SIMULATION answers store-manipulable counterfactuals ({mean:.2f}): copy the store, apply the hypothetical change, re-query. Extends the system from 'abstain on what-ifs' to 'answer the answerable what-ifs'. (One class only: membership changes; causal/open counterfactuals remain out of scope, GEO-75.)", flush=True)
    else:
        print(f"GEO-77: PARTIAL - {mean:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
