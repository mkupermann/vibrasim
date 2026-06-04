"""GEO-32b — re-run the GEO-32 abstention category WITH calibration (the legitimate GEO-23 method)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from geometric_reasoner import GeometricReasoner

EMP=[("Alice","data scientist","Analytics","Boston"),("Bob","backend engineer","Platform","Denver"),
     ("Carol","UX designer","Design","Austin"),("David","data scientist","Analytics","Boston"),
     ("Eve","site reliability engineer","Platform","Denver"),("Frank","product manager","Product","Seattle"),
     ("Grace","backend engineer","Platform","Denver"),("Heidi","UX designer","Design","Austin"),
     ("Ivan","data scientist","Analytics","Boston"),("Judy","product manager","Product","Seattle")]


def main():
    print("=== GEO-32b: abstention WITH dev-set calibration ===", flush=True)
    r=GeometricReasoner()
    for name,role,team,city in EMP:
        r.add_fact(f"{name} is a {role} on the {team} team.", subject=name, role=role, team=team, object=team)
        r.add_fact(f"The {team} team is based in {city}.", subject=team, object=city)
    # DEV split (labelled) — NOT the test questions
    dev_ans=["What team is Carol on?","Where is the Platform team based?","What does Eve do?"]
    dev_un =["What is the weather today?","What movie is playing?","How tall is the building?"]
    tau=r.calibrate_abstention(dev_ans, dev_un)
    # TEST out-of-KB (same as GEO-32) + held-out answerable
    test_un=["What is the capital of France?","Who is the CEO?","What is the stock price?"]
    test_ans=["What team is Alice on?","Where is the Design team based?"]
    ab=sum(1 for q in test_un if not r.ask(q)["grounded"])/len(test_un)
    an=sum(1 for q in test_ans if r.ask(q)["grounded"])/len(test_ans)
    print(f"  calibrated tau = {tau:.3f}", flush=True)
    print(f"  abstain on out-of-KB (test) = {ab:.2f}  (GEO-32 uncalibrated was 0.67)", flush=True)
    print(f"  answer on in-KB (test)      = {an:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if ab>=0.8 and an>=0.8:
        print("GEO-32b: PASS - calibrating the abstention threshold on a small labelled dev set (the GEO-23 method) lifts abstention to the bar without sacrificing in-KB answers. Closes the GEO-32 gap via the legitimate calibration path, not post-hoc tuning.", flush=True)
    else:
        print(f"GEO-32b: PARTIAL - abstain {ab:.2f}, answer {an:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
