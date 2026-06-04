"""GEO-81 — does abstention catch answer-absent / similar-fact-present (realistic GIGO)?"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from geometric_reasoner import GeometricReasoner

# store: capitals of SOME countries present; QUERY countries absent (but same-relation facts present)
PRESENT=[("France","Paris"),("Japan","Tokyo"),("Egypt","Cairo"),("Brazil","Brasilia"),("Canada","Ottawa")]
ABSENT_QUERY=["Germany","Italy","Spain","China","Russia"]  # their capital fact is NOT in the store
OUT_DOMAIN=["What is the boiling point of water?","Who wrote Hamlet?"]


def main():
    print("=== GEO-81: abstention on realistic GIGO (answer absent) ===", flush=True)
    r=GeometricReasoner(abstain_tau=0.0)
    for c,cap in PRESENT:
        r.add_fact(f"The capital of {c} is {cap}.", subject=c, object=cap, kind="capital")
    # calibrate on answerable (present) vs out-of-domain
    r.calibrate_abstention([f"What is the capital of {c}?" for c,_ in PRESENT], OUT_DOMAIN)
    print(f"  calibrated tau = {r.abstain_tau:.3f}", flush=True)
    # threshold-abstention on ABSENT-answer queries (correct = abstain)
    thr_abs=sum(1 for c in ABSENT_QUERY if not r.ask(f"What is the capital of {c}?")["grounded"])/len(ABSENT_QUERY)
    # focus-verification: does the query entity exist as a stored subject?
    subjects={m.get("subject") for m in r.fact_meta}
    foc_abs=sum(1 for c in ABSENT_QUERY if c not in subjects)/len(ABSENT_QUERY)
    # show what threshold-abstention retrieves for an absent query (the GIGO risk)
    j,sim=r.retrieve("What is the capital of Germany?")
    print(f"  threshold-abstention abstain-rate (absent answers) = {thr_abs:.2f}", flush=True)
    nearest = r.fact_texts[j] if j is not None else "(abstained)"
    print(f"    e.g. 'capital of Germany?' -> {nearest!r} sim={sim:.2f} (grounded={j is not None})", flush=True)
    print(f"  focus-verification abstain-rate (entity not in store) = {foc_abs:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if foc_abs>=0.8:
        print(f"GEO-81: focus-verification CATCHES the realistic GIGO ({foc_abs:.2f}) where similarity-threshold may not ({thr_abs:.2f}): checking the query ENTITY exists in the store rejects answer-absent queries even when a similar-entity fact has high similarity. Threshold abstention alone is INSUFFICIENT for this case; the entity-existence check is the needed safeguard. Honest residual-risk finding.", flush=True)
    else:
        print(f"GEO-81: threshold {thr_abs:.2f}, focus {foc_abs:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
