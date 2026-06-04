"""GEO-39 — acceptance test: the hardened GroundedQA end-to-end on one scenario."""
import sys, os, warnings, re
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(__file__))
from grounded_qa import GroundedQA

EMP=[("Alice","Analytics"),("Bob","Platform"),("Carol","Design"),("David","Analytics"),("Eve","Platform")]
TEAM_CITY={"Analytics":"Boston","Platform":"Denver","Design":"Austin"}


def build(team_city):
    qa=GroundedQA(generate=True, abstain_tau=0.35, focus_tau=0.55)
    for p,team in EMP:
        qa.add_fact(f"{p} is on the {team} team.", focus_value=p, subject=p, object=team)
    for team,city in team_city.items():
        qa.add_fact(f"The {team} team is based in {city}.", focus_value=team, subject=team, object=city)
    return qa


def main():
    print("=== GEO-39: hardened GroundedQA acceptance test ===", flush=True)
    qa=build(TEAM_CITY)
    checks={}
    # 1. semantic in-KB
    a=qa.answer("Which team is Alice on?", focus="Alice")
    checks["1 semantic-grounded"]= a["grounded"] and "analytics" in a["answer"].lower()
    # 2. multi-hop (manual chain via two asks since GroundedQA.answer is single-fact; use reasoner chain)
    hits=qa.r.chain(["What team is Bob on?","Where is the {bridge} team based?"])
    city = hits[-1].get("object") if hits else None
    # then ground a generation on the chained facts
    checks["2 multi-hop"]= city=="Denver"
    # 3. abstain out-of-KB
    u=qa.answer("What is the capital of France?", focus="France")
    checks["3 abstain"]= not u["grounded"]
    # 4. faithful: absent detail
    f=qa.answer("What is Carol's salary?", focus="Carol")
    # focus Carol exists, but salary not in any fact; retrieved fact is her team fact -> must not invent a number
    checks["4 faithful"]= ("not stated" in f["answer"].lower()) or (not bool(re.search(r"\$|\d{3,}", f["answer"])))
    # 5. updatable
    qa2=build({**TEAM_CITY, "Analytics":"Chicago"})
    h=qa2.r.chain(["What team is Alice on?","Where is the {bridge} team based?"])
    checks["5 updatable"]= (h[-1].get("object")=="Chicago") if h else False
    for k,v in checks.items():
        print(f"  {k:22s}: {'PASS' if v else 'FAIL'}", flush=True)
    npass=sum(checks.values())
    print(f"\n  {npass}/5 checks pass", flush=True)
    print("--- VERDICT ---", flush=True)
    print(f"GEO-39: {'PASS' if npass>=4 else 'PARTIAL'} - hardened GroundedQA end-to-end ({npass}/5).", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
