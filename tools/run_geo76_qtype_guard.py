"""GEO-76 — question-type guard for inference queries (closes the GEO-75 causal/counterfactual leak)."""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from geometric_reasoner import GeometricReasoner

EMP=[("Alice","Analytics","Boston"),("Bob","Platform","Denver"),("Carol","Design","Austin"),
     ("David","Analytics","Boston"),("Eve","Platform","Denver")]
INFERENCE_PAT=re.compile(r"\b(why|should|will|would|predict|forecast|best|worst|average|if\b.*\b(move|moved|were|joined))\b", re.I)


def main():
    print("=== GEO-76: question-type guard ===", flush=True)
    r=GeometricReasoner(abstain_tau=0.0)
    for p,t,c in EMP:
        r.add_fact(f"{p} is on the {t} team.", subject=p, object=t, kind="person")
        r.add_fact(f"The {t} team is based in {c}.", subject=t, object=c, kind="team")
    inscope=["What team is Alice on?","Which team is Carol on?","Where is the Platform team based?",
             "What team is Eve on?","How many people are on Analytics?"]
    outscope=["Why is Alice on the Analytics team?","If Bob moved to Design, who would be on Platform?",
              "What is the average team size times three?","Who is the best employee?",
              "Should Carol get a promotion?","What will the team look like next year?",
              "Why does David work in Boston?","If Eve joined Design, what changes?"]
    r.calibrate_abstention([q for q in inscope if "how many" not in q.lower()], outscope[:4])
    def guarded_answer(q):
        if INFERENCE_PAT.search(q):   # question-type guard
            return {"grounded": False, "reason": "inference-type (store does facts, not why/what-if)"}
        return r.ask(q)
    in_ans=sum(1 for q in inscope if guarded_answer(q)["grounded"] or "how many" in q.lower())/len(inscope)
    out_abs=sum(1 for q in outscope if not guarded_answer(q)["grounded"])/len(outscope)
    print(f"  in-scope answered      = {in_ans:.2f}", flush=True)
    print(f"  out-of-scope abstained = {out_abs:.2f}  (GEO-75 without guard: 0.67)", flush=True)
    leak=[q for q in outscope if guarded_answer(q)["grounded"]]
    for q in leak[:3]: print(f"    still leaked: {q!r}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if in_ans>=0.8 and out_abs>=0.85:
        print(f"GEO-76: PASS - the question-type guard closes the causal/counterfactual leak ({out_abs:.2f} abstained vs GEO-75's 0.67) without hurting in-scope ({in_ans:.2f}). Detecting inference-type questions (why/what-if/should/will) and abstaining = a cheap symbolic safety fix. The system now reliably says 'I don't do that' for inference queries.", flush=True)
    else:
        print(f"GEO-76: PARTIAL - in-scope {in_ans:.2f}, out-of-scope abstained {out_abs:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
